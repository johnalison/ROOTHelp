#! /usr/bin/env python

"""
Interactive script to plot histograms in the root file.

Example to load a root file:

  python -i iPlot.py \
  --base-dir=/disk/userdata00/atlas_data2/jkunkle/CutFlowResults/WWZZHWW_2011_11_04_MetResVexWtJetFix/ \
  --sub-dir=Studies \
  --histName=cutflow.root

Example in the python shell,

"""

### Parse command-line options
##from optparse import OptionParser
##p = OptionParser()
##p.add_option('', '--base-dir',      default=".",           dest='baseDir',         help='Path to base directory containing all ntuples')
##p.add_option('', '--sub-dir',       default="",          dest='subDir',          help='Directory in root files to plot')
##p.add_option('', '--output-dir',    default="plots",     dest='output',          help='Directory to put output .eps')
##p.add_option('', '--model',         default="BasicModel",dest='model',           help='Moduling to use a la MakeModeling.py')
##p.add_option('', '--mcscale',       default=1.0, type=float,dest='mcscale',         help='Set MC Scale')    
##p.add_option('', '--histName',      default=None,    dest='histName',        help='Histnames')
##p.add_option('', '--debug',         default=False, action='store_true', dest='debug',help='activate debugging')
###p.add_option('', '--tree',          default=False, action='store_true', dest='doTree',help='use tree')
##p.add_option('--labName', type = 'string', default = None,          dest = 'labName',   help = 'label Name' )
##(options, args) = p.parse_args()
##
##if not options.histName:
##    options.histName = args[0]

import sys,os
from ROOT import TDirectory,TH1F,TH2F,TH2,TH1, ROOT
import ROOT

import sys, os
#iStackDir = os.path.dirname(os.path.realpath(__file__))
#sys.path.insert(0,iStackDir+'/scripts/')

#from iPlotLoadPath import loadPath 
#loadPath()
from iUtils import parseOpts
(options, args) = parseOpts()


#
#  Load Atlas Style
#
#iStackDir = os.path.dirname(os.path.realpath(__file__))
#atlasstylesearch=[
#    iStackDir+'/AtlasStyle.C',
#    ]

import ROOTHelp.FancyROOTStyle
                   

#for p in atlasstylesearch:
#    if os.path.exists(p):
#        ROOT.gROOT.LoadMacro(p)
#        break
#
#try:
#    ROOT.SetAtlasStyle()
#    ROOT.gStyle.SetPalette(1)
#except:
#    print 'Could not load atlastyle, try?'
#    pass



#
# Global variables
#
pm                  = None
currentPlot         = None
currentRegBase      = None
currentCut          = None
currentVar          = None
#output              = None
currentLegendLimits = None

from iUtils import initHistory, save_history, getPlotName
from ROOTHelp.Utils         import do_variable_rebinning

# =================================================================
def main():

    #from iUtils import initHistory, save_history, getPlotName
    print "calling initHistory()"
    initHistory()

    import atexit
    atexit.register(save_history)


    #
    # Initialize Process Manager
    #
    InitPM(options.model,
           options.baseDir,
           options.subDir,
           options.histName,
           options.output,
           mcscale=options.mcscale
           )

    SetOutput(options.output)

    return


# -----------------------------------------------------------------
def InitPM(model,baseDir,subDir,histName,output,mcscale=1.0,interactive=True, debug=False):

    global pm,pmUp,pmDn
    Module = __import__(model)

    #
    #  Make plots from one file
    #
    if len(args) == 1:
        pm = Module.MakeModeling(baseDir,
                                 dirName = subDir,
                                 mcscale=mcscale,
                                 histName = histName,
                                 interactive=interactive)#,
                                 # debug=debug)

    #
    #  Compare files
    #
    elif len(args) == 2:
        if model == "BasicModel":
            Module = __import__("BasicComp")
        pm = Module.MakeModeling(baseDir,
                                 dirName = subDir,
                                 mcscale=mcscale,
                                 histName1 = histName,
                                 histName2 = args[1],
                                 interactive=interactive)
        

    #
    #  Load more complicated model
    #
    else:
        print "Loading Custom module"
        pm = Module.MakeModeling(baseDir,
                                 dirName = subDir,
                                 mcscale=mcscale,
                                 histName = options.histName,
                                 interactive=interactive)



    pm.InitializeProcesses()
    pm.updateDirs("")
    pm.output = output

    return pm


# ----------------------------------------------------------------------------
def clearData():
    global currentPlot
    global currentRegBase
    global currentCut
    global currentVar

    if currentPlot:
        if 'canvas' in currentPlot and currentPlot['canvas']:
            currentPlot['canvas'].Close()


    currentPlot    = None
    currentRegBase = None
    currentCut     = None
    currentVar     = None

# -----------------------------------------------------------------
def SetYLabels(ylabel, theHists):
    if ylabel is not None :
        for hist in theHists.values() :
            if hist is not None :
                hist.GetYaxis().SetTitle(ylabel)
    return


# -----------------------------------------------------------------
def SetXLabels(xlabel, theHists):
    if xlabel is not None :
        for hist in theHists.values() :
            if hist is not None :
                hist.GetXaxis().SetTitle(xlabel)
    return


# -----------------------------------------------------------------
def SetOutput(output):
    pm.output = output
    if not os.path.exists(output):
        os.mkdir(output)
    return 

def config2D():
    global oldMargin 
    ROOT.gStyle.SetPalette(1)
    oldMargin =  ROOT.gStyle.GetPadRightMargin()
    ROOT.gStyle.SetPadRightMargin(0.2)

def config1D():
    global oldMargin 
    ROOT.gStyle.SetPalette(1)
    #oldMargin =  ROOT.gStyle.GetPadRightMargin()
    ROOT.gStyle.SetPadRightMargin(oldMargin)



# ----------------------------------------------------------------------------
def plot(var, region = "",  **kw):
         
    global currentPlot
    global currentLegendLimits

    clearData()

    #
    #  Read in Options
    #
    ylabel     = kw.get('ylabel'    ,  None) 
    xlabel     = kw.get('xlabel'    ,  None) 
    isLogy     = kw.get('logy'      ,  False)
    isLogx     = kw.get('logx'      ,  False)
    plotPreFix = kw.get('plotPreFix',  "")
    binning    = kw.get('binning'   ,  None)
    debug          =  kw.get('debug'        ,  False)
        
    plotName  = getPlotName(var,region,isLogy,isLogx)
    plotName += plotPreFix

    theHists  = {}
    order    = []

    if isinstance(var,list) and isinstance(region,list):
        if debug: print "will plot different vars from differnt folders" 
        varName    = var[0]
        matchedRegion = [getRegName(region[0]),getRegName(region[1])]
        regionName = matchedRegion[0]

        if varName.find("*") != -1: return listVars(varName.replace("*",""),regionName)

        if debug: print "Hist 0 is "+matchedRegion[0]+"/"+var[0]
        
        pm.updateDirs(matchedRegion[0])
        order.append(matchedRegion[0])
        theHists[matchedRegion[0]] = pm.getHists(var[0], **kw)[pm.order[0]]
        if debug: print " got \t ",pm.getHists(var[0], **kw)
        
        if debug: print "Hist 1 is "+matchedRegion[1]+"/"+var[1]
        
        pm.updateDirs(matchedRegion[1])
        order.append(matchedRegion[1])
        theHists[matchedRegion[1]] = pm.getHists(var[1], **kw)[pm.order[1]]
        if debug: print " got \t ",pm.getHists(var[1], **kw)
        
    elif isinstance(var,list) and not isinstance(region,list):
        matchedRegion = getRegName(region)
        pm.updateDirs(matchedRegion)
        varName    = var[0]
        regionName = matchedRegion

        for i, vName in enumerate(var):
            if not i :
                order.append(pm.order[0])
                if vName.find("*") != -1: return listVars(vName.replace("*",""),regionName)
                theHists[pm.order[0]] = pm.getHists(vName, **kw)[pm.order[0]]
            else:
                order.append("var"+str(i))
                theHists["var"+str(i)] = pm.getHists(vName, **kw)[pm.order[0]]


    elif not isinstance(var,list) and isinstance(region,list):
        print "plot: will plot var from ",len(region)," differnt folders" 
        matchedRegion = [getRegName(region[0]),getRegName(region[1])]
        pm.updateDirs(matchedRegion[0])

        varName = var
        regionName = matchedRegion[0]

        if var.find("*") != -1: return listVars(var.replace("*",""),regionName)

        for i, rName in enumerate(matchedRegion):
            print "plot: update dirs",matchedRegion[i]
            pm.updateDirs(matchedRegion[i])

            if not i :
                order.append(pm.order[0])
                print "plot: order",order
                theHists[pm.order[0]] = pm.getHists(varName, **kw)[pm.order[0]]
                print "plot:",theHists[pm.order[0]].Integral()
            else:
                if len(pm.order)-1 < i:
                    order.append(rName)
                    #print "plot: order",order
                    #print pm.getHists(varName, **kw)
                    theHists[rName] = pm.getHists(varName, **kw)[pm.order[0]]
                    #print "plot:",theHists[pm.order[i]].Integral()

                else:
                    order.append(pm.order[i])
                    print "plot: order",order
                    print pm.getHists(varName, **kw)
                    theHists[pm.order[i]] = pm.getHists(varName, **kw)[pm.order[-1]]
                    print "plot:",theHists[pm.order[i]].Integral()
    else:
        regionName = getRegName(region)
        pm.updateDirs(regionName)
        varName = var

        if var.find("*") != -1: return listVars(var.replace("*",""),regionName)

        theHists = pm.getHists(var, **kw)
        #order    = theHists.values()
        order    = theHists.keys()
        order.sort()
        #print "order is ",
        
        matchedRegion = regionName

    #
    #  Set labels
    #
    SetYLabels(ylabel, theHists)
    SetXLabels(xlabel, theHists)

    if debug: print "theHists are",theHists
    
    theHistsRebinned = {}
    if binning:
        for h in theHists:
            print theHists
            if isinstance(binning, list):
                theHistsRebinned[h] = do_variable_rebinning(theHists[h], binning)
            else:
                theHistsRebinned[h] = theHists[h].Rebin(binning)
    else:
        theHistsRebinned = theHists

    #
    #   Make the plot
    #
    currentPlot = pm.makePlot(theHistsRebinned,
                              regiondesc=matchedRegion,
                              #legend_limits=currentLegendLimits,
                              plot_order = order,
                              **kw)



                                             
    pm.updateDirs("")
    if currentPlot:

        #currentPlot['canvas'].SaveAs(pm.output+"/"+plotName+".eps")
        currentPlot['canvas'].SaveAs(pm.output+"/"+plotName+".pdf")


    return currentPlot

# ----------------------------------------------------------------------------
def comp(var, region="",  **kw):

    global currentPlot
    global currentLegendLimits

    clearData()
    varName = var
    print region
    regionName = getRegName(region)

    #
    #  Read in Options
    #
    ylabel    = kw.get('ylabel'    ,  None) 
    xlabel    = kw.get('xlabel'    ,  None) 
    norm      = kw.get('norm'      ,  True) 
    

    theHists = {}
    order    = []

    if isinstance(var,list) and isinstance(region,list):
        print "will plot different vars from differnt folders" 
        varName    = var[0]
        regionName = region[0]

        if varName.find("*") != -1: return listVars(varName.replace("*",""),regionName)

        pm.updateDirs(region[0])
        order.append(region[0])
        theHists[region[0]] = pm.getHists(var[0], **kw)[pm.order[0]]
        

        pm.updateDirs(region[1])
        order.append(region[1]+pm.order[1])
        theHists[region[1]+pm.order[1]] = pm.getHists(var[1], **kw)[pm.order[1]]

    elif not isinstance(var,list) and isinstance(region,list):

        print "will plot var from ",len(region)," differnt folders" 
        varName = var
        regionName = region[0]

        if var.find("*") != -1: return listVars(var.replace("*",""),regionName)

        pm.updateDirs(region[0])
        order.append(region[0])
        theHists[region[0]] = pm.getHists(var, **kw)[pm.order[0]]

        pm.updateDirs(region[1])
        print pm.order
        order.append(region[1]+pm.order[1])
        theHists[region[1]+pm.order[1]] = pm.getHists(var, **kw)[pm.order[1]]

    elif isinstance(var,list) and not isinstance(region,list):

        print "will plot different vars from same folder"
        varName = var[0]
        regionName = region

        if varName.find("*") != -1: return listVars(varName.replace("*",""),regionName)

        pm.updateDirs(regionName)
        order.append(regionName)
        theHists[regionName] = pm.getHists(var[0], **kw)[pm.order[0]]

        order.append(regionName+pm.order[1])
        theHists[regionName+pm.order[1]] = pm.getHists(var[1], **kw)[pm.order[1]]

    else:

        if var.find("*") != -1: return listVars(var.replace("*",""),region)

        pm.updateDirs(region)
        order.append(region)

        theHists[region] = pm.getHists(var, **kw)[pm.order[0]]
        order.append(region+pm.order[1])
        theHists[region+pm.order[1]] = pm.getHists(var, **kw)[pm.order[1]]

    #
    #  Set labels
    #
    SetYLabels(ylabel, theHists)
    SetXLabels(xlabel, theHists)

    #
    #   Make the plot
    #
    currentPlot = pm.makePlot(theHists,
                              regiondesc    = region,
                              legend_limits = currentLegendLimits,
                              plot_order = order,
                              **kw)
    
    pm.updateDirs("")
    if currentPlot:
        #currentPlot['canvas'].SaveAs(pm.output+"/"+regionName+"_"+varName+".eps")
        currentPlot['canvas'].SaveAs(pm.output+"/"+regionName+"_"+varName+".pdf")

    return currentPlot


# ----------------------------------------------------------------------------
def stack(var, region,  **kw):
         
    global currentPlot
    global currentLegendLimits

    clearData()

    #
    #  Read in Options
    #
    ylabel    = kw.get('ylabel'    ,  None) 
    xlabel    = kw.get('xlabel'    ,  None) 
    #plotName  = kw.get('plotName'  ,  None)
    isLogy    = kw.get('logy'      ,  False)
    isLogx    = kw.get('logx'      ,  False)

    plotName  = getPlotName(var,region,isLogy,isLogx)

    theHists  = {}
    order    = []

    if isinstance(var,list) and isinstance(region,list):
        print "will plot different vars from differnt folders" 
        varName    = var[0]
        regionName = region[0]

        if varName.find("*") != -1: return listVars(varName.replace("*",""),regionName)

        pm.updateDirs(region[0])
        order.append(region[0])
        theHists[region[0]] = pm.getHists(var[0], **kw)["Data"]

        pm.updateDirs(region[1])
        order.append(region[1])
        theHists[region[1]] = pm.getHists(var[1], **kw)["Data"]
    
        
    elif isinstance(var,list) and not isinstance(region,list):
        pm.updateDirs(region)
        varName    = var[0]
        regionName = region

        for i, vName in enumerate(var):
            if not i :
                order.append("Data")
                if vName.find("*") != -1: return listVars(vName.replace("*",""),regionName)
                theHists["Data"] = pm.getHists(vName, **kw)["Data"]
            else:
                order.append("var"+str(i))
                theHists["var"+str(i)] = pm.getHists(vName, **kw)["Data"]


    elif not isinstance(var,list) and isinstance(region,list):
        pm.updateDirs(region[0])
        print "will plot vars from ",len(region)," differnt folders" 
        varName = var
        regionName = region[0]
        if var.find("*") != -1: return listVars(var.replace("*",""),regionName)

        for i, rName in enumerate(region):
            pm.updateDirs(region[i])

            if not i :
                order.append("Data")
                theHists["Data"] = pm.getHists(varName, **kw)["Data"]
            else:
                order.append(rName)
                theHists[rName] = pm.getHists(varName, **kw)["Data"]

    else:
        pm.updateDirs(region)
        varName = var
        regionName = region
        if var.find("*") != -1: return listVars(var.replace("*",""),regionName)
        
        theHists = pm.getHists(var, **kw)
        order    = theHists.values()

    #
    #  Set labels
    #
    SetYLabels(ylabel, theHists)
    SetXLabels(xlabel, theHists)


    #
    #   Make the plot
    #
    currentPlot = pm.makeStack(theHists,
                               regiondesc=region,
                               legend_limits=currentLegendLimits,
                               plot_order = order,
                               **kw)



                                             
    pm.updateDirs("")
    if currentPlot:

        #currentPlot['canvas'].SaveAs(pm.output+"/"+plotName+".eps")
        currentPlot['canvas'].SaveAs(pm.output+"/"+plotName+".pdf")

#        if not plotName:
#            currentPlot['canvas'].SaveAs(pm.output+"/"+regionName+"_"+varName+".eps")
#            currentPlot['canvas'].SaveAs(pm.output+"/"+regionName+"_"+varName+".pdf")
#        else:
#
#            # 
#            #  Need to do this twice to get the plots to come out with extra lines
#            #   (Crazy I know) 
#            # 
#            currentPlot['canvas'].SaveAs(pm.output+"/"+plotName+"_"+varName+".eps")
#            currentPlot['canvas'].SaveAs(pm.output+"/"+plotName+"_"+varName+".pdf")
#            currentPlot['canvas'].SaveAs(pm.output+"/"+plotName+"_"+varName+".eps")
#            currentPlot['canvas'].SaveAs(pm.output+"/"+plotName+"_"+varName+".pdf")
#
    return currentPlot


# ----------------------------------------------------------------------------    
def saveCan():
    #currentPlot['canvas'].SaveAs(pm.output+"/"+currentRegBase+"_"+currentCut+"_"+currentVar+".eps")
    currentPlot['canvas'].SaveAs(pm.output+"/"+currentRegBase+"_"+currentCut+"_"+currentVar+".pdf")
    print "Wrote "+pm.output+"/"+currentRegBase+"_"+currentCut+"_"+currentVar+".pdf"


# ----------------------------------------------------------------------------
def listDirs(key="",dir="",depth=0,max=10):
    if depth > max: return
    pm.updateDirs(dir)
    regions = pm.listDirs(key)
    for r in regions:
        for i in range(depth):
            print "\t",
        print r
        if dir:
            newdir = dir+"/"+r
        else:
            newdir = r
        listDirs(dir = newdir, key=key, depth = depth+1,max=max)

def ls(key="",dir="",depth=0,max=10):
    listDirs(key,dir, depth,max)

# ----------------------------------------------------------------------------
def getRegName(key,quiet=True):

    if key=="": return ""

    if isinstance(key,list):
        key = key[0]

    if not key.find("/") == -1: return key


    pm.updateDirs("")    

    subdir=pm.modeling[pm.order[0]].dir
    theTDirs=pm.getListOf(TDirectory, subdir)

    if not quiet:         print "Matching,",key

    matches = []

    for d in theTDirs:
        if not quiet:
            print "\t",d

        if not d.find(key) == -1:
            if not quiet:  print "Found Match,",d
            matches.append(d)

    if not quiet:  print "number of matches",len(matches)

    if len(matches) == 1:
        if not quiet:  print "retirn ,",matches[0]
        return matches[0]

    if len(matches) < 1:
        print 
        print "ERROR No Directory Matching ",key
        print 

    if len(matches) > 1:
        print "More than one dir match ",len(matches)
        print "\t(returning the smallest)"

        len_smallest = 1e4
        smallest     = ""
        for m in matches:
            if len(m) < len_smallest:
                len_smallest = len(m)
                smallest = m
        print "Matched dir:",smallest
        return smallest
            

# ----------------------------------------------------------------------------
def listVars(key="",region=None,subdir=None, quiet=False):
    pm.updateDirs(region)
        
    if not subdir:
        subdir=pm.modeling[pm.order[0]].dir

    #print "HERE"
    #print pm.data
    #print pm.data.dir

    vars = []
    #theHists=pm.getListOf(TH1F,subdir)
    #for h in theHists:
    #    if h.find(key)!=-1:
    #        vars.append(h)
            
    theHists=pm.getListOf(TH1,subdir)
    for h in theHists:
        if h.find(key)!=-1:
            vars.append(h)
    vars.sort()
    if not quiet :
        for v in vars :
            print v


    theTDirs=pm.getListOf(TDirectory, subdir)

    if region is None:

        for d in theTDirs:
            print 
            print d
            print "--------------"
            listVars(region=d, key=key, quiet=quiet)

        #return listVars(region=rand_reg,key=key, quiet=quiet)

    else :

        vars = []
        for d in theTDirs:
            if d.find(region)!=-1:

                theHists=pm.getListOf(TH1F,subdir.Get(region))
                for h in theHists:
                    if h.find(key)!=-1:
                        vars.append(h)

                theHists=pm.getListOf(TH1,subdir.Get(region))
                for h in theHists:
                    if h.find(key)!=-1:
                        vars.append(h)


                the2DHists=pm.getListOf(TH2F,subdir.Get(region))
                for h in the2DHists:
                    if h.find(key)!=-1:
                        vars.append(h)

                if not quiet :
                    for v in vars :
                        print v

                break

        #return vars



# -----------------------------------------------------------------
if __name__ == "__main__":
    main()
