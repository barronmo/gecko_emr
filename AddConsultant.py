import MySQLdb, getpass

print """

Welcome to the program that makes it easy to add consultants to the database.  This script will save you a lot of time.

Michael Barron MD 2014-04-04

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
    fn = raw_input("Consultant firstname: ")
    ln = raw_input("Consultant lastname: ")
    addr = raw_input("Consultant address: ")
    city = raw_input("Consultant city: ")
    state = raw_input("Consultant state: ")
    zc = raw_input("Consultant zipcode: ")
    phone = raw_input("Consultant phone number: ")
    fax = raw_input("Consultant fax number: ")
    spec = raw_input("Specialty: ")

    cursor = conn.cursor()
    qry = "INSERT INTO consultants SET firstname = %s, lastname = %s, address = %s, city = %s, state = %s, zipcode = %s, phone = %s, fax = %s, specialty = %s;"
    values = (fn, ln, addr, city, state, zc, phone, fax, spec)
    cursor.execute(qry, values) 
    cursor.close()
    print """

All done

"""
else: pass
    
