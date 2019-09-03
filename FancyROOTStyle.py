#from ROOT import 
import ROOT
import sys
#print "was:",ROOT.gROOT.GetMacroPath()
#print "Adding: ",(":").join(sys.path)
ROOT.gROOT.SetMacroPath(ROOT.gROOT.GetMacroPath()+":"+(":").join(sys.path))
ROOT.gROOT.LoadMacro("FancyROOTStyle.C")
ROOT.SetFancyStyle()

