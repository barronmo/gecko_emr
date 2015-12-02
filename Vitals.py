import wx
import EMR_utilities
from ObjectListView import ObjectListView, ColumnDefn, EVT_CELL_EDIT_STARTING, EVT_CELL_EDIT_FINISHED

class Vitals(wx.Panel):
    def __init__(self, parent, ID, PtID):
	wx.Panel.__init__(self, parent, ID)
	#I need some way to set the max size for the grid
	self.PtID = PtID
	self.qry = "SELECT * FROM vitals WHERE patient_ID = %s;" % (str(self.PtID))
	self.vitals = list(EMR_utilities.getAllDictData(self.qry))
	self.textctrl = {}
	self.vitalsList = ObjectListView(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
	self.vitalsList.SetColumns([
            ColumnDefn("Weight", "center", 80, valueGetter="wt"),
            ColumnDefn("Height", "center", 80, valueGetter="ht"),
            ColumnDefn("HC", "center", 80, valueGetter="hc"),
            ColumnDefn("Systolic", "center", 80, valueGetter="sBP"),
            ColumnDefn("Diastolic", "center", 80, valueGetter="dBP"),
            ColumnDefn("Pulse", "center", 80, valueGetter="pulse"),
            ColumnDefn("Resp", "center", 80, valueGetter="resp"),
            ColumnDefn("O2 Sat", "center", 80, valueGetter="sats"),
	    ColumnDefn("Temp", "center", 80, valueGetter="temp"),
	    ColumnDefn("Date", "center", 120, valueGetter="vitals_date")
            ])
	self.vitalsList.SetObjects(self.vitals)
	self.vitalsList.cellEditMode = ObjectListView.CELLEDIT_DOUBLECLICK
	self.vitalsList.Bind(EVT_CELL_EDIT_STARTING, self.HandleCellEditStarting)
	self.vitalsList.Bind(EVT_CELL_EDIT_FINISHED, self.listHandleCellEditFinished)
	self.vitalsbox = wx.BoxSizer(wx.HORIZONTAL)
	self.vitalsbox.Add(self.vitalsList, 1, wx.EXPAND |wx.ALL, 20)
	self.mainsizer = wx.BoxSizer(wx.VERTICAL)
	border = wx.StaticBox(self, -1, 'Add Vitals')
	f = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.LIGHT)
	border.SetFont(f)
	addvitals = wx.StaticBoxSizer(border, wx.HORIZONTAL)
	controls = [('Wt', 40), ('Ht', 30), ('HC', 30), ('Temp', 40), ('SBP', 40), ('DBP', 40), ('Pulse', 40), ('Resp', 30), \
		    ('O2 Sats', 30), ('Date', 80)]
	for label, size in controls:
	    EMR_utilities.buildOneTextCtrl(self, label, size, addvitals)
	self.textctrl['Date'].SetValue(str(EMR_utilities.dateToday()))
	self.mainsizer.Add(self.vitalsbox)
	self.mainsizer.Add(addvitals, 0, wx.ALL, 20)
	buttonAdd = EMR_utilities.buildOneButton(self, self, 'Update Vitals', self.UpdateVitals)
	buttonDel = EMR_utilities.buildOneButton(self, self, 'Delete Vitals', self.DeleteVitals)
	self.mainsizer.Add(buttonAdd, 0, wx.ALIGN_LEFT|wx.ALIGN_TOP|wx.LEFT|wx.TOP, 20)
	self.mainsizer.Add(buttonDel, 0, wx.ALIGN_LEFT|wx.ALIGN_TOP|wx.LEFT|wx.TOP, 20)
	self.SetSizer(self.mainsizer)

    def HandleCellEditStarting(self, event):
        pass

    def listHandleCellEditFinished(self, event):
        sqlstmt = 'UPDATE vitals SET %s = "%s" WHERE vitals_number = %s;' \
                  % (self.vitalsList.columns[event.subItemIndex].valueGetter,
                     self.vitalsList.GetItem(event.rowIndex, event.subItemIndex).GetText(),
                     event.rowModel["vitals_number"])
        EMR_utilities.updateData(sqlstmt)

    def UpdateVitals(self, event):
	updateqry = 'INSERT INTO vitals SET wt = "%s", ht = "%s", hc = "%s", temp = "%s", sBP = "%s", dBP = "%s", \
	      pulse = "%s", resp = "%s", sats = "%s", vitals_date = "%s", patient_ID = %s;' % (self.textctrl['Wt'].GetValue(), 
	      self.textctrl['Ht'].GetValue(), self.textctrl['HC'].GetValue(), self.textctrl['Temp'].GetValue(), 
	      self.textctrl['SBP'].GetValue(), self.textctrl['DBP'].GetValue(), self.textctrl['Pulse'].GetValue(), 
	      self.textctrl['Resp'].GetValue(), self.textctrl['O2 Sats'].GetValue(), self.textctrl['Date'].GetValue(), 
	      self.PtID)
	EMR_utilities.updateData(updateqry)
	self.UpdateList()
	data = EMR_utilities.getData("SELECT dob, sex FROM demographics WHERE patient_ID = %s;" % self.PtID)
	if data[1] == 'male':
	    sex = 'boy'
	else: sex = 'girl'
	s = data[0].strftime("%B") + ',' + str(data[0].day) + ',' + str(data[0].year) + ',' + sex + ',' + \
		self.textctrl['Ht'].GetValue() + ',' + self.textctrl['Wt'].GetValue() + ',' + self.textctrl['HC'].GetValue()
	with open('/home/mb/Dropbox/iMacros/Datasources/growth.txt', 'w') as f:
	    f.write(s)
	    f.close()
	self.Layout()			#this line from C M and Robin Dunn on the mailing list; see 20 Feb 08 email
	for items in self.textctrl:
	    self.textctrl[items].SetValue("")
	
    def DeleteVitals(self, event):
        obj = self.vitalsList.GetSelectedObjects()
        for items in obj:
            qry = 'DELETE FROM vitals WHERE vitals_number = %s;' % items['vitals_number']
            EMR_utilities.updateData(qry)
	self.UpdateList()

    def UpdateList(self):
	self.vitals = list(EMR_utilities.getAllDictData(self.qry))	#this function just updates the list after new vitals added or deleted
	self.vitalsList.SetObjects(self.vitals)

