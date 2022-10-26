# ----------------------------------------------------------------------------
# Data Class used for a component of the background modeling
#  eg: W+jet, Drell Yan, WW, ect
#
# Can deal with the MC corrections needed for W+jet modeling
#
from ROOT import TFile#,TH1F,TDirectory,gROOT
import os

# ----------------------------------------------------------------------------
class Process:
    # ----------------------------------------------------------------------------
    # Corrections are only needed for the W+Jet modeling.
    #  This deals with the MC subtraction in the L + D region
    def __init__(self,Name,fileName,dirName,color,corrections=None,scale=1.0,
                 regionCondition=None, disable=False, debug=False):
        print( "Processs::fileName is ",fileName)
        self.debug=debug
        self.name = Name
        self.fileName = fileName
        self.dirName = dirName
        self.color = color
        self.dir = 0 # Set In Init
        self.file = 0 # Set In Init
        self.makeCorrections = False
        self.scale = scale
        self.openDir = 0
        self.regionCondition=regionCondition
        self.disable=disable
        
        # Corrections are only needed for the W+Jet modeling.
        #  This deals with the MC subtraction in the L + D region
        # Dictionary of histograms used to correct the main dist
        if corrections:
            self.makeCorrections = True
            self.corrections = {}
            
            for thisCor in corrections:
                thisDir = corrections[thisCor][0]
                thisFile = corrections[thisCor][1]
                self.corrections[thisCor] = Process(thisCor,thisFile,thisDir,color)

                
        return

    # ----------------------------------------------------------------------------
    # Read the files and get the directory
    def Init(self):
        # First read the Data File

        print( "Process::Init",self.fileName,os.path.isfile(self.fileName))
        rdnm = "Reading %s (%s) " %(self.name, '/'.join(self.fileName.split('/')[-2:]))
        rdnm = rdnm.ljust(60)
        if not os.path.isfile(self.fileName) and not os.path.islink(self.fileName):
            print( rdnm + " [ \033[1;31mFailed\033[0m  ]")
            self.file = None
        else :
            print( rdnm + " [ \033[1;32mSuccess\033[0m ]" )
            self.file = TFile(self.fileName,"READ")

        if self.makeCorrections:
            for thisCor in self.corrections:
                self.corrections[thisCor].Init()

        return


    # ----------------------------------------------------------------------------
    # Read the files and get the directory
    def Finalize(self):
        # First read the Data File
        print( "Closing ",self.fileName)
        self.file.Close()
        print( "Closed")
        
        if self.makeCorrections:
            for thisCor in self.corrections:
                self.corrections[thisCor].Finalize()

        return    
    
    # ----------------------------------------------------------------------------
    def printInfo(self):

        print( " -------------------------------------------------")
        print( "Process", self.name)
        print( "FileName",self.fileName)
        print( "DirName",self.dirName)
        print( " -------------------------------------------------")


    # ----------------------------------------------------------------------------
    # Reset directory
    def resetDir(self):
        
        if self.openDir:
            if self.openDir != self.dirName:
                if self.dir:
                    #print( "Closing dir",self.dir)
                    self.dir.Close()
        return

    # ----------------------------------------------------------------------------
    # Set the directory
    def updateTopDir(self,subDir=""):

        
        self.openDir = subDir.lstrip("/")
        self.dirName = self.openDir

        if subDir=="":# and self.dirName == '':
            self.dir = self.file
        else :
            self.dir = self.file.Get(self.openDir)

        if not self.dir:
            if not self.name == "WJet" and self.debug :
                print( "Cant read Dir",self.openDir)
                self.printInfo()
            #self.file.ls()
            
            
        if self.makeCorrections:
            for thisCor in self.corrections:
                self.corrections[thisCor].updateDir(subDir)

        return

    # ----------------------------------------------------------------------------
    # Set the directory
    def flushDirs(self):
        self.file.Close()
        self.file = TFile(self.fileName,"READ")
        return        

    # ----------------------------------------------------------------------------
    # Set the directory
    def updateDir(self,subDir=""):

        
        if self.dirName == '' :
            self.openDir = subDir.lstrip("/")
        else :
            self.openDir = os.path.join(self.dirName,subDir.lstrip("/"))

        if subDir=="" and self.dirName != '':
            self.openDir=self.dirName

        if subDir=="":
            self.dir = self.file
        else :
            #self.file.Close()
            #self.file = TFile(self.fileName,"READ")
            if self.file is None :
                self.dir = None
            else :
                self.dir = self.file.Get(self.openDir)

        if not self.dir:
            if not self.name == "WJet" and self.debug :
                print( "Cant read Dir",self.openDir)
                self.printInfo()
            #self.file.ls()
            
            
        if self.makeCorrections:
            for thisCor in self.corrections:
                self.corrections[thisCor].updateDir(subDir)

        return

    # ----------------------------------------------------------------------------
    # Set the directory
    def flushDirs(self):
        self.file.Close()
        self.file = TFile(self.fileName,"READ")
        return        

    # ----------------------------------------------------------------------------
    # Set the directory
    def updateDir(self,subDir=""):

        
        if self.dirName == '' :
            self.openDir = subDir.lstrip("/")
        else :
            self.openDir = os.path.join(self.dirName,subDir.lstrip("/"))

        if subDir=="" and self.dirName != '':
            self.openDir=self.dirName

        if subDir=="":
            self.dir = self.file
        else :
            #self.file.Close()
            #self.file = TFile(self.fileName,"READ")
            if self.file is None :
                self.dir = None
            else :
                self.dir = self.file.Get(self.openDir)

        if not self.dir:
            if not self.name == "WJet" and self.debug :
                print( "Cant read Dir",self.openDir)
                self.printInfo()
            #print( "Do NOT HAVE DIR",subDir)
            #self.file.ls()
            
            
        if self.makeCorrections:
            for thisCor in self.corrections:
                self.corrections[thisCor].updateDir(subDir)

        return

    # ----------------------------------------------------------------------------
    # Return the input histogram,
    #   (corrected for the correction histograms, if needed)  
    def getHist(self,name):
        if not self.dir:
            return None

        if self.disable :
            return None

        totalHist = self.dir.Get(name)

        if not totalHist:
            print( "Couldn't get hist ",name,"from ",self.fileName)
            return None
            
        if self.makeCorrections:
            for thisCor in self.corrections:
                totalHist.Add(self.corrections[thisCor].getHist(name),-1)

        if not self.scale == 1.0:
            totalHist = totalHist.Clone()
            #print( "Scaling hist to:",self.scale)

            totalHist.Scale(float(self.scale))

        #if totalHist:
        #    totalHist.Sumw2()
        return totalHist



