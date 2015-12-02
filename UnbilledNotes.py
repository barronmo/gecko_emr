import MySQLdb, sets, datetime, getpass

print """

Welcome to the program that lists the name and date of every note that does 
not have a charge with the same name and date!  This should be checked at 
least once a month.  This script will save you a lot of time.

Michael Barron MD 2013-11-22

"""

try:
    conn = MySQLdb.connect(host = "192.168.1.13", #connects to the database
	user = raw_input("Please enter your user name: "),
        passwd = getpass.getpass(),
        db = "gecko")

except MySQLdb.Error, e:
    message = "Error %d: %s" % (e.args[0], e.args[1])
    print message
     
if conn:
    start = raw_input("What is the day before your start date? ")
    end = raw_input("What is the day after your end date? ")
    cursor = conn.cursor()
    cursor.execute("SELECT CONCAT(firstname, ' ', lastname) As Name, date \
				FROM demographics INNER JOIN notes USING (patient_ID) \
				WHERE date > '%s 23:59:00' AND date < '%s' \
				AND soap NOT LIKE '%%Phone%%';" % (start, end))
    n = cursor.fetchall()
    notes = []
    for i in n:
	notes.append((i[0], i[1].strftime("%Y-%m-%d")))

    cursor.execute("SELECT CONCAT(firstname, ' ', lastname) As Name, date \
				FROM demographics INNER JOIN billing USING (patient_ID) \
				WHERE date > '%s' AND date < '%s';" % (start, end))
    c = cursor.fetchall()
    charges = []
    for i in c:
	charges.append((i[0], i[1].strftime("%Y-%m-%d")))

    nSet = sets.Set(notes)
    cSet = sets.Set(charges)
    unbilled = nSet - cSet
    for x in unbilled:
	print x[0] + '  ' + x[1]
    cursor.close()

else: pass


