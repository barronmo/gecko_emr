import wx, os, sys
import EMR_utilities, settings
import Printer


class Notes(wx.Panel):
    def __init__(self, parent, id, ptID):
        wx.Panel.__init__(self, parent, id)

	self.PtID = ptID
	self.textctrl = {}
	self.not_billable = 0
	textcontrols = [('Date', 100)]
	cptsizer = wx.BoxSizer(wx.VERTICAL)
	for label, size in textcontrols:
	    EMR_utilities.buildOneTextCtrl(self, label, size, cptsizer)
	cptsizer.Add((-1,10))
	cptsizer.Add(wx.StaticText(self, -1, 'Select a template:'))
	self.tmplist = wx.ListBox(self, -1, pos=wx.DefaultPosition, size=(90, 110), choices = ['HTN', 'DM', \
		       'Obesity', 'GI', 'Back Pain'], style=wx.LB_HSCROLL)
	self.Bind(wx.EVT_LISTBOX, self.EvtSelTmplist, self.tmplist)
		
	cptsizer.Add(self.tmplist)
	cptsizer.Add((-1, 10))
	
	noteSizer = wx.BoxSizer(wx.VERTICAL)
	noteLabel = wx.StaticText(self, -1, 'SOAP Note')	
	self.educNote = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
	self.educNote.Show(False)
	self.neweducNote = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
	noteSizer.Add(noteLabel, 0, wx.ALIGN_TOP|wx.ALIGN_LEFT, 5)
	noteSizer.Add(self.educNote, 1, wx.EXPAND)
	noteSizer.Add(self.neweducNote, 1, wx.EXPAND)
			
	buttons = [('Save', self.OnSave), ('New', self.OnNew), ('Print', self.OnPrint), ('PDF', self.OnPDF)]
	leftsizer = wx.BoxSizer(wx.VERTICAL)
	for label, handler in buttons:
	    EMR_utilities.buildOneButton(self, self, label, handler, leftsizer)
	self.listctrl = wx.ListBox(self, -1, pos=wx.DefaultPosition, size=(145,200), choices = [], style=wx.LB_HSCROLL)
	leftsizer.AddMany([(-1, 20), (wx.StaticText(self, -1, 'Select a note:')), (self.listctrl)])
	self.Bind(wx.EVT_LISTBOX, self.EvtSelListBox, self.listctrl)
	self.Bind(wx.EVT_LISTBOX_DCLICK, self.EvtSelListBox, self.listctrl)

	mainsizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.AddMany([(leftsizer, 0, wx.ALL, 10),(noteSizer, 1, wx.EXPAND|wx.ALL, 10),(cptsizer, 0, wx.ALL, 10)])
	self.SetSizer(mainsizer)
	self.loadList()

    def loadList(self):
	#self.listctrl.Set("")
	qry = 'SELECT * FROM education WHERE patient_ID = %s ORDER BY date DESC;' % (self.PtID)
	self.results = EMR_utilities.getAllData(qry)
	for items in self.results:
	    self.listctrl.Append(str(items[3]))	
	  

    def OnNew(self, event):
	self.educNote.Show(False)
	self.neweducNote.Show(True)
	self.Layout()
	self.textctrl['Date'].SetValue(str(EMR_utilities.dateToday(t='sql')))
			
		
    def OnSave(self, event):
	#look to see which note is being saved, new vs old
	if self.neweducNote.IsShownOnScreen():
	    qry = 'INSERT INTO education (patient_ID, note, date) VALUES (%s, %s, %s)'
	    values = (self.PtID, self.neweducNote.GetValue(), EMR_utilities.strToDate(self.textctrl['Date'].GetValue()))
	    EMR_utilities.valuesUpdateData(qry, values)
	else:
	    qry = 'UPDATE education SET note = %s WHERE patient_ID = %s AND date = %s'
	    values = (self.educNote.GetValue(), self.PtID, self.textctrl['Date'].GetValue())
	    EMR_utilities.valuesUpdateData(qry, values)
	self.listctrl.Set("")
	self.loadList()
	self.textctrl['Date'].SetValue("")
	self.educNote.SetValue("")
	self.neweducNote.SetValue("")
	
    
	
    def EvtSelListBox(self, event):
	"""Problem: because the notes are displayed based on date, if there are more than one note with the same date
	   they will get displayed together in the text control in series.  To fix this I need to add another column 
	   for note_number to the listctrl which is not visible and then reference that number rather than the date 
	   so that notes can be displayed by their ID number.""" 
	#self.loadList()
	self.textctrl['Date'].SetValue("")
	self.educNote.SetValue("")
	self.textctrl['Date'].AppendText(event.GetString())
	self.neweducNote.Show(False)
	self.educNote.Show(True)
	self.Layout()
	for items in self.results:
	    if str(items[3]) == event.GetString():
		self.educNote.AppendText(items[2])
	    else: pass
	self.educ_number = EMR_utilities.getData('SELECT educ_number FROM education WHERE date = "%s";' % (event.GetString()))
	
	
    def EvtSelTmplist(self, event):
	p = "%s/Education/%s.txt" % (settings.FILESHARE, event.GetString())
	f = open(p, "r+")
	wholefile = f.readlines()
	headings = []
	s = ""
	for line in wholefile:
	    if '>>' in line:
		headings.append(line.strip('>>\n'))
	choice = wx.MultiChoiceDialog(self, "Please choose one or more.", "", headings)
	choice.ShowModal()
	for item in choice.GetSelections():
	    s = s + headings[item] + '\n'
	    for line in wholefile:
		if str(item) in line:
		    s = s + line.strip(str(item))
	    s = s + '\n'
	if self.neweducNote.IsShownOnScreen():
	    self.neweducNote.WriteText(s) 
	else:
	    self.educNote.WriteText(s)
	f.close()
	
	
    def OnPageSetup(self, evt):
        psdd = wx.PageSetupDialogData(self.printData)
        psdd.CalculatePaperSizeFromId()
        dlg = wx.PageSetupDialog(self, psdd)
        dlg.ShowModal()

        # this makes a copy of the wx.PrintData instead of just saving
        # a reference to the one inside the PrintDialogData that will
        # be destroyed when the dialog is destroyed
        self.printData = wx.PrintData( dlg.GetPageSetupData().GetPrintData() )
        dlg.Destroy()

    def OnPrintPreview(self, event):
        data = wx.PrintDialogData(self.printData)
        printout = MyPrintout(self.canvas, self.log)
        printout2 = MyPrintout(self.canvas, self.log)
        self.preview = wx.PrintPreview(printout, printout2, data)

        if not self.preview.Ok():
            pass

        pfrm = wx.PreviewFrame(self.preview, self.frame, "This is a print preview")

        pfrm.Initialize()
        pfrm.SetPosition(self.frame.GetPosition())
        pfrm.SetSize(self.frame.GetSize())
        pfrm.Show(True)

    def OnPrint(self, event):
        if self.educNote.IsShown():
            note = self.educNote.GetValue() 
        else:
            note = self.neweducNote.GetValue()
        qry = 'SELECT firstname, lastname \
                FROM demographics \
                WHERE patient_ID = "%s";' % self.PtID
        print_data = EMR_utilities.getDictData(qry)
        print_data['date'] = self.textctrl['Date'].GetValue()
        print_data['note'] = EMR_utilities.wrapper(note, 80)
	lt = "%s/EMR_outputs/educNote.html" % settings.LINUXPATH
	at = "%s/EMR_outputs/educNote.html" % settings.APPLEPATH
	wt = "%s\EMR_outputs\educNote.html" % settings.WINPATH
        form = open(EMR_utilities.platformText(lt, at, wt), 'r')
        s = form.read()
        form.close()        
        note_text = s % (print_data)
        printer = EMR_utilities.Printer()
	printer.PreviewText(note_text)

    def OnPDF(self, event):
	if self.educNote.IsShown():
	    EMR_utilities.notePDF(self.PtID, self.educNote.GetValue(), visit_date=self.textctrl['Date'].GetValue())
	else:
	    EMR_utilities.notePDF(self.PtID, self.neweducNote.GetValue(), visit_date=self.textctrl['Date'].GetValue())

