#from ROOT import 
import ROOT
import sys
ROOT.gROOT.SetMacroPath(ROOT.gROOT.GetMacroPath()+(":").join(sys.path))
ROOT.gROOT.LoadMacro("FancyROOTStyle.C")
ROOT.SetFancyStyle()

