from ROOT import TFile,gROOT
import ROOT

import os

from ProcessManager import ProcessManager


# -----------------------------------------------------------------
def MakeModeling(baseDir,dirName,outputFileName="",key="",pdfDir=None,mcscale=1.0,histName="hist.root",interactive=False):

    #
    # Create the Histogram manager which will do the stacking with the data
    #
    thisJob = ProcessManager()

    #
    # Add the Process
    #
    thisJob.  AddProcess("file1",
                         file = baseDir+"/"+histName,                         
                         dir = dirName,
                         color = ROOT.kYellow,
                         scale=mcscale)    


    if not interactive:
        outputFile = TFile(outputFileName,"RECREATE")
        thisJob.makeStacks(outputFile,key)
    
    return thisJob
        

# -----------------------------------------------------------------
if __name__ == "__main__":
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('', '--base-dir', default=None, dest='base_dir',help='path to base directory containing all ntuples')
    p.add_option('', '--output', default='test_out.root', dest='output',help='output root file name')
    p.add_option('', '--dirLL', default=None, dest='dirLL',help='ll directories')
    p.add_option('', '--mcscale', default=1.0, type='float', dest='mcscale',help='Scale factor to apply to monte carlo')
                     
    (options, args) = p.parse_args()

    MakeModeling(baseDir=options.base_dir,
                 dirName = options.dirLL,
                 outputFileName = options.output,
                 mcscale = options.mcscale
                 )

