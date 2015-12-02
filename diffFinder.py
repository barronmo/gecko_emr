import os

print '''

This is a script for find out any differences between the main files in GECKO on the server and a local computer.

Michael Barron MD'''

pyNames = ['Meds', 'Billing', 'CarePlan', 'PMH', 'UpdoxImporter', 'Vitals', 'Prevention', 'CreateCMS', 'EMR_notebook', 'Problems', \
	'Education', 'Printer', 'Notes', 'demographics', 'Selectable', 'EMR_formats', 'Queries', 'ToDo', 'EMR_utilities']

compare1 = raw_input('What is the directory you want to start with?')
compare2 = raw_input('What directory do you want to compare it to?')

for n in pyNames:
    print '%s.py:\n' % n
    os.system('diff %s/%s.py %s/%s.py' % (compare1, n, compare2, n))
    print '\n'

print 'All done.'
