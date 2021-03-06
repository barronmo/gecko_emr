import wx
import MySQLdb, sys, time
import EMR_utilities, EMR_formats, settings
from ObjectListView import ObjectListView, ColumnDefn, EVT_CELL_EDIT_STARTING, EVT_CELL_EDIT_FINISHED

class Prevention(wx.Panel):
    def __init__(self, parent, id, ptID):
        wx.Panel.__init__(self, parent, id)

        self.ptID = ptID
	prevents = prevent_find(ptID)
	self.preventList = ObjectListView(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
	self.preventList.SetColumns([
            ColumnDefn("Name", "left", 250, valueGetter="prevent_name", isEditable=True),
            ColumnDefn("Last Date", "center", 100, valueGetter="date", isEditable=True),
            ColumnDefn("Result", "center", 300, valueGetter="reason", isEditable=True),
	    ColumnDefn("Interval", "center", 60, valueGetter="p_interval", isEditable=True),
            ColumnDefn("Notes", "left", 500, valueGetter="notes", isEditable=True),
            ])
	self.preventList.SetObjects(prevents)
	self.preventList.cellEditMode = ObjectListView.CELLEDIT_DOUBLECLICK
	self.preventList.Bind(EVT_CELL_EDIT_STARTING, self.HandleCellEditStarting)
	self.preventList.Bind(EVT_CELL_EDIT_FINISHED, self.preventListHandleCellEditFinished)
	
	mainSizer = wx.BoxSizer(wx.VERTICAL)

	vaccines = vaccine_find(ptID)
	self.vaccineList = ObjectListView(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
	self.vaccineList.SetColumns([
            ColumnDefn("Vaccine", "left", 150, valueGetter = "vaccine", isEditable=True),
            ColumnDefn("Dates Given", "left", 600, valueGetter = "dates", isEditable=True),
	    ColumnDefn("Notes", "left", 500, valueGetter = "notes", isEditable=True),
	    ])
	self.vaccineList.SetObjects(vaccines)
	self.vaccineList.cellEditMode = ObjectListView.CELLEDIT_DOUBLECLICK
        self.vaccineList.Bind(EVT_CELL_EDIT_STARTING, self.HandleCellEditStarting)
        self.vaccineList.Bind(EVT_CELL_EDIT_FINISHED, self.vaccineListHandleCellEditFinished)
	
#Build the add/delete buttons for each list
	preventSizer = wx.BoxSizer(wx.HORIZONTAL)
	vaccineSizer = wx.BoxSizer(wx.HORIZONTAL)
	prevButtons = (('Add', self.OnAddPrevent), ('Delete', self.OnDelPrevent))
	for label, handler in prevButtons:
	    EMR_utilities.buildOneButton(self, self, label, handler, preventSizer)
	vacButtons = (('Add', self.OnAddVaccine), ('Delete', self.OnDelVaccine), ('Print', self.OnPrintVaccines))
	for label, handler in vacButtons:
	    EMR_utilities.buildOneButton(self, self, label, handler, vaccineSizer)
	
#Set the sizers	that have not already been set
	self.preventTitle = wx.StaticText(self, -1, 'Health Maintenance')
	self.vaccineTitle = wx.StaticText(self, -1, 'Vaccines')
	titlefont = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)
	self.preventTitle.SetFont(titlefont)
	self.vaccineTitle.SetFont(titlefont)
	preventSizer.Add(self.preventTitle, 0, wx.ALIGN_CENTER | wx.ALL, 5)
	mainSizer.Add(preventSizer)
	mainSizer.Add(self.preventList, 1, wx.EXPAND | wx.TOP, 3)
	mainSizer.Add((15, -1))
	vaccineSizer.Add(self.vaccineTitle, 0, wx.ALIGN_CENTER | wx.ALL, 5)
	mainSizer.Add(vaccineSizer)
	mainSizer.Add(self.vaccineList, 1, wx.EXPAND | wx.TOP, 3)
	mainSizer.Add((-1, 5))
		
        self.SetSizer(mainSizer)
        self.Centre()
        self.Show(True)

    #def getKey(item):
    #	return item['vaccine']

    def OnPrintVaccines(self, event):
        obj = self.vaccineList.GetObjects()
	string = ''
	v = []
        for items in obj:
	    v.append((items['vaccine'], items['dates'], items['notes']))
	for things in sorted(v):
	    string = '%s     %s     %s\n' % \
                     (things[1], things[0], things[2]) + string
        
	form_lt = "%s/EMR_outputs/Vaccines.html" % settings.LINUXPATH
	form_at = "%s/EMR_outputs/Vaccines.html" % settings.APPLEPATH
	form_wt = "%s\EMR_outputs\Vaccines.html" % settings.WINPATH
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
	'''path_lt = "%s/EMR_outputs/%s/Orders" % (settings.LINUXPATH, self.ptID)
	path_at = "%s/EMR_outputs/%s/Orders" % (settings.APPLEPATH, self.ptID)
	path_wt = "%s\EMR_outputs\%s\Orders" % (settings.WINPATH, self.ptID)
	path = EMR_utilities.platformText(path_lt, path_at, path_wt)
	filename = "%s\script%s.html" % (path, EMR_utilities.dateToday(t='yes'))
	f = open(filename, 'w')
	f.write(script_text)
	f.close()'''	

    def HandleCellEditStarting(self, event):
        pass

    def vaccineListHandleCellEditFinished(self, event):
        sqlstmt = 'UPDATE vaccines SET %s = "%s" WHERE vaccine_number = %s;' \
                  % (self.vaccineList.columns[event.subItemIndex].valueGetter,
                     self.vaccineList.GetItem(event.rowIndex, event.subItemIndex).GetText(),
                     event.rowModel["vaccine_number"])
	EMR_utilities.updateData(sqlstmt)
	
    def preventListHandleCellEditFinished(self, event):
        sqlstmt = 'UPDATE prevents2 SET %s = "%s" WHERE prevent_number = %s;' \
                  % (self.preventList.columns[event.subItemIndex].valueGetter,
                     self.preventList.GetItem(event.rowIndex, event.subItemIndex).GetText(),
                     event.rowModel["prevent_number"])
	EMR_utilities.updateData(sqlstmt)
	
        
    def OnAddPrevent(self, event):
	prev = wx.GetTextFromUser('What is the new health maintance item?', 'Health Maintenance')
	if prev == "": pass
	else:
	    note = wx.GetTextFromUser('Any notes?', 'Notes')
	    query = 'INSERT INTO prevents2 SET prevent_name = "%s", date = "%s", reason = "normal", p_interval = 1, notes = "%s", patient_ID = %s;' % \
		(prev, EMR_utilities.dateToday(), note, self.ptID)
	    EMR_utilities.updateData(query)
	    self.UpdatePrevents()

    def OnAddVaccine(self, event):
	vac = wx.GetTextFromUser('What is the new vaccine?', 'Vaccines')
	dates = wx.GetTextFromUser('What date(s) was vaccine given?', 'Vaccines')
	if vac == "": pass
	else:
	    note = wx.GetTextFromUser('Any notes?', 'Notes')
	    query = 'INSERT INTO vaccines SET vaccine = "%s", dates = "%s", notes = "%s", patient_ID = %s;' % \
			(vac, dates, note, self.ptID)
	    EMR_utilities.updateData(query)
	    self.UpdateVaccines()
	    
    def OnDelPrevent(self, event):
	obj = self.preventList.GetSelectedObjects()
        for items in obj:
            qry = 'DELETE FROM prevents2 WHERE prevent_number = %s;' % items['prevent_number']
            self.preventList.RemoveObject(items)
            EMR_utilities.updateData(qry)

    def OnDelVaccine(self, event):
	obj = self.vaccineList.GetSelectedObjects()
        for items in obj:
            qry = 'DELETE FROM vaccines WHERE vaccine_number = %s;' % items['vaccine_number']
            self.vaccineList.RemoveObject(items)
            EMR_utilities.updateData(qry)

    def UpdatePrevents(self):
	prevents = prevent_find(self.ptID)
	self.preventList.SetObjects(prevents)

    def UpdateVaccines(self):
	vac = vaccine_find(self.ptID)
	self.vaccineList.SetObjects(vac)
	

def prevent_find(pt_ID):
     a = wx.GetApp()
     cursor = a.conn.cursor(MySQLdb.cursors.DictCursor)
     cursor.execute("SELECT * FROM prevents2 WHERE patient_ID = %s" % (str(pt_ID)))
     results = list(cursor.fetchall())
     return results
     cursor.close()

def vaccine_find(pt_ID):
     a = wx.GetApp()
     cursor = a.conn.cursor(MySQLdb.cursors.DictCursor)
     cursor.execute("SELECT * FROM vaccines WHERE patient_ID = %s" % (str(pt_ID)))
     results = list(cursor.fetchall())
     return results
     cursor.close()

