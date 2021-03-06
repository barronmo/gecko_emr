import wx, os, sys
import EMR_utilities, settings
import EMR_formats
import Billing, CreateCMS, CarePlan
import Printer
import decimal
from itertools import chain
from collections import Counter
from nltk.tokenize import wordpunct_tokenize

lt = settings.LINUXPATH
at = settings.APPLEPATH
wt = settings.WINPATH
d = EMR_utilities.platformText(lt, at, wt)
sys.path.insert(0, d + '/ts_project.rc1')
import timestamping
del sys.path[0]

class Notes(wx.Panel):
    def __init__(self, parent, id, ptID):
        wx.Panel.__init__(self, parent, id)

	self.PtID = ptID
	self.textctrl = {}
	self.not_billable = 0
	self.note_number = ''
	textcontrols1 = [('Date', 100)]
	textcontrols2 = [('ICD #1', 60), ('ICD #2', 60), ('ICD #3', 60), ('ICD #4', 60), ('ICD #5', 60)]
	textcontrols3 = [('ICD #6', 60), ('ICD #7', 60), ('ICD #8', 60), ('ICD #9', 60), ('ICD #10', 60)]
	cptsizer = wx.BoxSizer(wx.VERTICAL)
	icd1sizer = wx.BoxSizer(wx.VERTICAL)
	icd2sizer = wx.BoxSizer(wx.VERTICAL)
	icdMainSizer = wx.BoxSizer(wx.HORIZONTAL)
	for label, size in textcontrols1:
	    EMR_utilities.buildOneTextCtrl(self, label, size, cptsizer)
	for label, size in textcontrols2:
	    EMR_utilities.buildOneTextCtrl(self, label, size, icd1sizer)
	for label, size in textcontrols3:
	    EMR_utilities.buildOneTextCtrl(self, label, size, icd2sizer)
	icdMainSizer.Add(icd1sizer)
	icdMainSizer.Add(icd2sizer)
	cptsizer.Add(icdMainSizer)
	cptsizer.Add((-1,10))
	cptsizer.Add(wx.StaticText(self, -1, 'Select a template:'))
	self.tmplist = wx.ListBox(self, -1, pos=wx.DefaultPosition, size=(90, 110), choices = ['generic', 'prenatal', \
		       'procedure', 'phonecon', 'well child'], style=wx.LB_HSCROLL)
	self.Bind(wx.EVT_LISTBOX, self.EvtSelTmplist, self.tmplist)
	self.Bind(wx.EVT_TEXT, self.OnTextEnterICD, self.textctrl['ICD #1'])
	self.Bind(wx.EVT_TEXT, self.OnTextEnterICD, self.textctrl['ICD #2'])
	self.Bind(wx.EVT_TEXT, self.OnTextEnterICD, self.textctrl['ICD #3'])
	self.Bind(wx.EVT_TEXT, self.OnTextEnterICD, self.textctrl['ICD #4'])
	self.Bind(wx.EVT_TEXT, self.OnTextEnterICD, self.textctrl['ICD #5'])
	self.Bind(wx.EVT_TEXT, self.OnTextEnterICD, self.textctrl['ICD #6'])
	self.Bind(wx.EVT_TEXT, self.OnTextEnterICD, self.textctrl['ICD #7'])
	self.Bind(wx.EVT_TEXT, self.OnTextEnterICD, self.textctrl['ICD #8'])
	self.Bind(wx.EVT_TEXT, self.OnTextEnterICD, self.textctrl['ICD #9'])
	self.Bind(wx.EVT_TEXT, self.OnTextEnterICD, self.textctrl['ICD #10'])
	#for some reason the EVT_KILL_FOCUS does not bind with the above method, ie self.bind
	self.textctrl['ICD #1'].Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusICD)
	self.textctrl['ICD #2'].Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusICD)
	self.textctrl['ICD #3'].Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusICD)
	self.textctrl['ICD #4'].Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusICD)
	self.textctrl['ICD #5'].Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusICD)
	self.textctrl['ICD #6'].Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusICD)
	self.textctrl['ICD #7'].Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusICD)
	self.textctrl['ICD #8'].Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusICD)
	self.textctrl['ICD #9'].Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusICD)
	self.textctrl['ICD #10'].Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusICD)
	
	cptsizer.Add(self.tmplist)
	cptsizer.Add((-1, 10))
	exambutton = EMR_utilities.buildOneButton(self, self, 'Exam', self.OnExamBtn, cptsizer)
	cpbutton = EMR_utilities.buildOneButton(self, self, 'Care Plan', self.OnCarePlanBtn, cptsizer)
	self.billBtn = EMR_utilities.buildOneButton(self, self, 'Billing', self.OnBillBtn, cptsizer)
	#self.CMSbutton = EMR_utilities.buildOneButton(self, self, 'Create 1500', self.OnCMSbutton, cptsizer)
	self.HCFAbutton = EMR_utilities.buildOneButton(self, self, 'Create HCFA', self.OnHCFAbutton, cptsizer)
	self.PtBillBtn = EMR_utilities.buildOneButton(self, self, 'Bill Pt', self.OnBillPt, cptsizer)

	#self.printData = wx.PrintData()
        #self.printData.SetPaperId(wx.PAPER_LETTER)
        #self.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)

	soapsizer = wx.BoxSizer(wx.VERTICAL)
	soapLabel = wx.StaticText(self, -1, 'SOAP Note')	
	self.soapNote = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
	self.soapNote.Show(False)
	self.newsoapNote = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
	soapsizer.Add(soapLabel, 0, wx.ALIGN_TOP|wx.ALIGN_LEFT, 5)
	soapsizer.Add(self.soapNote, 1, wx.EXPAND)
	soapsizer.Add(self.newsoapNote, 1, wx.EXPAND)
			
	buttons = [('Save', self.OnSave), ('New', self.OnNew), ('Print', self.OnPrint), ('PDF', self.OnPDF), ('Sign', self.OnSign)]
	leftsizer = wx.BoxSizer(wx.VERTICAL)
	for label, handler in buttons:
	    EMR_utilities.buildOneButton(self, self, label, handler, leftsizer)
	self.listctrl = wx.ListBox(self, -1, pos=wx.DefaultPosition, size=(145,200), choices = [], style=wx.LB_HSCROLL)
	leftsizer.AddMany([(-1, 20), (wx.StaticText(self, -1, 'Select a note:')), (self.listctrl)])
	self.Bind(wx.EVT_LISTBOX, self.EvtSelListBox, self.listctrl)
	self.Bind(wx.EVT_LISTBOX_DCLICK, self.EvtSelListBox, self.listctrl)

	mainsizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.AddMany([(leftsizer, 0, wx.ALL, 10),(soapsizer, 1, wx.EXPAND|wx.ALL, 10),(cptsizer, 0, wx.ALL, 10)])
	self.SetSizer(mainsizer)
	self.loadList()

    def loadList(self):
	#self.listctrl.Set("")
	qry = 'SELECT * FROM notes WHERE patient_ID = %s ORDER BY date DESC;' % (self.PtID)
	self.results = EMR_utilities.getAllData(qry)
	for items in self.results:
	    self.listctrl.Append(str(items[3]))	
	  

    def OnNew(self, event):
	self.soapNote.Show(False)
	self.newsoapNote.Show(True)
	self.Layout()
	self.textctrl['Date'].SetValue(str(EMR_utilities.dateToday(t='sql')))
	self.billBtn.Show(False)
	#self.CMSbutton.Show(False)
	
		
    def OnSave(self, event):
	if self.textctrl['ICD #1'].GetValue():
	    #look to see which note is being saved, new vs old
	    prnt = wx.GetTopLevelParent(self)
	    if self.newsoapNote.IsShownOnScreen():
		qry = 'INSERT INTO notes (patient_ID, soap, date, icd1, icd2, icd3, icd4, icd5, \
		    icd6, icd7, icd8, icd9, icd10, not_billable, user) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		values = (self.PtID, self.newsoapNote.GetValue(), EMR_utilities.strToDate(self.textctrl['Date'].GetValue()), 
		    self.textctrl['ICD #1'].GetValue(), self.textctrl['ICD #2'].GetValue(), 
		    self.textctrl['ICD #3'].GetValue(), self.textctrl['ICD #4'].GetValue(), 
		    self.textctrl['ICD #5'].GetValue(), self.textctrl['ICD #6'].GetValue(),
		    self.textctrl['ICD #7'].GetValue(), self.textctrl['ICD #8'].GetValue(),
		    self.textctrl['ICD #9'].GetValue(), self.textctrl['ICD #10'].GetValue(),self.not_billable, prnt.user)
		EMR_utilities.valuesUpdateData(qry, values)
	    else:
		#check to see if note has already been signed
		checkQry = 'SELECT stamp FROM notes WHERE patient_ID = "%s" AND date = "%s";' % (self.PtID, self.textctrl['Date'].GetValue())
		nullCheck = EMR_utilities.getData(checkQry)
		if nullCheck[0]:
		    wx.MessageBox('No changes allowed; note has already been signed.', 'Message')
		else:
		    qry = 'UPDATE notes SET soap = %s, user = %s WHERE patient_ID = %s AND date = %s'
		    values = (self.soapNote.GetValue(), prnt.user, self.PtID, self.textctrl['Date'].GetValue())
		    EMR_utilities.valuesUpdateData(qry, values)
	    self.listctrl.Set("")
	    self.loadList()
	    self.textctrl['Date'].SetValue("")
	    self.soapNote.SetValue("")
	    self.newsoapNote.SetValue("")
	    self.billBtn.Show(True)
	else:
	    wx.MessageBox('You forgot to enter an ICD-9 Code', 'Grave Mistake!')

    def OnSign(self, event):
        #check to see if note has already been signed
        checkQry = 'SELECT stamp FROM notes WHERE patient_ID = "%s" AND date = "%s";' % (self.PtID, self.textctrl['Date'].GetValue())
        nullCheck = EMR_utilities.getData(checkQry)
        try:
            if nullCheck[0]:
                wx.MessageBox('Note has already been signed.', 'Message')
            else:
                #get user
                prnt = wx.GetTopLevelParent(self)
                userQry = EMR_utilities.getData('SELECT full_name FROM users WHERE user_name = "%s";' % prnt.user)
                #add signed text at bottom of note
                note = self.soapNote.GetValue() + '\n\n' + 'ELECTRONICALLY SIGNED BY %s ON %s' % (userQry[0], str(EMR_utilities.dateToday(t='sql')))
                #use timestamper
                cli = timestamping.ts_client.TimeStampClient('http://198.199.64.101:8000')
                data = str(self.PtID) + note + self.textctrl['Date'].GetValue()
                val = cli.stamp(data)
                #update the record for that note to include utctime and stamp 
                noteQry = 'UPDATE notes SET soap = %s, utctime = %s, stamp = %s  WHERE patient_ID = %s AND date = %s'
                values = (note, val['utctime'], val['stamp'], self.PtID, self.textctrl['Date'].GetValue())
                EMR_utilities.valuesUpdateData(noteQry, values)
                self.listctrl.Set("")
                self.loadList() 
        except: 
            # catch *all* exceptions
            e0 = sys.exc_info()[0]
            e1 = sys.exc_info()[1]
            wx.MessageBox("Error: %s, %s" % (e0, e1))
            #wx.MessageBox('Please save the note first, then sign.', 'Message')
	
	    
	
    def EvtSelListBox(self, event):
	"""Problem: because the notes are displayed based on date, if there are more than one note with the same date
	   they will get displayed together in the text control in series.  To fix this I need to add another column 
	   for note_number to the listctrl which is not visible and then reference that number rather than the date 
	   so that notes can be displayed by their ID number.""" 
	#self.loadList()
	self.textctrl['Date'].SetValue("")
	self.soapNote.SetValue("")
	self.textctrl['Date'].AppendText(event.GetString())
	self.newsoapNote.Show(False)
	self.soapNote.Show(True)
	self.Layout()
	for items in self.results:
	    if str(items[3]) == event.GetString():
		self.soapNote.AppendText(items[2])
		try:
		    for i in range(1,11):
			self.textctrl['ICD #%s' % i].SetValue(items[i + 3])
		except: print 'Error: icd value would not set, line 197, Notes.py. Probably a NULL somewhere.'
		#self.textctrl['ICD #1'].SetValue(items[4])
		#self.textctrl['ICD #2'].SetValue(items[5])
		#self.textctrl['ICD #3'].SetValue(items[6])
		#self.textctrl['ICD #4'].SetValue(items[7])
		#self.textctrl['ICD #5'].SetValue(items[8])
		#self.textctrl['ICD #6'].SetValue(items[9])
		#self.textctrl['ICD #7'].SetValue(items[10])
		#self.textctrl['ICD #8'].SetValue(items[11])
		#self.textctrl['ICD #9'].SetValue(items[12])
		#self.textctrl['ICD #10'].SetValue(items[13])
	    else: pass
	self.note_number = EMR_utilities.getData('SELECT note_number FROM notes WHERE date = "%s";' % (event.GetString()))
	
	
    def EvtSelTmplist(self, event):
	lt = "/home/mb/Desktop/GECKO/wellchild/%s.txt"
	at = ""
	wt = "C:\Documents and Settings\mbarron\My Documents\GECKO\wellchild\%s.txt"
	if event.GetString() == 'generic':
	    gen_note = EMR_formats.note(self.PtID)
	    if wx.GetTopLevelParent(self).nb.GetPage(2).reviewed == 1:
		gen_note = gen_note.replace('Meds', 'Meds(reviewed today)')
		gen_note = gen_note.replace('Allergies', 'Allergies(reviewed today)')
	    self.newsoapNote.SetValue(gen_note)
	    self.not_billable = 0
	elif event.GetString() == 'prenatal':
	    self.newsoapNote.SetValue(EMR_formats.prenatal(self.PtID))
	elif event.GetString() == 'procedure':
	    self.newsoapNote.SetValue(EMR_formats.procedure(self.PtID))
	elif event.GetString() == 'phonecon':
	    self.newsoapNote.SetValue(EMR_formats.phonecon(self.PtID))
	    self.not_billable = 1
	elif event.GetString() == 'well child':
	    choice = wx.GetSingleChoice('What age child?', "", ['Wt Check', '2 month', '4 month', '6 month', '9 month',
		'12 month', '15 month', '18 month', '2 year', '3-4 year', '6-7_yr_old', '7-8 year', '10-11_yr_old', 
		'12-13_yr_old', '9-12 year', '13-15 year'])
	    string = open(EMR_utilities.platformText(lt, at, wt) % choice, 'r')
	    s = string.read()
	    string.close()
	    result = s % (EMR_utilities.getAge(self.PtID), EMR_utilities.getSex(self.PtID), 
		EMR_formats.getVitals(self.PtID, baby=1))
	    self.newsoapNote.SetValue(result)
	    self.not_billable = 0
	else: pass

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
        if self.soapNote.IsShown():
            note = self.soapNote.GetValue() 
        else:
            note = self.newsoapNote.GetValue()
        qry = 'SELECT firstname, lastname \
                FROM demographics \
                WHERE patient_ID = "%s";' % self.PtID
        print_data = EMR_utilities.getDictData(qry)
        print_data['date'] = self.textctrl['Date'].GetValue()
        print_data['soap'] = EMR_utilities.wrapper(note, 80)
	print print_data['soap']
	lt = "%s/EMR_outputs/SoapNote.html" % settings.LINUXPATH
	at = "%s/EMR_outputs/SoapNote.html" % settings.APPLEPATH
	wt = "%s\EMR_outputs\SoapNote.html" % settings.WINPATH
        form = open(EMR_utilities.platformText(lt, at, wt), 'r')
        s = form.read()
        form.close()        
        note_text = s % (print_data)
        printer = EMR_utilities.Printer()
	printer.PreviewText(note_text)

    def OnPDF(self, event):
	if self.soapNote.IsShown():
	    EMR_utilities.notePDF(self.PtID, self.soapNote.GetValue(), visit_date=self.textctrl['Date'].GetValue())
	else:
	    EMR_utilities.notePDF(self.PtID, self.newsoapNote.GetValue(), visit_date=self.textctrl['Date'].GetValue())

    def OnExamBtn(self, event):
	exam = Exam(self, -1, 'Select elements of exam', self.PtID)
	exam.Show(True)
	exam.notesinstance = self

    def OnCarePlanBtn(self, event):
	#check to make sure a note has been stared
	if self.newsoapNote.GetValue() == '':
	    #if there is a saved note for today, start care plan
	    if self.soapNote.GetValue():
		#check to make sure a care plan has not already been created; can only use it once
		qry = 'SELECT * FROM education WHERE date = "%s" AND patient_ID = "%s";' % (EMR_utilities.dateToday(), self.PtID)
		results = EMR_utilities.getData(qry)
		if results:
		    dlg = wx.MessageDialog(None, "A saved care plan for today already exists.  Look in the Education tab.", "Important", wx.OK)
		    dlg.ShowModal()
		else:
		    if self.GetParent().GetPage(7).neweducNote.GetValue() == '':
			cp = CarePlan.CarePlanFrame(self, self.PtID)
			cp.Show(True)
			cp.notesinstance = self
		    else:
			dlg = wx.MessageDialog(None, "A new care plan for today already exists.  Look in the Education tab.", "Important", wx.OK)
			dlg.ShowModal()
	    #now we know there is neither a new or saved note, so give error message
	    else:
		dlg = wx.MessageDialog(None, "Please start a note before starting care plan.", "Important", wx.OK)
		dlg.ShowModal()
	else:
	    #check to make sure a care plan has not already been created; can only use it once
	    qry = 'SELECT * FROM education WHERE date = "%s" AND patient_ID = "%s";' % (EMR_utilities.dateToday(), self.PtID)
	    results = EMR_utilities.getData(qry)
	    if results:
		dlg = wx.MessageDialog(None, "A saved care plan for today already exists.  Look in the Education tab.", "Important", wx.OK)
		dlg.ShowModal()
	    else:
		if self.GetParent().GetPage(7).neweducNote.GetValue() == '':
		    cp = CarePlan.CarePlanFrame(self, self.PtID)
		    cp.Show(True)
		    cp.notesinstance = self
		else:
		    dlg = wx.MessageDialog(None, "A new care plan for today already exists.  Look in the Education tab.", "Important", wx.OK)
		    dlg.ShowModal() 

    def OnBillBtn(self, event):
	bill = Billing.CptFrame(self, self.PtID, self.note_number)
	bill.Show(True)

    def OnHCFAbutton(self, event):
	hcfa = CreateCMS.cmsFrame(self, self.PtID)
	hcfa.Show(True)

    def OnBillPt(self, event):
	Printer.myPtBill(self.PtID)
	EMR_utilities.updateData('UPDATE billing SET ptDate = CURDATE() WHERE patient_ID = %s AND balance > 0;' % (self.PtID))
    
    def createOAText(self, fields, results, myfile):
	for items in fields:		#items from fields are in the correct order for Office Ally's tab delimited format
	    if results[items] == None:
		myfile.write('\t')
	    else:
		myfile.write(str(results[items]) + '\t')

    def OnTextEnterICD(self, event):
	#when user enters ' ' create single choice dialog with patient's problem list; inserts ICD code for selected problem
	if event.GetString() == ' ':
	    qry = "SELECT short_des FROM problems10 WHERE patient_ID = %s;" % (self.PtID)
	    results = EMR_utilities.getAllData(qry)
	    ptProbList = []
	    for items in results:
		ptProbList.append(items[0])
	    dialog = wx.SingleChoiceDialog(self, 'Select a problem', "Patient's Problem List", ptProbList)
	    if dialog.ShowModal() == wx.ID_OK:
		try:
		    r = EMR_utilities.getData('SELECT icd10 FROM ICD10billable WHERE short_des = "%s" AND billable = "1";' % dialog.GetStringSelection())
		    event.EventObject.SetValue((r)[0])
		    event.EventObject.MarkDirty()
		except: 
		    wx.MessageBox('Not a billable ICD10 code.  Please fix on problem list.', 'Message')
	    else: pass
	#when user enters '?' pull up problem dialog to search for codes
	elif event.GetString() == 'g':
	    string = wx.GetTextFromUser("Search diagnosis list for ...")
	    qry = 'SELECT disease_name FROM icd_9 WHERE disease_name LIKE "%%%s%%";' % (string)
	    results = EMR_utilities.getAllData(qry)
	    probList = []
	    for items in results:
		probList.append(items[0])
	    dialog = wx.SingleChoiceDialog(self, 'Select a problem', 'Master Problem List', probList)
	    if dialog.ShowModal() == wx.ID_OK:
		q = 'SELECT icd_9 FROM icd_9 WHERE disease_name = "%s";' % (dialog.GetStringSelection())
		event.EventObject.SetValue(EMR_utilities.getData(q)[0])
		event.EventObject.MarkDirty()
	    else: pass
	elif event.GetString() == 'f':
	    #this option allows search of www.icd9data.com for specified term
	    term = wx.GetTextFromUser("Look up ICD-9 Code: eg, rotator+cuff")
	    string = 'https://icd10.clindesk.org/#/?q=%s' % term
	    results = EMR_utilities.HTML_Frame(self, "ICD-9 Help", html_str=string)
            results.Show()
	elif event.GetString() == '?':
	    code = icd10picker(self, self, -1, 'ICD 10 Finder')
	    self.icd10code = ''
	    if code.ShowModal() == wx.ID_OK:
		event.EventObject.SetValue(self.icd10code[0])
		event.EventObject.MarkDirty()
	    else: pass
	    code.Destroy()
	else: pass
	event.Skip()

    def OnKillFocusICD(self, event):
	#for item in dir(event.GetEventObject()):
	#    print item, ": ", getattr(event.GetEventObject(), item)
	
	if event.GetEventObject().IsModified():
	    #remove any decimal points
	    icd = event.GetEventObject().GetValue().replace('.', '')
	    #save any updates to the database
	    d = {"ICD #1":"icd1", "ICD #2":"icd2", "ICD #3":"icd3", "ICD #4":"icd4", "ICD #5":"icd5",
		 "ICD #6":"icd6", "ICD #7":"icd7", "ICD #8":"icd8", "ICD #9":"icd9", "ICD #10":"icd10"}
	    try:
		qry = 'UPDATE notes SET %s = "%s" WHERE date = "%s";' % (d[event.GetEventObject().Name], \
				icd, self.textctrl['Date'].GetValue())
		EMR_utilities.updateData(qry)
	    except:
		print 'icd query didnt work, line 374'
	    if icd == ' ' or icd == '?' or icd == 'f' or icd == 'g':
		pass	#setting these values was triggering the OnTextEnterICD resulting in two dialog boxes
	    else:
		event.GetEventObject().SetValue(icd)
	    qry = 'SELECT * FROM notes WHERE patient_ID = %s ORDER BY date DESC;' % (self.PtID)
	    self.results = EMR_utilities.getAllData(qry)
	    
	else: pass

class icd10picker(wx.Dialog):
    def __init__(self, instance, parent, id, title):
	wx.Dialog.__init__(self, parent, id, title, size=(1100, 600))

	self.results = []
	self.textctrl = {}
	self.parentInstance = instance
	mainSizer = wx.BoxSizer(wx.VERTICAL)
	textSizer = wx.BoxSizer(wx.HORIZONTAL)
	btnSizer = wx.StdDialogButtonSizer()
	listSizer = wx.BoxSizer(wx.HORIZONTAL)
	self.textctrl['Search'] = wx.TextCtrl(self, -1, size=(250, -1), name='Search', style=wx.TE_PROCESS_ENTER)
	self.textctrl['Refine'] = wx.TextCtrl(self, -1, size=(150, -1), name='Refine', style=wx.TE_PROCESS_ENTER)
	textSizer.AddMany([(wx.StaticText(self, -1, 'Search')), (self.textctrl['Search']), (wx.StaticText(self, -1, 'Refine')), (self.textctrl['Refine'])])
	clearButton = EMR_utilities.buildOneButton(self, self, 'Clear', self.OnClear, textSizer)
	self.resultListBox = wx.ListBox(self, -1, pos=wx.DefaultPosition, choices = [], size=(700,300), style=wx.LB_HSCROLL)
	self.refineListBox = wx.ListBox(self, -1, pos=wx.DefaultPosition, choices = [], size=(200,300), style=wx.LB_HSCROLL)
	listSizer.AddMany([self.resultListBox, (20, -1), self.refineListBox])
	self.Bind(wx.EVT_TEXT_ENTER, self.OnSearchEnter, self.textctrl['Search'])
	self.Bind(wx.EVT_TEXT_ENTER, self.OnRefineEnter, self.textctrl['Refine'])
	btnOK = wx.Button(self, wx.ID_OK)
	btnCL = wx.Button(self, wx.ID_CANCEL)
        btnOK.SetDefault()
	btnCL.SetDefault()
	btnSizer.AddButton(btnOK)
	btnSizer.AddButton(btnCL)
	btnSizer.Realize()
	self.Bind(wx.EVT_LISTBOX, self.EvtSelRefineList, self.refineListBox)
	self.Bind(wx.EVT_LISTBOX, self.EvtSelResultList, self.resultListBox)
	mainSizer.AddMany([(textSizer, 0, wx.ALL, 10), (listSizer, 0, wx.ALL, 10), (btnSizer, 0, wx.ALL, 10)])
	self.SetSizer(mainSizer)

    def OnSearchEnter(self, event):
	qry = 'SELECT * FROM ICD10billable WHERE short_des LIKE "%%%s%%" AND billable = "1";' % (event.GetString())
	self.results = EMR_utilities.getAllData(qry)
	short_des_list = []
	for items in self.results:
	    self.resultListBox.Append(str(items[4]))
	    short_des_list.append(items[4])
	#find common words in results and present them in the refine list
	refined = Counter(chain.from_iterable(wordpunct_tokenize(x) for x in short_des_list)).most_common(10)
	for items in refined:
	    if len(items[0]) > 3:
		self.refineListBox.Append(str(items).strip("()'").replace("'", ""))

    def OnClear(self, event):
	self.resultListBox.Clear()
	self.refineListBox.Clear()
	self.textctrl['Search'].SetValue("")
	self.textctrl['Refine'].SetValue("")
	self.results = []

    def OnRefineEnter(self, event):
	qry1 = '(SELECT * FROM ICD10billable WHERE short_des LIKE "%%%s%%" AND billable = "1")' % self.textctrl['Search'].GetValue()
	qry2 = 'SELECT * FROM %s AS custom WHERE short_des LIKE "%%%s%%";' % (qry1, event.GetString())
        self.results = EMR_utilities.getAllData(qry2)
	self.resultListBox.Clear()
	self.refineListBox.Clear()
	short_des_list = []
	for items in self.results:
	    self.resultListBox.Append(str(items[4]))
	    short_des_list.append(items[4])
	refined = Counter(chain.from_iterable(wordpunct_tokenize(x) for x in short_des_list)).most_common(10)
	for items in refined:
	    self.refineListBox.Append(str(items).strip("()'").replace("'", ""))

    def EvtSelRefineList(self, event):
	if self.refineListBox.GetSelection() == 0:
	    #this was done because after appending new values to refineListBox the selection event was being triggered a second time
	    pass   
	else:
	    qry1 = '(SELECT * FROM ICD10billable WHERE short_des LIKE "%%%s%%" AND billable = "1")' % self.textctrl['Search'].GetValue()
	    qry2 = 'SELECT * FROM %s AS custom WHERE short_des LIKE "%%%s%%";' % (qry1, event.GetString().split(',')[0])
            self.results = EMR_utilities.getAllData(qry2)
	    self.resultListBox.Clear()
	    self.refineListBox.Clear()
	    short_des_list = []
	    for items in self.results:
		self.resultListBox.Append(str(items[1]))
		short_des_list.append(items[1])
	    refined = Counter(chain.from_iterable(wordpunct_tokenize(x) for x in short_des_list)).most_common(10)
	    for items in refined:
		if len(items[0]) > 3:	#removes small words that aren't useful search terms like of, and, the
		    self.refineListBox.Append(str(items).strip("()'").replace("'", ""))

    def EvtSelResultList(self, event):
	qry = 'SELECT icd10 FROM ICD10billable WHERE short_des = "%s" AND billable = "1";' % event.GetString()
	self.parentInstance.icd10code = EMR_utilities.getData(qry)
		
	
class Exam(wx.Frame):
    def __init__(self, parent, id, title, PtID):
	wx.Frame.__init__(self, parent, id, title, size=(900, 900))

	self.exam = {}
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	gen = [('alert and oriented', self.OnGen1), ('no obvious distress', self.OnGen2)]
	CV = [('RRR', self.OnCV1), ('no murmurs', self.OnCV2), ('normal S1 and S2', self.OnCV3), ('no JVD', self.OnCV4)]
	lungs = [('clear to auscultation, bilat', self.OnLungs1), ('normal resp effort', self.OnLungs2)]
	abd = [('soft', self.OnAbd1), ('nontender', self.OnAbd2), ('no guarding or rebound', self.OnAbd3), ('no masses', self.OnAbd4), ('no HSM', self.OnAbd5)]
	lymph = [('no peripheral edema', self.OnLymph1), ('no cervical LAD', self.OnLymph2)]
	neuro = [('gait normal', self.OnNeuro1), ('speech normal', self.OnNeuro2), ('cognition intact', self.OnNeuro3), ('regards face', self.OnNeuro4), ('nl tone', self.OnNeuro5), ('CN 2-12 intact', self.OnNeuro6)]
	psych = [('mood normal', self.OnPsych1), ('affect normal', self.OnPsych2)]
	MS = [('no joint swelling', self.OnMS1), ('normal ROM', self.OnMS2), ('no hip clicks', self.OnMS3), ('no deformities', self.OnMS4)]
	HENT = [('thyroid normal', self.OnHENT1), ('trachea midline', self.OnHENT2), ('palate intact', self.OnHENT3), ('oropharynx normal', self.OnHENT4), ('TMs clear bilat', self.OnHENT5)]
	back = [('SLR neg bilat', self.OnBack1), ('no scoliosis', self.OnBack2), ('no spinal tenderness', self.OnBack3), ('no paraspinal tenderness', self.OnBack4)]
	eyes = [('sclera clear', self.OnEyes1), ('EOMI', self.OnEyes2), ('no strabismus', self.OnEyes3), ('pos RR bilat', self.OnEyes4), ('vision 20/20 bilat', self.OnEyes5)]
	GU = [('nl female', self.OnGU1), ('testes descended bilat', self.OnGU2), ('no inguinal hernia', self.OnGU3)]
	breast = [('no masses', self.OnBreast1), ('no dimpling', self.OnBreast2), ('no nipple retraction', self.OnBreast3)]
	pelvic = [('vagina normal', self.OnPelvic1), ('cervix normal', self.OnPelvic2), ('thin discharge', self.OnPelvic3), ('adnexa nontender', self.OnPelvic4), ('uterus nl size', self.OnPelvic5)]
	self.systems = [(gen, 'gen'), (CV, 'CV'), (lungs, 'lungs'), (abd, 'abd'), (lymph, 'lymph'), (neuro, 'neuro'), (psych, 'psych'), (MS, 'MS'), (HENT, 'HENT'), (back, 'back'), (eyes, 'eyes'), (GU, 'GU'), (breast, 'breast'), (pelvic, 'pelvic')]
	
	for i, n in self.systems:
	    sizer = wx.BoxSizer(wx.HORIZONTAL)
	    sizer.Add(wx.StaticText(self, -1, n))
	    sizer.Add((30, -1))
	    for label, handler in i:
		EMR_utilities.buildOneButton(self, self, label, handler, sizer) 
	    mainsizer.Add(sizer, 1, wx.EXPAND)
	    mainsizer.Add((-1, 5))
	    self.exam[n]=""

	button = wx.Button(self, -1, "Done")
	self.Bind(wx.EVT_BUTTON, self.OnDone, button)
	mainsizer.Add((-1, 40))
	mainsizer.Add(button, 0)
	self.SetSizer(mainsizer)

    def syschk(self, string, ckstr):
	if string.find(ckstr) == -1:
	    string = string + '%s: ' % ckstr
	else: pass
	return string

    def commachk(self, string, addstr):
	if string.endswith(': ') == True:
	    string = string + addstr
	else: 
	    string = string + ', ' + addstr
	return string

    def OnGen1(self, event):
	self.exam['gen'] = self.syschk(self.exam['gen'], 'Gen')
	self.exam['gen'] = self.commachk(self.exam['gen'], "alert and oriented")

    def OnGen2(self, event):
	self.exam['gen'] = self.syschk(self.exam['gen'], 'Gen')
	self.exam['gen'] = self.commachk(self.exam['gen'], "no obvious distress")

    def OnCV1(self, event):
	self.exam['CV'] = self.syschk(self.exam['CV'], 'CV')
	self.exam['CV'] = self.commachk(self.exam['CV'], "RRR")

    def OnCV2(self, event):
	self.exam['CV'] = self.syschk(self.exam['CV'], 'CV')
	self.exam['CV'] = self.commachk(self.exam['CV'], "no murmurs")

    def OnCV3(self, event):
	self.exam['CV'] = self.syschk(self.exam['CV'], 'CV')
	self.exam['CV'] = self.commachk(self.exam['CV'], "normal S1 and S2")

    def OnCV4(self, event):
	self.exam['CV'] = self.syschk(self.exam['CV'], 'CV')
	self.exam['CV'] = self.commachk(self.exam['CV'], "no JVD")

    def OnLungs1(self, event):
	self.exam['lungs'] = self.syschk(self.exam['lungs'], 'Lungs')
	self.exam['lungs'] = self.commachk(self.exam['lungs'], "clear to auscultation, bilat")

    def OnLungs2(self, event):
	self.exam['lungs'] = self.syschk(self.exam['lungs'], 'Lungs')
	self.exam['lungs'] = self.commachk(self.exam['lungs'], "normal resp effort")

    def OnAbd1(self, event):
	self.exam['abd'] = self.syschk(self.exam['abd'], 'Abd')
	self.exam['abd'] = self.commachk(self.exam['abd'], "soft")

    def OnAbd2(self, event):
	self.exam['abd'] = self.syschk(self.exam['abd'], 'Abd')
	self.exam['abd'] = self.commachk(self.exam['abd'], "nontender")

    def OnAbd3(self, event):
	self.exam['abd'] = self.syschk(self.exam['abd'], 'Abd')
	self.exam['abd'] = self.commachk(self.exam['abd'], "no guarding or rebound")

    def OnAbd4(self, event):
	self.exam['abd'] = self.syschk(self.exam['abd'], 'Abd')
	self.exam['abd'] = self.commachk(self.exam['abd'], "no masses")

    def OnAbd5(self, event):
	self.exam['abd'] = self.syschk(self.exam['abd'], 'Abd')
	self.exam['abd'] = self.commachk(self.exam['abd'], "no HSM")

    def OnLymph1(self, event):
	self.exam['lymph'] = self.syschk(self.exam['lymph'], 'Lymph')
	self.exam['lymph'] = self.commachk(self.exam['lymph'], "no peripheral edema")

    def OnLymph2(self, event):
	self.exam['lymph'] = self.syschk(self.exam['lymph'], 'Lymph')
	self.exam['lymph'] = self.commachk(self.exam['lymph'], "no cervical LAD")

    def OnNeuro1(self, event):
	self.exam['neuro'] = self.syschk(self.exam['neuro'], 'Neuro')
	self.exam['neuro'] = self.commachk(self.exam['neuro'], "gait normal")

    def OnNeuro2(self, event):
	self.exam['neuro'] = self.syschk(self.exam['neuro'], 'Neuro')
	self.exam['neuro'] = self.commachk(self.exam['neuro'], "speech normal")

    def OnNeuro3(self, event):
	self.exam['neuro'] = self.syschk(self.exam['neuro'], 'Neuro')
	self.exam['neuro'] = self.commachk(self.exam['neuro'], "cognition intact")

    def OnNeuro4(self, event):
	self.exam['neuro'] = self.syschk(self.exam['neuro'], 'Neuro')
	self.exam['neuro'] = self.commachk(self.exam['neuro'], "regards face")

    def OnNeuro5(self, event):
	self.exam['neuro'] = self.syschk(self.exam['neuro'], 'Neuro')
	self.exam['neuro'] = self.commachk(self.exam['neuro'], "normal tone")

    def OnNeuro6(self, event):
	self.exam['neuro'] = self.syschk(self.exam['neuro'], 'Neuro')
	self.exam['neuro'] = self.commachk(self.exam['neuro'], "CN 2-12 intact")

    def OnPsych1(self, event):
	self.exam['psych'] = self.syschk(self.exam['psych'], 'Psych')
	self.exam['psych'] = self.commachk(self.exam['psych'], "mood normal")

    def OnPsych2(self, event):
	self.exam['psych'] = self.syschk(self.exam['psych'], 'Psych')
	self.exam['psych'] = self.commachk(self.exam['psych'], "affect normal")

    def OnMS1(self, event):
	self.exam['MS'] = self.syschk(self.exam['MS'], 'MS')
	self.exam['MS'] = self.commachk(self.exam['MS'], "no joint swelling")

    def OnMS2(self, event):
	self.exam['MS'] = self.syschk(self.exam['MS'], 'MS')
	self.exam['MS'] = self.commachk(self.exam['MS'], "normal ROM")

    def OnMS3(self, event):
	self.exam['MS'] = self.syschk(self.exam['MS'], 'MS')
	self.exam['MS'] = self.commachk(self.exam['MS'], "no hip clicks")

    def OnMS4(self, event):
	self.exam['MS'] = self.syschk(self.exam['MS'], 'MS')
	self.exam['MS'] = self.commachk(self.exam['MS'], "no deformities")

    def OnHENT1(self, event):
	self.exam['HENT'] = self.syschk(self.exam['HENT'], 'HENT')
	self.exam['HENT'] = self.commachk(self.exam['HENT'], "thyroid normal")

    def OnHENT2(self, event):
	self.exam['HENT'] = self.syschk(self.exam['HENT'], 'HENT')
	self.exam['HENT'] = self.commachk(self.exam['HENT'], "trachea midline")

    def OnHENT3(self, event):
	self.exam['HENT'] = self.syschk(self.exam['HENT'], 'HENT')
	self.exam['HENT'] = self.commachk(self.exam['HENT'], "palate intact")

    def OnHENT4(self, event):
	self.exam['HENT'] = self.syschk(self.exam['HENT'], 'HENT')
	self.exam['HENT'] = self.commachk(self.exam['HENT'], "oropharynx normal")

    def OnHENT5(self, event):
	self.exam['HENT'] = self.syschk(self.exam['HENT'], 'HENT')
	self.exam['HENT'] = self.commachk(self.exam['HENT'], "TMs clear bilat")

    def OnBack1(self, event):
	self.exam['back'] = self.syschk(self.exam['back'], 'Back')
	self.exam['back'] = self.commachk(self.exam['back'], "SLR neg bilat")

    def OnBack2(self, event):
	self.exam['back'] = self.syschk(self.exam['back'], 'Back')
	self.exam['back'] = self.commachk(self.exam['back'], "no scoliosis")

    def OnBack3(self, event):
	self.exam['back'] = self.syschk(self.exam['back'], 'Back')
	self.exam['back'] = self.commachk(self.exam['back'], "no spinal tenderness")

    def OnBack4(self, event):
	self.exam['back'] = self.syschk(self.exam['back'], 'Back')
	self.exam['back'] = self.commachk(self.exam['back'], "no paraspinal tenderness")

    def OnEyes1(self, event):
	self.exam['eyes'] = self.syschk(self.exam['eyes'], 'Eyes')
	self.exam['eyes'] = self.commachk(self.exam['eyes'], "sclera clear")

    def OnEyes2(self, event):
	self.exam['eyes'] = self.syschk(self.exam['eyes'], 'Eyes')
	self.exam['eyes'] = self.commachk(self.exam['eyes'], "EOMI")

    def OnEyes3(self, event):
	self.exam['eyes'] = self.syschk(self.exam['eyes'], 'Eyes')
	self.exam['eyes'] = self.commachk(self.exam['eyes'], "no strabismus")

    def OnEyes4(self, event):
	self.exam['eyes'] = self.syschk(self.exam['eyes'], 'Eyes')
	self.exam['eyes'] = self.commachk(self.exam['eyes'], "pos red reflex bilat")

    def OnEyes5(self, event):
	self.exam['eyes'] = self.syschk(self.exam['eyes'], 'Eyes')
	self.exam['eyes'] = self.commachk(self.exam['eyes'], "vision 20/20 bilat")

    def OnGU1(self, event):
	self.exam['GU'] = self.syschk(self.exam['GU'], 'GU')
	self.exam['GU'] = self.commachk(self.exam['GU'], "nl female")

    def OnGU2(self, event):
	self.exam['GU'] = self.syschk(self.exam['GU'], 'GU')
	self.exam['GU'] = self.commachk(self.exam['GU'], "testes descended bilat")

    def OnGU3(self, event):
	self.exam['GU'] = self.syschk(self.exam['GU'], 'GU')
	self.exam['GU'] = self.commachk(self.exam['GU'], "no inguinal hernia")

    def OnBreast1(self, event):
	self.exam['breast'] = self.syschk(self.exam['breast'], 'Breast')
	self.exam['breast'] = self.commachk(self.exam['breast'], "no masses")

    def OnBreast2(self, event):
	self.exam['breast'] = self.syschk(self.exam['breast'], 'Breast')
	self.exam['breast'] = self.commachk(self.exam['breast'], "no dimpling")

    def OnBreast3(self, event):
	self.exam['breast'] = self.syschk(self.exam['breast'], 'Breast')
	self.exam['breast'] = self.commachk(self.exam['breast'], "no nipple retraction")

    def OnPelvic1(self, event):
	self.exam['pelvic'] = self.syschk(self.exam['pelvic'], 'Pelvic')
	self.exam['pelvic'] = self.commachk(self.exam['pelvic'], "vagina normal")

    def OnPelvic2(self, event):
	self.exam['pelvic'] = self.syschk(self.exam['pelvic'], 'Pelvic')
	self.exam['pelvic'] = self.commachk(self.exam['pelvic'], "cervix normal")

    def OnPelvic3(self, event):
	self.exam['pelvic'] = self.syschk(self.exam['pelvic'], 'Pelvic')
	self.exam['pelvic'] = self.commachk(self.exam['pelvic'], "thin discharge")

    def OnPelvic4(self, event):
	self.exam['pelvic'] = self.syschk(self.exam['pelvic'], 'Pelvic')
	self.exam['pelvic'] = self.commachk(self.exam['pelvic'], "adnexa nontender")

    def OnPelvic5(self, event):
	self.exam['pelvic'] = self.syschk(self.exam['pelvic'], 'Pelvic')
	self.exam['pelvic'] = self.commachk(self.exam['pelvic'], "uterus normal size")
	
    def OnDone(self, event):
	examstring = ""
	for i, n in self.systems: 
	    if self.exam[n] == "":
		pass
	    else: 
		examstring = examstring + self.exam[n] + '\n'
	if self.notesinstance.newsoapNote.IsShown():
	    self.notesinstance.newsoapNote.WriteText(examstring)
	else:
	    self.notesinstance.soapNote.WriteText(examstring)
	self.Destroy()
	
		
