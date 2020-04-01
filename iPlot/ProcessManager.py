# ----------------------------------------------------------------------------
# ProcessManagerNoData:
#   - handles all the background modeling processes
#   - draws all the histograms in the data file with
#       the stacked modeling overlaid
import os
import math
from ROOT import TFile,TH1F,TH2,TDirectory,ROOT, TLine, Double

#import PlotLabeling

from Process import Process
#from CombinedProcess import CombinedProcess
import re
import string

#
#  The dirty work
#
import ROOTHelp
from   ROOTHelp.CanvasOptions import CanvasOptions 
from   ROOTHelp.PlotOptions   import PlotOptions
from   ROOTHelp.Plotting      import stack_with_data, stack_with_data_and_ratio, plot_hists, plot_hists_wratio, stack_no_data, plot_hists_wratio_errorband
from   ROOTHelp.Utils         import make_legend, calc_max_in_range, do_variable_rebinning, calc_min

# ----------------------------------------------------------------------------
class ProcessManager:
    # ----------------------------------------------------------------------------
    def __init__(self,debug=False):
                 

        # 
        # Debug 
        #
        self.debug = debug
        
        # 
        # Background Modeling
        #
        self.modeling = {}

        #
        # Systematic Vars
        #
        self.sysVars = {}
        self.drawErrorBand = False

        #
        # Data
        #
        self.data = None

        # 
        # Drawing order
        #
        self.order = []

        

    # ----------------------------------------------------------------------------
    # Add an additional process to keep track of.
    def AddData(self,name,file,dir):
        self.data = Process(name,file,dir,ROOT.kBlack,corrections=None,scale=1.0,
                            regionCondition=None, debug=self.debug)
        #self.order.append(name)
        return

    # ----------------------------------------------------------------------------
    # Add an additional process to keep track of.
    def AddProcess(self,name,file,dir,color,corrections = None,scale=1.0,regionCondition=None):
        self.modeling[name] = Process(name,file,dir,color,corrections,scale,
                                      regionCondition=regionCondition, debug=self.debug)
        if not regionCondition:
            self.order.append(name)
        return

    # 
    # Add Systematics Variations
    # 
    def AddSysVar(self,name,file,dir,scale=1.0):

        self.sysVars[name] = Process(name,file,dir,color=ROOT.kBlack,scale=scale,debug=self.debug)
        self.drawErrorBand = True
        return



    # ----------------------------------------------------------------------------
    # make the options for the plotting
    def makePlotOptions(self,stackNames):
        self.plot_options = []

        for name in stackNames :
            opt = dict() 
            opt['fill_color'] = self.modeling[name].color
            
            self.plot_options.append(PlotOptions(**opt))
    
    
        return

    # ----------------------------------------------------------------------------
    # Initialize all the sub-processes (read the files and get directories)
    def InitializeProcesses(self):

        #
        # Read the Data
        #
        if self.data:
            self.data.Init()

        #
        # Read the Modeling Files
        #
        for type in self.modeling.keys():
            self.modeling[type].Init()

        #
        # Read the Modeling Files
        #
        for sys in self.sysVars.keys():
            self.sysVars[sys].Init()

        return

    # ----------------------------------------------------------------------------
    def updateDirs(self,subDir):

        #
        # Read the Data
        #
        if self.data:
            self.data.updateDir(subDir)

        #
        # Read the Modeling Files
        # 
        for type in self.modeling.keys():
            self.modeling[type].updateDir(subDir)

        #
        #  Read the sys vars
        # 
        for sys in self.sysVars.keys():
            self.sysVars[sys].updateDir(subDir)

        return


    # ----------------------------------------------------------------------------
    def updateTopDir(self,subDir):


        #
        # Read the Data
        #
        if self.data:
            self.data.updateTopDir(subDir)


        # Read the Modeling Files
        # ----------------------------
        for type in self.modeling.keys():
            self.modeling[type].updateTopDir(subDir)

        return


    # ----------------------------------------------------------------------------
    def resetDirs(self):

        #
        # Read the Data
        #
        if self.data:
            self.data.resetDir()

        # Read the Modeling Files
        # ----------------------------
        for type in self.modeling.keys():
            self.modeling[type].resetDir()

        return    
        
    # ----------------------------------------------------------------------------
    # Return the list of a given type in the root directory
    def getListOf(self,type,inputDir):

        # Get the list of hists in file 1
        theTH1Fs = set()

        for k in inputDir.GetListOfKeys():
            thisName = k.GetName()
            if type == TDirectory and not k.IsFolder() :
                continue
            if thisName == "ReadKey":
                continue
            if isinstance(inputDir.Get(thisName),type):
                theTH1Fs.add(thisName)
            
        return theTH1Fs
                

    # ----------------------------------------------------------------------------
    def tuneHist(self,hist,do_cumulative=False, pre_rebin=None, norm=False, **kw):

        rebin         = kw.get('rebin'        ,  None) 


        histname=hist.GetName()

        hist.SetMarkerSize(1.2)

        #labeling_function = PlotLabeling.__dict__.get(histname)
        #if labeling_function:
        #    hist = labeling_function(hist)

        if isinstance(hist, TH2) :
            return hist
        
        if isinstance(rebin,list):
            binning=rebin
            orighist=hist
            if pre_rebin is not None :
                hist=hist.Clone(hist.GetName()+"_rebin")
                hist.Rebin(pre_rebin)
            hist=do_variable_rebinning(hist,binning)
            # make proper y-axis label assuming GeV!
            #nbins=orighist.GetNbinsX()
            nbins = len(rebin) - 1

            #xrang=hist.GetXaxis().GetXmax()-hist.GetXaxis().GetXmin()
            #nbins = hist.GetXaxis().GetNbins()
            #xrang=orighist.GetXaxis().GetXmax()-orighist.GetXaxis().GetXmin()
            xrang=rebin[-1] - rebin[0]
            print 'nbins, range = %d %d' %(nbins, xrang)
            #xrang = binning[-1]-binning[0]
            #nbins = len(binning) - 1
            #hist.GetYaxis().SetTitle('Events /%3.0f GeV' %(xrang/nbins))
            if xrang/nbins:
                if norm:
                    hist.GetYaxis().SetTitle('Normalized Events /%3.0f bin' %(xrang/nbins))
                else:
                    hist.GetYaxis().SetTitle('Events /%3.0f bin' %(xrang/nbins))
            

        if isinstance(rebin,int):
            hist=hist.Clone(hist.GetName()+"_rebin")
            hist.Rebin(rebin)
            bin_width = hist.GetXaxis().GetBinWidth(1)
            xrang=hist.GetXaxis().GetXmax()-hist.GetXaxis().GetXmin()
            #hist.GetYaxis().SetTitle('Events /%3.0f GeV' %(xrang/hist.GetNbinsX()))
            if norm:
                hist.GetYaxis().SetTitle('Normalized Events /%3.0f bins' %(rebin))
            else:
                hist.GetYaxis().SetTitle('Events /%3.0f bins' %(rebin))


        
        if isinstance(rebin, basestring) and rebin.count(',') == 2 :
            pre_rebin = int(rebin.split(',')[0])
            hist=hist.Clone(hist.GetName()+"_rebin")
            hist.Rebin(pre_rebin)
            bin_width = hist.GetXaxis().GetBinWidth(1)

        if do_cumulative :
            newhist = hist.Clone()

            errfull = Double()
            intfull = hist.IntegralAndError(1, hist.GetNbinsX()+2, errfull)
            print 'intfull = %f' %intfull
            for bin in range(0, hist.GetNbinsX()+2) :
                newerr = Double()
                newint = hist.IntegralAndError(bin, hist.GetNbinsX()+2, newerr)
                print 'newint = %f'%newint

                toterr = 0 
                if intfull > 0 and newint > 0 :
                    toterr = newint/intfull * math.sqrt( (newerr/newint)*(newerr/newint) + 
                                                         (errfull/intfull)*(errfull/intfull))
                
                print 'content = %f' %(newint/intfull)
                newhist.SetBinContent(bin, newint/intfull)
                newhist.SetBinError(bin, toterr)

            hist = newhist


        return hist
    
    #
    #  Get Hists
    #
    def getHists(self,hist, **kw):

        do_cumulative = kw.get('do_cumulative',  False) 
        pre_rebin     = kw.get('pre_rebin'    ,  None)

        thisHist = {}

        if self.data:
            thisHist["Data"] = self.data.getHist(hist)

            if thisHist["Data"] is not None :
                thisHist["Data"]=self.tuneHist(thisHist["Data"],do_cumulative=do_cumulative, pre_rebin=pre_rebin, **kw)

        #
        # Get the hist for each modeling type
        #
        for type in self.modeling:
            thisHist[type] = self.modeling[type].getHist(hist)

            if thisHist[type] is not None :
                thisHist[type]=self.tuneHist(thisHist[type],do_cumulative=do_cumulative, pre_rebin=pre_rebin, **kw)

        return thisHist

    #
    #  Get Sys Var hists
    #
    def getSysHists(self,hist, **kw):

        do_cumulative = kw.get('do_cumulative',  False) 
        pre_rebin     = kw.get('pre_rebin'    ,  None)

        thisHist = {}

        #
        # Get the hist for each modeling type
        #
        for sys in self.sysVars:
            thisHist[sys] = self.sysVars[sys].getHist(hist)

            if thisHist[sys] is not None :
                thisHist[sys]=self.tuneHist(thisHist[sys],do_cumulative=do_cumulative, pre_rebin=pre_rebin, **kw)
            else:
                print "ERROR Cant get hist",hist,"from",sys
                import sys
                sys.exit(-1)

        return thisHist


    # ----------------------------------------------------------------------------
    def makeErrorHist(self,thisHist_up,thisHist_low):

        histErr = TH1F(thisHist_up)

        for i in range(thisHist_up.GetNbinsX()+1):
            
            low = thisHist_low.GetBinContent(i)
            up = thisHist_up.GetBinContent(i)
            
            cvalue = (low+up)/2
            error = (up-low)/2

            histErr.SetBinContent(i,cvalue)

            if error==0.0:
                error=1e-10
            histErr.SetBinError(i,error)
            
        return histErr

    # ----------------------------------------------------------------------------
    # theHist is the map returned by getHists
    def makeErrorBandRatio(self,errorBand):
        ratioBand = TH1F(errorBand)
        ratioBand.SetFillColor(ROOT.kRed)
        ratioBand.SetMarkerColor(ROOT.kRed)
        ratioBand.SetMarkerSize(0)
        ratioBand.SetLineWidth(3)
        #ratioBand.SetFillStyle(3004)
        ratioBand.SetFillStyle(1001)
        
        for i in range(errorBand.GetNbinsX()+1):
            
            ratioBand.SetBinContent(i,1.0)
            
            err = 0
            if errorBand.GetBinContent(i):
                err = errorBand.GetBinError(i)/errorBand.GetBinContent(i)

            ratioBand.SetBinError(i,err)

        return ratioBand

    # ----------------------------------------------------------------------------
    # theHist is the map returned by getHists
    def makeErrorBand(self,thisHist_up,thisHist_low):

        #Find sample first in the order that exists
        top_entry = self.order[0]
        order_index=0
        while top_entry not in thisHist_up :
            order_index += 1
            top_entry = self.order[order_index]
        # Make the list of things to stack, and names

        errBand_up = TH1F(thisHist_up[top_entry])
        errBand_low = TH1F(thisHist_low[top_entry])

        order_notop = list(self.order)
        order_notop.pop(order_index)
        
        for p in order_notop:
            
            if thisHist_up.has_key(p) and thisHist_up[p]:
                errBand_up.Add(thisHist_up[p])

            if thisHist_low.has_key(p) and thisHist_low[p]:
                errBand_low.Add(thisHist_low[p])


        histErr = self.makeErrorHist(errBand_up,errBand_low)
        histErr.SetFillColor(ROOT.kRed)
        histErr.SetMarkerColor(ROOT.kRed)
        histErr.SetMarkerSize(0)
        histErr.SetFillStyle(3344)
        #histErr.SetFillStyle(1001)
        
        return histErr
                
                
    # ----------------------------------------------------------------------------
    # theHist is the map returned by getHists
    def makeStack(self,
                  thisHist,
                  regiondesc="",
                  **kw):


        #
        #  Read the options
        #
        doratio        =  kw.get('doratio'      ,  False)
        logy           =  kw.get('logy'         ,  False)
        logx           =  kw.get('logx'         ,  False)
        maxy           =  kw.get('maxy'         ,  ROOTHelp.default)
        rMin           =  kw.get('rMin'         ,  None)
        rMax           =  kw.get('rMax'         ,  None)
        label          =  kw.get('label'        ,  None)
        labels         =  kw.get('labels'        ,  None)
        legend_limits  =  kw.get('legend_limits',  None)                 
        doLeg          =  kw.get('doLeg'        ,  True)
        blind          =  kw.get('blind'        ,  False)
        norm           =  kw.get('norm'         ,  False)
        yields         =  kw.get('yields'       ,  False)

        #
        # Normalize
        #
        if norm:
            self.Normalize(thisHist,logy)

        #
        # Print Yeild
        #
        if yields:
            self.PrintYeilds(thisHist)

        #
        # Make the list of things to stack, and names
        #
        stackList = []
        stackNames = []
        for p in self.order:
            if thisHist.has_key(p) and thisHist[p]:
                if label is not None :
                    thisHist[p].GetXaxis().SetTitle(label)

                stackList.append(thisHist[p])
                stackNames.append(p)

        #
        #  Format the plots
        #
        self.makePlotOptions(stackNames)
        
        #
        #   Build the canvas
        #
        can_opts = CanvasOptions(log_y=logy,log_x=logx)

        #
        # Outsource the actually stacking...
        #
        #if doratio:
        #    theStack = stack_with_data_and_ratio(thisHist['Data'],
        #                                         stackList,
        #                                         thisHist['Data'].GetName()+"_stack",
        #                                         plot_options = self.plot_options,
        #                                         canvas_options = can_opts,
        #                                         **kw
        #                                         )
        #    theStack['top_pad'].cd()
        #else:
        
        if self.data:
                
            theStack = stack_with_data(thisHist['Data'],
                                       stackList,
                                       thisHist['Data'].GetName()+"_stack",
                                       plot_options = self.plot_options,
                                       canvas_options = can_opts,
                                       **kw)
        
        
            theStack['canvas'].cd()

        else:
            
            theStack = stack_no_data(stackList,
                                     thisHist[self.order[0]].GetName()+"_stack",
                                     plot_options = self.plot_options,
                                     canvas_options = can_opts,
                                     **kw)
        
        
            theStack['canvas'].cd()



        #
        # Make the legend 
        #
        if legend_limits is None :
            legend_limits={ 'width' : 0.30, 'height' : 0.05, 'x2' : 1.0, 'y2' : 0.92 }

        hists  = [theStack['sum']]+theStack['hists']
        draw_options = ['LPE']+['F' for p in stackNames ]
        
        if doLeg:

            hists  = theStack['hists'] 
            if not labels:
                labels = [p for p in stackNames] 
            draw_options = ['F' for p in stackNames ] 

            theStack['leg'] = make_legend(hists = hists[::-1],
                                         labels = labels[::-1],
                                         width = legend_limits['width'], 
                                         height= legend_limits['height'],
                                         x2=legend_limits['x2'],
                                         y2=legend_limits['y2'],
                                         draw_options = draw_options[::-1])



            theStack['leg'].Draw()


        theStack['allhists']=thisHist
        
        #
        #  Move leg if needed
        #
        if doLeg:
            self.doFancyLegendPlacement(theStack)


        return theStack


    # ----------------------------------------------------------------------------
    # theHist is the map returned by getHists
    def makePlot(self,
                 thisHist,
                 regiondesc="",
                 **kw
                 ):

        #
        #  Read the options
        #
        logy           =  kw.get('logy'         ,  False)
        logz           =  kw.get('logz'         ,  False)
        logx           =  kw.get('logx'         ,  False)
        rebin          =  kw.get('rebin'        ,  None)
        labels         =  kw.get('labels'       ,  None)
        rlabel         =  kw.get('rlabel'       ,  None)
        legend_limits  =  kw.get('legend_limits',  None)                 
        doLeg          =  kw.get('doLeg'        ,  True)
        doratio        =  kw.get('doratio'      ,  False)
        norm           =  kw.get('norm'         ,  False)
        draw_options   =  kw.get('draw_options' ,  ROOTHelp.default)
        max            =  kw.get('max'          ,  ROOTHelp.default)
        debug          =  kw.get('debug'        ,  False)
        
        if debug: print "in makePlot"


        #
        # Normalize
        #
        if norm:
            if debug: print "Normalize"
            self.Normalize(thisHist,logy)
            
            if logy: 
                #max = 2
                kw["max"] = 2
            
        #
        # Get the canvas
        #
        can_opts = CanvasOptions(log_y=logy, log_x=logx, log_z=logz)

        #
        # Outsource the actually stacking...
        #
        if len(thisHist) == 1:
            if debug: print "MakeOne Plot"
            thePlot = plot_hists([thisHist[self.order[0]]],
                                 thisHist[self.order[0]].GetName()+"_stack",
                                 canvas_options = can_opts,
                                 #max = max,
                                 **kw
                                 )
            hists  = [thePlot['hists']]
            if labels:
                labels = [labels[0]]
            else:
                doLeg = False
            
        else:
            if debug: print "More than One plot"
            plot_order  =  kw.get('plot_order',  None)                 
            theHists = []
            if plot_order:
                for pName in plot_order:
                    theHists.append(thisHist[pName])
            else:
                theHists = thisHist.values(),
            
            if doratio:
                if self.drawErrorBand:
                    theSysHists = self.getSysHists(thisHist.values()[0].GetName().replace("_rebin",""), **kw)
                    thePlot = plot_hists_wratio_errorband(theHists,
                                                          theSysHists.values(),
                                                          thisHist.values()[0].GetName()+"_stack",
                                                          canvas_options = can_opts,
                                                          #max = max,
                                                          **kw)
                else:
                    thePlot = plot_hists_wratio(theHists,
                                                thisHist.values()[0].GetName()+"_stack",
                                                #canvas_options = can_opts,
                                                #max = max,
                                                **kw)
                
            else:
                thePlot = plot_hists(theHists,
                                     thisHist.values()[0].GetName()+"_stack",
                                     canvas_options = can_opts,
                                     #max = max,
                                     #draw_options = draw_options,
                                     **kw)


            hists        = thePlot['hists']
            labels       = kw.get('labels',[""] )
            if len(labels) < 2:
                doLeg = False

        thePlot['canvas'].cd()

        #
        # Make the legend 
        #
        if legend_limits is None :
            legend_limits={ 'width' : 0.30, 'height' : 0.05, 'x2' : 0.9, 'y2' : 0.92 }
            if doratio:
                legend_limits['y2'] = 0.9
                

        if doLeg:
            
            if draw_options is ROOTHelp.default:
                draw_options = []
                for i, p in enumerate(hists):
                    if not i:
                        draw_options.append("LPE")
                    else:
                        draw_options.append("F")

            thePlot['leg'] = make_legend(hists = hists[::-1],
                                         labels = labels[::-1],
                                         width = legend_limits['width'], 
                                         height= legend_limits['height'],
                                         x2=legend_limits['x2'],
                                         y2=legend_limits['y2'],
                                         draw_options = draw_options[::-1])
            if doratio:
                thePlot['top_pad'].cd()

            thePlot['leg'].Draw()


        thePlot['allhists']=thisHist

        #if doLeg:
        #  self.doFancyLegendPlacement(thePlot)

        return thePlot



    #
    # Name says it all
    #
    def doFancyLegendPlacement(self,thePlot):

        # no stack legend overlap
        leg=thePlot['leg']

        # otherwise leg.GetX1() is in absolute not histogram units
        thePlot['canvas'].Update()
        x1=leg.GetX1()
        x2=leg.GetX2()

        # check if okay
        maxunderleg_right = calc_max_in_range(thePlot['hists'],x1,x2)            
        if maxunderleg_right < leg.GetY1():
            return

        maxunderleg=maxunderleg_right

        # check if left-side is better
        maxunderleg_left = calc_max_in_range(thePlot['hists'],0,x2-x1)
        betteronleft= (maxunderleg_left <maxunderleg_right)
        okayonleft=maxunderleg_left < leg.GetY1()
        if okayonleft or betteronleft:
            #print "better on left"
            delta=leg.GetX2NDC()-leg.GetX1NDC()
            leg.SetX1NDC(0.2)
            leg.SetX2NDC(0.2+delta)
            if okayonleft:
                # it's okay on left, we're done
                #print "okay on left"
                return 
            maxunderleg=maxunderleg_left

        # rescale the height
        h=thePlot['hists'][0]
        r=maxunderleg/(h.GetMaximum()-(leg.GetY2()-leg.GetY1()))+0.1
        #print "h=",maxunderleg
        #print "l=",leg.GetY2()-leg.GetY1()
        #print "m=",h.GetMaximum()
        #print "r=",r
        #print "setting=",r*h.GetMaximum()
        print "Setting MAximum"
        thePlot['hists'][0].SetMaximum(r*h.GetMaximum())
        
        # brutally force an update
        thePlot['canvas'].Modified()
        thePlot['canvas'].Paint()



    # ----------------------------------------------------------------------------
    def listDirs(self,key=None):
        regions=[]
        theTDirs=self.getListOf(TDirectory,self.modeling[self.order[0]].dir)
        for TDir in sorted(theTDirs):
            if not key or TDir.count(key):
                regions.append(TDir)
        return regions

    # ----------------------------------------------------------------------------
    def Normalize(self, thisHist, doLog=False):
        
        sf = []
        for i, h in enumerate(thisHist):
            print "Normalizing" ,h,
            thisHist[h].Sumw2()
            if thisHist[h].Integral():
                print "ScaleFactor",1.0/thisHist[h].Integral()
                sf.append(1.0/thisHist[h].Integral())
                thisHist[h].Scale(1.0/thisHist[h].Integral())
        if len(sf)>1:
            print "Ratio:",sf[0]/sf[1]
        if doLog:
            thisMin = calc_min(thisHist.values(),ignore_zeros=True,ignore_negatives=True)
            thisMin = thisMin / 10
        else:
            thisMin = 1e-10
            
        for i, h in enumerate(thisHist):
            thisHist[h].SetMinimum(thisMin)
        return

    # ----------------------------------------------------------------------------
    def PrintYeilds(self, thisHist):
    
        #
        # Make the list of things to stack, and names
        #
        totalBkg = 0.0
        for p in self.order:
            if thisHist.has_key(p) and thisHist[p]:

                integral = 0.0
                errsq = 0.0
                for bin in range( 1, thisHist[p].GetNbinsX()+2) :
                    integral += thisHist[p].GetBinContent(bin)
                    errsq    += thisHist[p].GetBinError(bin)*thisHist[p].GetBinError(bin)
         
                totalBkg += thisHist[p].Integral() 
                print 'Integral %s %f +- %f' %(p, integral, math.sqrt(errsq)) 


        print 'Total Bkg :', totalBkg
        return
