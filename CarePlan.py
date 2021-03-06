#!/usr/bon/env python

import wx
import EMR_utilities
import EMR_formats

class CarePlanFrame(wx.Frame):
    def __init__(self, parent, ptID=None, noteID=None):
	wx.Frame.__init__(self, parent, -1, "Care Plan", size=(600, 500))

	self.ptID = ptID
	self.counter = 1
	self.icd = ''
	#self.ePage = notesinstance.GetParent().GetPage(7)	#Getting pages out of order will screw this up
	self.ePage = wx.GetApp().frame.nb.GetPage(7)		#I think this works as well
	self.ePage.educNote.Show(False)
	self.ePage.neweducNote.Show(True)
	self.ePage.textctrl['Date'].SetValue(str(EMR_utilities.dateToday(t='sql')))
	self.ePage.Layout()
	self.ePage.neweducNote.WriteText(EMR_formats.educNote(self.ptID))
	sideSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainSizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	loadBtn = EMR_utilities.buildOneButton(self, self, "Load", self.OnLoad, btnSizer)
	doneBtn = EMR_utilities.buildOneButton(self, self, "Done", self.OnDone, btnSizer)
	dxLabel = wx.StaticText(self, -1, 'Diagnosis')
	self.dxTextCtrl = wx.TextCtrl(self, -1, size=(500, 25))
	instrLabel = wx.StaticText(self, -1, "Patient Instructions. Start lines with '-'.")
	self.instrTextCtrl = wx.TextCtrl(self, -1, size=(500, 150), style=wx.TE_MULTILINE)
	planLabel = wx.StaticText(self, -1, 'Other: thoughts, DDx, etc')
	self.planTextCtrl = wx.TextCtrl(self, -1, size=(500, 150), style=wx.TE_MULTILINE)
	mainSizer.AddMany([dxLabel, self.dxTextCtrl, (-1, 10), \
		instrLabel, self.instrTextCtrl, (-1, 10), \
		planLabel, self.planTextCtrl, (-1, 10), \
		btnSizer])
	sideSizer.AddMany([(10, -1), mainSizer])
	self.SetSizer(sideSizer)
	self.Bind(wx.EVT_TEXT, self.OnTextEnterICD, self.dxTextCtrl)

    def OnLoad(self, event):
	icdControl = 'ICD #%s' % self.counter
	planString = ""
	planString = str(self.counter) + ') ' + self.dxTextCtrl.GetValue() + ': ' + self.planTextCtrl.GetValue() + \
		'\n\tPatient Instructions:\n' + self.instrTextCtrl.GetValue().replace("-", "\t\t-") + '\n\n'
	if self.notesinstance.newsoapNote.IsShown():
	    self.notesinstance.newsoapNote.WriteText(planString)
	else:
	    self.notesinstance.soapNote.WriteText(planString)
	self.notesinstance.textctrl[icdControl].SetValue(self.icd)	#this will overwrite existing value; this is why we do care plan only once
	self.icd = ""
	ptInstructions = str(self.counter) + ') ' + self.dxTextCtrl.GetValue() + \
	    ': \n' + self.instrTextCtrl.GetValue().replace("-", "   -") + '\n'
	self.ePage.neweducNote.WriteText(ptInstructions)
	self.dxTextCtrl.SetValue("")
	self.instrTextCtrl.SetValue("")
	self.planTextCtrl.SetValue("")
	self.dxTextCtrl.SetFocus()
	self.counter = self.counter + 1

    def OnDone(self, event):
	dlg = wx.MessageDialog(None, "Are you sure you want to close?  You can only use the care plan button once.", "Important", wx.YES_NO | wx.ICON_QUESTION)
	if dlg.ShowModal() == wx.ID_YES:
	    self.Destroy()
	else: pass

    def OnTextEnterICD(self, event):
	#when user enters ' ' create single choice dialog with patient's problem list; inserts ICD code for selected problem
	if event.GetString() == ' ':
	    qry = "SELECT short_des FROM problems10 WHERE patient_ID = %s;" % (self.ptID)
	    results = EMR_utilities.getAllData(qry)
	    ptProbList = []
	    for items in results:
		ptProbList.append(items[0])
	    dialog = wx.SingleChoiceDialog(self, 'Select a problem', "Patient's Problem List", ptProbList)
	    if dialog.ShowModal() == wx.ID_OK:
		icdQry = 'SELECT icd_9 FROM icd_9 WHERE disease_name = "%s";' % dialog.GetStringSelection()
		icdResults = EMR_utilities.getData(icdQry)
		self.icd = icdResults[0]
		event.EventObject.SetValue(dialog.GetStringSelection())
		event.EventObject.MarkDirty()
	    else: pass
	#when user enters '?' pull up problem dialog to search for codes
	elif event.GetString() == '?':
	    string = wx.GetTextFromUser("Search diagnosis list for ...")
	    qry = 'SELECT disease_name FROM icd_9 WHERE disease_name LIKE "%%%s%%";' % (string)
	    results = EMR_utilities.getAllData(qry)
	    probList = []
	    for items in results:
		probList.append(items[0])
	    dialog = wx.SingleChoiceDialog(self, 'Select a problem', 'Master Problem List', probList)
	    if dialog.ShowModal() == wx.ID_OK:
		icdQry = 'SELECT icd_9 FROM icd_9 WHERE disease_name = "%s";' % dialog.GetStringSelection()
		icdResults = EMR_utilities.getData(icdQry)
		self.icd = icdResults[0]
		event.EventObject.SetValue(dialog.GetStringSelection())
		event.EventObject.MarkDirty()
	    else: pass
	elif event.GetString() == 'f':
	    #this option allows search of www.icd9data.com for specified term
	    term = wx.GetTextFromUser("Look up ICD-9 Code: eg, rotator+cuff")
	    string = 'http://www.icd10data.com/Search.aspx?search=%s&codeBook=ICD9CM' % term
	    results = EMR_utilities.HTML_Frame(self, "ICD-9 Help", html_str=string)
            results.Show()
	else: pass
	event.Skip()



if __name__ == '__main__':
    app = wx.PySimpleApp()
    CarePlanFrame().Show()
    app.MainLoop()
