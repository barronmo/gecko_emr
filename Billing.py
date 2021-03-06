#!/usr/bon/env python

import wx
import EMR_utilities

class CptFrame(wx.Frame):
    def __init__(self, parent, ptID=None, noteID=None):
	wx.Frame.__init__(self, None, -1, "Billing", size=(900, 700))
	
	self.noteID = noteID
	self.ptID = ptID
	self.textctrl = {}
	font1 = wx.Font(12, wx.SWISS, wx.NORMAL, wx.LIGHT)
	font2 = wx.Font(7, wx.SWISS, wx.NORMAL, wx.LIGHT)
	
	self.cptLabels = (('Date', 100, 'date'), ('POS', 30, 'POS'), ('CPT', 60, 'CPT_code'), ('A', 30, 'mod_A'),
			  ('B', 30, 'mod_B'), ('C', 30, 'mod_C'), ('D', 30, 'mod_D'), ('Pter', 40, 'dx_pter'),
			  ('Charges', 60, 'total_charge'), ('Units', 20, 'units'), ('1 Ins Pmt', 50, '1_ins_pmt'),
			  ('2 Ins Pmt', 50, '2_ins_pmt'), ('Pt Pmt', 50, 'pt_pmt'), ('Adj', 50, 'pmt_adj'),
			  ('Balance', 60, 'balance'), ('Rendering Doc', 90, 'rendering_doc'))

	lowerGridSizer = wx.FlexGridSizer(cols=16, hgap=5, vgap=5)
	mainSizer = wx.BoxSizer(wx.VERTICAL)
	for label, size, field in self.cptLabels:	#adds row of labels at top of grid
	    cptLabel = wx.StaticText(self, -1, label)
	    cptLabel.SetFont(font2)
	    lowerGridSizer.Add(cptLabel, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
	for label, size, field in self.cptLabels:
	    EMR_utilities.buildOneTextCtrl(self, label, size)
	    lowerGridSizer.Add(self.textctrl[label], 1)
	self.Bind(wx.EVT_TEXT, self.OnCPTlookup, self.textctrl['CPT'])
	self.textctrl['CPT'].Bind(wx.EVT_KILL_FOCUS, self.OnLeaveCPT, self.textctrl['CPT'])
	textLabel = wx.StaticText(self, -1, 'Billing Notes  CLICK UPDATE TO SAVE NOTES!')
	self.textctrl['Notes'] = wx.TextCtrl(self, -1, size=(800, 500), style=wx.TE_MULTILINE)
	
	cptLabel = wx.StaticText(self, -1, 'Procedure Codes')
	cptLabel.SetFont(font1)
	mainSizer.Add(cptLabel, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
	mainSizer.Add((-1, 10))
	mainSizer.Add(lowerGridSizer, 0)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL) 
	submitBtn = EMR_utilities.buildOneButton(self, self, "Submit", self.OnSubmit, btnSizer)
	self.dictNumber = 0
	if self.noteID == None:
	    msg = wx.MessageBox('You need to select a note to code.', 'No Note Selected')
	    msg.ShowModal()
	else:
	    self.results = EMR_utilities.getAllDictData('SELECT * FROM billing WHERE note_number = %s;' % (self.noteID[0]))
	    if self.results:
		for label, size, field in self.cptLabels:
		    self.textctrl[label].SetValue(str(self.results[self.dictNumber][field]))
		    self.textctrl['charge_number'] = wx.TextCtrl(self, -1, size=(0, -1))
		    self.textctrl['charge_number'].SetValue(str(self.results[self.dictNumber]['charge_number']))
		self.textctrl['Notes'].SetValue(str(self.results[self.dictNumber]['notes']))
	    else:
		qry = 'SELECT date FROM notes WHERE note_number = %s;' % self.noteID
		self.textctrl['Date'].SetValue(EMR_utilities.getData(qry)[0].strftime("%Y-%m-%d"))
		self.textctrl['POS'].SetValue('11')
		self.textctrl['Units'].SetValue('1')
		self.textctrl['Rendering Doc'].SetValue('Barron')
		self.textctrl['Notes'].SetValue("")
	    updateBtn = EMR_utilities.buildOneButton(self, self, "Update", self.OnUpdate, btnSizer)
	btnSizer.Add((50, -1))
	prevBtn = EMR_utilities.buildOneButton(self, self, "Prev", self.OnPrev, btnSizer)
	nextBtn = EMR_utilities.buildOneButton(self, self, "Next", self.OnNext, btnSizer)
	mainSizer.Add((-1, 10))
	mainSizer.Add(btnSizer, 0)
	mainSizer.Add((-1, 10))
	self.EPSDT_List = ['n/a', 'Partial', 'Referral', 'Partial and Referral']
	self.epsdtBox = wx.RadioBox(self, -1, "EPSDT modifiers", choices=self.EPSDT_List)
	self.Bind(wx.EVT_RADIOBOX, self.OnSelectEPSDT_Mod, self.epsdtBox)
	mainSizer.Add(self.epsdtBox, 0)
	mainSizer.Add((-1, 10))
	self.epsdtBox.Show(False)
	
	mainSizer.Add(textLabel, 0)
	mainSizer.Add(self.textctrl['Notes'], 0)
	self.SetSizer(mainSizer)

    def OnSubmit(self, event):
	#make sure numbers contain two digits in Charges
	self.textctrl['Charges'].SetValue('%.2f' % float(self.textctrl['Charges'].GetValue()))

	#check to prevent duplicate billing entries
	duplQry = 'SELECT note_number, CPT_code FROM billing WHERE note_number = %s AND CPT_code = "%s";' % (self.noteID[0], \
			self.textctrl['CPT'].GetValue())
	dupl_results = EMR_utilities.getAllDictData(duplQry)
	if dupl_results:
	    wx.MessageBox('This is a duplicate entry.  Please adjust units on original if needed.', 'Error')
	    pass
	else:
	    qry = 'INSERT INTO billing SET '
	    for label, size, field in self.cptLabels:
		#if self.textctrl[label].GetValue() == ''		Think of a way to bypass when ''
		qry = ' '.join([qry, '%s = "%s",' % (field, self.textctrl[label].GetValue())])
	    qry = ' '.join([qry, 'note_number = %s, patient_ID = %s, notes = "%s";' % (self.noteID[0], \
						self.ptID, self.textctrl['Notes'].GetValue())])
	    EMR_utilities.updateData(qry)
	    self.results = EMR_utilities.getAllDictData('SELECT * FROM billing WHERE note_number = %s;' % (self.noteID[0]))
	    if self.results:
		for label, size, field in self.cptLabels:
		    # may need if statement here to check for ''
		    self.textctrl[label].SetValue(str(self.results[self.dictNumber][field]))
		    self.textctrl['charge_number'] = wx.TextCtrl(self, -1, size=(0, -1))
		    self.textctrl['charge_number'].SetValue(str(self.results[self.dictNumber]['charge_number']))
	    self.textctrl['Notes'].SetValue(str(self.results[self.dictNumber]['notes']))
	    validation = [('Pter', 'You forgot the diagnosis pointer!'), 
		('Pt Pmt', 'Did the patient give you a copay?  If not enter 0.'),
		('Balance', "Don't forget the balance")]
	    for label, msg in validation:	#checks to make sure each of these fields is filled in
		if not self.textctrl[label].GetValue():
		    wx.MessageBox(msg, 'Grave Mistake!')
	#ask about e-prescribing codes for patients over 65
	gQry = "SELECT * FROM billing WHERE note_number = %s AND CPT_code = 'G8427';" % self.noteID[0]
	gQryResult = EMR_utilities.getData(gQry)
	if EMR_utilities.getAgeYears(self.ptID) > 100 and gQryResult is None:
	    dlg = wx.MessageDialog(None, "Add med review code?", "Important", wx.YES_NO | wx.ICON_QUESTION)
	    if dlg.ShowModal() == wx.ID_YES:
		q = "INSERT INTO billing SET note_number = '%s', patient_ID = '%s', date = '%s', \
			POS = '11', CPT_code = 'G8427', dx_pter = '1', total_charge = '0.01', units = '1', \
			pt_pmt = '0', balance = '0.01', rendering_doc = 'Barron', mod_A = '', mod_B = '', \
			mod_C = '', mod_D = '';" % (self.noteID[0], self.ptID, self.textctrl['Date'].GetValue())
		EMR_utilities.updateData(q)
	    else: pass 
	
		
    def OnUpdate(self, event):
	qry = 'UPDATE billing SET'
	for label, size, field in self.cptLabels:
	    qry = ' '.join([qry, '%s = "%s",' % (field, self.textctrl[label].GetValue())])
	qry = ' '.join([qry, 'notes = "%s" WHERE charge_number = %s;' % (self.textctrl['Notes'].GetValue(), \
								self.textctrl['charge_number'].GetValue())])
	EMR_utilities.updateData(qry)
	self.results = EMR_utilities.getAllDictData('SELECT * FROM billing WHERE note_number = %s;' % (self.noteID[0]))
		
    def OnPrev(self, event):
	if self.dictNumber == 0:
	    for label, size, field in self.cptLabels:
		self.textctrl[label].SetValue(str(self.results[self.dictNumber][field]))
	    self.textctrl['charge_number'].SetValue(str(self.results[self.dictNumber]['charge_number']))
	    self.textctrl['Notes'].SetValue(str(self.results[self.dictNumber]['notes']))
	else:
	    self.dictNumber = self.dictNumber - 1
	    for label, size, field in self.cptLabels:
		self.textctrl[label].SetValue(str(self.results[self.dictNumber][field]))
	    self.textctrl['charge_number'].SetValue(str(self.results[self.dictNumber]['charge_number']))
	    self.textctrl['Notes'].SetValue(str(self.results[self.dictNumber]['notes']))

    def OnNext(self, event):
	try:
	    self.dictNumber = self.dictNumber + 1
	    for label, size, field in self.cptLabels:
		self.textctrl[label].SetValue(str(self.results[self.dictNumber][field]))
	    self.textctrl['charge_number'].SetValue(str(self.results[self.dictNumber]['charge_number']))
	    self.textctrl['Notes'].SetValue(str(self.results[self.dictNumber]['notes']))
	except:
	    for label, size, field in self.cptLabels:
		self.textctrl[label].SetValue("")
	    qry = 'SELECT date FROM notes WHERE note_number = %s;' % self.noteID
	    self.textctrl['Date'].SetValue(EMR_utilities.getData(qry)[0].strftime("%Y-%m-%d"))
	    self.textctrl['POS'].SetValue('11')
	    self.textctrl['Units'].SetValue('1')
	    self.textctrl['Rendering Doc'].SetValue('Barron')
	    self.textctrl['Notes'].SetValue("")
	    self.dictNumber = self.dictNumber - 1

    def OnLeaveCPT(self, event):
	try:
	    if int(self.textctrl['CPT'].GetValue()) > 99380 and int(self.textctrl['CPT'].GetValue()) < 99396: 
		self.epsdtBox.Show(True)
		self.textctrl['A'].SetValue('EP')
		self.Layout()
	    else: pass
	except: pass
	#check to see if inpatient CPT used, adjust POS 
	hospList = ['99231', '99232', '99233', '99221', '99222', '99223', '99291', '99292', '99238', '99239', \
		'99218', '99219', '99220', '99217', '99234', '99235', '99236', '99224', '99225', '99226']
	nhList = ['99304', '99305', '99306', '99307', '99308', '99309', '99310', '99315', '99316', '99318']
	homeList = ['99341', '99342', '99343', '99344', '99345', '99347', '99348', '99349', '99350']
	lists = [(hospList, '21'), (nhList, '31'), (homeList, '12')]
	for someList, pos in lists:
	    for cpt in someList:
		if cpt == self.textctrl['CPT'].GetValue():
		    self.textctrl['POS'].SetValue(pos)
	    	else: pass
	
    def OnSelectEPSDT_Mod(self, event):		#modifiers for EPSDT codes per HealthCare USA provider manual
	self.textctrl['B'].SetValue('')
	self.textctrl['C'].SetValue('')
	if event.GetSelection() == 0:
	    pass
	elif event.GetSelection() == 1:
	    self.textctrl['B'].SetValue('52')
	elif event.GetSelection() == 2:
	    self.textctrl['B'].SetValue('UC')
	else:
	    self.textctrl['B'].SetValue('52')
	    self.textctrl['C'].SetValue('UC')

    def OnCPTlookup(self, event):
	if event.GetString() == ' ':
	    #string = wx.GetTextFromUser("Search diagnosis list for ...")
	    qry = 'SELECT proc FROM fee_schedule ORDER BY proc;'
	    results = EMR_utilities.getAllData(qry)
	    cptList = []
	    for items in results:
		cptList.append(items[0])
	    dialog = wx.SingleChoiceDialog(self, 'Select a CPT code', 'CPT List', cptList)
	    if dialog.ShowModal() == wx.ID_OK:
		q = 'SELECT cpt_code, my_fee FROM fee_schedule WHERE proc = "%s";' % dialog.GetStringSelection()
		res = EMR_utilities.getData(q)
		event.EventObject.SetValue(res[0])
		self.textctrl['Charges'].SetValue(str(res[1]))
	    else: pass
	else: pass
	
if __name__ == '__main__':
    app = wx.PySimpleApp()
    CptFrame().Show()
    app.MainLoop()
