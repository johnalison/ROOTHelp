#
# CanvasOptions Class
#
import ROOT

import ROOTHelp

#class PlotOptions(object):
class PlotOptions:
    """Class for configuring histogram/graph properties.""" 

    #
    #  Set Defaults
    #
    def __init__(self, **kw):
        kw.setdefault('line_color', ROOTHelp.default)
        kw.setdefault('line_width', ROOTHelp.default)
        kw.setdefault('line_style', ROOTHelp.default)
        kw.setdefault('fill_color', ROOTHelp.default)
        kw.setdefault('fill_style', ROOTHelp.default)
        kw.setdefault('marker_style', ROOTHelp.default)
        kw.setdefault('marker_color', ROOTHelp.default)
        kw.setdefault('marker_size', ROOTHelp.default)
        kw.setdefault('scale', 0) # zero means don't normalize
        kw.setdefault('norm', 0) # zero means don't normalize
        for k,v in kw.iteritems():
            setattr(self, k, v)

    #
    #  Config the plot
    #
    def configure(self, h):
        h.UseCurrentStyle()
        if not self.line_color is ROOTHelp.default:
            h.SetLineColor(self.line_color)
        if not self.line_width is ROOTHelp.default:
            h.SetLineWidth(self.line_width)
        if not self.line_style is ROOTHelp.default:
            h.SetLineStyle(self.line_style)
        if not self.fill_color is ROOTHelp.default:
            h.SetFillColor(self.fill_color)
        if not self.fill_style is ROOTHelp.default:
            h.SetFillStyle(self.fill_style)
        if not self.marker_style is ROOTHelp.default:
            h.SetMarkerStyle(self.marker_style)
        if not self.marker_color is ROOTHelp.default:
            h.SetMarkerColor(self.marker_color)
        if not self.marker_size is ROOTHelp.default:
            h.SetMarkerSize(self.marker_size)
        if isinstance(h, ROOT.TH1) or isinstance(h, ROOT.TH2):
            if self.scale:
                if not h.GetSumw2N(): h.Sumw2()
                h.Scale(self.scale)
            elif self.norm:
                normalize_hist(h, self.norm)
