#
# CanvasOptions Class
#
import ROOT

import ROOTCoreOLD

class CanvasOptions:
    """Class for configuring canvas properties.""" 
    
    #
    #  Set Defaults
    #
    def __init__(self, **kw):
        kw.setdefault('width',         800)
        kw.setdefault('height',        600)
        kw.setdefault('log_x',         0)
        kw.setdefault('log_y',         0)
        kw.setdefault('log_z',         0)
        kw.setdefault('grid_x',        0)
        kw.setdefault('grid_y',        0)
        kw.setdefault('tick_x',        1)
        kw.setdefault('tick_y',        1)
        kw.setdefault('left_margin',   ROOTCoreOLD.default)
        kw.setdefault('right_margin',  ROOTCoreOLD.default)
        kw.setdefault('top_margin',    ROOTCoreOLD.default)
        kw.setdefault('bottom_margin', ROOTCoreOLD.default)
        for k,v in kw.iteritems():
            setattr(self, k, v)


    #
    #  Config canvas
    #
    def configure(self, c):
        c.UseCurrentStyle()
        c.SetLogx(self.log_x)
        c.SetLogy(self.log_y)
        c.SetLogz(self.log_z)
        if not self.grid_x is ROOTCoreOLD.default:
            c.SetGridx(self.grid_x)
        if not self.grid_y is ROOTCoreOLD.default:
            c.SetGridy(self.grid_y)
        if not self.tick_x is ROOTCoreOLD.default:
            c.SetTickx(self.tick_x)
        if not self.tick_y is ROOTCoreOLD.default:
            c.SetTicky(self.tick_y)
        if not self.left_margin is ROOTCoreOLD.default:
            c.SetLeftMargin(self.left_margin)
        if not self.right_margin is ROOTCoreOLD.default:
            c.SetRightMargin(self.right_margin)
        if not self.top_margin is ROOTCoreOLD.default:
            c.SetTopMargin(self.top_margin)
        if not self.bottom_margin is ROOTCoreOLD.default:
            c.SetBottomMargin(self.bottom_margin)
        c.SetBorderSize(0)
        c.SetBorderMode(0)
        c.Update()
        
    #
    #  Create the specifed canvas
    # 
    def create(self, name, title=ROOTCoreOLD.default):
        if title is ROOTCoreOLD.default:
            title = name
        c = ROOT.TCanvas(name, name, 200, 10, self.width, self.height)
        self.configure(c)
        return c




