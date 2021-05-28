import optparse
import shlex
import sys
import subprocess
import math
ON_POSIX = 'posix' in sys.builtin_module_names
from commandLineHelpers import babySit



parser = optparse.OptionParser()
parser.add_option('-e',            action="store_true", dest="execute",        default=False, help="Execute commands. Default is to just print them")
parser.add_option('-i', '--inputPath',help="Run in loop mode")
parser.add_option('-x', '--xrootdPrefix', default="root://cmsxrootd.fnal.gov/", help="")
parser.add_option('--xrootdCopyPrefix', default="root://cmseos.fnal.gov/", help="")
parser.add_option('-m', '--maxFilesPerHadd', default=200, help="Run in loop mode")
o, a = parser.parse_args()




execute = o.execute

eosls='eos root://cmseos.fnal.gov ls '
command = eosls+o.inputPath

stdout = None
results = subprocess.check_output(shlex.split(command))
subDirs = results.split()

# Yield successive n-sized 
# chunks from l. 
def divide_chunks(l, n): 
      
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

def getHaddCommands(filesToHadd,name):

    haddCMDs = []
    outputs = []

    filesPerJob = list(divide_chunks(filesToHadd, o.maxFilesPerHadd))
    nHaddJobs = int(len(filesPerJob))


    for iJob in range(nHaddJobs):
        haddOutput = "haddOutput_"+name+"_job"+str(iJob)+".root"
        outputs.append(haddOutput)

        cmd = "hadd "+haddOutput+" "
        for f in filesPerJob[iJob]:
            cmd += " "+f
        haddCMDs.append(cmd)

    return haddCMDs, outputs

def getSubDirOutput(inputDir, subDir):
    

    command = eosls+inputDir+"/"+subDir
    results = subprocess.check_output(shlex.split(command))
    fileNames = results.split()
    
    filesToHadd = []
    for f in fileNames:
        filesToHadd.append(o.xrootdPrefix+inputDir+"/"+subDir+"/"+f)

    haddCMDs, outputs = getHaddCommands(filesToHadd,"subDir"+s)

    #print "Will output",outputs
    return haddCMDs, outputs


#
# Hadd all the subdirs
#
haddCommands = []
outputFiles = {}
for s in subDirs:
    
    sCMDs, sOutputs  = getSubDirOutput(o.inputPath, s)
    haddCommands    += sCMDs
    outputFiles[s]   = sOutputs

babySit(haddCommands, execute)


#
#  copy the combined files to eos
#
cpCommands = []
for s in outputFiles:
    for f in outputFiles[s]:
        cmd = "xrdcp "+f+" "+o.xrootdCopyPrefix+o.inputPath+"/"+s+"/"+f
        cpCommands.append(cmd)

babySit(cpCommands, execute)


#
#  Hadd the combined files
#
fileList = []
for s in outputFiles:
    for f in outputFiles[s]:
        fileList.append(o.xrootdPrefix + o.inputPath +"/"+s+"/"+f)

haddCMDsCombined, outputsCombined = getHaddCommands(fileList,"All")

babySit(haddCMDsCombined, execute)


#
#  copy the combined file to eos
#
cpCommands = []
for f in outputsCombined:
    cmd = "xrdcp "+f+" "+o.xrootdCopyPrefix+o.inputPath+"/"+f
    cpCommands.append(cmd)

babySit(cpCommands, execute)
