import base64
import urllib2
import json
import EMR_utilities


class Importer():
    def __init__(self, PtID):
	#Setup authentication - this can be done once
	username = 'barronmo@gmail.com'
	password = 'Barron85upd'

	auth_string = base64.encodestring('%s:%s' % (username, password))[:-1]
	baseurl = 'https://myupdox.com/udb/jsonapi/%s'
	qry = "SELECT * FROM demographics WHERE patient_ID = %s" % PtID
	results = EMR_utilities.getDictData(qry)
	#The following is done for each request

	list = [
	    {
    		"contactType" : "patient",
		"id" : PtID,
		"salutation" : "",
		"firstName" : results['firstname'],
		"middleName" : results['mid_init'],
		"lastName" : results['lastname'],
		"suffix" : "",
		"emailAddress" : results['email'],
		"sex" : results['sex'][:1].capitalize(),
		"homePhone" : results['phonenumber'],
		"workPhone" : "",
		"address1" : "",
		"city" : "",
		"state" : "",
 		"zip5" : "",
		"dob" : str(results['dob']),
		"addedDate" : str(EMR_utilities.dateToday()),
		"mobileNumber" : "",
		"faxNumber" : "",
		"defaultProvider" : "Barron",
		"active" : True
	    },]

	req = urllib2.Request(url = baseurl % 'Core.SyncPatients',
			      data = '{"list":%s}' % json.dumps(list))
	req.add_header("Authorization", "Basic %s" % auth_string)

	res = urllib2.urlopen(req)

	print res.read()
