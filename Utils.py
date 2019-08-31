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
    h = infile.Get(histName)
    
    if not h:
        infile.ls()
        print
        print "ERROR"
        print "Cannot find",histName
        print
        sys.exit(-1)

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
        log_x  = kw.get('log_x',         0)
        log_y  = kw.get('log_y',         0)
        log_z  = kw.get('log_z',         0)
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
