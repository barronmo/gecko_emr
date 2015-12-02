import wx
#from wx.html import HtmlEasyPrinting
import wx.calendar
import datetime, shutil, subprocess
import EMR_utilities, EMR_formats, Printer, settings

class todo(wx.Panel):
    def __init__(self, parent, ID, PtID):
	wx.Panel.__init__(self, parent, ID)
	
	self.PtID = PtID
	self.toggler = 'Active'
	self.todoTitle = wx.StaticText(self, -1, self.toggler)
	titlefont = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)
	self.todoTitle.SetFont(titlefont)
	todo_columns = (('Date', 110), ('Description', 250), ('Priority', 55), ('Category', 100), ('Memo', 200), ('Due Date', 85), ('Completed', 0), ('ToDoNumber', 0))
	todo_items = todo_find(self.PtID)
	self.todo_list = EMR_utilities.buildCheckListCtrl(self, todo_columns, todo_items)
	
	lefttodo = wx.BoxSizer(wx.VERTICAL)
	righttodo = wx.BoxSizer(wx.VERTICAL)
	mainsizer = wx.BoxSizer(wx.HORIZONTAL)

        self.cal = wx.calendar.CalendarCtrl(self, -1, wx.DateTime_Now(),\
                             style = wx.calendar.CAL_SHOW_HOLIDAYS
                             | wx.calendar.CAL_SUNDAY_FIRST
                             | wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION)
        self.Bind(wx.calendar.EVT_CALENDAR, self.OnCalSelected, id=self.cal.GetId())

	buttons = (('Remove', self.OnRemove, lefttodo), ('Edit', self.OnEdit, lefttodo), \
		   ('Complete', self.OnComplete, lefttodo), \
		   ('Test', self.OnTest, lefttodo), ('Consult', self.OnConsult, lefttodo), \
		   ('Toggle', self.OnToggle, lefttodo), ('Not Done', self.OnNotDone, lefttodo))
	for label, handler, sizer in buttons:
	    EMR_utilities.buildOneButton(self, self, label, handler, sizer)
	
	self.addtodo = AddToDo(self, -1, self.PtID, self.todo_list)
	righttodo.Add(self.todoTitle, 0, wx.ALIGN_CENTER)
	righttodo.Add(self.todo_list, 1.5, wx.EXPAND|wx.ALL, 5)
	righttodo.Add(self.addtodo, 1, wx.EXPAND)
	righttodo.Add(self.cal, 1, wx.ALIGN_RIGHT|wx.ALL, 5)
	mainsizer.Add(lefttodo, 0, wx.ALL, 3)
	mainsizer.Add(righttodo, 1, wx.EXPAND|wx.ALL, 3)
	self.SetSizer(mainsizer)

    def OnRemove(self, event):
	
	num = self.todo_list.GetItemCount()
	for i in range(num):
            if i == 0: pass
            if self.todo_list.IsChecked(i):
		qry = 'DELETE FROM todo WHERE todo_number = %s;' % (self.todo_list.GetItem(i, 7).GetText())
		EMR_utilities.updateData(qry)
		self.todo_list.DeleteItem(i)		
		

    def OnEdit(self, event):
	num = self.todo_list.GetItemCount()
	items = []
	n = 0
	for i in range(num):
            if i == 0: pass
            if self.todo_list.IsChecked(i):
		qry = 'DELETE FROM todo WHERE todo_number = %s;' % (self.todo_list.GetItem(i, 7).GetText())
		EMR_utilities.updateData(qry)
		for columns in range(self.todo_list.GetColumnCount()):
		    items.append(self.todo_list.GetItem(i, columns).GetText())
		self.todo_list.DeleteItem(i)
	ctrls = ['Date', 'Description', 'Priority', 'Category', 'Memo', 'Due Date']	
	for i in ctrls:
	    self.addtodo.textctrl[i].SetValue(items[n])
	    n = n + 1
	
		   
    def OnComplete(self, event):
	num = self.todo_list.GetItemCount()
	for i in range(num):
            if i == 0: pass
            if self.todo_list.IsChecked(i):
		qry = 'UPDATE todo SET complete = 1 WHERE todo_number = %s;' % (self.todo_list.GetItem(i, 7).GetText())
		EMR_utilities.updateData(qry)
		self.todo_list.DeleteItem(i)	

    def OnTest(self, event):
	Printer.myTestOrder(self, self.PtID)

	"""lt = "%s/EMR_outputs/Tests.html" % settings.LINUXPATH
	at = "%s/EMR_outputs/Tests.html" % settings.APPLEPATH
	wt = "%s\EMR_outputs\Tests.html" % settings.WINPATH
	string = open(EMR_utilities.platformText(lt, at, wt), 'r')
	s = string.read()
	string.close()
	dem_data = EMR_utilities.getDictData('SELECT * FROM demographics WHERE patient_ID = %s;' % self.PtID)
	test_dlg = wx.TextEntryDialog(self, "What studies would you like to order?", "Studies",style=wx.TE_MULTILINE|wx.OK|wx.CANCEL)
	if test_dlg.ShowModal() == wx.ID_OK:
	    dem_data['tests'] = test_dlg.GetValue()
	    dem_data['date'] = EMR_utilities.dateToday()
	else: pass
	dx_dlg = wx.TextEntryDialog(self, "What is the diagnosis?", "Diagnosis", style=wx.TE_MULTILINE|wx.OK|wx.CANCEL)
	if dx_dlg.ShowModal() == wx.ID_OK:
	    dem_data['dx'] = dx_dlg.GetValue()
	else: pass
	dem_data['name_address'] = EMR_formats.format_address(dem_data)
	report_text = s % (dem_data)
	results_date = wx.TextEntryDialog(self, "Due Date?", style=wx.OK|wx.CANCEL)
	if results_date.ShowModal() == wx.ID_OK:
	    qry = "INSERT INTO todo SET patient_ID = %s, date = '%s', description = '%s', priority = 3, category = 'Test', due_date = '%s', complete = 0;" % (self.PtID, EMR_utilities.dateToday(), dem_data['tests'], results_date.GetValue())
	    EMR_utilities.updateData(qry)
	else: pass
	EMR_utilities.updateList(todo_find(self.PtID), self.todo_list)
	printer = EMR_utilities.Printer()
	printer.PreviewText(report_text)
	path_lt = "%s/EMR_outputs/%s/Orders/%s.html" % (settings.LINUXPATH, self.PtID, EMR_utilities.dateToday(t='file format'))
	path_at = "%s/EMR_outputs/%s/Orders/%s.html" % (settings.APPLEPATH, self.PtID, EMR_utilities.dateToday(t='file format'))
	path_wt = "%s\EMR_outputs\%s\Orders\%s.html" % (settings.WINPATH, self.PtID, EMR_utilities.dateToday(t='file format'))
	filename = EMR_utilities.platformText(path_lt, path_at, path_wt)
	f = open(filename, 'w')
	f.write(report_text)
	f.close()"""
		
    def OnConsult(self, event):
	tree = TreeFrame(self, self.PtID)
	tree.todoInstance = self
	tree.Show()
		
    def OnToggle(self, event):					#changes list display from active to completed items
	if self.toggler == 'Active':				
	    self.toggler = 'Completed'
	    self.todoTitle.SetLabel(self.toggler)
	    data = todo_find(self.PtID, toggle=1)
	    EMR_utilities.updateList(data, self.todo_list)
	else:
	    self.toggler = 'Active'				#and back
	    self.todoTitle.SetLabel(self.toggler)
	    data = todo_find(self.PtID, toggle=0)
	    EMR_utilities.updateList(data, self.todo_list)

    def OnNotDone(self, event):
	num = self.todo_list.GetItemCount()
	for i in range(num):
            if i == 0: pass
            if self.todo_list.IsChecked(i):
		qry = 'UPDATE todo SET complete = 1, memo = "disregarded by patient" WHERE todo_number = %s;' % (self.todo_list.GetItem(i, 7).GetText())
		EMR_utilities.updateData(qry)
		self.todo_list.DeleteItem(i)

    def OnCalSelected(self, event):
	self.addtodo.textctrl['Due Date'].SetValue(str(event.PyGetDate()))


class AddToDo(wx.Panel):
    def __init__(self, parent, id, PtID, List):
	wx.Panel.__init__(self, parent, id)

	border = wx.StaticBox(self, -1, "Add To Do Item")
	SBsizer = wx.StaticBoxSizer(border, wx.HORIZONTAL)
	sizer = wx.GridBagSizer(hgap=5, vgap=5)
	self.PtID = PtID
	self.List = List
	self.textctrl = {}
	labels = (('Date', 90), ('Priority', 90), ('Category', 90), ('Due Date', 90))
	row = 0
	col = 0
	for label, size in labels:
	    self.textctrl[label] = wx.TextCtrl(self, -1, size=(size, -1))
	    sizer.Add(wx.StaticText(self, -1, label), pos=(row,col), flag=wx.ALIGN_RIGHT)
	    sizer.Add(self.textctrl[label], pos=(row, (col + 1)))
	    col = col + 2
	sizer.Add(wx.StaticText(self, -1, 'Description'), pos=(1, 0), flag=wx.ALIGN_RIGHT)
	self.textctrl['Description'] = wx.TextCtrl(self, -1, size=(300,50), style=wx.TE_MULTILINE)
	self.textctrl['Memo'] = wx.TextCtrl(self, -1, size=(300,50), style=wx.TE_MULTILINE)
	sizer.Add(self.textctrl['Description'], pos=(1, 1), span=(2, 3))
	sizer.Add(wx.StaticText(self, -1, 'Memo'), pos=(1, 4), flag=wx.ALIGN_RIGHT)
	sizer.Add(self.textctrl['Memo'], pos=(1, 5), span=(2, 3))  

	btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        sizer.Add(btn, pos=(3, 0))
	self.Bind(wx.EVT_BUTTON, self.OnOk, btn)
	SBsizer.Add(sizer)
	self.SetSizer(SBsizer)
	self.textctrl['Date'].SetValue(EMR_utilities.dateToday())
	self.textctrl['Priority'].SetValue('3')
 
    def OnOk(self, event):
	qry = 'INSERT INTO todo SET date = "%s", description = "%s", priority = "%s", category = "%s", memo = "%s", due_date = "%s", complete = "0", patient_ID = %s;' % (self.textctrl['Date'].GetValue(), 
		     self.textctrl['Description'].GetValue(), self.textctrl['Priority'].GetValue(), 
		     self.textctrl['Category'].GetValue(), self.textctrl['Memo'].GetValue(), 
		     self.textctrl['Due Date'].GetValue(), self.PtID)
	EMR_utilities.updateData(qry)	
	EMR_utilities.updateList(todo_find(self.PtID), self.List)
	 

class TreeFrame(wx.Frame):
    def __init__(self, parent, PtID):
        wx.Frame.__init__(self, parent, title='Add Consult', size=(700, 1000))
        
	self.PtID = PtID
	self.consultant = ''
	self.addSpecialist = 0	#need to keep track of whether Add Consultant button has been pushed

	#Controls created
	self.textctrl = {}
	reasonLBL = wx.StaticText(self, -1, 'Reason for consult')
	self.textctrl['reason'] = wx.TextCtrl(self, -1)

	memoLBL = wx.StaticText(self, -1, 'Further info...')
	self.textctrl['memo'] = wx.TextCtrl(self, -1, size=(-1,100), style=wx.TE_MULTILINE)

	dateLBL = wx.StaticText(self, -1, 'Date Due')
	self.cal = wx.calendar.CalendarCtrl(self, -1, wx.DateTime_Now(),\
                             style = wx.calendar.CAL_SHOW_HOLIDAYS
                             | wx.calendar.CAL_SUNDAY_FIRST
                             | wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION)
	self.Bind(wx.calendar.EVT_CALENDAR, self.OnCalSelected, self.cal)
	self.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, self.OnCalSelected, self.cal)
	self.textctrl['Due Date'] = ''	#not actually a text ctrl but don't need it; just holds date after cal selected
	
	self.tree_ctrl = wx.TreeCtrl(self, -1, style=wx.TR_DEFAULT_STYLE | \
                                wx.TR_FULL_ROW_HIGHLIGHT | \
                                wx.TR_EDIT_LABELS)
	specialties = EMR_utilities.getAllData('SELECT DISTINCT specialty FROM consultants ORDER BY specialty;')
	self.root = self.tree_ctrl.AddRoot('Pick a specialist')
	for items in specialties:
	    try:
		child = self.tree_ctrl.AppendItem(self.root, items[0])
		doctors = EMR_utilities.getAllData('SELECT firstname, lastname, address, city, state FROM consultants WHERE specialty = "%s";' % items[0])
		for n in doctors:
		    doc = self.tree_ctrl.AppendItem(child, '%s %s, %s, %s, %s' % (n[0], n[1], n[2], n[3], n[4]))
	    except: print 'there was an error in the specialist window'
	self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree_ctrl)


	nameLBL = wx.StaticText(self, -1, 'First/Last Name')
	self.textctrl['firstname'] = wx.TextCtrl(self, -1, size=(150,-1))
	self.textctrl['lastname'] = wx.TextCtrl(self, -1, size=(150,-1))

	addrLBL = wx.StaticText(self, -1, 'Address')
	self.textctrl['address'] = wx.TextCtrl(self, -1)

	cszLBL = wx.StaticText(self, -1, 'City, State, Zip')
	self.textctrl['city'] = wx.TextCtrl(self, -1, size=(150,-1))
	self.textctrl['state'] = wx.TextCtrl(self, -1, size=(50,-1))
	self.textctrl['zipcode'] = wx.TextCtrl(self, -1, size=(70,-1))

	phoneLBL = wx.StaticText(self, -1, 'Phone/Fax')
	self.textctrl['phonenumber'] = wx.TextCtrl(self, -1)
	self.textctrl['fax'] = wx.TextCtrl(self, -1)

	specLBL = wx.StaticText(self, -1, 'Specialty')
	self.textctrl['specialty'] = wx.TextCtrl(self, -1)
	
	conButton = wx.Button(self, -1, label='Add Consultant')
	doneButton = wx.Button(self, -1, label='Done')
        conButton.Bind(wx.EVT_BUTTON, self.add_consultant)
	doneButton.Bind(wx.EVT_BUTTON, self.OnDone)
	
	#Now the layout

        # the top level sizer is called mainSizer
	mainSizer = wx.BoxSizer(wx.VERTICAL)
	
	#sizer for top part of frame is topSizer
	topSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
	topSizer.AddGrowableCol(1)
	topSizer.Add(reasonLBL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	topSizer.Add(self.textctrl['reason'], 0, wx.EXPAND)
	topSizer.Add(memoLBL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	topSizer.Add(self.textctrl['memo'], 0, wx.EXPAND)
	topSizer.Add(dateLBL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	topSizer.Add(self.cal, 0)
	mainSizer.Add(topSizer, 0, wx.EXPAND|wx.ALL, 10)
	
	#middle part of frame is the tree control of consultants
	mainSizer.Add(self.tree_ctrl, 1, wx.EXPAND|wx.ALL, 5)

	#bottom part we add new consultants
        #similar flexgridsizer to the top
	addConsultFlexGridSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
	addConsultFlexGridSizer.AddGrowableCol(1)

	
	addConsultFlexGridSizer.Add(nameLBL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	#name needs a horizontal sub-sizer
	nameSizer = wx.BoxSizer(wx.HORIZONTAL)
	nameSizer.Add(self.textctrl['firstname'], 1, wx.RIGHT, 5)
        nameSizer.Add(self.textctrl['lastname'], 1)
	addConsultFlexGridSizer.Add(nameSizer, 0, wx.EXPAND)

	addConsultFlexGridSizer.Add(addrLBL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	addConsultFlexGridSizer.Add(self.textctrl['address'], 0, wx.EXPAND)

	addConsultFlexGridSizer.Add(cszLBL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	#city, state, zip needs a horizontal sub-sizer
	cszSizer = wx.BoxSizer(wx.HORIZONTAL)
	cszSizer.Add(self.textctrl['city'], 1)
	cszSizer.Add(self.textctrl['state'], 0, wx.LEFT|wx.RIGHT, 5)
	cszSizer.Add(self.textctrl['zipcode'])
	addConsultFlexGridSizer.Add(cszSizer, 0, wx.EXPAND)

	addConsultFlexGridSizer.Add(phoneLBL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	#phone/fax need horizontal sub-sizer
	phoneSizer = wx.BoxSizer(wx.HORIZONTAL)
	phoneSizer.Add(self.textctrl['phonenumber'], 1, wx.RIGHT, 5)
        phoneSizer.Add(self.textctrl['fax'], 1)
	addConsultFlexGridSizer.Add(phoneSizer, 0, wx.EXPAND)

	addConsultFlexGridSizer.Add(specLBL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	addConsultFlexGridSizer.Add(self.textctrl['specialty'], 0, wx.EXPAND)

	#add addConsultFlexGridSizer to mainSizer
	mainSizer.Add(addConsultFlexGridSizer, 0, wx.EXPAND|wx.ALL, 10)
	
	#add buttons with horizontal sizer
	buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
	buttonSizer.Add(doneButton, 1)
	buttonSizer.Add(conButton, 1)
        mainSizer.Add(buttonSizer, 0, wx.EXPAND|wx.ALL)
        self.SetSizer(mainSizer)

	self.Centre()

       
    # called when the button is clicked.
    def add_consultant(self, evt):
        qry = "INSERT INTO consultants SET firstname = '%s', lastname = '%s', address = '%s', city = '%s', state = '%s', zipcode = '%s', phone = '%s', fax = '%s', specialty = '%s';" % \
		(self.textctrl['firstname'].GetValue(), self.textctrl['lastname'].GetValue(), self.textctrl['address'].GetValue(), \
		self.textctrl['city'].GetValue(), self.textctrl['state'].GetValue(), self.textctrl['zipcode'].GetValue(), \
		self.textctrl['phonenumber'].GetValue(), self.textctrl['fax'].GetValue(), self.textctrl['specialty'].GetValue())
	EMR_utilities.updateData(qry)
	self.consultant = self.textctrl['firstname'].GetValue() + ' ' + self.textctrl['lastname'].GetValue() + ','
	self.addSpecialist = 1	#tells whether Add Consultant button has been pushed

    def OnDone(self, evt):
	#check to make sure user hit Add Consultant button if he entered new consultant info
	if self.textctrl['lastname'].GetValue():
	    if self.addSpecialist == 1:
		self.PrintLtr()
	    else:
		wx.MessageBox('Please hit the Add Consultant button first', caption='Message', style=wx.OK)
	else:
	    self.PrintLtr()

    def PrintLtr(self):
	#need consultant first and lastname by parsing self.consultant 
	conName = self.consultant[0:self.consultant.find(',')]
	Printer.myConsultLtr(self, self.PtID, self.textctrl['reason'].GetValue(), self.textctrl['memo'].GetValue(), \
				conName, self.textctrl['Due Date'])
	EMR_utilities.updateList(todo_find(self.PtID, toggle=0), self.todoInstance.todo_list)
	self.Destroy()

    def OnSelChanged(self, event):
        self.consultant = self.tree_ctrl.GetItemText(event.GetItem())

    def OnCalSelected(self, event):
	self.textctrl['Due Date'] = str(event.PyGetDate())
		


def todo_find(PtID, toggle=0):
    qry = 'SELECT date, description, priority, category, memo, due_date, complete, todo_number FROM todo WHERE patient_ID = %s AND complete = %s;' % (PtID, toggle)
    return EMR_utilities.getAllData(qry)
