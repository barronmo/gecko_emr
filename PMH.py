import wx
import EMR_utilities


class PMH(wx.Panel):
    def __init__(self, parent, id, PtID):
	wx.Panel.__init__(self, parent, id)
	
	self.PtID = PtID
	self.tobStatus = wx.RadioBox(self, -1, 'Tobacco User Status', choices = ['Unknown', 'Current', 'Former', 'Never'])
	self.typeTob = wx.RadioBox(self, -1, 'Type of Tobacco', choices = ['Unknown', 'Cigarettes', 'Pipe', 'Cigars', 'Smokeless'])
	packyrLabel = wx.StaticText(self, -1, 'Pack*Years')
	self.packyr = wx.TextCtrl(self, -1, size=(30, 20))
	quitLabel = wx.StaticText(self, -1, 'Year of last quit attempt')
	self.quit = wx.TextCtrl(self, -1, size=(50, 20))
	shName = wx.StaticText(self, -1, 'Social History')
	self.sh = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
	fhName = wx.StaticText(self, -1, 'Family History')
	self.fh = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
	pmhName = wx.StaticText(self, -1, 'Past Medical History')
	self.pmh = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)

	packyrSizer = wx.BoxSizer(wx.HORIZONTAL)
	packyrSizer.AddMany([(packyrLabel, 0), (self.packyr, 0), (10, -1), (quitLabel, 0), (self.quit, 0)])
	leftsizer = wx.BoxSizer(wx.VERTICAL)
	leftsizer.AddMany([(self.tobStatus, 0), (-1, 10), (packyrSizer, 0), (-1, 10), (self.typeTob, 0), (-1, 10),  (shName, 0, wx.ALL, 5),(self.sh, 1, wx.EXPAND), 
		(-1, 20), (fhName, 0, wx.ALL, 5), (self.fh, 1, wx.EXPAND), (-1, 10)])
	rightsizer = wx.BoxSizer(wx.VERTICAL)
	rightsizer.AddMany([(pmhName, 0, wx.ALL, 5), (self.pmh, 1, wx.EXPAND), (-1, 10)])
	mainsizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.AddMany([(leftsizer, 1, wx.EXPAND), (15, -1), (rightsizer, 1, wx.EXPAND)])
	self.SetSizer(mainsizer)
 
	qry = 'SELECT sh, fh, pmh, tob_status, tob_type, pack_yrs, last_quit FROM past_history WHERE patient_ID = %s' % (self.PtID)
	#results = self.NullToEmpty(EMR_utilities.getData(qry))
	results = EMR_utilities.getData(qry)
	try: 
	    results[3]
	    try:
		self.sh.AppendText(results[0])
	    except: pass
	    try:
		self.fh.AppendText(results[1])
	    except: pass
	    try:
		self.pmh.AppendText(results[2])
	    except: pass
	    try:
		self.tobStatus.SetStringSelection(results[3])
	    except: EMR_utilities.MESSAGES = 'Please update smoking status.\n\n'
	    try:
		self.typeTob.SetStringSelection(results[4])
	    except: 
		if results[3] == 'Current':
	            wx.MessageBox('Please enter type of tobacco used.', 'Alert')
	    try:
		self.packyr.SetValue(str(results[5]))
	    except:
		if results[3] == 'Current':
		    wx.MessageBox('Please enter pack*year history.', 'Alert')
	    try:
		self.quit.SetValue(str(results[6]))
	    except:
		if results[3] == 'Current':
		    wx.MessageBox('Please enter last quit attempt.', 'Alert')
	except: pass
		
	self.tobStatus.Bind(wx.EVT_RADIOBOX, self.OnTobStatus, self.tobStatus)
	self.typeTob.Bind(wx.EVT_RADIOBOX, self.OnTobType, self.typeTob)
	self.packyr.Bind(wx.EVT_KILL_FOCUS, self.OnPackYr, self.packyr)
	self.quit.Bind(wx.EVT_KILL_FOCUS, self.OnQuitYear, self.quit)
	self.sh.Bind(wx.EVT_KILL_FOCUS, self.shOnLoseFocus, self.sh)
	self.fh.Bind(wx.EVT_KILL_FOCUS, self.fhOnLoseFocus, self.fh)
	self.pmh.Bind(wx.EVT_KILL_FOCUS, self.pmhOnLoseFocus, self.pmh)

    def shOnLoseFocus(self, event):
	EMR_utilities.changeData(self.sh.GetValue(), 'past_history', 'sh', self.PtID)

    def fhOnLoseFocus(self, event):
	EMR_utilities.changeData(self.fh.GetValue(), 'past_history', 'fh', self.PtID)

    def pmhOnLoseFocus(self, event):
	EMR_utilities.changeData(self.pmh.GetValue(), 'past_history', 'pmh', self.PtID)

    def NullToEmpty(self, value):
	"""This function exists because there are some patient_ID's in the db without entries in the past_history table.
	When this happens and I try to pull up their PMH panel the qry results=None.  None has no elements and there-
	fore causes an error.  To get around that we test for None both in results and in each element of results.  If 
	found then empty strings are substituted."""
	newvalue = []
	if value is None:
	    newvalue = ['','','']
	else:
	    for item in range(len(value)):
	        if value[item] is None:
	            newvalue.append("")
	        else:
	            newvalue.append(value[item])
	return newvalue

    def OnTobStatus(self, event):
	EMR_utilities.changeData(self.tobStatus.GetItemLabel(event.GetSelection()), 'past_history', 'tob_status', self.PtID)

    def OnTobType(self, event):
	EMR_utilities.changeData(self.typeTob.GetItemLabel(event.GetSelection()), 'past_history', 'tob_type', self.PtID)

    def OnPackYr(self, event):
	EMR_utilities.changeData(self.packyr.GetValue(), 'past_history', 'pack_yrs', self.PtID)

    def OnQuitYear(self, event):
	EMR_utilities.changeData(self.quit.GetValue(), 'past_history', 'last_quit', self.PtID)
