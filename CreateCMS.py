#!/usr/bin/env python

import wx, time, decimal, datetime
import EMR_utilities, settings

class myApp(wx.App):
    def OnInit(self):
	myFrame = cmsFrame(3)
	myFrame.Show()
	return True

class cmsFrame(wx.Frame):
    def __init__(self, parent, PtID):
	wx.Frame.__init__(self, parent, -1, title='Create CMS 1500 Form', pos=(100,100), size=(800,775))
	self.PtID = PtID
	self.myparent = parent	#allows access to notes page
	self.panel = wx.Panel(self, -1)
	self.columns = {}
	#this one is for the Gateway EDI print image file
	self.printImageDict = {}
	for n in range(1, 292):
	    self.columns[n] = ""
	qry = "SELECT * FROM demographics WHERE patient_ID = %s;" % self.PtID
	self.ptResults = EMR_utilities.getDictData(qry)
	self.printImageDict.update(self.ptResults)	#starts collecting the data we need for print image
	self.columns[56] = 'X'
	self.columns[58] = 'X'
	self.columns[61] = 'X'
	self.renderingNPI = '1326063991'
	self.printImageDict['Admit'] = ''
	self.printImageDict['DC'] = ''
	self.whichIns = self.ptResults['insurance_company']
	if self.ptResults['sex'].lower() == 'male':
	    self.columns[21] = 'X'
	    self.printImageDict['msex'] = 'X'
	elif self.ptResults['sex'] == '':
	    dlg = wx.MessageBox('Gender information is missing on this patient.', 'Need more info', style=wx.OK)
	else: 
	    self.columns[22] = 'X'
	    self.printImageDict['fsex'] = 'X'
	if self.ptResults['OtherInsuredGender'] == None:
	    pass
	elif self.ptResults['OtherInsuredGender'].lower() == 'male':
	    self.columns[51] = 'X'
	else: self.columns[52] = 'X'
	if self.ptResults['InsuredGender'] == None:
	    pass
	elif self.ptResults['InsuredGender'].lower() == 'male':
	    self.columns[65] = 'X'
	else: self.columns[66] = 'X'
	self.columns[70] = 'X'
	self.columns[71] = 'sof'			#patient signature
	self.columns[73] = 'sof'			#insured signature- authorizes payment to provider
	self.columns[100] = '26D2013625'		#CLIA number
	self.columns[261] = '386525225'			#TaxID
	self.columns[262] = 'X'				#SSN; either SSN or EIN is checked
	self.columns[264] = self.PtID			#PatientAcctNumber
	self.columns[265] = 'X'				#AcceptAssignYes
	self.columns[267] = decimal.Decimal()		#TotalCharges
	self.columns[268] = decimal.Decimal()		#AmountPaid
	self.columns[270] = 'sof'			#PhysicianSignature
	self.columns[271] = str(EMR_utilities.dateToday())	#PhysicianSignatureDate
	self.columns[272] = 'Barron'			#PhysicianLast
	self.columns[273] = 'Michael'			#PhysicianFirst
	self.columns[274] = 'O'				#PhysicianMidInit
	self.columns[275] = 'Michael Barron MD'		#FacilityName
	self.columns[276] = '8515 Delmar Blvd 217'	#FacilityStreetAddr
	self.columns[277] = 'St. Louis'			#FacilityCity
	self.columns[278] = 'MO'			#FacilityState
	self.columns[279] = '63124-2168'		#FacilityZip
	self.columns[280] = 'St. Louis, MO 63124-2168'	#FacilityCityStateZip
	self.columns[281] = '1326063991'		#FacilityNPI
	self.columns[284] = 'Michael Barron MD'		#SupplierName
	self.columns[285] = '8515 Delmar Blvd #217'	#SupplierStreetAddr
	self.columns[286] = 'St. Louis'			#SupplierCity
	self.columns[287] = 'MO'			#SupplierState
	self.columns[288] = '63124-2168'		#SupplierZip
	self.columns[289] = 'St. Louis, MO 63124-2168'	#SupplierCityStateZip
	self.columns[290] = '3146675276'		#SupplierPhone
	self.columns[291] = '1326063991'		#SupplierNPI
	self.columns[292] = '1326063991'		#GroupID
	
	self.printImageDict['Fac_Adr'] = self.columns[280]

	
	"""Basic plan is to create a dictionary with keys numbered from 1-228 which correspond to the columns in the 
	office ally headers.  Will then fill in the values based on queried data.  Finally will step through the 
	dictionary by key values and build the text file to submit to Office Ally.  The columns are numbers rather 
	than the columns names because we can easily step the number range to create the text file for OA.  Comments
	include the Office Ally header names."""

	#Insurance Address
	cpt_aFields = ('date', 'date', 'POS')
	cpt_bFields = ('CPT_code', 'mod_A', 'mod_B', 'mod_C', 'mod_D', 'dx_pter', 'total_charge')
	
	#insurance type, Box 1, is handled in OnSelectIns
        
	
	sizer = wx.GridBagSizer(10, 30)

	sizer.Add(wx.StaticText(self.panel, -1, "Insurance Type"), pos=(1, 1))
	insListBox = wx.ListBox(self.panel, -1, choices=['Medicare', 'Medicaid', 'Tricare', 'Champus', 'GHP', 'FECA', 'Other'], style=wx.LB_SINGLE)
	sizer.Add(insListBox, pos=(2, 1), span=(4, 1), flag=wx.EXPAND)
	self.Bind(wx.EVT_LISTBOX, self.OnSelectIns, insListBox)

	sizer.Add(wx.StaticText(self.panel, -1, "Relation to Insured"), pos=(1, 2))
	relListBox = wx.ListBox(self.panel, -1, choices=['self', 'spouse', 'child', 'other'], style=wx.LB_SINGLE)
	sizer.Add(relListBox, pos=(2, 2), span=(3, 1), flag=wx.EXPAND)
	self.Bind(wx.EVT_LISTBOX, self.OnSelectRel, relListBox)
	
	self.accList = ['n/a', 'employment', 'auto accident', 'other accident']
	accBox = wx.RadioBox(self.panel, -1, "Illness/Injury due to ..?", choices=self.accList)
	self.Bind(wx.EVT_RADIOBOX, self.OnSelectAcc, accBox)
	sizer.Add(accBox, pos=(4, 3), span=(1, 3))
	
	self.emplList = ['n/a', 'employed', 'full time student', 'part time student']
	emplBox = wx.RadioBox(self.panel, -1, "Employment Status?", choices=self.emplList)
	self.Bind(wx.EVT_RADIOBOX, self.OnSelectEmpl, emplBox)
	sizer.Add(emplBox, pos=(5, 3), span=(1, 3))

	self.marList = ['n/a', 'single', 'married', 'other']
	marBox = wx.RadioBox(self.panel, -1, "Marital status", choices=self.marList)
	self.Bind(wx.EVT_RADIOBOX, self.OnSelectMar, marBox)
	sizer.Add(marBox, pos=(6, 3), span=(1, 3))

	
	otherInsBox = wx.CheckBox(self.panel, -1, "Check if there is other insurance")
	sizer.Add(otherInsBox, pos=(1, 3))
	self.Bind(wx.EVT_CHECKBOX, self.OnSelectOtherIns, otherInsBox)

	self.billSecInsBox = wx.CheckBox(self.panel, -1, "Bill secondary insurance?")
	self.billSecAsPrim = wx.CheckBox(self.panel, -1, "as Primary?")
	secSizer = wx.BoxSizer(wx.HORIZONTAL)
	secSizer.Add(self.billSecInsBox, 0, wx.RIGHT, 5)
	secSizer.Add(self.billSecAsPrim, 0)
	sizer.Add(secSizer, pos=(2, 3))
	self.Bind(wx.EVT_CHECKBOX, self.OnSelectSecIns, self.billSecInsBox)

	self.billForSue = wx.CheckBox(self.panel, -1, "Sue Leon is rendering provider")
	sizer.Add(self.billForSue, pos=(3, 3))
	self.Bind(wx.EVT_CHECKBOX, self.OnBillForSue, self.billForSue)
	
	sizer.Add(wx.StaticText(self.panel, -1, "Date of Injury/Illness?"), pos=(7, 3))
	dpc = wx.TextCtrl(self.panel, size=(120,-1))
	sizer.Add(dpc, pos=(8, 3))
        self.Bind(wx.EVT_KILL_FOCUS, self.OnDateChanged, dpc)
	#below pulls problem date from problem list; if not available then puts in the note's date
	dxQry = 'SELECT short_des FROM icd10 WHERE icd10 = "%s";' % self.myparent.textctrl['ICD #1'].GetValue()
	dx = EMR_utilities.getData(dxQry)
	probDateQry = 'SELECT prob_date FROM problems10 WHERE short_des = "%s" AND patient_ID = %s;' % (dx[0], self.PtID)
	probDate = EMR_utilities.getData(probDateQry)
	if probDate:
	    dpc.SetValue(str(probDate[0]))
	else: 
	    dpc.SetValue(self.myparent.textctrl['Date'].GetValue()[:10])

	self.hospAdmBox = wx.CheckBox(self.panel, -1, "Hospital Admission?")
	sizer.Add(self.hospAdmBox, pos=(9, 3))
	self.admit_dpc = wx.DatePickerCtrl(self.panel, size=(100,-1), style = wx.DP_DEFAULT | wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE)
	sizer.Add(self.admit_dpc, pos=(10, 3))
	self.admit_dpc.Show(False)
	self.Bind(wx.EVT_DATE_CHANGED, self.OnAdmitDateChanged, self.admit_dpc)
	self.Bind(wx.EVT_CHECKBOX, self.OnHospAdmCheck, self.hospAdmBox)

	self.hospDC_Text = wx.StaticText(self.panel, -1, "Hospital Discharge")
	sizer.Add(self.hospDC_Text, pos=(8, 4))
	self.hospDC_Text.Show(False)
	self.dc_dpc = wx.DatePickerCtrl(self.panel, size=(100,-1), style = wx.DP_DEFAULT | wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE)
	self.dc_dpc.Show(False)
	sizer.Add(self.dc_dpc, pos=(9, 4))
	self.Bind(wx.EVT_DATE_CHANGED, self.OnDischargeDateChanged, self.dc_dpc)

	self.FieldText = wx.StaticText(self.panel, -1, "Column:Content eg, 62:marcaine 1% 3cc")
	sizer.Add(self.FieldText, pos=(7, 1), span=(1, 2))
	self.Field1 = wx.TextCtrl(self.panel, size=(200, -1))
	sizer.Add(self.Field1, pos=(8, 1), span=(1, 2))
	self.Field1.Bind(wx.EVT_KILL_FOCUS, self.OnFieldLoseFocus, self.Field1)
	

	doneBtn = EMR_utilities.buildOneButton(self, self.panel, "Done", self.OnDone)
	sizer.Add(doneBtn, pos=(11, 1))
        
	self.panel.SetSizer(sizer)

	dt = time.strptime(dpc.GetValue(), "%Y-%m-%d")
	self.columns[74] = time.strftime("%m/%d/%y", dt)

    def get1500Data(self):
	#collect CPT info from the Billing module
	noteQry = 'SELECT * FROM notes WHERE date = "%s";' % self.myparent.textctrl['Date'].GetValue()
	noteResults = EMR_utilities.getDictData(noteQry)
	self.noteNumber = noteResults['note_number']	#need this for OnDone
	self.columns[89] = noteResults['icd1']		#DiagCode1, etc
	self.columns[90] = noteResults['icd2']
	self.columns[91] = noteResults['icd3']
	self.columns[92] = noteResults['icd4']
	self.columns[93] = noteResults['icd5']
	self.columns[94] = noteResults['icd6']
	self.columns[95] = noteResults['icd7']
	self.columns[96] = noteResults['icd8']
	self.printImageDict['icd9'] = noteResults['icd9']
	self.printImageDict['icd10'] = noteResults['icd10']
	
	cptQry = 'SELECT * FROM billing WHERE note_number = %d;' % noteResults['note_number']
	cptResults = EMR_utilities.getAllDictData(cptQry)
	#amt_pd = decimal.Decimal()
	res = len(cptResults)
	if res > 6:
	    dlg = wx.MessageDialog(None, "No more than 6 CPT codes per 1500 form.", "Error")
	    dlg.ShowModal()
	else:
	    for n in range(res):
	    	self.columns[101 + (n*16)] = cptResults[n]['date']		#FromDateOfService
		self.columns[102 + (n*16)] = cptResults[n]['date']		#ToDateOfService
		self.columns[103 + (n*16)] = cptResults[n]['POS']		#PlaceOfService
		self.columns[104 + (n*16)] = ""					#EMG (not used so blank)
		self.columns[105 + (n*16)] = cptResults[n]['CPT_code']		#CPT
		self.columns[106 + (n*16)] = cptResults[n]['mod_A']		#ModifierA
		self.columns[107 + (n*16)] = cptResults[n]['mod_B']		#ModifierB
		self.columns[108 + (n*16)] = cptResults[n]['mod_C']		#ModifierC
		self.columns[109 + (n*16)] = cptResults[n]['mod_D']		#ModifierD
		self.columns[110 + (n*16)] = cptResults[n]['dx_pter']		#DiagCodePointer
		self.columns[111 + (n*16)] = cptResults[n]['total_charge']	#Charges
		self.columns[112 + (n*16)] = cptResults[n]['units']		#Units
		try:
		    if int(cptResults[n]['CPT_code']) > 99380 and int(cptResults[n]['CPT_code']) < 99396:
			self.columns[113 + (n*16)] = 'Y'			#EPSDT- catches well-baby and physicals
			#puts Y in all physicals, should only be EPSDT physicals
		except: pass							#J/G codes raise error- not integers
		self.columns[114 + (n*16)] = ""					#RenderingPhysQualifier
		self.columns[115 + (n*16)] = ""					#RenderingPhysID
		self.columns[116 + (n*16)] = self.renderingNPI			#RenderingPhysNPI  
		emptyStringProblemChildren = ['total_charge', '1_ins_pmt', '2_ins_pmt', 'pt_pmt']
		for kids in emptyStringProblemChildren:				#empty strings raised decimal error
		    try: decimal.Decimal(cptResults[n][kids])
		    except decimal.InvalidOperation: cptResults[n][kids] = 0 	#must convert them to 0 before using them
		self.columns[267] = self.columns[267] + decimal.Decimal(cptResults[n]['total_charge'])	#TotalCharges
		self.columns[268] = self.columns[268] + decimal.Decimal(cptResults[n]['1_ins_pmt']) + \
				    decimal.Decimal(cptResults[n]['2_ins_pmt']) + \
				    decimal.Decimal(cptResults[n]['pt_pmt'])	#AmountPaid
	    for i in range(101, 292):
		self.printImageDict[str(i)] = self.columns[i]
		  
    
    def OnBillForSue(self, event):
	self.renderingNPI = '1053756759'

    def OnSelectIns(self, event):
	#tested: 
	for n in range(7):
	    self.columns[n + 9] = ''
	self.columns[event.GetSelection() + 9] = 'X'
	
    def OnSelectRel(self, event):
	#tested: 
	for n in range(4):
	    self.columns[n + 31] = ''
	self.columns[event.GetSelection() + 31] = 'X'
	
    def OnSelectMar(self, event):
	#tested: 
	for n in range (2):
	    self.columns[n + 40] = ''
	if event.GetSelection() == 0:
	    pass
	else:
	    self.columns[event.GetSelection() + 39] = 'X'	#marital status
	    self.printImageDict[event.GetString()] = 'X'
	
    def OnSelectAcc(self, event):
	#these yes/no questions have 7 related fields including which state for auto accident
	#tested:
	self.columns[56] = 'X'
	self.columns[58] = 'X'
	self.columns[61] = 'X'
	self.columns[55] = ''
	self.columns[57] = ''
	self.columns[60] = ''
	if event.GetSelection() == 1:
	    self.columns[55] = 'X'  
	    self.columns[56] = ''  
	elif event.GetSelection() == 2:
	    self.columns[57] = 'X'
	    self.columns[59] = wx.GetTextFromUser("What state (2 letter abbreviation)?", default_value='MO')
	    self.columns[58] = ''
	elif event.GetSelection() == 3:
	    self.columns[60] = 'X'
	    self.columns[61] = ''
	else: pass
	    
	

    def OnSelectEmpl(self, event):
	#tested: works with multiple clicks
	for n in range(3):
	    self.columns[n + 43] = ''
	if event.GetSelection() == 0:
	    pass
	else:
	    #selections 1, 2, or 3 will put an X in 43, 44, or 45
	    self.columns[event.GetSelection() + 42] = 'X'
	
    def OnSelectOtherIns(self, event):
	#tested: works fine with multiple clicks
	self.columns[69] = ''
	self.columns[70] = ''
	if event.IsChecked() == True:
	    self.columns[69] = 'X'
	else: self.columns[70] = 'X'
	
    def OnSelectSecIns(self, event):
	#tested: works fine with mult clicks
	if event.IsChecked() == True:
	    self.whichIns = self.ptResults['secondary_ins']
	else: self.whichIns = self.ptResults['insurance_company']
	
    def OnDateChanged(self, event):
	dt = time.strptime(str(event.GetDate()), "%a %d %b %Y %H:%M:%S %p %Z")
	self.columns[74] = time.strftime("%m/%d/%y", dt)

    def OnAdmitDateChanged(self, event):
	dt = time.strptime(str(event.GetDate()), "%c")
	self.columns[83] = time.strftime("%m/%d/%y", dt)
	self.printImageDict['Admit'] = self.columns[83]

    def OnDischargeDateChanged(self, event):
	dt = time.strptime(str(event.GetDate()), "%c")
	self.columns[84] = time.strftime("%m/%d/%y", dt)
	self.printImageDict['DC'] = self.columns[84]

    def OnFieldLoseFocus(self, event):
	#user enters data in '19:this is some text' format
	text = self.Field1.GetValue().strip().split(':')
	self.columns[int(text[0])] = text[1]
	
    def OnDone(self, event):
	#create file
	prnt = wx.GetTopLevelParent(self.myparent)
	#dem_page = parent.nb.GetPage(1)		#figured this out using PyCrust (*this will mess up if you have extra pages*)
	path = EMR_utilities.getData("SELECT home_dir FROM users WHERE user_name = '%s'" % prnt.user)
	linuxpath = "/home/%s/Desktop/GECKO/Billing/OfficeAlly" % path[0] + "_%s.txt"
	applepath = "/Users/%s/Desktop/GECKO/Billing/OfficeAlly" % path[0] + "_%s.txt"
	windowspath = "C:\\Documents and Settings\\%s\\My Documents\\GECKO\\Billing\\OfficeAlly" % path[0] + "_%s.txt"
        daily_billing = EMR_utilities.platformText(linuxpath, applepath, windowspath) % EMR_utilities.dateToday()
	a_file = open(daily_billing, 'a')		#'a' will both append to existing and create if nonexistent
	gateway_file = open("/home/%s/Desktop/GECKO/Billing/Gateway" % settings.HOME_FOLDER + "%s.txt" % EMR_utilities.dateToday(), 'a')
	
	#get demographic and insurance data
	insFields = (('InsurancePlanName', 1), ('InsurancePayerID', 2), ('InsuranceStreetAddr', 3), ('InsuranceCity', 4), \
		     ('InsuranceState', 5), ('InsuranceZip', 6), ('InsuranceCityStateZip', 7), ('InsurancePhone', 8))
	fields = (('lastname', 17), ('firstname', 18), ('mid_init', 19), ('dob', 20), ('address', 26), \
		     ('city', 27), ('state', 28), ('zipcode', 29), ('phonenumber', 30), ('sof', 72), \
		     \
		     ('policy_ID', 16), ('InsuredLast', 23), ('InsuredFirst', 24), ('InsuredMidInit', 25), \
		     ('InsuredStreetAddress', 35), ('InsuredCity', 36), ('InsuredState', 37), \
		     ('InsuredZip', 38), ('InsuredPhone', 39), \
		     ('InsuredPolicyGroupOrFecaNumber', 63), ('InsuredDOB', 64), \
		     ('InsuredEmployerNameOrSchoolName', 67), ('InsuredInsurancePlanNameOrProgramName', 68), \
		     \
		     ('OtherInsuredLast', 46), ('OtherInsuredFirst', 47), ('OtherInsuredMidInit', 48), \
		     ('OtherInsuredPolicyOrGroupNumber', 49), ('OtherInsuredDOB', 50), \
		     ('OtherInsuredEmployerNameOrSchoolName', 53), ('OtherInsuredInsurancePlanOrProgramName', 54))    
	
        insQry = "SELECT * FROM ins_companies WHERE InsurancePlanName = '%s';" % self.whichIns
	insResults = EMR_utilities.getDictData(insQry)
	self.printImageDict.update(insResults)	#adds more necessary data for print image
	self.createOADict(insFields, insResults)
	self.createOADict(fields, self.ptResults)
	self.get1500Data()
	self.columns[269] = self.columns[267] - self.columns[268]	#BalanceDue
	if self.billSecInsBox.IsChecked():
	    EMR_utilities.updateData('UPDATE billing SET 2ndDate = CURDATE() \
					WHERE note_number = %s;' % (self.noteNumber))
	    self.columns[16] = self.ptResults['secondary_ins_ID']			#replaces the primary ins ID
	    self.columns[63] = self.ptResults['sec_PolicyGroupOrFecaNumber']	#replaces primary ins policy number
	    if self.billSecAsPrim.IsChecked():						#allows billing secondary as primary
		pass
	    else:
		self.columns[1] = self.columns[1] + ' secondary'		#this is how OA does sec ins billing
	else: 
	    EMR_utilities.updateData('UPDATE billing SET 1stDate = CURDATE() \
					WHERE note_number = %s;' % (self.noteNumber))
	if self.hospAdmBox.IsChecked():					#checks to make sure dates are filled in
	    if not self.columns[83]:
		self.columns[83] = EMR_utilities.dateToday('OA')
	    if not self.columns[84]:
		self.columns[84] = EMR_utilities.dateToday('OA')
	for n in range(1, 292):						#remove all the None entries which OA doesn't like
	    if self.columns[n] == None:
		self.columns[n] = ''
	    else: pass
	for n in range(1, 292):
	    a_file.write(str(self.columns[n]) + '\t')
	a_file.write('\n')
	

	"""Print image for Gateway EDI"""

	self.printImageDict['Name'] = self.printImageDict['lastname'] + ', ' + self.printImageDict['firstname']
	self.printImageDict['InsuredName'] = self.printImageDict['InsuredLast'] + ', ' + self.printImageDict['InsuredFirst']
	self.printImageDict['InsuranceCityStateZip'] = insResults['InsuranceCity'] + ', ' + insResults['InsuranceState'] + ' ' \
		+ insResults['InsuranceZip']
	self.printImageDict['Medicare'] = self.columns[9]
	self.printImageDict['Medicaid'] = self.columns[10]
	self.printImageDict['Other'] = self.columns[15]
	self.printImageDict['self'] = self.columns[31]
	self.printImageDict['spouse'] = self.columns[32]
	self.printImageDict['child'] = self.columns[33]
	self.printImageDict['other'] = self.columns[34]
	self.printImageDict['empl_no'] = self.columns[56]
	self.printImageDict['auto_no'] = self.columns[58]
	self.printImageDict['other_no'] = self.columns[61]
	self.printImageDict['empl_yes'] = self.columns[55]
	self.printImageDict['auto_yes'] = self.columns[57]
	self.printImageDict['other_yes'] = self.columns[60]
    	self.printImageDict['auto_state'] = self.columns[59]
	self.printImageDict['icd1'] = self.columns[89]
	self.printImageDict['icd2'] = self.columns[90]
	self.printImageDict['icd3'] = self.columns[91]
	self.printImageDict['icd4'] = self.columns[92]
	self.printImageDict['icd5'] = self.columns[93]
	self.printImageDict['icd6'] = self.columns[94]
	self.printImageDict['icd7'] = self.columns[95]
	self.printImageDict['icd8'] = self.columns[96]
	dateList = ['dob', 'sof', 'Admit', 'DC', '101', '117', '133', '149', '165', '181']
	for item in dateList:	#fixes problem with dates not showing up on print image
	    try:
		self.printImageDict[item] = self.printImageDict[item].strftime("%m %d %y")
	    except: 
		self.printImageDict[item] = self.printImageDict[item].replace('/', ' ')
	self.printImageDict['sig'] = 'Signature on File'
	self.printImageDict['267'] = str(self.columns[267])	#total charges converting decimal.decimal to string
	self.printImageDict['268'] = str(self.columns[268])	#this is amount paid, same as above
	#this brings in secondary/other insurance info if present
	if self.ptResults['secondary_ins']:
	    self.printImageDict['OtherInsuredDOB'] = self.printImageDict['dob']
	    self.printImageDict['OtherName'] = self.printImageDict['Name']
	self.printImageDict['Taxonomy'] = '207Q00000X'
	self.printImageDict['CLIA'] = '26D2013625'
	
	myMap = {1:((49, 'InsurancePlanName'),),
	    2:((49, 'InsuranceStreetAddr'),),
	    3:((49, 'InsuranceCityStateZip'),),
	    4:((49, 'InsurancePayerID'),),
	    7:((2, 'Medicare'), (12, 'Medicaid'), (47, 'Other'), (51, 'policy_ID')),
	    9:((2, 'Name'), (31, 'dob'), (44, 'msex'), (48, 'fsex'), (51, 'InsuredName')),
	    11:((2, 'address'), (33, 'self'), (35, 'spouse'), (37, 'child'), (39, 'other'), (51, 'InsuredStreetAddress')),
	    13:((2, 'city'), (28, 'state'), (51, 'InsuredCity'), (74, 'InsuredState')),
	    15:((2, 'zipcode'), (16, 'phonenumber'), (51, 'InsuredZip'), (66, 'InsuredPhone')),
	    17:((2, 'OtherName'), (51, 'InsuredPolicyGroupOrFecaNumber')),
	    19:((2, 'secondary_ins_ID'), (38, 'empl_yes'), (42, 'empl_no')),
	    21:((2, 'OtherInsuredDOB'), (38, 'auto_yes'), (42, 'auto_no'), (45, 'auto_state')),
	    23:((38, 'other_yes'), (42, 'other_no'), (51, 'InsuredInsurancePlanNameOrProgramName')),
	    25:((2, 'secondary_ins'),),
	    29:((9, 'sig'), (39, 'sof'), (59, 'sig')),
	    33:((60, 'Admit'), (72, 'DC')),
	    #37:((4, 'icd1'), (31, 'icd3')),
	    37:((4, 'icd1'), (10, 'icd3'), (16, 'icd5'), (22, 'icd7'), (28, 'icd9')),
	    #39:((4, 'icd2'), (31, 'icd4'), (51, 'CLIA')),
	    39:((4, 'icd2'), (10, 'icd4'), (16, 'icd6'), (22, 'icd8'), (28, 'icd10'), (51, 'CLIA')),
	    #42:((2, '101'), (21, '103'), (27, '105'), (34, '106'), (37, '107'), (40, '108'), (43, '109'), (47, '110'), (54, '111'), (61, '112'), (71, '116')),
	    #44:((2, '117'), (21, '119'), (27, '121'), (34, '122'), (37, '123'), (40, '124'), (43, '125'), (47, '126'), (54, '127'), (61, '128'), (71, '132')),
	    #46:((2, '133'), (21, '135'), (27, '137'), (34, '138'), (37, '139'), (40, '140'), (43, '141'), (47, '142'), (54, '143'), (61, '144'), (71, '148')),
	    #48:((2, '149'), (21, '151'), (27, '153'), (34, '154'), (37, '155'), (40, '156'), (43, '157'), (47, '158'), (54, '159'), (61, '160'), (71, '164')),
	    #50:((2, '165'), (21, '167'), (27, '169'), (34, '170'), (37, '171'), (40, '172'), (43, '173'), (47, '174'), (54, '175'), (61, '176'), (71, '180')),
	    #52:((2, '181'), (21, '183'), (27, '185'), (34, '186'), (37, '187'), (40, '188'), (43, '189'), (47, '190'), (54, '191'), (61, '192'), (71, '196')),
	    42:((2, '101'), (21, '103'), (27, '105'), (34, '106'), (37, '107'), (40, '108'), (43, '109'), (47, '110'), (59, '111'), (66, '112'), (76, '116')),
	    44:((2, '117'), (21, '119'), (27, '121'), (34, '122'), (37, '123'), (40, '124'), (43, '125'), (47, '126'), (59, '127'), (66, '128'), (76, '132')),
	    46:((2, '133'), (21, '135'), (27, '137'), (34, '138'), (37, '139'), (40, '140'), (43, '141'), (47, '142'), (59, '143'), (66, '144'), (76, '148')),
	    48:((2, '149'), (21, '151'), (27, '153'), (34, '154'), (37, '155'), (40, '156'), (43, '157'), (47, '158'), (59, '159'), (66, '160'), (76, '164')),
	    50:((2, '165'), (21, '167'), (27, '169'), (34, '170'), (37, '171'), (40, '172'), (43, '173'), (47, '174'), (59, '175'), (66, '176'), (76, '180')),
	    52:((2, '181'), (21, '183'), (27, '185'), (34, '186'), (37, '187'), (40, '188'), (43, '189'), (47, '190'), (59, '191'), (66, '192'), (76, '196')),
	    53:((2, '261'), (18, '262'), (24, '264'), (40, '265'), (56, '267')),
	    54:((67, '290'),),
	    55:((25, '275'), (54, '284')),
	    56:((25, '276'), (54, '285')),
	    57:((2, '284'), (25, 'Fac_Adr'), (54, '289')),
	    58:((9, '101'), (25, '281'), (54, '291'), (71, 'Taxonomy'))}

	for a in range(1,59):
	    s = ''
	    try:
		for space, entry in myMap[a]:
		    padding = space - len(s)
		    bump = " " * padding
		    try: 
			s = s + bump + self.printImageDict[entry]
		    except: pass #print entry + ' was empty'	#this takes care of empty entries
	    except: pass
	    s = s + '\n'
	    #write newline to myfile
	    gateway_file.write(s)
	gateway_file.write('\n\n\n\n')
	gateway_file.close()
	a_file.close()
	self.Destroy()


    def OnCloseWindow(self, event):
	self.Destroy()

    #def OnFinish(self, event):

    def OnHospAdmCheck(self, event):
	self.hospDC_Text.Show(True)
	self.admit_dpc.Show(True)
	self.dc_dpc.Show(True)
	dlg = wx.SingleChoiceDialog(self, "Which hospital?", "Pick one", ["Glennon", "St. Mary's", "St. Alexius"])
	dlg.ShowModal()
	if dlg.GetStringSelection() == "Glennon":
	    self.columns[275] = 'Cardinal Glennon'				#FacilityName
	    self.columns[276] = '1465 S Grand Blvd'				#FacilityStreetAddr
	    self.columns[277] = 'St. Louis'					#FacilityCity
	    self.columns[278] = 'MO'						#FacilityState
	    self.columns[279] = '63104-1003'					#FacilityZip
	    self.columns[281] = '1508935891'					#FacilityNPI
	    self.printImageDict['Fac_Adr'] = 'St. Louis, MO 63104-1003'
	elif dlg.GetStringSelection() == "St. Alexius":
	    self.columns[275] = 'St. Alexius'					#FacilityName
	    self.columns[276] = '3933 S Broadway'				#FacilityStreetAddr
	    self.columns[277] = 'St. Louis'					#FacilityCity
	    self.columns[278] = 'MO'						#FacilityState
	    self.columns[279] = '63118-4601'					#FacilityZip
	    self.columns[281] = '1023017746'					#FacilityNPI
	    self.printImageDict['Fac_Adr'] = 'St. Louis, MO 63118-4601'
	else:
	    self.columns[275] = "St. Mary's Hospital"		
	    self.columns[276] = '6420 Clayton Road'	
	    self.columns[277] = 'St. Louis'		
	    self.columns[278] = 'MO'			
	    self.columns[279] = '63117-1811'	
	    self.columns[281] = '1497937213'
	    self.printImageDict['Fac_Adr'] = 'St. Louis, MO 63117-1811'
	self.panel.Layout()

    def createOADict(self, fields, results):
	for items in fields:
	    if results[items[0]] == None:
		pass
	    else:
		self.columns[items[1]] = results[items[0]]
		self.printImageDict[items[0]] = results[items[0]]
	
	 

if __name__ == '__main__':
    app = myApp()
    app.MainLoop()
