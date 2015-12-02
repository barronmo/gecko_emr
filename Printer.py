import wx
import EMR_utilities, decimal, EMR_formats, settings
import time, os
import cups
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

 
class MyFancyReceipt():
    def __init__(self, ptID, amount):

	self.ptID = ptID
	lt = "%s/EMR_outputs/%s/Other/rcpt-%s.pdf" % (settings.LINUXPATH, self.ptID, EMR_utilities.dateToday())
	at = "%s/EMR_outputs/%s/Other/rcpt-%s.pdf" % (settings.APPLEPATH, self.ptID, EMR_utilities.dateToday())
	wt = "%s\EMR_outputs\%s\Other\rcpt-%s.pdf" % (settings.WINPATH, self.ptID, EMR_utilities.dateToday())
	filename = EMR_utilities.platformText(lt, at, wt)
	doc = SimpleDocTemplate(filename,pagesize=letter,
                        rightMargin=72,leftMargin=72,
                        topMargin=72,bottomMargin=18)
	Story=[]
	#logo = "/home/mb/Documents/icons/idealmedicalpractice-logo-small.png"
	formatted_time = time.strftime("%d %b %Y")
	full_name = settings.NAME
	address_parts = ["8515 Delmar Blvd #217", "University City, MO 63124"]
 
	#im = Image(logo, 2.5*inch, 2*inch)
	#Story.append(im)
 
	styles=getSampleStyleSheet()
	Story.append(Spacer(1, 12))
	styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
	ptext = '<font size=12>%s</font>' % formatted_time
 
	Story.append(Paragraph(ptext, styles["Normal"]))
	Story.append(Spacer(1, 12))
 
	# Create return address
	ptext = '<font size=12>%s</font>' % full_name
	Story.append(Paragraph(ptext, styles["Normal"]))
	for part in address_parts:
	    ptext = '<font size=12>%s</font>' % part.strip()
	    Story.append(Paragraph(ptext, styles["Normal"]))
 
	Story.append(Spacer(1, 12))
	ptext = '<font size=12>To Whom it May Concern::</font>'
	Story.append(Paragraph(ptext, styles["Normal"]))
	Story.append(Spacer(1, 12))

	qry = 'SELECT firstname, lastname FROM demographics WHERE patient_ID = %s;' % ptID 
	results = EMR_utilities.getData(qry)
	ptext = "<font size=12>%s %s was seen in my office today and paid $%s toward their bill.  \
		If there are any further questions, please don't hesitate to contact me at the \
		above address or by phone at (314) 667-5276.</font>" % (results[0], 
									results[1],
									amount)
	Story.append(Paragraph(ptext, styles["Justify"]))
	Story.append(Spacer(1, 12))
 
	ptext = '<font size=12>Sincerely,</font>'
	Story.append(Paragraph(ptext, styles["Normal"]))
	Story.append(Spacer(1, 48))
	ptext = '<font size=12>%s</font>' % settings.NAME
	Story.append(Paragraph(ptext, styles["Normal"]))
	Story.append(Spacer(1, 12))
	doc.build(Story)

    def open_file(self):
	os.system('/usr/bin/gnome-open ' + "%s/EMR_outputs/%s/Other/rcpt-%s.pdf" % \
							(settings.LINUXPATH, self.ptID, EMR_utilities.dateToday()))




class MyReceipt():
    def __init__(self, pt_ID, amount):
	self.amount = amount
	self.pt_ID = pt_ID
	from reportlab.lib.pagesizes import letter
	from reportlab.pdfgen import canvas
	
	lt = "%s/EMR_outputs/%s/Other/rcpt-%s.pdf" % (settings.LINUXPATH, self.pt_ID, EMR_utilities.dateToday('file format'))
	at = "%s/EMR_outputs/%s/Other/rcpt-%s.pdf" % (settings.APPLEPATH, self.pt_ID, EMR_utilities.dateToday('file format'))
	wt = "%s\EMR_outputs\%s\Other\rcpt-%s.pdf" % (settings.WINPATH, self.pt_ID, EMR_utilities.dateToday('file format'))
	filename = EMR_utilities.platformText(lt, at, wt)
	canvas = canvas.Canvas(filename, pagesize=letter)
	canvas.setLineWidth(.3)
	canvas.setFont('Helvetica', 12)
 
	canvas.drawString(30,750,'PAYMENT FOR MEDICAL SERVICES FOR %s' % self.name_find())
	canvas.drawString(30,735,'RENDERED AT BARRON FAMILY MEDICINE')
	canvas.drawString(500,750,"%s" % EMR_utilities.dateToday())
	canvas.line(480,747,580,747)
 
	canvas.drawString(275,725,'AMOUNT PAID:')
	canvas.drawString(500,725,"$%s" % self.amount)
	canvas.line(378,723,580,723)
 
	canvas.drawString(30,703,'RECEIVED BY:')
	canvas.line(120,700,580,700)
	canvas.drawString(120,703, settings.NAME)
 
	canvas.save()

    def open_file(self):
	os.system('/usr/bin/gnome-open ' + "/home/mb/Desktop/GECKO/EMR_outputs/%s/Other/rcpt-%s.pdf" % \
							(self.pt_ID, EMR_utilities.dateToday()))

    def name_find(self):
	q = "SELECT CONCAT(firstname, ' ', lastname) FROM demographics WHERE patient_ID = %s;" % self.pt_ID
	return EMR_utilities.getData(q)

class MyPrintout(wx.Printout):
    def __init__(self, canvas, log):
        wx.Printout.__init__(self)
        self.canvas = canvas
        self.log = log

    def OnBeginDocument(self, start, end):
        return super(MyPrintout, self).OnBeginDocument(start, end)

    def OnEndDocument(self):
        super(MyPrintout, self).OnEndDocument()

    def OnBeginPrinting(self):
        super(MyPrintout, self).OnBeginPrinting()

    def OnEndPrinting(self):
        super(MyPrintout, self).OnEndPrinting()

    def OnPreparePrinting(self):
        super(MyPrintout, self).OnPreparePrinting()

    def HasPage(self, page):
        if page <= 2:
            return True
        else:
            return False

    def GetPageInfo(self):
        return (1, 2, 1, 2)

    def OnPrintPage(self, page):
        dc = self.GetDC()

        #-------------------------------------------
        # One possible method of setting scaling factors...

        maxX = self.canvas.getWidth()
        maxY = self.canvas.getHeight()

        # Let's have at least 50 device units margin
        marginX = 50
        marginY = 50

        # Add the margin to the graphic size
        maxX = maxX + (2 * marginX)
        maxY = maxY + (2 * marginY)

        # Get the size of the DC in pixels
        (w, h) = dc.GetSizeTuple()

        # Calculate a suitable scaling factor
        scaleX = float(w) / maxX
        scaleY = float(h) / maxY

        # Use x or y scaling factor, whichever fits on the DC
        actualScale = min(scaleX, scaleY)

        # Calculate the position on the DC for centering the graphic
        posX = (w - (self.canvas.getWidth() * actualScale)) / 2.0
        posY = (h - (self.canvas.getHeight() * actualScale)) / 2.0

        # Set the scale and origin
        dc.SetUserScale(actualScale, actualScale)
        dc.SetDeviceOrigin(int(posX), int(posY))

        #-------------------------------------------

        self.canvas.DoDrawing(dc, True)
        dc.DrawText("Page: %d" % page, marginX/2, maxY-marginY)

        return True

class myPtBill():
    def __init__(self, ptID):
	self.ptID = ptID
	lt = "%s/EMR_outputs/%s/Other/bill-%s.pdf" % (settings.LINUXPATH, self.ptID, EMR_utilities.dateToday('file format'))
	at = "%s/EMR_outputs/%s/Other/bill-%s.pdf" % (settings.APPLEPATH, self.ptID, EMR_utilities.dateToday('file format'))
	wt = "%s\EMR_outputs\%s\Other\bill-%s.pdf" % (settings.WINPATH, self.ptID, EMR_utilities.dateToday('file format'))
	filename = EMR_utilities.platformText(lt, at, wt)
	doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=60)
	# container for the 'Flowable' objects
	elements = []
 
	styleSheet = getSampleStyleSheet()

	P0 = Paragraph('Barron Family Medicine', styleSheet['Normal'])
	P2 = Paragraph('8515 Delmar Blvd #217', styleSheet['Normal'])
	P3 = Paragraph('University City, MO 63124', styleSheet['Normal'])

	T0 = Paragraph('<para align=RIGHT><font size=16><b>Charges and Payments</b></font></para>', styleSheet['Normal'])
	T1 = Spacer(1, 12)
	T2 = Paragraph('<para align=RIGHT><b>Date Printed:</b> %s</para>' % EMR_utilities.dateToday(), styleSheet['Normal'])
	T3 = Paragraph('<para align=RIGHT><b>Provider:</b> %s</para>' % settings.NAME, styleSheet['Normal'])
	T4 = Paragraph('<para align=RIGHT><b>Office Phone:</b> (314) 667-5276</para>', styleSheet['Normal'])

	data = [[[P0, P2, P3], [T0, T1, T2, T3, T4]]]
 
	t=Table(data, style=[('LEFTPADDING', (0,0), (-1,-1), 0),
			     ('RIGHTPADDING', (0,0), (-1,-1), 0),
			     ('VALIGN', (0,0), (-1,-1), 'TOP')])
	t._argW[0]=2.5*inch 
	elements.append(t)

	qry = 'SELECT * FROM demographics WHERE patient_ID = %s;' % self.ptID
	results = EMR_utilities.getDictData(qry)
	elements.append(Spacer(1,12))
	ptext = '<para align=RIGHT><b>Patient:</b> %s %s</para>' % (results['firstname'], results['lastname'])
	elements.append(Paragraph(ptext, styleSheet['Normal']))
	elements.append(Spacer(1,24))
	elements.append(Paragraph('%(firstname)s %(lastname)s' % (results), styleSheet['Normal']))
	elements.append(Paragraph('%(address)s' % results, styleSheet['Normal']))
	elements.append(Paragraph('%(city)s, %(state)s  %(zipcode)s' % results, styleSheet['Normal']))
	elements.append(Spacer(1,36))

	bill_data = [['Service Date', 'Qty', 'Description', 'CPT', 'Amount', 'Patient Balance'],]
	bill_qry = 'SELECT date, units, CPT_code, pt_pmt, 1_ins_pmt, 2_ins_pmt, balance \
			FROM billing \
			WHERE patient_ID = %s AND balance > 0 AND 1_ins_pmt IS NOT NULL;' % self.ptID
	bill_results = EMR_utilities.getAllDictData(bill_qry)
	balance_due = decimal.Decimal()
	for n in range(len(bill_results)):
	    cpt_qry = 'SELECT proc FROM fee_schedule WHERE cpt_code = "%s";' % bill_results[n]['CPT_code']#finds CPT description
	    cpt_results = EMR_utilities.getData(cpt_qry)
	    try: decimal.Decimal(bill_results[n]['1_ins_pmt'])
	    except decimal.InvalidOperation: bill_results[n]['1_ins_pmt'] = 0
	    try: decimal.Decimal(bill_results[n]['2_ins_pmt'])
	    except decimal.InvalidOperation: bill_results[n]['2_ins_pmt'] = 0 
	    ins_payed = decimal.Decimal(bill_results[n]['1_ins_pmt']) + decimal.Decimal(bill_results[n]['2_ins_pmt'])#primary + secondary
	    mylist = [bill_results[n]['date'],
		      bill_results[n]['units'],
		      cpt_results[0] + '\n   Patient Co-pay\n   Paid by Insurance',
		      bill_results[n]['CPT_code'],
		      '\n' + bill_results[n]['pt_pmt'] + '\n' + str(ins_payed),
		      '\n\n\n' + bill_results[n]['balance']]
	    bill_data.append(mylist)
	    balance_due = balance_due + decimal.Decimal(bill_results[n]['balance'])
	T2 = Table(bill_data, style=[('VALIGN', (0,0), (-1,-1), 'TOP'),
				     ('LEFTPADDING', (0,0), (-1,-1), 0),
			     	     ('RIGHTPADDING', (0,0), (-1,-1), 20),
				     ('LINEABOVE', (0,1), (-1,1), 1, colors.black)])
	T2.hAlign = "LEFT"
	elements.append(T2)

	elements.append(Spacer(1,24))
	elements.append(Paragraph('<para align=RIGHT><font size=14><b>Balance Due: </b>$%s</font>' % balance_due, styleSheet['Normal']))
	elements.append(Spacer(1,24))
	mystring = wx.GetTextFromUser("Enter additional notes")
	elements.append(Paragraph('<b>NOTE:</b> %s' % mystring, styleSheet['Normal']))
	elements.append(Spacer(1, 12))
	elements.append(Paragraph('Sincerely,', styleSheet['Normal']))
	
	'''logo = "/home/mb/Dropbox/Office/Signature.png"
	im = Image(logo, 2*inch, 0.75*inch)
	im.hAlign = "LEFT"
	elements.append(im)'''
	chooseSig(elements)
	elements.append(Paragraph(settings.NAME, styleSheet['Normal']))
	elements.append(Spacer(1,24))
	elements.append(Paragraph('<b>Address Change?</b>   Please write below:', styleSheet['Normal']))
	# write the document to disk
	doc.build(elements)
	choosePrinter(filename)


class myPtLtr():
    def __init__(self, parent, ptID, text=""):
	'''Prints a letter, saves a copy to pt folder'''
	self.ptID = ptID
	lt = "%s/EMR_outputs/%s/Other/ltr-%s.pdf" % (settings.LINUXPATH, self.ptID, EMR_utilities.dateToday('file format'))
	at = "%s/EMR_outputs/%s/Other/ltr-%s.pdf" % (settings.APPLEPATH, self.ptID, EMR_utilities.dateToday('file format'))
	wt = "%s\EMR_outputs\%s\Other\ltr-%s.pdf" % (settings.WINPATH, self.ptID, EMR_utilities.dateToday('file format'))
	filename = EMR_utilities.platformText(lt, at, wt)
	doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=60)
	# container for the 'Flowable' objects
	elements = []
 
	styleSheet = getSampleStyleSheet()
	styleSheet.add(ParagraphStyle(name='Address', fontSize=13, leading=15))
	styleSheet.add(ParagraphStyle(name='Body', fontSize=12, leading=14))

	elements.append(Paragraph('Barron Family Medicine', styleSheet['Address']))
	elements.append(Paragraph('8515 Delmar Blvd #217', styleSheet['Address']))
	elements.append(Paragraph('University City, MO 63124', styleSheet['Address']))

	qry = 'SELECT * FROM demographics WHERE patient_ID = %s;' % self.ptID
	results = EMR_utilities.getDictData(qry)
	elements.append(Spacer(1,48))
	elements.append(Paragraph('%(firstname)s %(lastname)s' % (results), styleSheet['Address']))
	elements.append(Paragraph('%(address)s' % results, styleSheet['Address']))
	elements.append(Paragraph('%(city)s, %(state)s  %(zipcode)s' % results, styleSheet['Address']))
	elements.append(Spacer(1,24))
	elements.append(Paragraph('<para align=RIGHT>%s</para>' % EMR_utilities.dateToday(t='display'), styleSheet['Body']))
	
	elements.append(Spacer(1,36))

	if results['sex'] == 'male':
	    def_salutation = 'Dear Mr. %s:' % results['lastname']
	else: 
	    def_salutation = 'Dear Ms. %s:' % results['lastname']
	salutation = wx.GetTextFromUser("Dear ?:", default_value=def_salutation)
	elements.append(Paragraph(salutation, styleSheet['Body']))
	elements.append(Spacer(1,12))
	
	if text == "":
	    body = wx.TextEntryDialog(parent, "Main Paragraph", style=wx.TE_MULTILINE|wx.OK|wx.CANCEL)
	    body.ShowModal()
	    elements.append(Paragraph(body.GetValue(), styleSheet['Body']))
	else:
	    elements.append(Paragraph(text, styleSheet['Body']))
	elements.append(Spacer(1,12))
	elements.append(Paragraph("If you have any questions, don't hesitate to call me at (314) 667-5276.", styleSheet['Body']))
	elements.append(Spacer(1,12))

	elements.append(Paragraph('Sincerely,', styleSheet['Body']))
	chooseSig(elements)

	elements.append(Paragraph(settings.NAME, styleSheet['Body']))
	
	# write the document to disk
	doc.build(elements)
	choosePrinter(filename)
	

class myConsultLtr():
    def __init__(self, parent, ptID, reason, background, consultant, dueDate):
	lt = "%s/EMR_outputs/%s/Consults/%s.pdf" % (settings.LINUXPATH, ptID, EMR_utilities.dateToday('file format'))
	at = "%s/EMR_outputs/%s/Consults/%s.pdf" % (settings.APPLEPATH, ptID, EMR_utilities.dateToday('file format'))
	wt = "%s\EMR_outputs\%s\Consults\%s.pdf" % (settings.WINPATH, ptID, EMR_utilities.dateToday('file format'))
	filename = EMR_utilities.platformText(lt, at, wt)
	doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=60)
	# container for the 'Flowable' objects
	elements = []
	styleSheet = getSampleStyleSheet()
	styleSheet.add(ParagraphStyle(name='Address', fontSize=13, leading=15))
	styleSheet.add(ParagraphStyle(name='Body', fontSize=12, leading=14))

	dem_data = EMR_utilities.getDictData('SELECT * FROM demographics WHERE patient_ID = %s;' % ptID)
	consultDoc = EMR_utilities.name_fixer(consultant)
	if consultDoc.firstname == '':
            consult_data = EMR_utilities.getDictData('SELECT * FROM consultants WHERE lastname = "%s";' \
		% (consultDoc.lastname))
        else:
            consult_data = EMR_utilities.getDictData('SELECT * FROM consultants WHERE lastname = "%s" \
		AND firstname = "%s";' % (consultDoc.lastname, consultDoc.firstname))
	
	dem_data['phonenumber'] = EMR_formats.phone_format(dem_data['phonenumber'])
	patient = 'RE: %(firstname)s %(lastname)s, DOB: %(dob)s, Phone: %(phonenumber)s' % dem_data
	salutation = 'Dear Dr. %(lastname)s:' % consult_data
	body = 'I am sending %s, a %s %s, to see you regarding %s. %s' % \
		(dem_data['firstname'], EMR_utilities.getAge(ptID), dem_data['sex'], reason, background)
	problems = EMR_formats.getProblems(ptID)
	meds = EMR_formats.getMeds(ptID, display='column')
	qry = "INSERT INTO todo SET patient_ID = %s, date = '%s', description = '%s- %s', priority = 3, \
		category = 'Consult', due_date = '%s', complete = 0;" % (ptID, EMR_utilities.dateToday(), \
		consult_data['lastname'], reason, dueDate)
	EMR_utilities.updateData(qry)
	
	styleSheet = getSampleStyleSheet()
	styleSheet.add(ParagraphStyle(name='Address', fontSize=13, leading=15))
	styleSheet.add(ParagraphStyle(name='Body', fontSize=12, leading=14))

	elements.append(Paragraph('Barron Family Medicine', styleSheet['Address']))
	elements.append(Paragraph('8515 Delmar Blvd #217', styleSheet['Address']))
	elements.append(Paragraph('University City, MO 63124', styleSheet['Address']))
	elements.append(Paragraph('(314)667-5276  fax:(314)677-3838', styleSheet['Address']))
	elements.append(Spacer(1,24))
	elements.append(Paragraph('<para align=RIGHT>%s</para>' % EMR_utilities.dateToday(t='display'), styleSheet['Body']))
	elements.append(Spacer(1,24))

	elements.append(Paragraph('Dr. %(lastname)s' % consult_data, styleSheet['Body']))
	elements.append(Paragraph('%(address)s' % consult_data, styleSheet['Body']))
	elements.append(Paragraph('%(city)s, %(state)s  %(zipcode)s' % consult_data, styleSheet['Body']))
	elements.append(Spacer(1, 12))
	elements.append(Paragraph(patient, styleSheet['Body']))
	elements.append(Spacer(1, 12))
	elements.append(Paragraph(salutation, styleSheet['Body']))
	elements.append(Spacer(1, 12))
	elements.append(Paragraph(body, styleSheet['Body']))
	elements.append(Spacer(1,12))
	elements.append(Paragraph("I have attached current medications and problems.  \
		If you have any questions, don't hesitate to call me at (314) 667-5276.", styleSheet['Body']))
	elements.append(Spacer(1,12))
	elements.append(Paragraph('Sincerely,', styleSheet['Body']))
	#If you want the signature automatically then can un-comment these lines.  For now I will sign all.
	#logo = "/home/%s/Dropbox/Office/%sSignature.png" % (settings.HOME_FOLDER, settings.HOME_FOLDER)
	#im = Image(logo, 2*inch, 0.75*inch)
	#im.hAlign = "LEFT"
	#elements.append(im)
	chooseSig(elements)

	elements.append(Paragraph(settings.NAME, styleSheet['Body']))
	elements.append(Spacer(1, 12))

	tableList = [[problems, meds,]]
	table = Table(tableList, colWidths=(3*inch, 3*inch), style=[('VALIGN', (0,0), (-1,-1), 'TOP'),
				     							('LEFTPADDING', (0,0), (-1,-1), 0),
			     	     							('RIGHTPADDING', (0,0), (-1,-1), 20)])
	table.hAlign = "LEFT"
	elements.append(table)
	
	# write the document to disk
	doc.build(elements)
	choosePrinter(filename)


class myWorkRelease():
    def __init__(self, parent, ptID):
	self.ptID = ptID
	lt = "%s/EMR_outputs/%s/Other/release-%s.pdf" % (settings.LINUXPATH, self.ptID, EMR_utilities.dateToday('file format'))
	at = "%s/EMR_outputs/%s/Other/release-%s.pdf" % (settings.APPLEPATH, self.ptID, EMR_utilities.dateToday('file format'))
	wt = "%s\EMR_outputs\%s\Other\release-%s.pdf" % (settings.WINPATH, self.ptID, EMR_utilities.dateToday('file format'))
	filename = EMR_utilities.platformText(lt, at, wt)
	doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=60)
	# container for the 'Flowable' objects
	elements = []
 
	styleSheet = getSampleStyleSheet()
	styleSheet.add(ParagraphStyle(name='Address', fontSize=13, leading=15))
	styleSheet.add(ParagraphStyle(name='Body', fontSize=12, leading=14))
	styleSheet.add(ParagraphStyle(name='Indent', fontSize=12, leading=14, leftIndent=25))

	elements.append(Paragraph('Barron Family Medicine', styleSheet['Address']))
	elements.append(Paragraph('8515 Delmar Blvd #217', styleSheet['Address']))
	elements.append(Paragraph('University City, MO 63124', styleSheet['Address']))

	elements.append(Spacer(1, 36))
	elements.append(Paragraph('<para align=RIGHT>%s</para>' % EMR_utilities.dateToday(t='display'), styleSheet['Body']))
	
	qry = 'SELECT * FROM demographics WHERE patient_ID = %s;' % self.ptID
	results = EMR_utilities.getDictData(qry)
	name = '%(firstname)s %(lastname)s' % (results)
	elements.append(Spacer(1,56))
	elements.append(Paragraph('Physician Statement regarding %(firstname)s %(lastname)s, \
				DOB: %(dob)s' % (results), styleSheet['Address']))
	
	elements.append(Spacer(1,36))
	date_dlg = wx.TextEntryDialog(parent,
		"", 
		"Return to Work Date",
		EMR_utilities.dateToday(t='display'),
		style=wx.OK|wx.CANCEL)
	date_dlg.ShowModal()
	place_dlg = wx.TextEntryDialog(parent,
		"Return to ...?", 
		"school? work? daycare?",
		"work",
		style=wx.OK|wx.CANCEL)
	place_dlg.ShowModal()
	elements.append(Paragraph('%s has been under my care and is released to return to %s on %s \
		with the following restrictions:' % (name, place_dlg.GetValue(), date_dlg.GetValue()), styleSheet['Body']))

	elements.append(Spacer(1,24))
	
	body = wx.TextEntryDialog(parent,
	       "",
	       "Work Restrictions",
	       "No prolonged standing, bending, twisting, squatting or lifting more than 15 pounds for one week.",
	       style=wx.TE_MULTILINE|wx.OK|wx.CANCEL)
	body.ShowModal()
	elements.append(Paragraph(body.GetValue(), styleSheet['Indent']))
	elements.append(Spacer(1,24))
	elements.append(Paragraph("If you have any questions, don't hesitate to call me at (314) 667-5276.", styleSheet['Body']))
	elements.append(Spacer(1,12))

	elements.append(Paragraph('Sincerely,', styleSheet['Body']))
	'''If you want the signature automatically then can un-comment these lines.  For now I will sign all.
	logo = "/home/mb/Dropbox/Office/Signature.png"
	im = Image(logo, 2*inch, 0.75*inch)
	im.hAlign = "LEFT"
	elements.append(im)'''
	chooseSig(elements)

	elements.append(Paragraph(settings.NAME, styleSheet['Body']))
	
	# write the document to disk
	doc.build(elements)
	choosePrinter(filename)

class sendPanelLtr():
    def __init__(self, parent, visitSince='2010-10-01'):

	'''Send letters to all my active patients.'''

	#Here is the letter
	myLtr = '''As you may recall from my letter dated September 8, 2011, I have been deployed by the US Army to Kuwait until early January 2012. I arranged for the Family Care Health Center to see my patients while I am gone. Unfortunately, their capacity to see my patients is more limited than I anticipated.

In order to address this issue, Dr Ladonna Finch has generously agreed to help. If you need an appointment, rather than calling the Family Care Health Center as my previous letter suggested, please call her office at 314-645-7265.  Her office is located at 1031 Bellevue Avenue, Suite 349 in Richmond Heights, across the street from St. Mary's Hospital.

I encourage you to call my office for medication refills and non-urgent questions/issues that can be addressed via email.  

Thank you for your understanding.'''
    
	#Figure out who the active patients are and create a list of their patient_ID numbers
	qry = 'SELECT patient_ID FROM notes WHERE date >= "%s";' % visitSince
	results = EMR_utilities.getAllData(qry)

	#Remove duplicates from the list
	d = {}
	for x in results:
	    d[x] = 1
	myList = list(d.keys())
	print len(myList)
	
	#Step through the list creating letter using template in Printer
	for items in myList:
	    myPtLtr(self, items[0], text=myLtr)


class myTestOrder():
    def __init__(self, parent, ptID):
	lt = "%s/EMR_outputs/%s/Orders/%s.pdf" % (settings.LINUXPATH, ptID, EMR_utilities.dateToday('file format'))
	at = "%s/EMR_outputs/%s/Orders/%s.pdf" % (settings.APPLEPATH, ptID, EMR_utilities.dateToday('file format'))
	wt = "%s\EMR_outputs\%s\Orders\%s.pdf" % (settings.WINPATH, ptID, EMR_utilities.dateToday('file format'))
	filename = EMR_utilities.platformText(lt, at, wt)
	doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=60)
	# container for the 'Flowable' objects
	elements = []
	styleSheet = getSampleStyleSheet()
	styleSheet.add(ParagraphStyle(name='Address', fontSize=13, leading=15))
	styleSheet.add(ParagraphStyle(name='Body', fontSize=12, leading=14))

	dem_data = EMR_utilities.getDictData('SELECT * FROM demographics WHERE patient_ID = %s;' % ptID)
	dem_data['phonenumber'] = EMR_formats.phone_format(dem_data['phonenumber'])
	test_dlg = wx.TextEntryDialog(None, "What studies would you like to order?", "Studies",style=wx.TE_MULTILINE|wx.OK|wx.CANCEL)
	if test_dlg.ShowModal() == wx.ID_OK:
	    dem_data['tests'] = test_dlg.GetValue()
	    dem_data['date'] = EMR_utilities.dateToday()
	else: pass
	dx_dlg = wx.TextEntryDialog(None, "What is the diagnosis?", "Diagnosis", style=wx.TE_MULTILINE|wx.OK|wx.CANCEL)
	if dx_dlg.ShowModal() == wx.ID_OK:
	    dem_data['dx'] = dx_dlg.GetValue()
	else: pass
	results_dlg = wx.TextEntryDialog(None, "Due Date?", style=wx.OK|wx.CANCEL)
	if results_dlg.ShowModal() == wx.ID_OK:
	    dem_data['results_date'] = results_dlg.GetValue()
	else: pass
	qry = "INSERT INTO todo SET patient_ID = %s, date = '%s', description = '%s', priority = 3, \
		category = 'Test', due_date = '%s', complete = 0;" % (ptID, EMR_utilities.dateToday(), \
		dem_data['tests'], dem_data['results_date'])
	EMR_utilities.updateData(qry)
	
	styleSheet = getSampleStyleSheet()
	styleSheet.add(ParagraphStyle(name='Address', fontSize=13, leading=15))
	styleSheet.add(ParagraphStyle(name='Body', fontSize=12, leading=14))

	elements.append(Paragraph('<para align=CENTER>Barron Family Medicine</para>', styleSheet['Address']))
	elements.append(Paragraph('<para align=CENTER>8515 Delmar Blvd #217</para>', styleSheet['Address']))
	elements.append(Paragraph('<para align=CENTER>University City, MO 63124</para>', styleSheet['Address']))
	elements.append(Paragraph('<para align=CENTER>(314)667-5276   fax:(314)677-3838</para>', styleSheet['Address']))
	elements.append(Paragraph('<para align=CENTER>Quest #33007741, Labcorp #24864540</para>', styleSheet['Address']))
	elements.append(Spacer(1,48))
	elements.append(Paragraph('<para align=RIGHT>%s</para>' % EMR_utilities.dateToday(t='display'), styleSheet['Body']))
	elements.append(Spacer(1,48))

	elements.append(Paragraph('%(firstname)s %(lastname)s' % dem_data, styleSheet['Body']))
	elements.append(Paragraph('%(address)s' % dem_data, styleSheet['Body']))
	elements.append(Paragraph('%(city)s, %(state)s  %(zipcode)s' % dem_data, styleSheet['Body']))
	elements.append(Paragraph('%(phonenumber)s' % dem_data, styleSheet['Body']))
	elements.append(Paragraph('DOB: %(dob)s' % dem_data, styleSheet['Body']))
	elements.append(Spacer(1, 36))
	elements.append(Paragraph('<U>Tests:</U>', styleSheet['Address']))
	elements.append(Spacer(1, 12))
	elements.append(Paragraph(dem_data['tests'], styleSheet['Body']))
	elements.append(Spacer(1, 24))
	elements.append(Paragraph('<U>Diagnosis:</U>', styleSheet['Address']))
	elements.append(Spacer(1,12))
	elements.append(Paragraph(dem_data['dx'], styleSheet['Body']))
	elements.append(Spacer(1,96))
	#elements.append(Spacer(1, 48))
	#If you want the signature automatically then can un-comment these lines.  For now I will sign all.
	#logo = "/home/mb/Dropbox/Office/Signature.png"
	#im = Image(logo, 2*inch, 0.75*inch)
	#im.hAlign = "LEFT"
	#elements.append(im)
	chooseSig(elements)

	elements.append(Paragraph(settings.NAME, styleSheet['Body']))
	
	# write the document to disk
	doc.build(elements)
	choosePrinter(filename)

def choosePrinter(filename):
    conn = cups.Connection()
    p = conn.getPrinters()
    pList = []
    for printer in p:
	pList.append(printer)
    printerDialog = wx.SingleChoiceDialog(None, "Choose a printer.", "Printers", pList, style = wx.OK | wx.CANCEL)
    if printerDialog.ShowModal() == wx.ID_OK:
	os.system("lp -d %s %s" % (printerDialog.GetStringSelection(), filename))	#extremely slick: prints directly to printer
    #conn.close() 	Not sure I need to close.  This raises error and I couldn't find anything equivalent.

def chooseSig(elements):
    msg = wx.MessageDialog(None, "Include signature?", "Message", wx.YES_NO | wx.ICON_QUESTION)
    if msg.ShowModal() == wx.ID_YES:
	logo = "/home/mb/Dropbox/Office/%sSignature.png" % settings.HOME_FOLDER
	im = Image(logo, 2*inch, 0.75*inch)
	im.hAlign = "LEFT"
	elements.append(im)
    else:
	elements.append(Spacer(1, 36))



