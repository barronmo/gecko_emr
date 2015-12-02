import wx
from ObjectListView import ObjectListView, ColumnDefn, ListCtrlPrinter, ReportFormat
import EMR_utilities

class queries(wx.Panel):
    def __init__(self, parent, id=-1, title=None, ptID=None):
        wx.Panel.__init__(self, parent, id, title)
        self.ptID = ptID

        #sizers
        top = wx.BoxSizer(wx.HORIZONTAL)
        midtop = wx.BoxSizer(wx.VERTICAL)
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        #list of table names in gecko, goes in top
        tables = [{'title':'allergies'}, {'title':'consultants'}, {'title':'demographics'}, {'title':'icd_9'}, {'title':'meds'}, \
                  {'title':'notes'}, {'title':'past_history'}, {'title':'problems'}, {'title':'todo'}, {'title':'vitals'}]
        self.tablesList = ObjectListView(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.tablesList.SetColumns([ColumnDefn("Tables", "center", 300, valueGetter='title')])
        self.tablesList.SetObjects(tables)
        top.Add(self.tablesList, 3, wx.EXPAND|wx.ALL, 5)

        #buttons go in midtop; midtop goes in top sizer
        btns = (('Show Columns', self.OnShowColumns),
                ('Delete Query', self.OnDelQuery),
                ('Run Query', self.OnRunQuery),
                ('Print Query', self.OnPrintQuery))
        for label, handler in btns:
            EMR_utilities.buildOneButton(self, self, label, handler, midtop)
        top.Add(midtop, 1, wx.EXPAND|wx.ALL, 5)

        #columns list goes in top sizer
        self.columns = []
        self.columnsList = ObjectListView(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.columnsList.SetColumns([ColumnDefn("Columns", "center", 300, valueGetter="Field")])
        self.columnsList.SetObjects(self.columns)
        top.Add(self.columnsList, 3, wx.EXPAND|wx.ALL, 5)
        mainsizer.Add(top, 3, wx.EXPAND)

        #textctrl for 'where' statement goes below top sizer in main sizer
        self.wherectrl = wx.TextCtrl(self, -1, size=(-1, -1))
        wheretxt = wx.StaticText(self, -1, 'e.g. WHERE patient_ID > 1000 AND short_des LIKE %%DM%%')
        mainsizer.Add(self.wherectrl, 1, wx.EXPAND|wx.ALL, 5)
        mainsizer.Add((-1, 10))
        mainsizer.Add(wheretxt, 1, wx.EXPAND| wx.ALL, 5)
        
        #results list goes below 'where' statement in mainsizer
        
        self.resultsList = ObjectListView(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        mainsizer.Add(self.resultsList, 5, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(mainsizer)

    def OnShowColumns(self, event):
        self.selTables = self.tablesList.GetSelectedObjects()
        for items in self.selTables:
            self.columns = self.columns + list(EMR_utilities.getAllDictData(('SHOW COLUMNS IN %s;' % items['title'])))
        self.columnsList.SetObjects(self.columns)
        
    def OnDelQuery(self, event):
        self.columns = []
        self.columnsList.ClearAll()
        self.resultsList.ClearAll()
        self.columnsList.SetColumns([ColumnDefn("Columns", "center", 300, valueGetter="Field")])
        self.columnsList.SetObjects(self.columns)
        

    def OnRunQuery(self, event):
        columnList = ""
        defnList = []
        if self.wherectrl == '':
            msg = wx.MessageDialog(self, "Do you want a WHERE statement?", "Question", wx.YES|wx.NO|wx.CANCEL)
            msg.ShowModal()
        else:
            if self.columnsList.GetSelectedItemCount() > 1:
                selColumns = self.columnsList.GetSelectedObjects()
            elif self.columnsList.GetSelectedItemCount() == 0:
                msg = wx.MessageDialog(self, "Please select a column", "Info", wx.OK)
                msg.ShowModal()
            else:
                selColumns = self.columnsList.GetSelectedObject()
            for items in selColumns:
                columnList = columnList + items["Field"] + ', '
            columnList = columnList.rstrip(', ')
            if self.tablesList.GetSelectedItemCount() == 3:
                qry = "SELECT %s FROM %s INNER JOIN %s USING (patient_ID) INNER JOIN %s USING (patient_ID) %s"  % \
                      (columnList, self.selTables[0]['title'], self.selTables[1]['title'], self.selTables[2]['title'], self.wherectrl.GetValue())
            elif self.tablesList.GetSelectedItemCount() == 2:
                qry = "SELECT %s FROM %s INNER JOIN %s USING (patient_ID) %s" % (columnList, self.selTables[0]['title'],
                                                                                 self.selTables[1]['title'],
                                                                                 self.wherectrl.GetValue())
            else:
                qry = "SELECT %s FROM %s %s" % (columnList, self.selTables[0]['title'], self.wherectrl.GetValue())
            results = list(EMR_utilities.getAllDictData(qry))
            for items in selColumns:
                defn = ColumnDefn(items["Field"].capitalize(), "center", 100, valueGetter=items["Field"])
                defnList.append(defn)
            self.resultsList.SetColumns(defnList)
            self.resultsList.SetObjects(results)
            

    def OnPrintQuery(self, event):
        prnt = ListCtrlPrinter()
        #prntPreview = prnt.printout.GetPrintPreview()
        prnt.Clear()
        prnt.AddListCtrl(self.resultsList)
        prnt.Watermark ='SIHF'
        prnt.Print()
