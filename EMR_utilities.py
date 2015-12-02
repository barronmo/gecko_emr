"""The idea behind this module is to take the code that is repeated many times in the application and refactor it
so that the following functions can be used multiple times rather using duplicate code."""

import wx, wx.html
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
import MySQLdb, sys
import wx.lib.analogclock as ac
import time, datetime, tempfile
import wx.grid
import textwrap, os, sane
import settings
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from wx.html import HtmlEasyPrinting
from pyPdf import PdfFileWriter, PdfFileReader



def buildOneButton(instance, parent, label, handler, sizer=None):
	button = wx.Button(parent, -1, label)
	instance.Bind(wx.EVT_BUTTON, handler, button)
	if sizer == None:
	    pass
	else:
	    sizer.Add(button, 1, wx.EXPAND|wx.ALL, 3)
	return button

def buildOneTextCtrl(instance, label, size, sizer=None):
	"""This function stores the newly created text controls in a dictionary for future reference."""
	instance.textctrl[label] = wx.TextCtrl(instance, -1, size=(size, -1), name=label)
	if sizer == None:
	    pass
	else: 
	    f = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL)
	    l = wx.StaticText(instance, -1, label)
	    l.SetFont(f)
	    sizer.Add(l)
	    sizer.Add((3, -1))
	    sizer.Add(instance.textctrl[label])
	    sizer.Add((15, -1))
		
class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

def buildCheckListCtrl(instance, columns, data):
	"""Robin Dunn helped me with a problem where the program was
        crashing, segfault, because the columns I was setting did not match up
        with the number of columns I was inserting.  This stemmed in part from
        using a dictionary cursor.  Switching to a regular cursor also gave me
        a tuple with the results in the same order every time.  The dictionary cursor
        gives dictionaries which are unordered."""
	ctrl = CheckListCtrl(instance)
	index = 0
	for columnName, columnWidth in columns:
		ctrl.InsertColumn(index, columnName, width = columnWidth)
		index = index + 1
	for i in data:
            col = 1  	
	    newindex = ctrl.InsertStringItem(sys.maxint, str(i[0]))
	    for parts in i[1:]:
                ctrl.SetStringItem(newindex, col, str(parts))
		col = col + 1
		#assert col < len(medcolumns)			#this is where Robin Dunn solved my problem
		if not col < len(columns):
		    break 					#need error msg here
	return ctrl

"""class myObjectListView():
    def __init__(self, instance, columns, data):
        self.ctrl = ObjectListView(instance, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        for columnName, columnWidth in columns:
            for i in data:
                ctrl.SetColumns(ColumnDefn(columnName, "left", columnWidth, i)"""
	
 
def updateList(data, a_list):
	a_list.DeleteAllItems()
	for i in data:	  
	    col = 1  	
	    newindex = a_list.InsertStringItem(sys.maxint, str(i[0]))
	    for parts in i[1:]:
		a_list.SetStringItem(newindex, col, str(parts))
		col = col + 1
		#assert col < len(medcolumns)			#this is where Robin Dunn solved my problem
		if not col < len(i):
		    break					#need error msg here

def getData(query):
	a = wx.GetApp()
	cursor = a.conn.cursor()
	cursor.execute(query)
	results = cursor.fetchone()
	return results
	cursor.close()

def getAllData(query):
	a = wx.GetApp()
	cursor = a.conn.cursor()
	cursor.execute(query)
	results = cursor.fetchall()
	return results
	cursor.close()

def getDictData(query):
	a = wx.GetApp()
	cursor = a.conn.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute(query)
	results = cursor.fetchone()
	return results
	cursor.close()

def getAllDictData(query):
        a = wx.GetApp()
        cursor = a.conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query)
        results = cursor.fetchall()
        return results
        cursor.close()

def changeData(newData, table, field, patient_ID):
	a = wx.GetApp()
	cursor = a.conn.cursor()
	results = cursor.execute('SELECT * FROM past_history WHERE patient_ID = %s;' % (patient_ID))
	if not results:
	    cursor.execute('INSERT INTO %s SET %s = "%s", patient_ID = %s;' % (table, field, newData, patient_ID))
	else:
	    try:
		#for strings (I'm not sure integers will raise error here)
		cursor.execute('UPDATE %s SET %s = "%s" WHERE patient_ID = %s;' % (table, field, newData, patient_ID)) 
	    except:
		#for integers
		cursor.execute('UPDATE %s SET %s = %d WHERE patient_ID = %s;' % (table, field, newData, patient_ID))
	cursor.close()

def makeClock(parent, sizer):
	clock = ac.AnalogClock(parent, size=(80,80), style=wx.RAISED_BORDER,
                                hoursStyle=ac.TICKS_DECIMAL,
                                minutesStyle=ac.TICKS_NONE,
                                clockStyle=ac.SHOW_HOURS_TICKS| \
                                           ac.SHOW_HOURS_HAND| \
                                           ac.SHOW_MINUTES_HAND)
	sizer.Add(clock, 0, wx.ALIGN_BOTTOM | wx.ALL, 5)
	return clock

def dateToday(t='no'):
	if t == 'no':
	    date = time.strftime("%Y-%m-%d", time.localtime())
        elif t == 'sql':
            date = time.strftime("%Y-%m-%d %H.%M.%S", time.localtime()) #comes with time in 00.00.00 format  
	elif t == 'display':
	    date = time.strftime("%d %b %Y", time.localtime()) #gives 26 Aug 1965 format for display 
	elif t == 'file format':
	    date = time.strftime("%Y-%m-%d_%H.%M.%S", time.localtime()) #comes with underscore between date and time
	elif t == 'OA':
	    date = time.strftime("%m/%d/%y", time.localtime()) #Office Ally format for billing
	else: 
	    date = time.strftime("%Y-%m-%d %H%M%S", time.localtime()) #comes with time in 000000 format
	return date

def strToDate(string):
	date = datetime.datetime.strptime(string, "%Y-%m-%d %H.%M.%S")
	return date

def updateData(query):
	a = wx.GetApp()
	cursor = a.conn.cursor()
	cursor.execute(query)
	a.conn.commit()
	cursor.close()
	
def valuesUpdateData(query, values):
	#this allows binary data to be passed to database
	a = wx.GetApp()
	cursor = a.conn.cursor()
	cursor.execute(query, values)
	a.conn.commit()
	cursor.close()
        
class myGrid(wx.grid.Grid):
    def __init__(self, parent, ID, PtID, labels, data, hide=[]):
	wx.grid.Grid.__init__(self, parent, ID)
	self.CreateGrid(len(data), len(labels))
	for row in range(len(data)):
	    for col in range(len(labels)):
		self.SetColLabelValue(col, labels[col])
		self.SetCellValue(row, col, str(data[row][col]))
	self.SetColMinimalAcceptableWidth(0)
	self.AutoSize()
	self.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
	if hide == []:
	    pass
	else:
	    for items in hide:
		self.SetColSize(items, 0)
	self.EnableGridLines(False)

def notePDF(PtID, text, title='Barron Family Medicine', visit_date=dateToday()):
	lt = '%s/EMR_outputs/%s/SOAP_notes/%s.pdf' % (settings.LINUXPATH, PtID, visit_date.replace(' ', '_'))
	at = '%s/EMR_outputs/%s/SOAP_notes/%s.pdf' % (settings.APPLEPATH, PtID, visit_date.replace(' ', '_'))
	wt = '%s\EMR_outputs\%s\SOAP_notes\%s.pdf' % (settings.WINPATH, PtID, visit_date.replace(' ', '_'))
	doc = SimpleDocTemplate(platformText(lt, at, wt))
	styles = getSampleStyleSheet()
	normal = styles['Normal']
	h1 = styles['h1']
	story = [Paragraph(title, h1)]
	story.append(Spacer(1, 0.2*inch))
	story.append(Paragraph("<u>%s   %s</u>" % (getName(PtID), visit_date), normal))
	story.append(Paragraph("<u>DOB: %s</u>" % (getDOB(PtID)), normal))
	story.append(Spacer(1, 0.2*inch))
	go_bold = ('cc:', 'Problems:', 'Meds:', 'Allergies:', 'Vitals:', 'A/P:', 'SH:', 'FH:')
	for i in go_bold:
	    text = text.replace(i, '<b>%s</b>' % i, 1)
	for line in text.split('\n'):
	    if line == '':
		story.append(Spacer(1, 0.15*inch))
	    else:
		story.append(Paragraph(line, normal))
	story.append(Spacer(1, 0.2*inch))
	story.append(Paragraph("%s,  DOB: %s  Visit Date: %s  End of note" % (getName(PtID), getDOB(PtID), visit_date), normal))
	doc.build(story)

def getName(ptID):
	qry = "SELECT firstname, lastname FROM demographics WHERE patient_ID = %s" % ptID
	results = getData(qry)
	name = results[0] + ' ' + results[1]
	return name

def getDOB(ptID):
	qry = "SELECT dob FROM demographics WHERE patient_ID = %s" % ptID
	results = getData(qry)
	return results[0]


class Printer(HtmlEasyPrinting):
    def __init__(self):
        HtmlEasyPrinting.__init__(self)

    def GetHtmlText(self,text):
        "Simple conversion of text.  Use a more powerful version"
        html_text = text.replace('\n\n','<P>')
        html_text = text.replace('\n', '<BR>')
	#html_text = text.replace('\t', '&nbsp')
        return html_text

    def Print(self, text, doc_name = ''):
        self.SetHeader(doc_name)
        self.PrintText(text, doc_name)

    def PreviewText(self, text, doc_name = ''):
        self.SetHeader(doc_name)
        HtmlEasyPrinting.PreviewText(self, text)

def getAge(ptID):
	qry = 'SELECT dob FROM demographics WHERE patient_ID = %s;' % ptID
	dob = getData(qry)	
	age = datetime.date.today() - dob[0]
	if age.days < 32:
	    result = '%s day old' % age.days
	elif 730 > age.days > 31:
	    months, days = divmod(age.days, 30)
	    result = '%s month %s day old' % (months, days)
	elif age.days > 729:
	    years, days = divmod(age.days, 365)
	    result = '%s year old' % years
	else: pass
	return result

def getAgeYears(ptID):
	qry = 'SELECT dob FROM demographics WHERE patient_ID = %s;' % ptID
	dob = getData(qry)
	today = datetime.date.today()
	try:
	    birthday = dob[0].replace(year=today.year)
	except ValueError: # raised when birth date is February 29 and the current year is not a leap year
	    birthday = dob[0].replace(year=today.year, day=born.day-1)
	if birthday > today:
	    return today.year - dob[0].year - 1
	else:
	    return today.year - dob[0].year

def getSex(ptID):
	qry = 'SELECT sex FROM demographics WHERE patient_ID = %s;' % ptID
	sex = getData(qry)
	return sex[0]

def wrapper(text, width):
    """
    A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\n).  This code from Mike Brown found
    at http://code.activestate.com/recipes/148061/.
    """
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line)-line.rfind('\n')-1
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )


class name_fixer():
    def __init__(self, name):
        n = name.strip()
        self.firstname = ''
        self.lastname = ''
        #for lastname, firstname or lastname,firstname
        if n.count(',') == 1:
                np = n.partition(',')
                self.firstname = np[2].strip()
                self.lastname = np[0].strip()
        #for just lastname
        elif n.count(' ') == 0 and n.count(',') == 0:
                self.lastname = n
        #for just firstname if query returns NULL then use name to search for firstnames
        #for fistname lastname
        elif n.count(' ') == 1 and n.count(',') == 0:
                np = n.partition(' ')
                self.firstname = np[0]
                self.lastname = np[2]
        else:
                msg = 'Please provide name as: Lastname, Firstname.'
                dlg = wx.MessageDialog(None, msg, "I didn't catch that name",
                        style=wx.OK, pos=wx.DefaultPosition)
                dlg.ShowModal()
                dlg.Destroy()
                pass

class HTML_Frame(wx.Frame):
    def __init__(self, parent, title, html_str=''):
        wx.Frame.__init__(self, parent, -1, title, size=(700,900))
        html = wx.html.HtmlWindow(self)
        html.LoadPage(html_str)

def platformText(ltext, atext, wtext):
    if sys.platform == 'linux2':
	return ltext
    elif sys.platform == 'darwin':
	return atext
    else:
	return wtext

def CMS_column_choice(numColumns, markColumn):
    #this function marks the chosen column with an 'x' and inserts tabs to match the number of columns
    string = ''
    for n in range(numColumns):
	if n == markColumn:
	    string = string + "x" + "\t" 
	else:
	    string = string + "\t"
    return string

def Scan(x, y, ptID, pt_dir, file_name, device='hpaio:/usb/Officejet_4500_G510n-z?serial=CN078H70X905HR', mode='simplex'):
    sane.init()
    d = sane.get_devices()
    lt = "%s/EMR_outputs/%s/%s/%s-%s.pdf" % (settings.LINUXPATH, ptID, pt_dir, file_name, dateToday('file format'))
    at = "%s/EMR_outputs/%s/%s/%s-%s.pdf" % (settings.LINUXPATH, ptID, pt_dir, file_name, dateToday('file format'))
    wt = "%s\EMR_outputs\%s\%s\%s-%s.pdf" % (settings.WINPATH, ptID, pt_dir, file_name, dateToday('file format'))
    if mode == 'duplex':
	#check which scanner and then opens the HP which I use for scanning ID cards
	try:						#need try in case there is only one scanner attached
	    if d[1][1] == 'Hewlett-Packard':
		s = sane.open(d[1][0])
	    else:
		s = sane.open(d[0][0])
	except:
	    s = sane.open(d[0][0])
	s.mode = 'gray'
	s.resolution = 150
	s.br_x = x
	s.br_y = y
	image = s.scan()
	wx.MessageBox("Turn doc over in the scanner, then click 'OK'.", "", wx.OK)
	t = tempfile.mkstemp(suffix='.pdf')
	image.save(t[1])
	image2 = s.scan()
	t2 = tempfile.mkstemp(suffix='.pdf')
	image2.save(t2[1])
	inpt = PdfFileReader(open(t[1], 'rb'))
	inpt2 = PdfFileReader(open(t2[1], 'rb'))
	otpt = PdfFileWriter()
	otpt.addPage(inpt.getPage(0))
	otpt.addPage(inpt2.getPage(0))
	newfile = file(platformText(lt, at, wt), 'wb')
	otpt.write(newfile)
	s.close()
	os.remove(t[1])
	os.remove(t2[1])
	sane.exit()
    elif mode == 'ADF':
	if d[1][1] == 'Hewlett-Packard':
	    s = sane.open(d[1][0])
	else:
	    s = sane.open(d[0][0])
	s.mode = 'gray'
	s.resolution = 150
	s.br_x = x
	s.br_y = y
	msg = wx.MessageDialog(None, "Would you like an ADF Scan?", "", style=wx.YES_NO)
	otpt = PdfFileWriter()
	while msg.ShowModal() == wx.ID_YES:
	    image = s.multi_scan()
	    t = tempfile.mkstemp(suffix='.pdf')
	    image.save(t[1])
	    inpt = PdfFileReader(open(t[1], 'rb'))
	    otpt.addPage(inpt.getPage(0)) 
	    #s.cancel()
	newfile = file(platformText(lt, at, wt), 'wb')
	otpt.write(newfile)
	s.close()
	os.remove(t[1])
	sane.exit()    
    else:
	try:						#need try in case there is only one scanner attached
	    if d[1][1] == 'Hewlett-Packard':
		s = sane.open(d[1][0])
	    else:
		s = sane.open(d[0][0])
	except:
	    s = sane.open(d[0][0])
	s.mode = 'gray'
	s.resolution = 150
	s.br_x = x
	s.br_y = y
	image = s.scan()
	image.save(platformText(lt, at, wt))
	s.close()
	sane.exit()
	
def OnNunova(PtID):
    """This function builds a txt file that iMacros uses to load new pt info via their webpage."""
    qry = 'SELECT * FROM demographics WHERE patient_ID = %s;' % PtID
    dem_data = getDictData(qry)
    if dem_data['state'] == 'MO':
	dem_data['state'] = 'Missouri'
    elif dem_data['state'] == 'IL':
	dem_data['state'] = 'Illinois'
    else: print 'pass'	#I may need error msg here for people that don't live in the MO/IL area
    s = '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' % (dem_data['firstname'], dem_data['lastname'], dem_data['address'], \
						    dem_data['city'], dem_data['state'], dem_data['zipcode'], \
						    dem_data['phonenumber'], dem_data['dob'].strftime("%m/%d/%Y"), \
						    dem_data['dob'].strftime('%b'), dem_data['dob'].strftime('%d').lstrip('0'), \
						    dem_data['dob'].strftime('%Y'), dem_data['sex'].capitalize(), PtID)
    with open('/home/mb/Dropbox/iMacros/Datasources/dem_data.txt', 'w') as f:
	f.write(s)
	f.close()

def createDataFile(PtID, data, macro):
    '''This function takes patient_ID and a list of data to pull from the demographics table.  Saves macro specific
    text file for iMacros in the appropriate Dropbox folder.  Items in data must be correct names of demographics fields.'''
    qry = 'SELECT * FROM demographics WHERE patient_ID = %s;' % PtID
    dem_data = getDictData(qry)
    s = ''
    dem_data['dob'] = dem_data['dob'].strftime("%m,%d,%Y")
    if macro == 'medicare_eligibility':
	dem_data['firstname'] = dem_data['firstname'][:1]
    else: pass
    for items in data:
	s = s + dem_data[items] + ', '
    with open('/home/mb/Dropbox/iMacros/Datasources/%s.txt' % macro, 'w') as f:
	f.write(s)  
	f.close() 

def findObjectAttr(obj):
    for item in dir(obj):
	print item, ": ", getattr(obj, item)

MESSAGES = ''
	
