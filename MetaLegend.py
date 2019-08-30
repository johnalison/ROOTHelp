import ROOTHelp
import ROOT

#
# MetaLegend Class
#
class MetaLegend(ROOT.TLegend):
    """
    A better TLegend class that increases in height as you call AddEntry.
    """ 
#______________________________________________________________________________
    def __init__(self, width=0.15, height=0.05,
            x1=None, y1=None,
            x2=None, y2=None,
            border=0, fill_color=0, fill_style=0):
#        assert (x1 == y1 == None) or (x2 == y2 == None)
#        assert (x1 != None and y1 != None) or (x2 != None and y2 != None)

        if x1 == x2 == None:
            x2 = 0.93
            x1 = x2 - width
        elif x1 == None:
            x1 = x2 - width
        elif x2 == None:
            x2 = x1 + width

        if y1 == y2 == None:
            y2 = 0.93
            y1 = y2 - width
        elif y1 == None:
            y1 = y2 - width
        elif y2 == None:
            y2 = y1 + width

        ROOT.TLegend.__init__(self, x1, y1, x2, y2)
        self.SetBorderSize(border)
        self.SetFillColor(fill_color)
        self.SetFillStyle(fill_style)
        self.width = width
        self.height = height # per entry
        self._nentries = 0
        self._has_drawn = False

    def AddEntry(self, obj, label='', option='P'):
        self._nentries += 1
        self.resize()
        ROOT.TLegend.AddEntry(self, obj, label, option)

    def Draw(self):
        self.resize()
        ROOT.TLegend.Draw(self)
        self._has_drawn = True

    def resize(self):
        if self._has_drawn:
            y2 = self.GetY2NDC()
            self.SetY1NDC(y2 - (self.height*self._nentries) - 0.01)
        else:
            y2 = self.GetY2()
            self.SetY1(y2 - (self.height*self._nentries) - 0.01)
