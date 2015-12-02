import string
import EMR_utilities
import re
import datetime
import decimal


def format_address(somedictionary):
	"""parameter is a dictionary with appropriate keys for an address"""
	somedictionary['phonenumber'] = phone_format(somedictionary['phonenumber'])
	address = """%(firstname)s %(lastname)s
%(address)s 
%(city)s, %(state)s %(zipcode)s
%(phonenumber)s""" % somedictionary
	return address

def phone_format(somenumber):
	a = str(somenumber)
	a = a.strip()
	if len(a) == 10:
		return '(%s) %s-%s' % (a[:3], a[3:6], a[6:])
	elif len(a) == 11 and a[0] == '1':
		return '(%s) %s-%s' % (a[1:4], a[4:7], a[7:])
	else:
		return a

def quick_pt_find(somedictionary):
	"""Function returns patient info to be presented after last name search.  The parameter
	is the results of a cursor.dictionary MySQL search for demographic info."""
	somedictionary['phonenumber'] = phone_format(somedictionary['phonenumber'])
	info = "%(firstname)s %(lastname)s   %(DOB)s   %(phonenumber)s" % somedictionary
	return info

def getProblems(ptID, display=''):
	qry = 'SELECT short_des FROM problems10 WHERE patient_ID = %s;' % (ptID)
	results = EMR_utilities.getAllData(qry)
	shortList = []
	try:
	    for items in results:
		#query = 'SELECT short_des FROM icd10 WHERE disease_name = "%s";' % items[0]
		#short_name = EMR_utilities.getData(query)
		shortList.append(items)
	except: pass
	if display == 'HTML':
	    string = "<b>Problems:</b><BR>"
	    separator = "<BR>"
	else:
	    string = "Problems:\n"
	    separator = "\n"
	if results == ():
	    string = string + "none"
	else:
	    n = 1
	    for p in shortList:
		try:
		    string = string + "%s) %s%s" % (n, p[0], separator)
		    n = n + 1
		except: pass
	return string


def getMeds(ptID, display='wrap'):
	qry = 'SELECT med_name, dose, number_tablets, frequency FROM meds WHERE patient_ID = %s AND archive = 0;' % \
	      (ptID)
	results = EMR_utilities.getAllData(qry)
	if display == 'wrap':
	    string = "Meds: "
	    separator = ','
	elif display == 'column':
	    string = "Current Medications:\n\t"
	    separator = '\n\t'
	else: 
	    string = "<b>Meds:</b><BR> "
	    separator = '<BR>'
	if results == ():
	    string = string + "none"
	else:
	    for items in results:
		string = string + '%s %s take %s %s%s' % (items[0], items[1], items[2], items[3], separator)
	return string


def getAllergies(ptID):
	qry = 'SELECT allergy FROM allergies WHERE patient_ID = %s;' % (ptID)
	results = EMR_utilities.getAllData(qry)
	string = "Allergies: "
	if results == ():
	    string = string + "not recorded in chart"
	else:
	    for items in results:
		string = string + '%s, ' % (items)
	return string

def getVitals(ptID, baby=0):
	qry = "SELECT temp, sBP, dBP, pulse, resp, sats, wt, ht FROM vitals WHERE patient_ID = %s AND vitals_date = '%s;'" \
	      % (ptID, str(EMR_utilities.dateToday()))
	results = EMR_utilities.getData(qry)
	string = "Vitals: "
	try:
	    bmi = format((decimal.Decimal(results[6])/(decimal.Decimal(results[7])*decimal.Decimal(results[7])))*703, '.1f')
	except:
	    bmi = 'not calculated'
	if baby == 0:
	    if results == None:
		string = string + "none taken today"
	    else:
		string = string + 'T%s %s/%s P%s R%s O2Sats: %s Wt:%s BMI: %s' % (results[0], results[1], results[2], results[3], \
		     results[4], results[5], results[6], bmi)
	    return string
	else: 
	    if results == None:
		string = string + "none taken today"
	    else:
		string = string + 'Wt: %s, Length: %s' % (results[6], results[7])
	    return string

def getHistory(ptID):
	qry = "SELECT * FROM past_history WHERE patient_ID = %s" % ptID
	results = EMR_utilities.getData(qry)
	return results

def note(ptID):
	history = getHistory(ptID)
	SH = history[2]
	FH = history[3]
	generic_note = """cc:

ONSET: 
LOCATION: 
DURATION:
CHARACTER:
AGGRAVATING FACTORS:
RELIEVING FACTORS:
BETTER/WORSE:
SEVERITY:
ASSOCIATED SYMPTOMS:

Other doctor visits (specialists or hospital visits) since your last appointment?

%s

%s

%s

SH: %s
FH: %s
ROS: except as noted above, all systems are negative

%s


On scale of 0-10 how confident are you that you can control and
manage most of your health problems: 

A/P:


Follow up in: """ % (getProblems(ptID), getMeds(ptID), getAllergies(ptID), SH, FH, getVitals(ptID))
	return generic_note

def prenatal(ptID):
	prenatal_note = """Prenatal Visit

%s at %s who comes in with no complaints.  Pos FM.  No bleeding, LOF or regular contractions.

%s

%s

%s

%s
Gen: gravid female in NAD
Uterus: 
FHT: 
LE: no edema

A/P: %s at %s doing well.""" % (geesandpees(ptID), OBweeks(ptID), getProblems(ptID), getMeds(ptID), \
				      getAllergies(ptID), getVitals(ptID), geesandpees(ptID), OBweeks(ptID))
	return prenatal_note

def geesandpees(ptID):
	qry = 'SELECT short_des FROM problems10 WHERE patient_ID = %s;' % (ptID)
	results = EMR_utilities.getAllData(qry)
	for items in results:
	    r = re.search('G\dP\d', str(items))
	    if r:
		return r.group() 
	    else: pass

def OBweeks(ptID):
	qry = 'SELECT short_des FROM problems10 WHERE patient_ID = %s;' % (ptID)
	results = EMR_utilities.getAllData(qry)
	for items in results:
	    r = re.search('\d\d\d\d-\d\d-\d\d', str(items))
	    if r:
		edc = datetime.date(*map(int, r.group().split('-')))
		pregnancy = datetime.timedelta(weeks=-40)
		conception = edc + pregnancy
		howfar = datetime.date.today() - conception
		weeks, days = divmod(howfar.days, 7)
		return '%s %s/7 weeks' % (weeks, days) 
	    else: pass
	 
def phonecon(ptID):
	note = """Phone Conversation:

Pt called regarding 

Advice/Action:"""
	return note

def procedure(ptID):
	note = """Procedure:

Indication:
Verbal consent obtained after discussing the following.
  Risks:
  Benefits:
Performed by Barron
Description:
Complications: none
Estimated blood loss: minimal
Post Care:"""
	return note


def educNote(ptID):
	note = """Patient Care Plan

%s

TODAY YOU WERE SEEN FOR THE FOLLOWING PROBLEMS:

""" % (getMeds(ptID, 'column'))
	return note

