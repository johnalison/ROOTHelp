import os

#
# The following is to get the history 
#
global historyPath
global output


#
#  Get Options
#
def parseOpts():
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--base-dir', type = 'string', default = ".",          dest = 'baseDir',    help = 'input Dir' )
    p.add_option('', '--sub-dir',       default="",          dest='subDir',          help='Directory in root files to plot')
    p.add_option('--output',   type = 'string', default = "plots",          dest = 'output',     help = 'output dir' )
    p.add_option('--histName', type = 'string', default = None,          dest = 'histName',   help = 'candName' )
    p.add_option('', '--mcscale',       default=1.0, type=float,dest='mcscale',         help='Set MC Scale')    
    p.add_option('--model'   , type = 'string', default = "BasicModel",  dest = 'model',      help = 'candName' )
    p.add_option('--labName', type = 'string', default = None,          dest = 'labName',   help = 'label Name' )
    p.add_option('', '--debug',         default=False, action='store_true', dest='debug',help='activate debugging')
    p.add_option('--norm', action="store_true",help = 'label Name' )
    p.add_option('', '--tree',          default=False, action='store_true', dest='doTree',help='use tree')    
    (o,a) = p.parse_args()

    if not o.histName:
        o.histName = a[0]

    return (o,a)


def initHistory():

    global historyPath
    historyPath = os.path.expanduser("~/pyhistory")
    try:
        import readline
    except ImportError:
        print "Module readline not available."
    else:

        import rlcompleter        
        
        if os.path.exists(historyPath):
            #pass
            print "historyPath is ("+historyPath+")"
            readline.read_history_file(historyPath)
        
        class IrlCompleter(rlcompleter.Completer):
            """
            This class enables a "tab" insertion if there's no text for
            completion.
        
            The default "tab" is four spaces. You can initialize with '\t' as
            the tab if you wish to use a genuine tab.
        
            """
        
            def __init__(self, tab='    '):
                self.tab = tab
                rlcompleter.Completer.__init__(self)
        
        
            def complete(self, text, state):
                if text == '':
                    readline.insert_text(self.tab)
                    return None
                else:
                    return rlcompleter.Completer.complete(self,text,state)
        
        
        #you could change this line to bind another key instead tab.
        #readline.parse_and_bind("tab: complete")
        import sys
        thisSys = sys.platform
        onMac = (not thisSys.find('darwin') == -1)
        if onMac:
            readline.parse_and_bind ("bind ^I rl_complete") 
        
        #readline.parse_and_bind('tab: complete')
        readline.set_completer(IrlCompleter('\t').complete)
    

    return historyPath


# -----------------------------------------------------------------
def save_history():
    global historyPath
    #historyPath = os.path.expanduser("~/pyhistory")
    try:
        import readline
    except ImportError:
        print "Module readline not available."
    else:
        readline.write_history_file(historyPath)




# -----------------------------------------------------------------
def getPlotName(var,region,isLogY=False,isLogX=False):

    if isinstance(var,list) and isinstance(region,list):
        retName = region[0]+"_"+var[0]+"_vs_"+region[1]+"_"+var[1]
    elif isinstance(var,list) and not isinstance(region,list):
        retName = region+"_"+var[0]+"_vs_"+var[1]
    elif not isinstance(var,list) and isinstance(region,list):
        retName = region[0]+"_vs_"+region[1]+"_"+var
    else:
        retName = region+"_"+var
    

    if isLogY:
        retName += "_logY"
    if isLogX:
        retName += "_logX"

    return retName.replace("/","_")


#
# Calculates the max of the a bunch of hists in a given range
#
def calc_max_in_range(hists,x1,x2,incErr=True):
    m=-1e10
    for h in hists:
        xaxis=h.GetXaxis()
        for b in range(xaxis.FindBin(x1),max(xaxis.FindBin(x2),xaxis.FindBin(x1)+1)):
            if incErr:
                m=max(m,h.GetBinContent(b)+h.GetBinError(b))
            else:
                m=max(m,h.GetBinContent(b))

    return m
