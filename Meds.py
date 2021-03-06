import wx
import MySQLdb, sys, time
import EMR_utilities, EMR_formats, settings
from ObjectListView import ObjectListView, ColumnDefn, EVT_CELL_EDIT_STARTING, EVT_CELL_EDIT_FINISHED

class Meds(wx.Panel):
    def __init__(self, parent, id, ptID):
        wx.Panel.__init__(self, parent, id)

        self.ptID = ptID
	self.toggler = 'Current Meds'
	self.reviewed = 0
	meds = med_find(ptID)
	self.list = ObjectListView(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
	self.list.SetColumns([
            ColumnDefn("Name", "left", 250, valueGetter="med_name"),
            ColumnDefn("Dose", "center", 180, valueGetter="dose"),
            ColumnDefn("Tablets", "center", 60, valueGetter="number_tablets"),
            ColumnDefn("Route", "left", 60, valueGetter="route"),
            ColumnDefn("Frequency", "left", 80, valueGetter="frequency"),
            ColumnDefn("#", "center", 40, valueGetter="number_pills"),
            ColumnDefn("Refills", "center", 50, valueGetter="refills"),
            ColumnDefn("Date", "left", 100, valueGetter="script_date")
            ])
	self.list.SetObjects(meds)
	self.list.cellEditMode = ObjectListView.CELLEDIT_DOUBLECLICK
	self.list.Bind(EVT_CELL_EDIT_STARTING, self.HandleCellEditStarting)
	self.list.Bind(EVT_CELL_EDIT_FINISHED, self.listHandleCellEditFinished)
	
	leftmed = wx.BoxSizer(wx.VERTICAL)
	rightmed = wx.BoxSizer(wx.VERTICAL)		
	mainmed = wx.BoxSizer(wx.HORIZONTAL)

	medbuttons = (('Archive', self.OnArchMed),
		   ('Print', self.OnpRintMed),
		   ('Delete', self.OnDeleteMed),
		   ('Toggle', self.OnToggleMed),
                   ('Interactions', self.OnInteractions),
		   ('Reviewed', self.OnReviewed))
	for label, handler in medbuttons:
	    EMR_utilities.buildOneButton(self, self, label, handler, leftmed)

	
	allergies = allergy_find(ptID)
	self.allergylist = ObjectListView(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
	self.allergylist.SetColumns([
            ColumnDefn("Allergy", "left", 200, valueGetter = "allergy"),
            ColumnDefn("Reaction", "left", 250, valueGetter = "reaction")
            ])
	self.allergylist.SetObjects(allergies)
	self.allergylist.cellEditMode = ObjectListView.CELLEDIT_DOUBLECLICK
        self.allergylist.Bind(EVT_CELL_EDIT_STARTING, self.HandleCellEditStarting)
        self.allergylist.Bind(EVT_CELL_EDIT_FINISHED, self.allergyHandleCellEditFinished)
	
	leftall = wx.BoxSizer(wx.VERTICAL)
	rightall = wx.BoxSizer(wx.VERTICAL)
	mainall = wx.BoxSizer(wx.HORIZONTAL)

	allbuttons = (('Add', self.OnNewAll, leftall), ('Remove', self.OnRemAll, leftall))	
	for label, handler, sizer in allbuttons:
	    EMR_utilities.buildOneButton(self, self, label, handler, sizer)
	addmed = AddMed(self, -1, self.ptID)
#Set the sizers	that have not already been set
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	rightmed.Add(self.list, 1, wx.EXPAND | wx.TOP, 3)
	self.medtitle = wx.StaticText(self, -1, self.toggler)
	titlefont = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)
	self.medtitle.SetFont(titlefont)
	mainmed.Add(leftmed, 0)
	mainmed.Add((15, -1))
	mainmed.Add(rightmed, 1, wx.EXPAND)
	rightall.Add(self.allergylist, 1, wx.EXPAND | wx.TOP, 3)
	rightmed.Add(addmed, 1, wx.EXPAND)
	mainall.Add(leftall, 0)
	mainall.Add((15, -1))
	mainall.Add(rightall, 1, wx.EXPAND)
	mainsizer.Add(mainall, 2, wx.EXPAND)
	mainsizer.Add(self.medtitle, 0, wx.ALIGN_CENTER | wx.ALL, 5)
	mainsizer.Add(mainmed, 4, wx.EXPAND)
	mainsizer.Add((-1, 5))
		
        self.SetSizer(mainsizer)
        self.Centre()
        self.Show(True)


    def OnArchMed(self, event):		#need add/edit form pulled up on selected meds, update query, requery meds 
        #open AddEditMed form with selected/checked med filled in
        obj = self.list.GetSelectedObjects()
        for items in obj:
            qry = 'UPDATE meds SET archive = 1 WHERE med_number = %s;' % items['med_number']
            self.list.RemoveObject(items)
            EMR_utilities.updateData(qry)
	
    def OnpRintMed(self, event):
        obj = self.list.GetSelectedObjects()
        string = ''
        for items in obj:
            string = '%s %s\n   take %s %s %s   #%s refills: %s\n\n' % \
                     (items["med_name"],
                      items["dose"],
                      items["number_tablets"],
                      items["route"],
                      items["frequency"],
                      items["number_pills"],
                      items["refills"]) + string
        
	form_lt = "%s/EMR_outputs/Script.html" % settings.LINUXPATH
	form_at = "%s/EMR_outputs/Script.html" % settings.APPLEPATH
	form_wt = "%s\EMR_outputs\Script.html" % settings.WINPATH
        form = open(EMR_utilities.platformText(form_lt, form_at, form_wt), 'r')
	s = form.read()
	form.close()
	dem_data = EMR_utilities.getDictData('SELECT * FROM demographics WHERE patient_ID = %s;' % self.ptID)
	dem_data['string'] = string
	dem_data['date'] = EMR_utilities.dateToday()
	dem_data['name_address'] = EMR_formats.format_address(dem_data)
	script_text = s % (dem_data)
	printer = EMR_utilities.Printer()
	printer.PreviewText(script_text)
	path_lt = "%s/EMR_outputs/%s/Orders" % (settings.LINUXPATH, self.ptID)
	path_at = "%s/EMR_outputs/%s/Orders" % (settings.APPLEPATH, self.ptID)
	path_wt = "%s\EMR_outputs\%s\Orders" % (settings.WINPATH, self.ptID)
	path = EMR_utilities.platformText(path_lt, path_at, path_wt)
	filename = "%s/script%s.html" % (path, EMR_utilities.dateToday(t='file format'))
	f = open(filename, 'w')
	f.write(script_text)
	f.close()	

    def OnDeleteMed(self, event):
        obj = self.list.GetSelectedObjects()
        for items in obj:
            qry = 'DELETE FROM meds WHERE med_number = %s;' % items['med_number']
            self.list.RemoveObject(items)
            EMR_utilities.updateData(qry)
	
    def OnToggleMed(self, event):
	if self.toggler == 'Current Meds':
	    self.toggler = 'Archived Meds'
	    self.medtitle.SetLabel(self.toggler)
	    qry = 'SELECT * FROM meds WHERE archive = 1 AND patient_ID = %s' % (self.ptID)
	    data = EMR_utilities.getAllDictData(qry)
	    self.list.SetObjects(list(data))
	else:
	    self.toggler = 'Current Meds'
	    self.medtitle.SetLabel(self.toggler)
	    self.UpdateList()

    def OnInteractions(self, event):
        obj = self.list.GetSelectedObjects()
        string = 'http://mletter.best.vwh.net/Psc/dip2.cgi?userid=guest'
        count = 1
        for items in obj:
            string = string + '&drug%s=%s' % (count, items['med_name'])
            count = count + 1
        results = EMR_utilities.HTML_Frame(self, "Medication Interactions", html_str=string)
        results.Show()

    def OnReviewed(self, event):
	self.reviewed = 1

    def OnNewAll(self, event):
	allergy = wx.GetTextFromUser('What is the patient allergic to?', 'New Allergy')
	if allergy == "": pass
	else:
	    reaction = wx.GetTextFromUser('What happened?', 'Reaction')
	    query = 'INSERT INTO allergies SET allergy = "%s", reaction = "%s", patient_ID = %s;' % \
			(allergy, reaction, self.ptID)
	    EMR_utilities.updateData(query)
	    self.UpdateAllergy()
	
    def OnRemAll(self, event):
        obj = self.allergylist.GetSelectedObjects()
        for items in obj:
            qry = 'DELETE FROM allergies WHERE allergy_number = %s;' % items['allergy_number']
            self.allergylist.RemoveObject(items)
            EMR_utilities.updateData(qry)
	
    def UpdateList(self):				#this function just updates the list after new med added or deleted
	meds = med_find(self.ptID)			#These lines put the data from the query
	self.list.SetObjects(meds)

    def UpdateAllergy(self):
	allergies = allergy_find(self.ptID)
	self.allergylist.SetObjects(allergies)

    def HandleCellEditStarting(self, event):
        pass

    def allergyHandleCellEditFinished(self, event):
        sqlstmt = 'UPDATE allergies SET %s = "%s" WHERE allergy_number = %s;' \
                  % (self.allergylist.columns[event.subItemIndex].valueGetter,
                     self.allergylist.GetItem(event.rowIndex, event.subItemIndex).GetText(),
                     event.rowModel["allergy_number"])
        EMR_utilities.updateData(sqlstmt)

    def listHandleCellEditFinished(self, event):
        sqlstmt = 'UPDATE meds SET %s = "%s" WHERE med_number = %s;' \
                  % (self.list.columns[event.subItemIndex].valueGetter,
                     self.list.GetItem(event.rowIndex, event.subItemIndex).GetText(),
                     event.rowModel["med_number"])
        EMR_utilities.updateData(sqlstmt)
        	

class AddMed(wx.Panel):
    def __init__(self, parent, id, PtID):
	wx.Panel.__init__(self, parent, id)
        
	border = wx.StaticBox(self, -1, 'Add Meds')
	addmeds = wx.StaticBoxSizer(border, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(hgap=5, vgap=5)
        self.ptID = PtID
	labelName = wx.StaticText(self, -1, "Name")
        sizer.Add(labelName, pos=(0,0), flag=wx.ALIGN_RIGHT)
	self.comboName = wx.ComboBox(self, -1, name = "", choices = [], size=(330,-1), style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.comboName, pos=(0,1), span=(1,4))
	self.Bind(wx.EVT_TEXT_ENTER, self.EvtOnEnter, self.comboName)
	self.Bind(wx.EVT_COMBOBOX, self.EvtComboBox, self.comboName)

	labelDose = wx.StaticText(self, -1, "Dose")
        sizer.Add(labelDose, pos=(0,5), flag=wx.ALIGN_RIGHT)
        self.listDose = wx.ListBox(self, -1, pos=wx.DefaultPosition, size=(120,104), choices = [], style=wx.LB_HSCROLL)
        sizer.Add(self.listDose, pos=(0,6), span=(3,2))
	self.Bind(wx.EVT_LISTBOX, self.EvtSelListbox, self.listDose)
	
	
	self.textctrl = {}
	labels = [('Take', 85), ('Frequency', 85), ('#', 85), ('Route', 85), ('Refills', 85), ('Date', 85)]
	row = 1
	col = 0
        for label, size in labels:
	    self.textctrl[label] = wx.TextCtrl(self, -1, size=(size, -1))
	    sizer.Add(wx.StaticText(self, -1, label), pos=(row, col), flag=wx.ALIGN_RIGHT)
	    sizer.Add(self.textctrl[label], pos=(row, (col + 1)))
	    if col == 4:
		row = 2
		col = -2
	    else: pass
	    col = col + 2 

        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        sizer.Add(btn, pos=(0, 8))
	self.Bind(wx.EVT_BUTTON, self.OnOK, btn)
	addmeds.Add((80, -1), 0)
	addmeds.Add(sizer, 1)

        self.SetSizer(addmeds)
        self.Fit()
	self.comboName.SetFocus()

    def EvtOnEnter(self, event):
	a = wx.GetApp()
     	cursor = a.conn.cursor()
     	cursor.execute('SELECT drug_name FROM multum_drug_id WHERE drug_name LIKE "%%%s%%";' % (event.GetString()))
     	results = cursor.fetchall()
     	cursor.close()
	for item in results:
		string = (str(item)).lower()
		self.comboName.Append(string.strip("(',)"))     	
	
	
    def EvtComboBox(self, event):
	a = wx.GetApp()
	sqldosefind = """SELECT multum_product_strength.product_strength_description
		FROM multum_drug_id, multum_product_strength, main_multum
		WHERE multum_product_strength.product_strength_code = main_multum.product_strength_code AND main_multum.drug_id = multum_drug_id.drug_id AND multum_drug_id.drug_name = "%s";"""
	cursor = a.conn.cursor()
	cursor.execute(sqldosefind % (event.GetString()))
	results = cursor.fetchall()
	cursor.close()
	for item in results:
		string = (str(item)).lower()
		self.listDose.Append(string.strip("(',)"))
	
    def EvtSelListbox(self, event):
	self.textctrl['Take'].SetValue('1')
	self.textctrl['Frequency'].SetValue('daily')
	self.textctrl['Route'].SetValue('oral')
	self.textctrl['Date'].SetValue(str(EMR_utilities.dateToday()))
	self.textctrl['#'].SetFocus()

    def OnOK(self, event):
	a = wx.GetApp()
	cursor = a.conn.cursor()
	query = 'INSERT INTO meds SET med_name = "%s", dose = "%s", number_tablets = "%s", frequency = "%s", number_pills = "%s", refills = "%s", route = "%s", script_date = "%s", patient_ID = %s, archive = 0;' % (self.comboName.GetValue(), 
						self.listDose.GetString(self.listDose.GetSelection()), 
						self.textctrl['Take'].GetValue(), self.textctrl['Frequency'].GetValue(), 
						self.textctrl['#'].GetValue(), self.textctrl['Refills'].GetValue(), 
						self.textctrl['Route'].GetValue(), self.textctrl['Date'].GetValue(), 
						self.ptID)
	cursor.execute(query)
	self.GetParent().UpdateList()
	self.listDose.Clear()
	for key in self.textctrl:
	    self.textctrl[key].Clear()
	self.comboName.Clear()
	self.comboName.SetValue("")
	cursor.close()

def med_find(pt_ID):
     a = wx.GetApp()
     cursor = a.conn.cursor(MySQLdb.cursors.DictCursor)
     cursor.execute("SELECT * FROM meds WHERE archive = 0 AND patient_ID = %s" % (str(pt_ID)))
     results = list(cursor.fetchall())
     return results
     cursor.close()

def allergy_find(pt_ID):
     a = wx.GetApp()
     cursor = a.conn.cursor(MySQLdb.cursors.DictCursor)
     cursor.execute("SELECT allergy, allergy_number, reaction FROM allergies WHERE patient_ID = %s" % (str(pt_ID)))
     results = list(cursor.fetchall())
     return results
     cursor.close()

