#!/usr/bin/python

import wx
import sys, time
import MySQLdb
import EMR_utilities, EMR_formats
import os
import settings


def name_find(namefrag):
     a = wx.GetApp()
     cursor = a.conn.cursor()
     cursor.execute("SELECT patient_ID, firstname, lastname, phonenumber, SSN, DOB FROM demographics WHERE lastname LIKE '%s%%'" % (namefrag))
     results = list(cursor.fetchall())
     return results
     cursor.close()

class Repository(wx.Panel):
    def __init__(self, parent, id, starts_with='ba'):
        wx.Panel.__init__(self, parent, id)

        self.log = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
	ptcolumns = (('Patient ID', 95), ('Firstname', 125), ('Lastname', 150), ('Phone', 125), ('SSN', 125), 
		     ('DOB', 100))
	patients = name_find(starts_with)
	self.list = EMR_utilities.buildCheckListCtrl(self, ptcolumns, patients)
        
	vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
	vbox2 = wx.BoxSizer(wx.VERTICAL)

        buttons = (('Get Record', self.OnGetPt, vbox2),
		   ('Deselect', self.OnDeselectAll, vbox2),
		   ('Patient Info', self.OnApply, vbox2))
	for label, handler, sizer in buttons:
	    EMR_utilities.buildOneButton(self, self, label, handler, sizer)
	clock = EMR_utilities.makeClock(self, vbox2)
		
        vbox.Add(self.list, 2, wx.EXPAND | wx.TOP, 3)
        vbox.Add((-1, 10))
        vbox.Add(self.log, 1, wx.EXPAND)
        vbox.Add((-1, 10))
	hbox.Add(vbox2, 0, wx.RIGHT, 5)
        hbox.Add(vbox, 1, wx.EXPAND)
        hbox.Add((3, -1))

        self.SetSizer(hbox)

        self.Centre()
        self.Show(True)

    def OnGetPt(self, event):
        t1=time.clock()
        import Meds, Problems, PMH, Vitals, Notes, demographics, ToDo, Queries, Prevention, Education
        t2=time.clock()
	lt = "%s/EMR_outputs" % settings.LINUXPATH
	at = "%s/EMR_outputs" % settings.APPLEPATH
	wt = "%s\EMR_outputs" % settings.WINPATH
	f = wx.GetTopLevelParent(self)
	num = self.list.GetItemCount()
	if num == 0: 
	    dlg = wx.MessageDialog(None, 'There are no patients to select.  Close window?', 
		  'Problem',  style=wx.YES_NO | wx.YES_DEFAULT)  
	    answer = dlg.ShowModal()
	    if answer == wx.ID_YES:
		f.nb.DeletePage(self)
	    
	else:
	    for i in range(num):
	    	if self.list.IsChecked(i):
		    medspage = Meds.Meds(f.nb, -1, self.list.GetItemText(i))
		    medspage.ptID = self.list.GetItemText(i)
		    probpage = Problems.Problems(f.nb, -1, self.list.GetItemText(i))
		    probpage.ptID = self.list.GetItemText(i)
		    pmhpage = PMH.PMH(f.nb, -1, self.list.GetItemText(i))
		    pmhpage.ptID = self.list.GetItemText(i)
		    vitalspage = Vitals.Vitals(f.nb, -1, self.list.GetItemText(i))
		    vitalspage.ptID = self.list.GetItemText(i)
		    notespage = Notes.Notes(f.nb, -1, self.list.GetItemText(i))
		    f.nb.DeletePage(0)
		    demogr_page = demographics.demographics(f.nb, ptID=self.list.GetItemText(i))
		    todo_page = ToDo.todo(f.nb, -1, PtID=self.list.GetItemText(i))
		    queries_page = Queries.queries(f.nb, ptID=self.list.GetItemText(i))
		    preventspage = Prevention.Prevention(f.nb, -1, ptID=self.list.GetItemText(i))
		    preventspage.ptID = self.list.GetItemText(i)
		    educpage = Education.Notes(f.nb, -1, self.list.GetItemText(i))
		    f.nb.AddPage(demogr_page, 'Demographics')
		    f.nb.AddPage(medspage, 'Medications')
		    f.nb.AddPage(probpage, 'Problems')
		    f.nb.AddPage(pmhpage, 'Past Medical History')
		    f.nb.AddPage(vitalspage, 'Vitals')
		    f.nb.AddPage(notespage, 'Notes')
		    f.nb.AddPage(educpage, 'Education')
		    f.nb.AddPage(todo_page, 'To Do')
		    f.nb.AddPage(preventspage, 'Health Maintenance')
		    f.nb.AddPage(queries_page, 'Queries')
		    base_path = EMR_utilities.platformText(lt, at, wt)
		    folders = ['SOAP_notes', 'Labs', 'Radiology', 'Consults', 'Old_Records', 'Insurance', 'Other', 'Orders']
		    if sys.platform == 'win32':
			if os.path.exists("%s\%s" % (base_path, self.list.GetItemText(i))):
			    pass
			else:
			    for item in folders:
				os.makedirs('%s\%s\%s' % (base_path, self.list.GetItemText(i), item))
		    else:
			if os.path.exists("%s/%s" % (base_path, self.list.GetItemText(i))):
			    pass
			else:
			    for item in folders:
				os.makedirs('%s/%s/%s' % (base_path, self.list.GetItemText(i), item))
		    qry = 'SELECT firstname, lastname, SUM(balance) FROM demographics INNER JOIN billing \
				USING (patient_ID) WHERE patient_ID = "%s";' % self.list.GetItemText(i)
		    results = EMR_utilities.getDictData(qry)
		    try:
			f.ptText.SetLabel('  %s %s    %s        $%d' % (results['firstname'], results['lastname'], \
			    EMR_utilities.getAge(self.list.GetItemText(i)), results['SUM(balance)']))
		    except:
			f.ptText.SetLabel('  %s %s    %s    no balance' % (results['firstname'], results['lastname'], \
			    EMR_utilities.getAge(self.list.GetItemText(i))))
                    f.ptID = self.list.GetItemText(i)
		    
        t3=time.clock()
	if f.ptMsgs:
	    f.ptMsgs.messages.SetLabel(EMR_utilities.MESSAGES)
	    f.ptMsgs.panel.Layout()
	else:
	    wx.MessageBox("You have turned off messages.  Please restart program to see patient messages.", "Messages OFF")
	    pass
                    
    def OnDeselectAll(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            self.list.CheckItem(i, False)

    def OnApply(self, event):
	num = self.list.GetItemCount()
	for i in range(num):
            if i == 0: self.log.Clear()
            if self.list.IsChecked(i):
		#retrieve the patient_ID: p = patient_ID
		#query database for complete demographic info on that patient
		results = EMR_utilities.getDictData('SELECT * FROM demographics WHERE patient_ID = %s;' % (self.list.GetItemText(i)))
		b = EMR_formats.format_address(results)
                self.log.AppendText(b + '\n')
		




