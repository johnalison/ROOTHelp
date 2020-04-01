import ROOT
from   ROOTHelp.MetaLegend import MetaLegend
import ROOTHelp
import math
from array import array
#
#   Do variable rebinning for a histogram
#
def do_variable_rebinning(hist,bins):
    newhist=ROOT.TH1F(hist.GetName()+"_rebin",
                      hist.GetTitle()+";"+hist.GetXaxis().GetTitle()+";"+hist.GetYaxis().GetTitle(),
                      len(bins)-1,
                      array('d',bins))
    a=hist.GetXaxis()
    newa=newhist.GetXaxis()
    for b in range(1, hist.GetNbinsX()+1):
        newb=newa.FindBin(a.GetBinCenter(b))
        val=newhist.GetBinContent(newb)
        err=newhist.GetBinError(newb)

        ratio_bin_widths=newa.GetBinWidth(newb)/a.GetBinWidth(b)
        val=val+hist.GetBinContent(b)/ratio_bin_widths
        err=math.sqrt(err*err+hist.GetBinError(b)/ratio_bin_widths*hist.GetBinError(b)/ratio_bin_widths)
        newhist.SetBinContent(newb,val)
        newhist.SetBinError(newb,err)

    return newhist



def getHist(infile, histName, binning=None):
    hist = infile.Get(histName)
    
    if not h:
        infile.ls()
        print
        print "ERROR"
        print "Cannot find",histName
        print
        sys.exit(-1)

    if type(binning ) == type(list()):
        hist  = do_variable_rebinning(hist,binning)
    else:
        hist.Rebin(binning)


    if binning:
        print "Rebin"
        h_rebin    = do_variable_rebinning(h,binning)
        return h_rebin

    return h


#
# Calculate the min of a bunch of histograms
#
def calc_min(hists, include_errors=False, ignore_zeros=False, ignore_negatives=False):
    extremes = []
    for h in hists:
        points = []
        if isinstance(h, ROOT.TH1) or isinstance(h, ROOT.THStack): 
            if isinstance(h, ROOT.THStack): 
                h = h.GetHistogram()
            for i_bin in xrange(1, h.GetXaxis().GetNbins()+1):
                point = h.GetBinContent(i_bin)
                if include_errors:
                    point -= h.GetBinError(i_bin) # -= : min/max differnce
                points.append(point)
        elif isinstance(h, ROOT.TGraph) or isinstance(h, ROOT.TGraphErrors) or isinstance(h, ROOT.TGraphAsymmErrors): 
            x = ROOT.Double() ;  y = ROOT.Double()
            for i_bin in xrange(1, h.GetN()+1):
                h.GetPoint(i_bin, x, y)
                point = float(y)
                if include_errors:
                    if isinstance(h, ROOT.TGraphErrors):
                        point -= h.GetErrorY(i_bin) # -= : min/max differnce
                    elif isinstance(h, ROOT.TGraphAsymmErrors): 
                        point -= h.GetErrorYlow(i_bin) # -= : min/max differnce
                points.append(point)

        if ignore_zeros:
            points = filter(lambda x: x, points)
        if ignore_negatives:
            points = filter(lambda x: x > 0, points)
        if points:
            extremes.append(min(points)) # min/max differnce

    if extremes:
        return min(extremes) # min/max differnce
    else:
        return 0.


#______________________________________________________________________________
def calc_max(hists, include_errors=False, ignore_zeros=False, ignore_negatives=False):
    extremes = []
    for h in hists:
        points = []
        if isinstance(h, ROOT.TH1) or isinstance(h, ROOT.THStack): 
            if isinstance(h, ROOT.THStack): 
                h = h.GetHistogram()
            for i_bin in xrange(1, h.GetXaxis().GetNbins()+1):
                point = h.GetBinContent(i_bin)
                if include_errors:
                    point += h.GetBinError(i_bin) # -= : min/max differnce
                points.append(point)
        elif isinstance(h, ROOT.TGraph) or isinstance(h, ROOT.TGraphErrors) or isinstance(h, ROOT.TGraphAsymmErrors): 
            x = ROOT.Double() ;  y = ROOT.Double()
            for i_bin in xrange(1, h.GetN()+1):
                h.GetPoint(i_bin, x, y)
                point = float(y)
                if include_errors:
                    if isinstance(h, ROOT.TGraphErrors):
                        point += h.GetErrorY(i_bin) # -= : min/max differnce
                    elif isinstance(h, ROOT.TGraphAsymmErrors): 
                        point += h.GetErrorYhigh(i_bin) # -= : min/max differnce
                points.append(point)

        if ignore_zeros:
            points = filter(lambda x: x, points)
        if ignore_negatives:
            points = filter(lambda x: x > 0, points)
        if points:
            extremes.append(max(points)) # min/max differnce

    if extremes:
        return max(extremes) # min/max differnce
    else:
        return 0.


#
#
#
def set_min(hists, min=ROOTHelp.default, top_buffer=0.15, bottom_buffer=0.15,
        log_y=False, limit=None, include_errors=True,
        include=None):
    """ 
    Sets the minimum of all histograms or graphs in the list hists to be the
    factor times the minimum among hists.  If limit is specified, then the
    miniumum cannot be set below that.
    """
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    if min is None:
        return None
    if include is None:
        include = []
    if not isinstance(include, list):
        include = [include]


    if min is ROOTHelp.default or min is ROOTHelp.ignore_zeros:
        ## calculated range
        if min is ROOTHelp.default:
            y_min = calc_min(hists, include_errors, ignore_zeros=False, ignore_negatives=log_y)
            y_max = calc_max(hists, include_errors, ignore_zeros=False, ignore_negatives=log_y)
        elif min is ROOTHelp.ignore_zeros:
            y_min = calc_min(hists, include_errors, ignore_zeros=True, ignore_negatives=log_y)
            y_max = calc_max(hists, include_errors, ignore_zeros=True, ignore_negatives=log_y)
        ## check to change range to include values
        for y in include:
            if y < y_min:
                y_min = y
            if y > y_max:
                y_max = y
        ## calculate setting with buffer
        if log_y and y_min and y_max:
            setting = math.pow( 10, math.log(y_min,10) - (math.log(y_max,10) - math.log(y_min,10)) * bottom_buffer / (1 + top_buffer + bottom_buffer) )
        else:
            setting = y_min - (y_max - y_min) * bottom_buffer / (1 + top_buffer + bottom_buffer)

    ## user set range
    else:
        setting = min
    if not limit is None and setting < limit:
        setting = limit
    for h in hists:
        h.SetMinimum(setting)
    return setting


#______________________________________________________________________________
def set_max(hists, max=ROOTHelp.default, top_buffer=0.15, bottom_buffer=0.15,
        log_y=False, limit=None, include_errors=True,
        include=None):
    """
    Sets the maximum of all histograms or graphs in the list hists to be the
    factor times the maximum among hists.  If limit is specified, then the
    maxiumum cannot be set above that.
    """
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    if max is None:
        return None
    if include is None:
        include = []
    if not isinstance(include, list):
        include = [include]

    if max is ROOTHelp.default or max is ROOTHelp.ignore_zeros:
        ## calculated range
        if max is ROOTHelp.default:
            y_min = calc_min(hists, include_errors, ignore_zeros=False, ignore_negatives=log_y)
            y_max = calc_max(hists, include_errors, ignore_zeros=False, ignore_negatives=log_y)
        elif max is ROOTHelp.ignore_zeros:
            y_min = calc_min(hists, include_errors, ignore_zeros=True, ignore_negatives=log_y)
            y_max = calc_max(hists, include_errors, ignore_zeros=True, ignore_negatives=log_y)
        ## check to change range to include values
        for y in include:
            if y < y_min:
                y_min = y
            if y > y_max:
                y_max = y
                print "y_max is now", y_max
        ## calculate setting with buffer
        if log_y and y_min and y_max:
            #setting = math.pow( 10, math.log(y_max,10) + (math.log(y_max,10) - math.log(y_min,10)) * top_buffer / (1 + top_buffer + bottom_buffer) )
            setting = math.pow( 10, math.log(y_max,10) + (math.log(y_max,10)) * top_buffer / (1 + top_buffer + bottom_buffer) )
            
        else:
            setting = y_max + (y_max - y_min) * top_buffer / (1 + top_buffer + bottom_buffer)
    ## user set range
    else:
        setting = max
    if not limit is None and setting > limit:
        setting = limit
    for h in hists:
        h.SetMaximum(setting)
    return setting



def getXMinMax(hist, x_min, x_max):
    if not x_max:
        x_max = hist.GetXaxis().GetXmax()
    if not x_min:
        x_min = hist.GetXaxis().GetXmin()
    return x_min, x_max

def setXMinMax(hist, x_min, x_max):
    x_min, x_max = getXMinMax(hist, x_min, x_max)
    hist.GetXaxis().SetRangeUser(x_min,x_max) 

def getZMinMax(hist, z_min, z_max):
    if not z_max:
        z_max = hist.GetZaxis().GetXmax()
    if not z_min:
        z_min = hist.GetZaxis().GetXmin()
    return z_min, z_max


def setZMinMax(hist, z_min, z_max):
    z_min, z_max = getZMinMax(hist, z_min, z_max)
    hist.GetZaxis().SetRangeUser(z_min,z_max) 


#
#   Creates a legend from a list of hists (or graphs).
#
def make_legend(hists, labels, draw_options=ROOTHelp.default,
                width=0.15, height=0.05, x1=None, y1=None, x2=None, y2=None):
    """
    Creates a legend from a list of hists (or graphs).
    """

    assert len(hists) == len(labels)
    leg = MetaLegend(width=width, height=height, x1=x1, y1=y1, x2=x2, y2=y2)
    for h, lab, opt in zip(hists, labels, draw_options):

        if not opt in ('P', 'F', 'L', 'l'):
            ## assume opt is of the same format as draw_options used with Draw
            if opt.count('P'):
                if opt.count('E'):
                    opt = 'PL'
                else:
                    opt = 'P'
            elif opt.count('l'):
                opt = 'l'
            else: # '', 'HIST', etc.
                opt = 'F'
        #print "Adding entry on ",lab
        leg.AddEntry(h, label=lab, option=opt)
    return leg



def makeCanvas(name, title, **kw):
        width  = kw.get('width',         800)
        height = kw.get('height',        600)
        log_x  = kw.get('logx',         0)
        log_y  = kw.get('logy',         0)
        log_z  = kw.get('logz',         0)
        #kw.get('grid_x',        0)
        #kw.get('grid_y',        0)
        #kw.get('tick_x',        1)
        #kw.get('tick_y',        1)
        #kw.get('left_margin',   ROOTHelp.default)
        #kw.get('right_margin',  ROOTHelp.default)
        #kw.get('top_margin',    ROOTHelp.default)
        #kw.get('bottom_margin', ROOTHelp.default)
        
        c = ROOT.TCanvas(name, title, 200, 10, width, height)
        c.SetLogx(log_x)
        c.SetLogy(log_y)
        c.SetLogz(log_z)
            
        return c


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



def getCMSText(xStart,yStart,subtext = "Work in Progress", lumiText="",xLumiStart=0.70,yLumiStart=0.95):

    yStartFirstLine = yStart
    yStartSecondLine = yStart - 0.047

    cmsScale=1.2
    textsize=0.045

    firstline = '#scale['+str(cmsScale)+']{#bf{CMS}}'
    additionaltext = ""
    if additionaltext == "Sim":
        firstline += " #it{Simulation}"
    elif additionaltext == "Supp":
        firstline += " #it{Supplementary}"
                    
    cmsfistLine = ROOT.TLatex(xStart, yStartFirstLine, firstline)
    cmsfistLine.SetTextFont(42)
    cmsfistLine.SetTextSize(textsize)
    cmsfistLine.SetNDC()

    cmssecondline = ROOT.TLatex(xStart, yStartSecondLine, '#it{'+subtext+'}')
    cmssecondline.SetTextFont(42)
    cmssecondline.SetTextSize(textsize)
    cmssecondline.SetNDC()

    if lumiText:
        cmsLumi = ROOT.TLatex(xLumiStart, yLumiStart, lumiText)
        cmsLumi.SetTextFont(42)
        cmsLumi.SetTextSize(0.035)
        cmsLumi.SetNDC()
        
        return cmsfistLine, cmssecondline, cmsLumi

    return cmsfistLine, cmssecondline


def drawStackCompRatio(outName,dataInfo,MCInfo,yTitle,xTitle,rTitle,outDir,min=1,setLogy=1,x_min=None,x_max=None,cmsText="", lumiText=""):
    from   ROOTHelp.Plotting      import makeRatio
    histData = dataInfo[0].Clone()

    stacksum=MCInfo[0][0].Clone("tmp")
    stacksum.Reset()
    for h in MCInfo:
        stacksum.Add(h[0])

    stacksum.Integral()
    scaleFactor = histData.Integral()/stacksum.Integral()

    stack = ROOT.THStack("TestStack", outName)
    for hMC in MCInfo:
        hMC[0].SetFillColor(hMC[2])
        hMC[0].Scale(scaleFactor)
        stack.Add(hMC[0], 'sames')

    stacksum.Scale(scaleFactor)

#    hist2 = histInfo[1][0].Clone()
#    hist2.SetFillColor(ROOT.kYellow)
        
    maxY = max(histData.GetMaximum(),stack.GetMaximum())

    if setLogy:
        histData.SetMaximum(4e0*maxY)
        histData.SetMinimum(min)
        stack.SetMaximum(4e0*maxY)
        stack.SetMinimum(min)
    else:
        stack.SetMaximum(1.4*maxY)
        histData.SetMaximum(1.4*maxY)


    histData.GetYaxis().SetTitle(yTitle)
    histData.GetXaxis().SetTitle(xTitle)


    xpos = 0.5
    ypos = 0.69
    xwidth = 0.3
    ywidth = 0.05*(len(MCInfo)+1)
    
    leg = ROOT.TLegend(xpos, ypos, xpos+xwidth, ypos+ywidth)
    leg.AddEntry(histData,dataInfo[1],"PEL")
    for hMC in MCInfo:
        leg.AddEntry(hMC[0],hMC[1] ,"F")
    #leg.AddEntry(offLF,"Offline tracks light-flavor jets","L")
    #leg.AddEntry(hltLF,"HLT tracks light-flavor jets"    ,"PEL")

    canvas = makeCanvas(outName, outName, width=600, height=600)
    split=0.3
    top_pad    = ROOT.TPad("pad1", "The pad 80% of the height",0,split,1,1,0)
    bottom_pad = ROOT.TPad("pad2", "The pad 20% of the height",0,0,1,split,0)
    top_pad.Draw()
    bottom_pad.Draw()
    
    axissep = 0.02
    top_pad.cd()
    top_pad.SetLogy(setLogy)
    top_pad.SetTopMargin(canvas.GetTopMargin()*1.0/(1.0-split))
    top_pad.SetBottomMargin(0.5*axissep)
    top_pad.SetRightMargin(canvas.GetRightMargin())
    top_pad.SetLeftMargin(canvas.GetLeftMargin());
    top_pad.SetFillStyle(0) # transparent
    top_pad.SetBorderSize(0)
        

    stack.Draw()
    if x_max is not None and x_min is not None:
        stack.GetXaxis().SetRangeUser(x_min,x_max)
        histData.GetXaxis().SetRangeUser(x_min,x_max)

    stack.GetYaxis().SetTitle(yTitle)
    stack.GetXaxis().SetTitle(xTitle)
    stack.Draw("hist")


    #hltLF.SetMarkerSize(0.75)
    #hltLF.SetMarkerStyle(21)
    histData.Draw("same pe")
    #offBQ.Draw("hist same")
    #hltBQ.SetMarkerSize(0.75)
    #hltBQ.SetMarkerStyle(21)
    #hltBQ.Draw("same pe")
    leg.Draw("same")

    histRatio = makeRatio(num = histData.Clone(),  den = stacksum.Clone())

    cmsLines = getCMSText(xStart=0.225,yStart=0.85,subtext=cmsText,lumiText=lumiText)
    for cmsl in cmsLines:
        cmsl.Draw("same")



    bottom_pad.cd()
    bottom_pad.SetTopMargin(2*axissep)
    bottom_pad.SetBottomMargin(canvas.GetBottomMargin()*1.0/split)
    bottom_pad.SetRightMargin(canvas.GetRightMargin())
    bottom_pad.SetLeftMargin(canvas.GetLeftMargin());
    bottom_pad.SetFillStyle(0) # transparent
    bottom_pad.SetBorderSize(0)
    ratio_axis = histData.Clone()
    #ratio_axis.GetYaxis().SetTitle("PF to Calo")
    ratio_axis.GetYaxis().SetTitle("Ratio")
    ratio_axis.GetXaxis().SetTitle(histData.GetXaxis().GetTitle())
    ratio_axis.GetYaxis().SetNdivisions(507)
    rMin = 0
    rMax = 2
    ratio_axis.GetYaxis().SetRangeUser(rMin, rMax)
    histRatio.GetYaxis().SetRangeUser(rMin, rMax)
    histRatio.GetYaxis().SetTitle(rTitle)


    histRatio.Draw("PE")
    histRatio.Draw("PE same")
    oldSize = histRatio.GetMarkerSize()
    histRatio.SetMarkerSize(0)
    histRatio.DrawCopy("same e0")
    histRatio.SetMarkerSize(oldSize)
    histRatio.Draw("PE same")

    line = ROOT.TLine()
    if x_max is not None and x_min is not None:
        line.DrawLine(x_min, 1.0, x_max, 1.0)
    else:
        line.DrawLine(histData.GetXaxis().GetXmin(), 1.0, histData.GetXaxis().GetXmax(), 1.0)

    ndivs=[505,503]

    pads = [top_pad, bottom_pad]
    factors = [0.8/(1.0-split), 0.7/split]
    for i_pad, pad in enumerate(pads):

        factor = factors[i_pad]
        ndiv   = ndivs[i_pad]
        
        prims = [ p.GetName() for p in pad.GetListOfPrimitives() ]
        
        #
        #  Protection for scaling hists multiple times
        #
        procedHist = []
        
        for name in prims:
            
            if name in procedHist: continue
            procedHist.append(name)
        
            h = pad.GetPrimitive(name)
            if isinstance(h, ROOT.TH1) or isinstance(h, ROOT.THStack) or isinstance(h, ROOT.TGraph) or isinstance(h, ROOT.TGraphErrors) or isinstance(h, ROOT.TGraphAsymmErrors):
                if isinstance(h, ROOT.TGraph) or isinstance(h, ROOT.THStack) or isinstance(h, ROOT.TGraphErrors) or isinstance(h, ROOT.TGraphAsymmErrors):
                    h = h.GetHistogram()
                #print "factor is",factor,h.GetName(),split
        
                if i_pad == 1:
                    h.SetLabelSize(h.GetLabelSize('Y')*factor, 'Y')
                    h.SetTitleSize(h.GetTitleSize('X')*factor, 'X')
                    h.SetTitleSize(h.GetTitleSize('Y')*factor, 'Y')
                    h.SetTitleOffset(h.GetTitleOffset('Y')/factor, 'Y')
                    
                if i_pad == 1:
                    h.GetYaxis().SetNdivisions(ndiv)
                h.GetXaxis().SetNdivisions()                
                if i_pad == 0:
                    h.SetLabelSize(0.0, 'X')
                    h.GetXaxis().SetTitle("")
                else:
                    h.SetLabelSize(h.GetLabelSize('X')*factor, 'X')
                    ## Trying to remove overlapping y-axis labels.  Doesn't work.
                    # h.GetYaxis().Set(4, h.GetYaxis().GetXmin(), h.GetYaxis().GetXmax()) 
                    # h.GetYaxis().SetBinLabel( h.GetYaxis().GetLast(), '')


    canvas.SaveAs(outDir+"/"+outName+".pdf")
