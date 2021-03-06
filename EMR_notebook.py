"""Simple electronic medical record designed 2007 by Michael Barron, MD.  This program is loosely based on the EMR 
created for my office in O'Fallon, IL with MSAccess.  This program is written in Python using wxPython for the graphical 
user interface (GUI).  MySQL is the database.

System Requirements: MySQL 5.0, Python 2.6, wxPython 2.8, mysqldb python module, ReportLab module, ObjectListView module 1.2, python imaging library, and python-imaging-sane"""



import time
t1=time.clock()
import wx, os
import sys
import EMR_utilities, Printer, UpdoxImporter
lt = "/home/mb/Desktop/GECKO"
at = ""
wt = "C:\Documents and Settings\mbarron\My Documents\GECKO"
d = EMR_utilities.platformText(lt, at, wt)
sys.path.append(d)
import Selectable, demographics
import wx.lib.flatnotebook as fnb
import MySQLdb
import settings
t2=time.clock()
print 'Importing takes ', round((t2-t1),3), ' seconds.'

"""Note 1: this took me forever to figure out, but I did it without help.  Gives 4 login attempts and then closes.  
Even cooler would be checking a log for last time startup was attempted and force a 5 or 10 minute wait.  
I think connect() function below is my first use of try-except.  Need many more throughout of course."""

class MyApp(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        t1=time.clock()

	self.retry = 0					#see Note 1
	self.connect()
	while self.retry < 4:
	    self.connect()
	if self.retry == 4:
	    sys.exit(1)
	
        self.frame = MyFrame(None, -1, 'EMR', self.user)           #create instance of MyFrame
        self.frame.Show(True)                           #make visible and center frame
        #self.frame.Centre()      			Not necessary.  Interfered with placement of the PtMsg frame.
	#						Turning this off may cause problem with smaller monitors, however.
	
        t2=time.clock()
        print 'MyApp takes ', round((t2-t1),3), ' seconds.'

    def OnExit(self):
        self.conn.close()                               #closes connection to MySQL

    def connect(self):
	self.user = wx.GetTextFromUser("Please enter your user name")
	try:
	    self.conn = MySQLdb.connect(host = "192.168.1.13", #connects to the database
                user = self.user,
                passwd = wx.GetPasswordFromUser("Please enter your password"),
                db = "gecko")
	    self.retry = 5
	except MySQLdb.Error, e:
	    message = "Error %d: %s" % (e.args[0], e.args[1])
	    errorbox = wx.MessageBox(message, "Try again?", wx.YES_NO |wx.ICON_QUESTION) 
	    if errorbox == wx.NO:
		sys.exit(1)
	    else: 
		self.retry = self.retry + 1
		
		
class MyFrame(wx.Frame):
    def __init__(self, parent, id, title, user):
        wx.Frame.__init__(self, parent, id, title, pos=(500, 200), size=(1200,800))

	self.user = user
        t1=time.clock()
        wx.InitAllImageHandlers()                                #this was added for Windows version
        self.nb = fnb.FlatNotebook(self)                #create instance of flatnotebook
        self.ptID = ""
        vbox = wx.BoxSizer(wx.VERTICAL)

        toolbar = wx.ToolBar(self, -1, style=wx.TB_HORIZONTAL | wx.NO_BORDER)
        self.ptname = wx.TextCtrl(toolbar, 1109, "", wx.DefaultPosition, wx.Size(140, -1), style=wx.TE_PROCESS_ENTER)
        
	menuBar = wx.MenuBar()
	sendMenu = wx.Menu()
	macroMenu = wx.Menu()
	sendMenu.Append(101, 'Data to &Updox', 'Send Pt Data to Updox')
	sendMenu.Append(102, 'Data to &Nunova', 'Send Pt Data to Nunova')
	sendMenu.Append(103, '&Letter to Pt', 'Send Pt a Letter')
	sendMenu.Append(105, '&Work Release Ltr', 'Compose Work Release')
	sendMenu.Append(106, '&Panel Ltr', 'Send entire panel a letter')
	sendMenu.Append(107, 'Print Pt &Chart', 'Print notes, labs, consults, and radiology')
	macroMenu.Append(104, '&Medicare Eligibility', 'Send Pt Data to C-SNAP')
	macroMenu.Append(102, 'Data to &Nunova', 'Send Pt Data to Nunova')
	menuBar.Append(sendMenu, '&Send')
	menuBar.Append(macroMenu, '&Macros')
	self.SetMenuBar(menuBar)
	wx.EVT_MENU(self, 101, self.OnUpdox)
	wx.EVT_MENU(self, 102, self.OnNunova)
	wx.EVT_MENU(self, 103, self.OnPtLtr)
	wx.EVT_MENU(self, 104, self.OnMedicare)
	wx.EVT_MENU(self, 105, self.OnWorkRelease)
	wx.EVT_MENU(self, 106, self.OnPanelLtr)
	wx.EVT_MENU(self, 107, self.OnPrintChart)
	
	toolbar.AddSeparator()
        toolbar.AddControl(self.ptname)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter, id = 1109)
        searchBtn = wx.Button(toolbar, wx.ID_ANY, "Search", wx.DefaultPosition, wx.DefaultSize)
        deleteBtn = wx.Button(toolbar, wx.ID_ANY, "Close Patient Record", wx.DefaultPosition, size=(160, -1))
        findFilesBtn = wx.Button(toolbar, wx.ID_ANY, "Find Pt Files", wx.DefaultPosition, size=(150, -1))
	receiptBtn = wx.Button(toolbar, wx.ID_ANY, "Receipt", wx.DefaultPosition, size=(125, -1))
        self.ptText= wx.StaticText(toolbar, wx.ID_ANY, "   No patient selected", wx.DefaultPosition, size=(300, -1), style=wx.ALIGN_CENTER)
        toolbar.AddControl(searchBtn)
        toolbar.AddControl(deleteBtn)
        toolbar.AddControl(findFilesBtn)
	toolbar.AddControl(receiptBtn)
        toolbar.AddControl(self.ptText)
        self.Bind(wx.EVT_BUTTON, self.OnSearch, searchBtn)
        self.Bind(wx.EVT_BUTTON, self.OnDeleteAll, deleteBtn)
        self.Bind(wx.EVT_BUTTON, self.OnFindFiles, findFilesBtn)
	self.Bind(wx.EVT_BUTTON, self.OnReceipt, receiptBtn)
        toolbar.Realize()        

        vbox.Add(toolbar, 0, border=5)
        vbox.Add(self.nb, 1, wx.EXPAND, 5)
        self.SetSizer(vbox)
        self.demogr = demographics.demographics(self.nb)
        self.nb.AddPage(self.demogr, "Demographics")
	self.ptMsgs = MsgFrame(self)
	self.ptMsgs.Show()
	#to prevent errors with other users, make all users home directory the same 
	path = EMR_utilities.getData("SELECT home_dir FROM users WHERE user_name = '%s'" % self.user)
	linuxpath = "%s/Overdue Tasks/Overdue" % (settings.LINUXPATH) + "_%s.txt"
	applepath = "%s/Overdue Tasks/Overdue" % (settings.APPLEPATH) + "_%s.txt"
	windowspath = "%s\\Overdue Tasks\\Overdue" % (settings.WINPATH) + "_%s.txt"
	overdue_file = EMR_utilities.platformText(linuxpath, applepath, windowspath) % EMR_utilities.dateToday()
        qry = """SELECT CONCAT(firstname,' ',lastname), DATEDIFF(CURDATE(),due_date) AS overdue, description 
                FROM todo INNER JOIN demographics USING (patient_ID) 
                WHERE due_date < '%s' AND complete = 0 
                ORDER BY overdue DESC;""" % (EMR_utilities.dateToday())
        if os.access(overdue_file, os.F_OK):		#this tests for overdue_file's existence
            pass
        else:
            results = EMR_utilities.getAllData(qry)
            file = open(overdue_file, 'w')
            for items in results:
                file.write(items[0].ljust(20) + '\t\t' + str(items[1]) + '\t' + items[2] + '\n\n')
            file.close()
        t2=time.clock()
	self.ptname.SetFocus()
        print 'MyFrame takes ', round((t2-t1),3), ' seconds.' 

    def OnTextEnter(self, event):
        self.patient_lookup(event.GetString())

    def OnSearch(self, event):
        self.patient_lookup(self.ptname.GetValue())
        
    def OnDeleteAll(self, event):
        qry = 'SELECT date FROM notes WHERE date > "%s" AND patient_ID = "%s";' % (EMR_utilities.dateToday(), self.ptID)
        if EMR_utilities.getData(qry) == None:
            dlg = wx.MessageDialog(self, "Do you have a note you want to close?", "", wx.YES_NO|wx.ICON_QUESTION)
            answer = dlg.ShowModal()
            if answer == wx.ID_YES: pass
            else:
                self.nb.DeleteAllPages()
                self.demogr = demographics.demographics(self.nb)
                self.nb.AddPage(self.demogr, "Demographics")
                self.ptText.SetLabel("")
		EMR_utilities.MESSAGES = ''
		try:
		    self.ptMsgs.messages.SetLabel(EMR_utilities.MESSAGES)
		except: pass
        else:
            self.nb.DeleteAllPages()
            self.demogr = demographics.demographics(self.nb)
            self.nb.AddPage(self.demogr, "Demographics")
            self.ptText.SetLabel("No patient selected")
	    EMR_utilities.MESSAGES = ''
	    try:
		self.ptMsgs.messages.SetLabel(EMR_utilities.MESSAGES)
	    except: pass

#Another way to reference nb would be to take it out of the __init__ method:
#   nb = wx.Notebook(self)
#
#If I just put 'nb' in the __init__ method then it disappears once __init__ is done and other methods can't 
#reference it. 

    def patient_lookup(self, first_ltrs):               #passes first letters of last name and creates new page c results
        self.page2 = Selectable.Repository(self.nb, -1, first_ltrs)     #creates instance of panel Repository 
        self.nb.AddPage(self.page2, "Patient Lookup")   #adds second page with results
        self.page2.SetFocus()                           #give focus to new page (this isn't working)

    """def onPrintAll(self, event):
        date_dlg = wx.TextEntryDialog(self, "Which date?", style=wx.OK|wx.CANCEL)
        date_dlg.ShowModal()
        qry = 'SELECT firstname, lastname, soap, date \
                FROM notes INNER JOIN demographics USING (patient_ID) \
                WHERE date > "%s" AND date < ADDDATE("%s", 1);' % (date_dlg.GetValue(), date_dlg.GetValue()) 
        notes = EMR_utilities.getAllDictData(qry)
        printer = EMR_utilities.Printer()
	lt = "/home/mb/Desktop/GECKO/EMR Outputs/SoapNote.html"
	at = ""
	wt = "C:\Documents and Settings\mbarron\My Documents\GECKO\EMR_outputs\SoapNote.html"
        for items in notes:
            items['soap'] = EMR_utilities.wrapper(items['soap'], 80)
            form = open(EMR_utilities.platformText(lt, at, wt), 'r')
            s = form.read()
            form.close()
            note_text = s % (items)
            printer.Print(note_text)"""

    def OnFindFiles(self, event):
	#home = EMR_utilities.getData("SELECT home_dir FROM users WHERE user_name = '%s'" % self.user)
	linux = '%s/EMR_outputs/%s' % (settings.LINUXPATH, self.ptID)
	apple = '%s/EMR_outputs/%s' % (settings.APPLEPATH, self.ptID)
	windows = '%s\\EMR_outputs\\%s' % (settings.WINPATH, self.ptID)
	mydir = EMR_utilities.platformText(linux, apple, windows)	#returns path based on OS
	myfile = wx.FileDialog(self, "Open patient file...", mydir, style=wx.OPEN)
	if myfile.ShowModal() == wx.ID_OK:
	    #http://stackoverflow.com/questions/434597/open-document-with-default-application-in-python
	    if sys.platform == 'darwin':
		import subprocess
    		subprocess.call('open', myfile.GetPath())
	    elif sys.platform == 'linux2':
    		os.system('gnome-open ' + myfile.GetPath())
	    else:
		import subprocess
	    	subprocess.call('start', myfile.GetPath())
	    myfile.Destroy()
	else: pass
	

    def OnReceipt(self, event):
	try:
	    print self.ptID
	    p = Printer.MyFancyReceipt(self.ptID, wx.GetTextFromUser("Patient paid how much?"))
	    p.open_file()
	except:
	    wx.MessageBox("Error: Do you have a patient selected?")

    def OnUpdox(self, event):
	UpdoxImporter.Importer(self.ptID)

    def OnNunova(self, event):
	try:
	    EMR_utilities.OnNunova(self.ptID)
	except:
	    wx.MessageBox("Error: Do you have a patient selected?")
	
    def OnPtLtr(self, event):
	Printer.myPtLtr(self, self.ptID)

    def OnWorkRelease(self, event):
	Printer.myWorkRelease(self, self.ptID)

    def OnMedicare(self, event):
	mylist = ['policy_ID', 'firstname', 'lastname', 'dob']
	EMR_utilities.createDataFile(self.ptID, mylist, 'medicare_eligibility')

    def OnPanelLtr(self, event):
	Printer.sendPanelLtr(self)
	
    def OnPrintChart(self, event):
	import pyPdf
	folders = ['Labs', 'Radiology', 'SOAP_notes', 'Consults']
	output = pyPdf.PdfFileWriter()
	for f in folders:
	    try:
		someFiles = os.listdir('/mnt/GECKO/EMR_outputs/%s/%s' % (self.ptID, f))
		for item in someFiles:
		    pdfDocument = os.path.join("/mnt/GECKO/EMR_outputs/%s/%s" % (self.ptID, f), item)
		    input1 = pyPdf.PdfFileReader(file(pdfDocument, "rb"))
		    for page in range(input1.getNumPages()):
			output.addPage(input1.getPage(page))
	    except: pass
	outputStream = file('/mnt/GECKO/EMR_outputs/%s/Other/Chart.pdf' % self.ptID, 'wb')
	output.write(outputStream)
	outputStream.close()
	os.system("lp -d Updox /mnt/GECKO/EMR_outputs/%s/Other/Chart.pdf" % self.ptID)	#prints to Updox Printer
	

"""This is copied from wxPython in Action, p190.  At this point I'm not quite sure what to do if user types in 
wrong username or password.  There is some error msg to capture and then should re-display this dialog."""
class userPwd(wx.Frame):
    def __init__(self, parent):
	wx.Frame.__init__(self, parent, -1, "Login Window", size=(300, 100))
	panel = wx.Panel(self, -1)

	userLabel = wx.StaticText(panel, -1, "User Name:")
	userText = wx.TextCtrl(panel, -1, size=(175, -1))
	userText.SetInsertionPoint(0)
	
	pwdLabel = wx.StaticText(panel, -1, "Password:")
	pwdText = wx.TextCtrl(panel, -1, size=(175, -1), style=wx.TE_PASSWORD)

	sizer = wx.FlexGridSizer(cols=2, hgap=6, vgap=6)
	sizer.AddMany([userLabel, userText, pwdLabel, pwdText])
	panel.SetSizer(sizer)

class MsgFrame(wx.Frame):
    def __init__(self, parent, msg = ''):
	wx.Frame.__init__(self, parent, -1, "Patient Messages", pos = (50,200), size = (400, 600))
	self.panel = wx.Panel(self, -1)
	self.messages = wx.StaticText(self.panel, -1, msg)
	sizer = wx.BoxSizer(wx.HORIZONTAL)
	sizer.Add((10,-1))
        sizer.Add(self.messages, 1, wx.EXPAND, 5)
	sizer.Add((10,-1))
        self.panel.SetSizer(sizer)

app = MyApp()                                           #create instance of MyApp
app.MainLoop()                                          #run program
