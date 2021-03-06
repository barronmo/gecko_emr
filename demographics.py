import wx
import EMR_utilities, EMR_formats, UpdoxImporter

class demographics(wx.Panel):
    def __init__(self, parent, id=-1, title=None, ptID=None):
	wx.Panel.__init__(self, parent, id, title)

	self.ptID = ptID	
	self.textctrl = {}
	font1 = wx.Font(12, wx.SWISS, wx.NORMAL, wx.LIGHT)
	Font2 = wx.Font(7, wx.SWISS, wx.NORMAL, wx.LIGHT)
	self.labels = (('First Name', 50, 'firstname'), ('Last Name', 75, 'lastname'), ('Mid Initial', 20, 'mid_init'),
		('Address', 100, 'address'), ('City', 75, 'city'), ('State', 30, 'state'), ('Zip', 40, 'zipcode'), 
		('Phone', 40, 'phonenumber'), ('Sex', 20, 'sex'), ('DOB', 50, 'dob'), 
		('Insured', 30,  'relation_to_insured'), ('SSN', 30, 'SSN'), ('Email', 125, 'email'), 
		('Signature on File', 40, 'sof'),

		('Insurance Co', 0, 'insurance_company'), ('Policy ID', 50, 'policy_ID'), 
		('Sec Insurance', 100, 'secondary_ins'), ('Sec Policy ID', 50, 'secondary_ins_ID'), 
		('Sec Policy #', 50, 'sec_PolicyGroupOrFecaNumber'), 
		('Plan Name', 75, 'InsuredInsurancePlanNameOrProgramName'), 
		('Ins Policy/Group/FECA Number', 50, 'InsuredPolicyGroupOrFecaNumber'), 

		('Ins Last', 75, 'InsuredLast'),  ('Ins First', 50, 'InsuredFirst'), 
		('Ins Mid Initial', 20, 'InsuredMidInit'), ('Ins Address', 100, 'InsuredStreetAddress'), 
		('Ins City', 75, 'InsuredCity'), ('Ins State', 30, 'InsuredState'), ('Ins Zip', 40, 'InsuredZip'), 
		('Ins Phone', 40, 'InsuredPhone'), 

		#These were removed to make space for other demographics fields; they were not being used; still in the db though
		#('Ins DOB', 40, 'InsuredDOB'),
		#('Ins Gender', 20, 'InsuredGender'), ('Ins Employer', 100, 'InsuredEmployerNameOrSchoolName'),
		 
		('Guarantor Last', 75, 'guarantor_last'), ('Guarantor First', 50, 'guarantor_first'), 
		('Guarantor Address', 100, 'guarantor_address'), ('Guarantor City', 75, 'guarantor_city'),
		('Guarantor State', 30, 'guarantor_state'), ('Guarantor Zip', 40, 'guarantor_zip'), 
		('Guarantor Phone', 40, 'guarantor_phone'),

		('Race', 100, 'race'), ('Primary Language', 50, 'language'), ('PCP', 50, 'pcp'))
		
	for label, size, field in self.labels:
	    EMR_utilities.buildOneTextCtrl(self, label, size)

	demosizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
	demo2sizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
	demo3sizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
	demo4sizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
	demo5sizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
	demosizer.AddGrowableCol(1)
	demo2sizer.AddGrowableCol(1)
	demo3sizer.AddGrowableCol(1)
	demo4sizer.AddGrowableCol(1)
	demo5sizer.AddGrowableCol(1)

	#Patient Info
	nameLabel = wx.StaticText(self, -1, 'First, Middle, Last')
	nameLabel.SetFont(Font2)
	demosizer.Add(nameLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	namesizer = wx.BoxSizer(wx.HORIZONTAL)
	namesizer.Add(self.textctrl['First Name'], 2)
	namesizer.Add(self.textctrl['Mid Initial'], 1, wx.RIGHT|wx.LEFT, 5)
	namesizer.Add(self.textctrl['Last Name'], 3, wx.EXPAND)
	demosizer.Add(namesizer, 0, wx.EXPAND)
	addrLabel = wx.StaticText(self, -1, 'Address')
	addrLabel.SetFont(Font2)
	demosizer.Add(addrLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	demosizer.Add(self.textctrl['Address'], 1, wx.EXPAND)
	cityLabel = wx.StaticText(self, -1, ' City State Zip Phone')
	cityLabel.SetFont(Font2)
	demosizer.Add(cityLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	cstsizer = wx.BoxSizer(wx.HORIZONTAL)
	cstsizer.Add(self.textctrl['City'], 3)
	cstsizer.Add(self.textctrl['State'], 1, wx.LEFT|wx.RIGHT, 5)
	cstsizer.Add(self.textctrl['Zip'], 2, wx.RIGHT, 5)
	cstsizer.Add(self.textctrl['Phone'], 4, wx.EXPAND)
	demosizer.Add(cstsizer, 0, wx.EXPAND)
	dobLabel = wx.StaticText(self, -1, 'DOB Sex email')
	dobLabel.SetFont(Font2)
	demosizer.Add(dobLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	sexsizer = wx.BoxSizer(wx.HORIZONTAL)
	sexsizer.Add(self.textctrl['DOB'], 3)
	sexsizer.Add(self.textctrl['Sex'], 2, wx.LEFT|wx.RIGHT, 5)
	sexsizer.Add(self.textctrl['Email'], 5, wx.EXPAND)
	demosizer.Add(sexsizer, 0, wx.EXPAND)
	InsLabel = wx.StaticText(self, -1, 'Insured  SSN SOF')
	InsLabel.SetFont(Font2)
	demosizer.Add(InsLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	insuredsizer = wx.BoxSizer(wx.HORIZONTAL)
	insuredsizer.Add(self.textctrl['Insured'], 2, wx.RIGHT, 5)
	insuredsizer.Add(self.textctrl['SSN'], 4, wx.RIGHT, 5)
	insuredsizer.Add(self.textctrl['Signature on File'], 3, wx.EXPAND)
	demosizer.Add(insuredsizer, 0, wx.EXPAND)
	
	#Insurance Info
	insTuple = EMR_utilities.getAllData('SELECT InsurancePlanName FROM ins_companies;')
	insList = []	#this control forces me to choose from one of the insurance policies I accept or 'self'
	for item in insTuple:
	    insList.append(item[0])
	self.insChoice = wx.Choice(self, -1, choices=insList)

	InsCoLabel = wx.StaticText(self, -1, 'Primary Insurance Co')
	InsCoLabel.SetFont(Font2)
	demo3sizer.Add(InsCoLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	demo3sizer.Add(self.insChoice, 1, wx.EXPAND)
	IDLabel = wx.StaticText(self, -1, 'ID  Group#  Plan')
	IDLabel.SetFont(Font2)
	demo3sizer.Add(IDLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	pgrpsizer = wx.BoxSizer(wx.HORIZONTAL)
	pgrpsizer.Add(self.textctrl['Policy ID'], 1)
	pgrpsizer.Add(self.textctrl['Ins Policy/Group/FECA Number'], 1, wx.LEFT|wx.RIGHT, 5)
	pgrpsizer.Add(self.textctrl['Plan Name'], 1, wx.EXPAND)
	demo3sizer.Add(pgrpsizer, 0, wx.EXPAND)
	SecInsLabel = wx.StaticText(self, -1, 'Secondary Ins Co')
	SecInsLabel.SetFont(Font2)
	demo3sizer.Add(SecInsLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	demo3sizer.Add(self.textctrl['Sec Insurance'], 1, wx.EXPAND)
	SecIDLabel = wx.StaticText(self, -1, 'Sec ID  Policy#')
	SecIDLabel.SetFont(Font2)
	demo3sizer.Add(SecIDLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	sgrpsizer = wx.BoxSizer(wx.HORIZONTAL)
	sgrpsizer.Add(self.textctrl['Sec Policy ID'], 1, wx.RIGHT, 5)
	sgrpsizer.Add(self.textctrl['Sec Policy #'], 1, wx.EXPAND)
	demo3sizer.Add(sgrpsizer, 0, wx.EXPAND)
	
	#Insured Info (if not the patient)
	InsNameLabel = wx.StaticText(self, -1, 'First, Middle, Last')
	InsNameLabel.SetFont(Font2)
	demo2sizer.Add(InsNameLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	insnamesizer = wx.BoxSizer(wx.HORIZONTAL)
	insnamesizer.Add(self.textctrl['Ins First'], 2)
	insnamesizer.Add(self.textctrl['Ins Mid Initial'], 1, wx.LEFT|wx.RIGHT, 5)
	insnamesizer.Add(self.textctrl['Ins Last'], 3, wx.EXPAND)
	self.textctrl['Ins Last'].Bind(wx.EVT_KILL_FOCUS, self.OnInsKillFocus)
	demo2sizer.Add(insnamesizer, 0, wx.EXPAND)
	InsAddrLabel = wx.StaticText(self, -1, 'Address')
	InsAddrLabel.SetFont(Font2)
	demo2sizer.Add(InsAddrLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	demo2sizer.Add(self.textctrl['Ins Address'], 1, wx.EXPAND)
	InsCityLabel = wx.StaticText(self, -1, 'City State Zip Phone')
	InsCityLabel.SetFont(Font2)
	demo2sizer.Add(InsCityLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	inscstsizer = wx.BoxSizer(wx.HORIZONTAL)
	inscstsizer.Add(self.textctrl['Ins City'], 3)
	inscstsizer.Add(self.textctrl['Ins State'], 1, wx.LEFT|wx.RIGHT, 5)
	inscstsizer.Add(self.textctrl['Ins Zip'], 2, wx.RIGHT, 5)
	inscstsizer.Add(self.textctrl['Ins Phone'], 4, wx.EXPAND)
	demo2sizer.Add(inscstsizer, 0, wx.EXPAND)
	#InsDOBLabel = wx.StaticText(self, -1, 'DOB  Sex')
	#InsDOBLabel.SetFont(Font2)
	#demo2sizer.Add(InsDOBLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	#inssexsizer = wx.BoxSizer(wx.HORIZONTAL)
	#inssexsizer.Add(self.textctrl['Ins DOB'], 1, wx.RIGHT, 5)
	#inssexsizer.Add(self.textctrl['Ins Gender'], 1, wx.EXPAND)
	#demo2sizer.Add(inssexsizer, 0, wx.EXPAND)
	#emplLabel = wx.StaticText(self, -1, 'Employer')
	#emplLabel.SetFont(Font2)
	#demo2sizer.Add(emplLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	#demo2sizer.Add(self.textctrl['Ins Employer'], 1, wx.EXPAND)
	
	#Contact Info
	relationshipLabel = wx.StaticText(self, -1, 'Advanced Directive?') 
	relationshipLabel.SetFont(Font2)
	demo4sizer.Add(relationshipLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	relationshipSizer = wx.BoxSizer(wx.HORIZONTAL)
	self.adv_dirYesRB = wx.RadioButton(self, -1, 'Yes', style=wx.RB_GROUP)
        self.adv_dirNoRB = wx.RadioButton(self, -1, 'No')
	self.adv_dirUnknownRB = wx.RadioButton(self, -1, 'Unknown')
	self.adv_dirYesRB.SetFont(Font2)
	relationshipSizer.Add(self.adv_dirYesRB)
	self.adv_dirNoRB.SetFont(Font2)
	relationshipSizer.Add(self.adv_dirNoRB)
	self.adv_dirUnknownRB.SetFont(Font2)
	relationshipSizer.Add(self.adv_dirUnknownRB)
	self.proxyBox = wx.CheckBox(self, -1, "Contact is healthcare proxy.")
	self.proxyBox.SetFont(Font2)
	relationshipSizer.Add((35, -1))
	relationshipSizer.Add(self.proxyBox)
	demo4sizer.Add(relationshipSizer, 0, wx.EXPAND)
	guarNameLabel = wx.StaticText(self, -1, 'First, Last Name')
	guarNameLabel.SetFont(Font2)
	demo4sizer.Add(guarNameLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	guarnamesizer = wx.BoxSizer(wx.HORIZONTAL)
	guarnamesizer.Add(self.textctrl['Guarantor First'], 1, wx.RIGHT, 5)
	guarnamesizer.Add(self.textctrl['Guarantor Last'], 1, wx.EXPAND)
	self.textctrl['Guarantor Last'].Bind(wx.EVT_KILL_FOCUS, self.OnGuarKillFocus)
	demo4sizer.Add(guarnamesizer, 0, wx.EXPAND)
	gAddrLabel = wx.StaticText(self, -1, 'Address')
	gAddrLabel.SetFont(Font2)
	demo4sizer.Add(gAddrLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	demo4sizer.Add(self.textctrl['Guarantor Address'], 0, wx.EXPAND)
	gCityLabel = wx.StaticText(self, -1, 'City State Zip Phone')
	gCityLabel.SetFont(Font2)
	demo4sizer.Add(gCityLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	guarcstsizer = wx.BoxSizer(wx.HORIZONTAL)
	guarcstsizer.Add(self.textctrl['Guarantor City'], 3)
	guarcstsizer.Add(self.textctrl['Guarantor State'], 1, wx.LEFT|wx.RIGHT, 5)
	guarcstsizer.Add(self.textctrl['Guarantor Zip'], 2, wx.RIGHT, 5)
	guarcstsizer.Add(self.textctrl['Guarantor Phone'], 4, wx.EXPAND)
	demo4sizer.Add(guarcstsizer, 0, wx.EXPAND)

	#Other Info (mainly added for NCQA purposes)
	demo5sizer.Add(wx.StaticText(self, -1, '                        ')) #no label needed, spacing only
	marriedSizer = wx.BoxSizer(wx.HORIZONTAL)
	self.marriedBox = wx.CheckBox(self, -1, "Married?")
	self.marriedBox.SetFont(Font2)
	marriedSizer.Add(self.marriedBox)
	self.inactiveBox = wx.CheckBox(self, -1, "Inactive Patient")
	self.inactiveBox.SetFont(Font2)
	marriedSizer.Add(self.inactiveBox)
	demo5sizer.Add(marriedSizer, 0, wx.EXPAND)
	languageLabel = wx.StaticText(self, -1, 'Language, PCP')
	languageLabel.SetFont(Font2)
	demo5sizer.Add(languageLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	languageSizer = wx.BoxSizer(wx.HORIZONTAL)
	languageSizer.Add(self.textctrl['Primary Language'], 1, wx.RIGHT, 5)
	languageSizer.Add(self.textctrl['PCP'], 1, wx.EXPAND)
	demo5sizer.Add(languageSizer, 0, wx.EXPAND)
	raceLabel = wx.StaticText(self, -1, 'Race')
	raceLabel.SetFont(Font2)
	demo5sizer.Add(raceLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	demo5sizer.Add(self.textctrl['Race'], 0, wx.EXPAND)


	
	box = wx.StaticBox(self, -1, 'Patient')
	box2 = wx.StaticBox(self, -1, 'Insured')		
	box3 = wx.StaticBox(self, -1, 'Insurance Information')		
	box4 = wx.StaticBox(self, -1, 'Contact')
	box5 = wx.StaticBox(self, -1, 'Other Info')	
	box.SetFont(font1)
	box2.SetFont(font1)
	box3.SetFont(font1)
	box4.SetFont(font1)
	box5.SetFont(font1)
	boxsizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
	box2sizer = wx.StaticBoxSizer(box2, wx.HORIZONTAL)
	box3sizer = wx.StaticBoxSizer(box3, wx.HORIZONTAL)
	box4sizer = wx.StaticBoxSizer(box4, wx.HORIZONTAL)
	box5sizer = wx.StaticBoxSizer(box5, wx.HORIZONTAL)
	boxsizer.Add(demosizer, 1, wx.EXPAND|wx.TOP|wx.BOTTOM, 25)
	box2sizer.Add(demo2sizer, 1, wx.EXPAND|wx.TOP|wx.BOTTOM, 25)
	box3sizer.Add(demo3sizer, 1, wx.EXPAND|wx.TOP|wx.BOTTOM, 25)
	box4sizer.Add(demo4sizer, 1, wx.EXPAND|wx.TOP|wx.BOTTOM, 25)
	box5sizer.Add(demo5sizer, 1, wx.EXPAND|wx.TOP|wx.BOTTOM, 25)

	leftsizer = wx.BoxSizer(wx.VERTICAL)
	leftsizer.Add(boxsizer, 0, wx.EXPAND|wx.BOTTOM, 10)
	leftsizer.Add(box3sizer, 0, wx.EXPAND)
	addPtBtn = EMR_utilities.buildOneButton(self, self, "Add New Patient", self.OnAddPt)
	buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
	leftsizer.Add((-1, 25))
	buttonSizer.Add(addPtBtn, 0)
	rightsizer = wx.BoxSizer(wx.VERTICAL)
	rightsizer.Add(box2sizer, 0, wx.EXPAND|wx.BOTTOM, 10)
	rightsizer.Add(box4sizer, 0, wx.EXPAND|wx.BOTTOM, 10)
	rightsizer.Add(box5sizer, 0, wx.EXPAND)

	if ptID == None:
	    pass
	else:
	    results = EMR_utilities.getDictData('SELECT * FROM demographics WHERE patient_ID = %s;' % (ptID))
	    for label, size, field in self.labels:
		self.textctrl[label].SetValue(str(results[field]))
	    self.textctrl['Phone'].SetValue(EMR_formats.phone_format(self.textctrl['Phone'].GetValue()))
	    self.textctrl['Ins Phone'].SetValue(EMR_formats.phone_format(self.textctrl['Ins Phone'].GetValue()))
	    self.textctrl['Guarantor Phone'].SetValue(EMR_formats.phone_format(self.textctrl['Guarantor Phone'].GetValue()))
	    self.insChoice.SetStringSelection(self.textctrl['Insurance Co'].GetValue())
	    if results['adv_dir'] == '1':
		self.adv_dirYesRB.SetValue(True)
	    elif results['adv_dir'] == '2':
		self.adv_dirNoRB.SetValue(True)
	    else: 
		self.adv_dirUnknownRB.SetValue(True)
	    if results['proxy'] == '1':
		self.proxyBox.SetValue(1)
	    if results['marital_status'] == '1':
		self.marriedBox.SetValue(1)
	    if results['inactive'] == '1':
		self.inactiveBox.SetValue(1)
	    editPtBtn = EMR_utilities.buildOneButton(self, self, "Update Demographics", self.OnEditPt)
	    scanBtn = EMR_utilities.buildOneButton(self, self, "Scan", self.OnScan)
	    buttonSizer.Add(scanBtn, wx.ALL, 10)
	    buttonSizer.Add(editPtBtn, 0)

	leftsizer.Add(buttonSizer, 0)
	mainsizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(leftsizer, 0, wx.RIGHT, 10)
	mainsizer.Add(rightsizer, 0, wx.EXPAND)
	self.SetSizer(mainsizer)
	    
			
    def OnAddPt(self, event):
	self.textctrl['Insurance Co'].SetValue(self.insChoice.GetStringSelection())
	checkBoxes = ''
	if self.adv_dirYesRB.GetValue() == True:
	    checkBoxes = ' adv_dir = "1",'
	elif self.adv_dirNoRB.GetValue() == True:
	    checkBoxes = ' adv_dir = "2",'
	else: 
	    checkBoxes = ' adv_dir = "0",'
	if self.proxyBox.IsChecked():
	    checkBoxes = checkBoxes + ' proxy = "1",'
	if self.marriedBox.IsChecked():
	    checkBoxes = checkBoxes + ' marital_status = "1",'
	qry = 'INSERT INTO demographics SET' + checkBoxes
	for label, size, field in self.labels:
	    qry = ' '.join([qry, '%s = "%s",' % (field, self.textctrl[label].GetValue())])
	qry = qry.rstrip(',') + ';'
	#check to make sure patient doesn't already exist
	dupCheck = 'SELECT firstname, lastname, dob FROM demographics WHERE firstname = "%s" AND lastname = "%s";' \
		% (self.textctrl['First Name'].GetValue(), self.textctrl['Last Name'].GetValue())
	dupResults = EMR_utilities.getData(dupCheck)
	if dupResults:
	    wx.MessageBox("A patient with this name already exists.", 'DUPLICATE', wx.OK)
	else:
	    EMR_utilities.updateData(qry)
	    pt_ID = EMR_utilities.getData("SELECT LAST_INSERT_ID();")
	    UpdoxImporter.Importer(str(pt_ID[0]))

    def OnEditPt(self, event):
	self.textctrl['Insurance Co'].SetValue(self.insChoice.GetStringSelection())
	checkBoxes = ''
	if self.adv_dirYesRB.GetValue() == True:
	    checkBoxes = ' adv_dir = "1",'
	elif self.adv_dirNoRB.GetValue() == True:
	    checkBoxes = ' adv_dir = "2",'
	else:
	    checkBoxes = ' adv_dir = "0",'
	if self.proxyBox.IsChecked():
	    checkBoxes = checkBoxes + ' proxy = "1",'
	else:
	    checkBoxes = checkBoxes + ' proxy = "0",'
	if self.marriedBox.IsChecked():
	    checkBoxes = checkBoxes + ' marital_status = "1",'
	else:
	    checkBoxes = checkBoxes + ' marital_status = "0",'
	if self.inactiveBox.IsChecked():
	    checkBoxes = checkBoxes + ' inactive = "1",'
	else:
	    checkBoxes = checkBoxes + ' inactive = "0",'
	qry = 'UPDATE demographics SET' + checkBoxes
	for label, size, field in self.labels:
	    qry = ' '.join([qry, '%s = "%s",' % (field, self.textctrl[label].GetValue())])
	qry = qry.rstrip(',') + ' WHERE patient_ID = %s;' % (self.ptID)
	EMR_utilities.updateData(qry)

    def OnInsKillFocus(self, event):
	#easy way to populate insured info
	if self.textctrl['Ins Last'].GetValue() == 'self':
	    self.textctrl['Ins Last'].SetValue(self.textctrl['Last Name'].GetValue())
	    self.textctrl['Ins First'].SetValue(self.textctrl['First Name'].GetValue())
	    self.textctrl['Ins Mid Initial'].SetValue(self.textctrl['Mid Initial'].GetValue())
	    self.textctrl['Ins Address'].SetValue(self.textctrl['Address'].GetValue())
	    self.textctrl['Ins City'].SetValue(self.textctrl['City'].GetValue())
	    self.textctrl['Ins State'].SetValue(self.textctrl['State'].GetValue())
	    self.textctrl['Ins Zip'].SetValue(self.textctrl['Zip'].GetValue())
	    self.textctrl['Ins Phone'].SetValue(self.textctrl['Phone'].GetValue())
	    self.textctrl['Ins DOB'].SetValue(self.textctrl['DOB'].GetValue())
	    self.textctrl['Ins Gender'].SetValue(self.textctrl['Sex'].GetValue())
	else: pass

    def OnGuarKillFocus(self, event):
	#easy way to populate guarantor info
	if self.textctrl['Guarantor Last'].GetValue() == 'self':
	    self.textctrl['Guarantor Last'].SetValue(self.textctrl['Last Name'].GetValue())
	    self.textctrl['Guarantor First'].SetValue(self.textctrl['First Name'].GetValue())
	    self.textctrl['Guarantor Address'].SetValue(self.textctrl['Address'].GetValue())
	    self.textctrl['Guarantor City'].SetValue(self.textctrl['City'].GetValue())
	    self.textctrl['Guarantor State'].SetValue(self.textctrl['State'].GetValue())
	    self.textctrl['Guarantor Zip'].SetValue(self.textctrl['Zip'].GetValue())
	    self.textctrl['Guarantor Phone'].SetValue(self.textctrl['Phone'].GetValue())
	elif self.textctrl['Guarantor Last'].GetValue() == 'ins':
	    self.textctrl['Guarantor Last'].SetValue(self.textctrl['Ins Last'].GetValue())
	    self.textctrl['Guarantor First'].SetValue(self.textctrl['Ins First'].GetValue())
	    self.textctrl['Guarantor Address'].SetValue(self.textctrl['Ins Address'].GetValue())
	    self.textctrl['Guarantor City'].SetValue(self.textctrl['Ins City'].GetValue())
	    self.textctrl['Guarantor State'].SetValue(self.textctrl['Ins State'].GetValue())
	    self.textctrl['Guarantor Zip'].SetValue(self.textctrl['Ins Zip'].GetValue())
	    self.textctrl['Guarantor Phone'].SetValue(self.textctrl['Ins Phone'].GetValue())
	else:
	    pass

    def OnScan(self, event):
	dlg = wx.MultiChoiceDialog(self, "What would you like to scan?", "Scan Options", ['ID Cards', 'Assignment Notice', \
				   'Release of Information', 'Consult Note', 'Old Records', 'Insurance Info', 'Labs', \
				   'Radiology', 'Other'])
	if dlg.ShowModal() == wx.ID_OK:
	    if dlg.GetSelections() == [0]:
		EMR_utilities.Scan(185, 65, self.ptID, "Insurance", "card", mode='duplex')
	    elif dlg.GetSelections() == [1]:
		EMR_utilities.Scan(215, 278, self.ptID, "Insurance", "notice")
	    elif dlg.GetSelections() == [2]:
		EMR_utilities.Scan(215, 278, self.ptID, "Other", "ROI", mode='ADF')
	    elif dlg.GetSelections() == [3]:
		EMR_utilities.Scan(215, 278, self.ptID, "Consults", "note", mode='ADF')
	    elif dlg.GetSelections() == [4]:
		EMR_utilities.Scan(215, 278, self.ptID, "Old_Records", "rec", mode='ADF')
	    elif dlg.GetSelections() == [5]:
		EMR_utilities.Scan(215, 278, self.ptID, "Insurance", "misc", mode='ADF')
	    elif dlg.GetSelections() == [6]:
		EMR_utilities.Scan(215, 278, self.ptID, "Labs", "lab", mode='ADF')
	    elif dlg.GetSelections() == [7]:
		EMR_utilities.Scan(215, 278, self.ptID, "Radiology", "rads", mode='ADF')
	    elif dlg.GetSelections() == [8]:
		EMR_utilities.Scan(215, 278, self.ptID, "Other", "misc", mode='ADF')
	else: 
	    wx.MessageBox("If you need to scan, hit the scan button again and select what you want to scan", '', wx.OK)
