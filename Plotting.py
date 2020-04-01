import ROOT
import ROOTHelp

from ROOTHelp.Utils       import makeCanvas, set_max, set_min, setXMinMax, setZMinMax, make_legend
from ROOTHelp.PlotOptions import PlotOptions

def plot_hist_list(hists, **kw):
    draw_options      = kw.get('draw_options',   ['hist','hist'])
    x_min             = kw.get("x_min",             None)
    x_max             = kw.get("x_max",             None)
    y_title           = kw.get('y_title',           ROOTHelp.default)
    x_title           = kw.get('x_title',           ROOTHelp.default)
    debug             = kw.get('debug',             False)

    if debug: print "\t\t In plot_hist_list"

    #
    # Draw
    #
    for i, h in enumerate(hists):

        # draw
        if not draw_options:
            if debug: print "\t\t Setting draw_options to ''"
            draw_options = ""
            
        if x_min or x_max:
            setXMinMax(h, x_min, x_max)
            
        if i:
            if debug: print "\t\t Dawing ",draw_options[i]+"same"
            h.Draw(draw_options[i]+"same")    
        else:
            #h.Draw(draw_options)
            if not y_title == ROOTHelp.default:
                h.GetYaxis().SetTitle(y_title)
            if not x_title == ROOTHelp.default:
                h.GetXaxis().SetTitle(x_title)

            if len(hists) > 1:
                if debug: print "\t\t Drawing ",draw_options[i]+"PE"
                h.Draw(draw_options[i]+"PE")
            else:
                if debug: print "\t\t Drawing ",draw_options[i]
                h.SetFillColor(ROOT.kYellow)
                h.Draw(draw_options[i])

    #
    #  Redraw the points
    #
    if len(hists) > 1:
        hists[0].Draw(draw_options[0]+"PEsame")
    hists[0].Draw(draw_options[0]+"sameaxis")


def config_hists(hists, **kw):

    #
    #  Read the congif
    #
    #title             = kw.get('title',             ROOTHelp.default)
    y_min             = kw.get('min',               None)
    y_max             = kw.get('max',               ROOTHelp.default)
    x_min             = kw.get("x_min",             None)
    x_max             = kw.get("x_max",             None)
    z_min             = kw.get("z_min",             None)
    z_max             = kw.get("z_max",             None)
    log_y             = kw.get('logy',           False)

    fill_colors       = kw.get('fill_colors'  ,  [ROOT.kBlack,ROOT.kYellow,ROOT.kRed])
    fill_style        = kw.get('fill_style'  ,   [ROOTHelp.default,ROOTHelp.default])
    line_colors       = kw.get('line_colors'  ,  [ROOT.kBlack,ROOT.kBlack,ROOT.kRed])
    marker_styles     = kw.get('marker_styles',  [ROOTHelp.default,ROOTHelp.default,ROOTHelp.default])
    styles            = kw.get('styles'       ,  [ROOT.kSolid,ROOT.kSolid,ROOT.kSolid])
    widths            = kw.get('widths'       ,  [ROOTHelp.default, ROOTHelp.default,ROOTHelp.default])


    #
    #  Congigure the plots
    #
    for i, h in enumerate(hists):
        opt = dict() 
        opt['line_color']   = line_colors[i]
        opt['marker_color'] = line_colors[i]
        opt['line_style']   = styles[i]
        opt['line_width']   = widths[i]
        opt['fill_color']   = fill_colors[i]
        opt['fill_style']   = fill_style[i]
        opt['marker_style']   = marker_styles[i]
        plot_options = PlotOptions(**opt)
        plot_options.configure(h)


    #
    # Find the global min/max
    #
    set_min(hists, y_min, log_y=log_y)
    set_max(hists, y_max, log_y=log_y)


    #
    # Draw
    #
    for i, h in enumerate(hists):

        if x_min or x_max:
            setXMinMax(h, x_min, x_max)

        if z_min or z_max:
            setZMinMax(h, z_min, z_max)


    return {'hists':hists}
    


#
# Plot histsogram on top of each other 
#
def plot_hists( hists, name, **kw):
    """
    Function for formatting a list of histograms and plotting them on the same
    canvas, stacked. Returns a dictionary with the following keys:
    'canvas', 'stack', 'hists'.
    """

    #
    #  Read the congif
    #
    show_stats        = kw.get('show_stats',        False)
    debug             = kw.get('debug',             False)

    if debug: print "\t in plot_hists"

    #
    #  Config Hists
    #
    plot = config_hists(hists, **kw)

    #
    #  Build the canvas
    #
    c = makeCanvas(name,name, **kw)

    if debug: print "\t calling plot_hists_lists"
    plot_hist_list(hists, **kw)

    # arrange stats
    if show_stats:
        c.Update()
        arrange_stats(hists)
    c.Update()
    return {'canvas':c, 'hists':hists}


#
#
#
def plot_shared_axis(top_hists, bottom_hists,name='',split=0.5
                     ,**kw):

    # options with defaults
    axissep       = kw.get('axissep'       ,0.0)
    ndivs         = kw.get('ndivs'           ,[503,503])
    rLabel        = kw.get("rlabel", "Ratio")
    rMin          = kw.get("rMin", 0)
    rMax          = kw.get("rMax", 2)
    bayesRatio    = kw.get('bayesRatio',     False)

    canvas = makeCanvas(name, name, width=600, height=600)
    top_pad    = ROOT.TPad("pad1", "The pad 80% of the height",0,split,1,1,0)
    bottom_pad = ROOT.TPad("pad2", "The pad 20% of the height",0,0,1,split,0)
    top_pad.Draw()
    bottom_pad.Draw()

    top_pad.cd()
    top_pad.SetLogy(kw.get('logy', False))
    top_pad.SetTopMargin(canvas.GetTopMargin()*1.0/(1.0-split))
    top_pad.SetBottomMargin(0.5*axissep)
    top_pad.SetRightMargin(canvas.GetRightMargin())
    top_pad.SetLeftMargin(canvas.GetLeftMargin());
    top_pad.SetFillStyle(0) # transparent
    top_pad.SetBorderSize(0)
    plot_hist_list(top_hists, **kw)
    
    bottom_pad.cd()
    bottom_pad.SetTopMargin(2*axissep)
    bottom_pad.SetBottomMargin(canvas.GetBottomMargin()*1.0/split)
    bottom_pad.SetRightMargin(canvas.GetRightMargin())
    bottom_pad.SetLeftMargin(canvas.GetLeftMargin());
    bottom_pad.SetFillStyle(0) # transparent
    bottom_pad.SetBorderSize(0)
    ratio_axis = top_hists[0].Clone()
    ratio_axis.GetYaxis().SetTitle(rLabel)
    ratio_axis.GetXaxis().SetTitle(top_hists[0].GetXaxis().GetTitle())
    ratio_axis.GetYaxis().SetNdivisions(507)
    ratio_axis.GetYaxis().SetRangeUser(rMin, rMax)
    bottom_hists.GetYaxis().SetRangeUser(rMin, rMax)
    bottom_hists.GetYaxis().SetTitle(rLabel)
    

    if bayesRatio:
        ratio_axis.Draw("axis")
        bottom_hists.Draw("PE")
        ratio_axis.Draw("axis same")
    else:
        bottom_hists.Draw("PE")
        if ("sys_band" in kw) and (not kw["sys_band"] == None):  kw["sys_band"].Draw("E2 same")
        bottom_hists.Draw("PE same")
        oldSize = bottom_hists.GetMarkerSize()
        bottom_hists.SetMarkerSize(0)
        bottom_hists.DrawCopy("same e0")
        bottom_hists.SetMarkerSize(oldSize)
        bottom_hists.Draw("PE same")

    line = ROOT.TLine()
    line.DrawLine(top_hists[0].GetXaxis().GetXmin(), 1.0, top_hists[0].GetXaxis().GetXmax(), 1.0)

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

    return {'canvas':canvas,'ratio_axis':ratio_axis,"top_pad":top_pad,"bottom_pad":bottom_pad}


def moveDataPointsToBarycenter(ratio,histForXBarycenterCalc, debug=False):

    for p in range(ratio.GetN()):
        xValue = ROOT.Double(0)
        theEff = ROOT.Double(0)
        ratio.GetPoint(p,xValue,theEff)
        errHigh = ratio.GetErrorXhigh(p)
        errLow = ratio.GetErrorXlow(p)
        
        xMin = xValue - errLow
        xMax = xValue + errHigh

        if debug: print "Have bin",xMin,"-",xMax
        x_values  = []
        x_weights = []
        sumWeights = 0

        for iBinOrig in range(histForXBarycenterCalc.GetNbinsX()):        
            thisBinCenter = histForXBarycenterCalc.GetBinCenter(iBinOrig)
            thisNEvents   = float(histForXBarycenterCalc.GetBinContent(iBinOrig))
            if thisBinCenter > xMin and thisBinCenter < xMax:
                if debug: print "\tMatch ",thisBinCenter,thisNEvents
                x_values.append(thisBinCenter)
                x_weights.append(thisNEvents)
                sumWeights += thisNEvents
            

        #
        # Calculate weighted average
        #
        x_barycenter = 0

        if sumWeights:
            for ixV in range(len(x_values)):
                x_barycenter += x_values[ixV] * x_weights[ixV]/sumWeights
        else:
            x_barycenter = xValue

        ratio.SetPoint(p,x_barycenter,theEff)
        xShift = x_barycenter - xValue

        xErrLow = errLow+xShift
        xErrHigh = errHigh-xShift
            
        if debug: 
            print "OLD",xMin,"-",xMax            
            print "NEW",x_barycenter-xErrLow,"-",x_barycenter+xErrHigh
        ratio.SetPointError(p,xErrLow,xErrHigh,ratio.GetErrorYlow(p),ratio.GetErrorYhigh(p))

        if debug: print "barycenter is ",x_barycenter
        #print "Loop over original histograms save x_pos and weights"


    return



#
#
#
def makeBayesRatio(num, den, histForXBarycenterCalc=None):
    num.Sumw2()
    den.Sumw2()
    print "Doing Bayes Ratio"
    ratio = ROOT.TGraphAsymmErrors()#num.GetNbinsX())
    ratio.BayesDivide(num,den)
    ratio.SetName(num.GetName()+"_ratio")

    if histForXBarycenterCalc:
        #
        #  Calculate the correct barycenter of the x-bins
        #
        moveDataPointsToBarycenter(ratio,histForXBarycenterCalc)


    return ratio

#
#  Ratio of two hists, but return TGraphAsymmErrors like for baseDivide
#
def makeBayesLikeRatio(num, den, histForXBarycenterCalc=None):
    num.Sumw2()
    den.Sumw2()
    print "Doing Bayes-Like Ratio"
    hratio = num.Clone(num.GetName()+"_rhist")
    hratio.Divide(den)

    ratio = ROOT.TGraphAsymmErrors(hratio)#num.GetNbinsX())

    #
    # Test
    #
    for p in range(ratio.GetN()):
        xValue = ROOT.Double(0)
        theEff = ROOT.Double(0)
        ratio.GetPoint(p,xValue,theEff)
        #print xValue-ratio.GetErrorXlow(p),"-",xValue+ratio.GetErrorXhigh(p),":",theEff,"+",ratio.GetErrorYhigh(p),"-",ratio.GetErrorYlow(p)
        #print "\t",hratio.GetBinCenter(p+1),hratio.GetBinContent(p+1),hratio.GetBinError(p+1)
        #errLow = ratio.GetErrorXlow(p)


    if histForXBarycenterCalc:
        #
        #  Calculate the correct barycenter of the x-bins
        #
        moveDataPointsToBarycenter(ratio,histForXBarycenterCalc)


    return ratio



#
#
#
def makeRatio(num, den, histForXBarycenterCalc=None):
    num.Sumw2()
    den.Sumw2()
    
    ratio = num.Clone(num.GetName()+"_ratio")
    ratio.Divide(den)
        
    debugRatioErrors = False
    if debugRatioErrors:
        xAxis = hists[0].GetXaxis()
        nBins = xAxis.GetNbins()
        for i in range(nBins):
            print "Bin",i
            print "\tnum",num.GetBinContent(i+1),"+/-",num.GetBinError(i+1)
            print "\tden",den.GetBinContent(i+1),"+/-",den.GetBinError(i+1)
            print "\trat",ratio.GetBinContent(i+1),"+/-",ratio.GetBinError(i+1)



    if histForXBarycenterCalc:
        #
        #  Calculate the correct barycenter of the x-bins
        #
        moveDataPointsToBarycenter(ratio,histForXBarycenterCalc)


            
        


    return ratio


#
#
#
def makeStatRatio(num, den, **kw):
    print "Doing Stats Ratio"

    mcscale        = kw.get('mcscale',       1.0)

    ratio_axis = num.Clone(num.GetName()+"_ratioaxis")
    ratio      = num.Clone(num.GetName()+"_ratio")
    ratio.Divide(den)

    xAxis = num.GetXaxis()
    nBins = xAxis.GetNbins()
    var_band   = ROOT.TGraphAsymmErrors(nBins)
    var_band.SetFillColor(ROOT.kRed)
    
    for i in range(nBins):

        #
        # Only use the numerator uncertianty in the ratio
        #
        newError = 0
        if num.GetBinContent(i):
            newError = ratio.GetBinContent(i)/pow(num.GetBinContent(i),0.5)

        ratio.SetBinError(i,newError)

        #
        # Use the scaled denominator uncertianty in the band
        #

        var_band.SetPoint(i,xAxis.GetBinCenter(i+1),1.0)


        error   = den.GetBinError(i+1)
        content = den.GetBinContent(i+1)

        relError = 0
        if content:
            relError = error/content * pow(mcscale,0.5)

        var_band.SetPointError(i,
                               xAxis.GetBinCenter(i+1)-xAxis.GetBinLowEdge(i+1),xAxis.GetBinUpEdge(i+1)-xAxis.GetBinCenter(i+1),
                               relError,relError)
    
    return ratio, var_band

#
#
#
def makeDenErrorBand(den, **kw):
    print "Doing Den Error Band"

    xAxis = den.GetXaxis()
    nBins = xAxis.GetNbins()
    var_band   = ROOT.TGraphAsymmErrors(nBins)
    var_band.SetFillColor(ROOT.kRed)
    
    for i in range(nBins):

        var_band.SetPoint(i,xAxis.GetBinCenter(i+1),1.0)

        error   = den.GetBinError(i+1)
        content = den.GetBinContent(i+1)

        relError = 0
        if content:
            relError = error/content

        var_band.SetPointError(i,
                               xAxis.GetBinCenter(i+1)-xAxis.GetBinLowEdge(i+1),xAxis.GetBinUpEdge(i+1)-xAxis.GetBinCenter(i+1),
                               relError,relError)
    
    return var_band


#
# Plot histsogram on top of each other 
#
def plot_hists_wratio( hists, name, **kw):
    """
    Function for formatting a list of histograms and plotting them on the same
    canvas, stacked. Returns a dictionary with the following keys:
    'canvas', 'stack', 'hists'.
    """

    logy           = kw.get('logy',     False)
    logx           = kw.get('logx',     False)
    bayesRatio     = kw.get('bayesRatio',     False)
    statRatio      = kw.get('statRatio',     False)
    showDenError   = kw.get('showDenError',     False)
    x_title = hists[0].GetXaxis().GetTitle()

    #
    #  Config Hists
    #
    plot = config_hists(hists, **kw)

    #
    #  make ratio
    #
    #num  = plot['hists'][0]
    #num.Sumw2()
    #den  = plot['hists'][1]
    #den.Sumw2()

    if bayesRatio:  
        plot["ratio"] = makeBayesRatio(num = plot['hists'][0].Clone(), den = plot['hists'][1].Clone())
    elif showDenError: 
        plot["ratio"] = makeRatio(num = plot['hists'][0].Clone(),  den = plot['hists'][1].Clone())
        var_band = makeDenErrorBand(den = plot['hists'][1].Clone(), **kw) 
        kw["sys_band"] = var_band
        plot["sys_band"] = var_band        
    elif statRatio: 
        ratio, var_band = makeStatRatio(num = plot['hists'][0].Clone(), den = plot['hists'][1].Clone(), **kw) 
        plot['ratio']  = ratio
        kw["sys_band"] = var_band
        plot["sys_band"] = var_band
    else:
        plot["ratio"] = makeRatio(num = plot['hists'][0].Clone(),  den = plot['hists'][1].Clone())



    #
    # draw ratio
    #
    shared = plot_shared_axis(plot['hists'],  plot['ratio'], name+"_with_ratio", split=0.3, axissep=0.02, ndivs=[505,503], **kw)

    plot['canvas']     = shared['canvas']
    plot['canvas'].Update()
    plot['top_pad']=shared['top_pad']
    plot['bottom_pad']=shared['bottom_pad']
    plot['ratio_axis'] = shared['ratio_axis']
    
    return plot



#
# Depreicated
#
######################
######################
######################
######################


#
#  Stack Data and MC
#
def stack_with_data(data, mc, name, **kw):

    #
    # defaults
    #
    title             = kw.get('title',             ROOTHelp.default)
    ymin              = kw.get('min',               None)
    ymax              = kw.get('max',               ROOTHelp.default)
    plot_options      = kw.get('plot_options',      None)
    canvas_options    = kw.get('canvas_options',    ROOTHelp.default)
    draw_options      = kw.get('draw_options',      'hist')
    show_stats        = kw.get('show_stats',        False)
    max_factor        = kw.get('max_factor',        None)
    data_plot_options = kw.get('data_plot_options', None)
    x_min             = kw.get("x_min",None)
    x_max             = kw.get("x_max",None)

    plot = stack_hists(
        hists         = mc,
        name          = name,
        title         = title,
        min           = None,
        max           = None,
        plot_options  = plot_options,
        canvas_options= canvas_options,
        draw_options  = draw_options,
        show_stats    = show_stats,
        x_min         = x_min,
        x_max         = x_max,
        )

    # make the stack sum
    stacksum=mc[0].Clone("tmp")
    stacksum.Reset()
    for h in mc:
        stacksum.Add(h)
    
    # make stack plot
    stack = plot['stack']

    # set min/max
    if canvas_options.log_y:
        for b in range(1,data.GetNbinsX()+1):
            if data.GetBinContent(b) > 0.0:
                if ymin==None:
                    ymin=1e10
                ymin=min(ymin,0.1*data.GetBinContent(b))

    set_min([data, stack, stacksum], ymin, log_y=canvas_options.log_y)
    set_max([data, stack, stacksum], ymax, log_y=canvas_options.log_y)

    # draw data
    if data_plot_options:
        data_plot_options.configure(data)
    # data.GetXaxis().SetTitle("")
    # data.GetYaxis().SetTitle("")
    data.Draw('PE same')
    
    plot['canvas'].Update()    
    plot['data'] = data
    plot['sum'] = stacksum
    return plot


# 
#   Make a stack plot with a ratio below
# 
def stack_with_data_and_ratio(data, mc, name,**kw):
    canvas_options= kw.get('canvas_options', ROOTHelp.default)

    x_title = data.GetXaxis().GetTitle()

    #
    # make stack
    #
    stack = stack_with_data(data, mc, name,**kw)

    #
    # make ratio
    #
    data=stack['data']
    ratio=data.Clone(data.GetName()+"_ratio")
    ratio.Divide(stack['sum'])
    ratio_plot_options = PlotOptions()
    ratio_plot_options.configure(ratio)
    ratio.GetYaxis().SetTitle("Data/MC")
    ratio.GetXaxis().SetTitle(x_title)
    ratio.GetYaxis().SetNdivisions(507)

    #    set_min_max_ratio([ratio],2.0)
    rMin = kw.get("rMin",ROOTHelp.default)
    rMax = kw.get("rMax",ROOTHelp.default)
    set_min([ratio],  rMin, log_y=canvas_options.log_y)
    set_max([ratio],  rMax, log_y=canvas_options.log_y)
    stack['ratio']=ratio

    x_min = kw.get("x_min",None)
    x_max = kw.get("x_max",None)


    # draw ratio

    canvas_options.log_y=False
    ratio_canvas  = canvas_options.create(name+"_ratio")

    if x_min or x_max:
        setXMinMax(ratio,x_min,x_max)
        
    ratio.Draw("PE")
    line=ROOT.TLine()
    a=ratio.GetXaxis()
    if x_min or x_max:
        x_min, x_max = getXMinMax(ratio, x_min, x_max)
        line.DrawLine(x_min,1.0,x_max,1.0)
    else:
        line.DrawLine(a.GetXmin(),1.0,a.GetXmax(),1.0)
 
    shared = plot_shared_axis(stack['canvas'],ratio_canvas,name+"_with_ratio",split=0.3,axissep=0.04,ndivs=[505,503])
    #stack['top_canvas']=stack['canvas']
    #stack['bottom_canvas']=ratio_canvas
    stack['top_pad']=shared['top_pad']
    stack['bottom_pad']=shared['bottom_pad']
    stack['canvas']=shared['canvas']
    
    return stack



#
#  Stack Data and MC
#
def stack_no_data(mc, name, **kw):

    #
    # defaults
    #
    title             = kw.get('title',             ROOTHelp.default)
    ymin              = kw.get('min',               None)
    ymax              = kw.get('max',               ROOTHelp.default)
    plot_options      = kw.get('plot_options',      None)
    canvas_options    = kw.get('canvas_options',    ROOTHelp.default)
    draw_options      = kw.get('draw_options',      'hist')
    show_stats        = kw.get('show_stats',        False)
    max_factor        = kw.get('max_factor',        None)
    x_min             = kw.get("x_min",None)
    x_max             = kw.get("x_max",None)

    plot = stack_hists(
        hists         = mc,
        name          = name,
        title         = title,
        min           = None,
        max           = None,
        plot_options  = plot_options,
        canvas_options= canvas_options,
        draw_options  = draw_options,
        show_stats    = show_stats,
        x_min         = x_min,
        x_max         = x_max,
        )

    # make the stack sum
    stacksum=mc[0].Clone("tmp")
    stacksum.Reset()
    for h in mc:
        stacksum.Add(h)
    
    # make stack plot
    stack = plot['stack']

    # set min/max
    if canvas_options.log_y:
        for b in range(1,stacksum.GetNbinsX()+1):
            if stacksum.GetBinContent(b) > 0.0:
                if ymin==None:
                    ymin=1e10
                ymin=ymin#(ymin,0.1*stacksum.GetBinContent(b))

    set_min([stack, stacksum], ymin, log_y=canvas_options.log_y)
    set_max([stack, stacksum], ymax, log_y=canvas_options.log_y)

    plot['canvas'].Update()    
    plot['sum'] = stacksum
    return plot


#
# Plot histsogram on top of each other 
#
def plot_hists_wratio_errorband( hists, histErros, name, **kw):
    """
    Function for formatting a list of histograms and plotting them on the same
    canvas, stacked. Returns a dictionary with the following keys:
    'canvas', 'stack', 'hists'.
    """

    #
    # Calc bands
    #
    varUp   = []
    varDown = []

    for sysHist in histErros:
        thisUpVar, thisDownVar = calcBinByBinDiffs(hists[1],sysHist)

        if varUp:
            varUp   = addInQuad(thisUpVar,   varUp)
        else:
            varUp = thisUpVar


        if varDown:
            varDown = addInQuad(thisDownVar, varDown)
        else:
            varDown = thisDownVar

    #
    # Build Band
    #
    xAxis = hists[0].GetXaxis()
    nBins = xAxis.GetNbins()
    var_band   = ROOT.TGraphAsymmErrors(nBins)
    var_band.SetFillColor(ROOT.kRed)
    for i in range(nBins):
        var_band.SetPoint(i,xAxis.GetBinCenter(i+1),1.0)
        
        up   = varUp  [i]
        down = varDown[i]
        nom  = hists[1].GetBinContent(i+1)
        
        if nom:
            errUp   = float(up)/nom
            errDown = float(down)/nom
        else:
            errUp   = 0
            errDown = 0

        var_band.SetPointError(i,
                               xAxis.GetBinCenter(i+1)-xAxis.GetBinLowEdge(i+1),xAxis.GetBinUpEdge(i+1)-xAxis.GetBinCenter(i+1),
                               errUp,errDown)


    #
    # Make ratio
    #
    kw["sys_band"] = var_band
    res = plot_hists_wratio(hists, name, **kw)
    
    return res


#
# Plot histsogram on top of each other with ratio
#
def plot_hists_wratio_legend( hists, name, **kw):


    plot = plot_hists_wratio(hists,name,**kw)

    plot['leg'] = make_legend(hists = hists,
                              labels = kw["labels"],
                              width = 0.3,
                              height= 0.05,
                              x2 = 0.9,
                              y2=0.9,
                              draw_options = kw["draw_options"],
                              )


    plot['top_pad'].cd()
    plot['leg'].Draw()
    return plot
