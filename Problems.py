import wx
import MySQLdb, sys, time, datetime
import EMR_utilities
from ObjectListView import ObjectListView, ColumnDefn, EVT_CELL_EDIT_STARTING, EVT_CELL_EDIT_FINISHED
from itertools import chain
from collections import Counter
from nltk.tokenize import wordpunct_tokenize


class Problems(wx.Panel):
    def __init__(self, parent, id, ptID):
        wx.Panel.__init__(self, parent, id)

        self.ptID = ptID
        self.problem = '' 	#receives the newly selected problem back from AddProblemDialog
        self.probs = []
        for items in prob_find(ptID):
                self.probs.append(Problem(items["short_des"], items["prob_date"], items["icd10"], items["problem_number"]))
        self.problist = ObjectListView(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.problist.SetColumns([
                ColumnDefn("Problem", "left", 400, valueGetter="short_des"),
                ColumnDefn("First Treated", "left", 100, valueGetter="prob_date"),
                ColumnDefn("ICD-10 Code", "left", 100, valueGetter="icd10")
                ])
        self.problist.rowFormatter = self.rowFormatter
        self.problist.useAlternateBackColors = False
        self.problist.SetObjects(self.probs)
        self.problist.cellEditMode = ObjectListView.CELLEDIT_DOUBLECLICK
        self.problist.Bind(EVT_CELL_EDIT_STARTING, self.HandleCellEditStarting)
        self.problist.Bind(EVT_CELL_EDIT_FINISHED, self.HandleCellEditFinished)
        
                
        leftprob = wx.BoxSizer(wx.VERTICAL)
        rightprob = wx.BoxSizer(wx.VERTICAL)
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)

        buttons = (('Add', self.OnNewProb, leftprob),
             ('Remove', self.OnRemProb, leftprob),
             ('icd Toggle', self.OnToggle, leftprob))
        for label, handler, sizer in buttons:
            EMR_utilities.buildOneButton(self, self, label, handler, sizer)
        clock = EMR_utilities.makeClock(self, leftprob)
            
        rightprob.Add(self.problist, 1, wx.EXPAND | wx.TOP, 5)
        mainsizer.Add(leftprob, 0)
        mainsizer.Add(rightprob, 1, wx.EXPAND)
        self.SetSizer(mainsizer)
        listBilledICD(ptID)
        self.myFont = wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD)


    def OnNewProb(self, event):
        #opens dialog window with fields for new problem, does lookup based on description only, updates MySQL,
        #then clears the list and resets the lists with new query for problems
        dlg = AddProblemDialog(self, self, -1, 'New Problem')
        dlg.ProbInstance = self
        dlg.CenterOnScreen()
        if dlg.ShowModal() == wx.ID_OK:
            today = datetime.date.today()
            newICD = EMR_utilities.getData('SELECT icd10 FROM ICD10billable WHERE short_des = "%s";' % self.problem)
            query = 'INSERT INTO problems10 SET short_des = "%s", prob_date = "%s", patient_ID = "%s", icd10 = "%s";' % \
                (self.problem, today, self.ptID, newICD[0])
            EMR_utilities.updateData(query)
            self.UpdateList()
        dlg.Destroy()


    def OnRemProb(self, event):
        obj = self.problist.GetSelectedObjects()
        for items in obj:
            qry = 'DELETE FROM problems10 WHERE problem_number = %s;' % items.problem_number
            self.problist.RemoveObject(items)
            EMR_utilities.updateData(qry)

    def UpdateList(self):				
        #problems = prob_find(self.ptID)
        self.probs = []
        for items in prob_find(self.ptID):
                self.probs.append(Problem(items["short_des"], items["prob_date"], items["icd10"], items["problem_number"]))
        self.problist.SetObjects(self.probs)

    def HandleCellEditStarting(self, event):
        pass

    def HandleCellEditFinished(self, event):
        sqlstmt = 'UPDATE problems10 SET short_des = "%s" WHERE problem_number = %s;' \
                  % (self.problist.GetItem(event.rowIndex, event.subItemIndex).GetText(),
                     event.rowModel["problem_number"])
        EMR_utilities.updateData(sqlstmt)

    def OnToggle(self, event):
        pass
        
    def rowFormatter(self, listItem, model):
        qryBill = 'SELECT billable FROM ICD10billable WHERE icd10 = "%s";' % model.icd10
        qryHCC = 'SELECT hcc FROM hcc WHERE icd10 = "%s";' % model.icd10
        resultsBill = EMR_utilities.getData(qryBill)
        resultsHCC = EMR_utilities.getData(qryHCC)
        if resultsBill[0] == '0':
            listItem.SetTextColour(wx.RED)
        else: pass
        try:
            if resultsHCC[0] == 'Yes':
                listItem.SetBackgroundColour('Light Grey')
        except: pass      
        


def prob_find(pt_ID):
    a = wx.GetApp()
    cursor = a.conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT short_des, problem_number, prob_date, icd10 FROM problems10 WHERE patient_ID = %s;" % (str(pt_ID)))
    results = list(cursor.fetchall())
    return results
    cursor.close()

def findICD(problem):
    a = wx.GetApp()
    cursor = a.conn.cursor()
    cursor.execute('SELECT icd_9 FROM icd_9 WHERE disease_name = "%s";' % (problem))
    results = cursor.fetchone()
    return str(results).strip("'(),")
    cursor.close()

def listBilledICD(pt_ID):
    icdList = []
    billedProblems = []
    problems = []
    for i in range(1,11):
        #collect the icd10 codes billed with each note for every note in a given calendar year
        qry = "SELECT icd%d FROM notes INNER JOIN demographics USING (patient_ID) \
                WHERE date LIKE '2015%%' AND patient_ID = %s AND icd%d != '';" % (i,pt_ID,i)
        results = EMR_utilities.getAllData(qry)
	for r in results:
        #create a list from the tuple
	    icdList.append(r)
    #we make a set which eliminates any duplicates
    billedIcdList = set(icdList) #during 2015 some will be icd9 and some icd10
    for part in EMR_utilities.getAllData('SELECT short_des FROM problems10 WHERE patient_ID = %s;' % pt_ID):
        #collects problem names in a list
        problems.append(part[0])
    for item in billedIcdList:
        #gets list of billed problem's descriptions but pulls only icd10
        try:
            des = EMR_utilities.getData('SELECT short_des FROM icd10 WHERE icd10 = "%s";' % item[0])
            billedProblems.append(des[0])
        except: pass
            #print 'Icd %s not found!' % item[0]    #these should be all the icd9 codes billed
    for val in billedProblems:
        #subtracts billed problem's names from the pt's problem list
        if val in problems:
            problems.remove(val)
    EMR_utilities.MESSAGES = EMR_utilities.MESSAGES + 'ICD codes not billed this year:\n\n'
    for x in problems:
        EMR_utilities.MESSAGES = EMR_utilities.MESSAGES + '--' + x + '\n'	    
        EMR_utilities.MESSAGES = EMR_utilities.MESSAGES + '\n\n'
        
	
    

class AddProblemDialog(wx.Dialog):
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
                self.resultListBox.Append(str(items[4]))
                short_des_list.append(items[4])
                refined = Counter(chain.from_iterable(wordpunct_tokenize(x) for x in short_des_list)).most_common(10)
            for items in refined:
                if len(items[0]) > 3:	#removes small words that aren't useful search terms like of, and, the
                    self.refineListBox.Append(str(items).strip("()'").replace("'", ""))

    def EvtSelResultList(self, event):
        self.ProbInstance.problem = event.GetString()


class Problem(object):
    '''Need this class so the ObjectListView rowFormatter will work'''
    def __init__(self, short_des, prob_date, icd10, problem_number):
        self.short_des = short_des
        self.prob_date = prob_date
        self.icd10 = icd10
        self.problem_number = problem_number
        




'''
class AddProblemDialog(wx.Dialog):
    def __init__(self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE, useMetal=False,):
	wx.Dialog.__init__(self, parent, ID, title)

#set the controls
	labelDisease = wx.StaticText(self, -1, 'Problem Name')
	self.comboDisease = wx.ComboBox(self, -1, name = '', choices = [], size = (300, -1), style=wx.TE_PROCESS_ENTER)
	self.Bind(wx.EVT_TEXT_ENTER, self.EvtOnEnter, self.comboDisease)
	btnOK = wx.Button(self, wx.ID_OK)
	btnCL = wx.Button(self, wx.ID_CANCEL)
        btnOK.SetDefault()
	btnCL.SetDefault()
	self.Bind(wx.EVT_BUTTON, self.OnOK, btnOK)
	
#set the sizers(layout)
	box = wx.BoxSizer(wx.VERTICAL)
	btnsizer = wx.StdDialogButtonSizer()
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	box.Add(labelDisease)
	box.Add(self.comboDisease)
	btnsizer.AddButton(btnOK)
	btnsizer.AddButton(btnCL)
	btnsizer.Realize()
	mainsizer.Add(box)
	mainsizer.Add(btnsizer)
	self.SetSizer(mainsizer)

	self.comboDisease.SetFocus()

    def EvtOnEnter(self, event):
	a = wx.GetApp()
     	cursor = a.conn.cursor()
     	cursor.execute('SELECT short_des FROM icd10 WHERE short_des LIKE "%%%s%%";' % (event.GetString()))
     	results = cursor.fetchall()
     	cursor.close()
	for item in results:
		string = str(item[0])
		self.comboDisease.Append(string) 

    def OnOK(self, event):
	a = wx.GetApp()
	cursor = a.conn.cursor()
	today = datetime.date.today()
	query = 'INSERT INTO problems SET short_des = "%s", prob_date = "%s", patient_ID = "%s"' % \
			(self.comboDisease.GetValue(), today, self.ProbInstance.ptID)
	cursor.execute(query)
	self.ProbInstance.UpdateList()
	cursor.close()
'''
	
