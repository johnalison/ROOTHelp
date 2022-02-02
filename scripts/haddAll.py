import optparse
import shlex
import sys, os
import subprocess
import math
ON_POSIX = 'posix' in sys.builtin_module_names
from commandLineHelpers import babySit, makeCondorFile, execute, makeDAGFile, makeTARBALL
#from commandLineHelpers import *



parser = optparse.OptionParser()
parser.add_option('-e',            action="store_true", dest="execute",        default=False, help="Execute commands. Default is to just print them")
parser.add_option('-i', '--inputPath',help="Run in loop mode")
parser.add_option('-x', '--xrootdPrefix', default="root://cmseos.fnal.gov/", help="")
parser.add_option('--xrootdCopyPrefix', default="root://cmseos.fnal.gov/", help="")
parser.add_option('-m', '--maxFilesPerHadd', default=200, help="Run in loop mode")
parser.add_option('--makeTarball',  action="store_true",      help="make Output file lists")
parser.add_option('-c', '--condor', action="store_true")
o, a = parser.parse_args()


# Yield successive n-sized 
# chunks from l. 
def divide_chunks(l, n): 
      
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

def getHaddCommands(filesToHadd,name,inputDir):

    haddCMDs = []
    outputs = []

    filesPerJob = list(divide_chunks(filesToHadd, int(o.maxFilesPerHadd)))
    nHaddJobs = int(len(filesPerJob))


    for iJob in range(nHaddJobs):
        haddOutput = o.xrootdPrefix+inputDir+"/haddOutput_"+name+"_job"+str(iJob)+".root"
        outputs.append(haddOutput)

        cmd = "hadd -f "+haddOutput+" "
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

    haddCMDs, outputs = getHaddCommands(filesToHadd,"subDir"+s, inputDir)

    #print "Will output",outputs
    return haddCMDs, outputs



if o.makeTarball:
    makeTARBALL(o.execute)



else:
    #execute = o.execute
    
    eosls='eos root://cmseos.fnal.gov ls '
    command = eosls+o.inputPath
    
    stdout = None
    results = subprocess.check_output(shlex.split(command))
    subDirs = results.split()
    print "subDirs",subDirs
    


    if o.condor:
        dag_config = []
        condor_jobs = []
        jobName = "haddEOS_"
        outputDir = "ROOTHelp/condorLogs/"
        if not os.path.exists(outputDir):
            print "making", outputDir
            os.mkdir(outputDir)
    
    #
    # Hadd all the subdirs
    #
    haddCommands = []
    outputFiles = {}
    for s in subDirs:
        
        sCMDs, sOutputs  = getSubDirOutput(o.inputPath, s)
        haddCommands    += sCMDs
        outputFiles[s]   = sOutputs
    
    if o.condor:
        for icmd, cmd in enumerate(haddCommands):
            condor_jobs.append(makeCondorFile(cmd, "None", str(icmd), outputDir=outputDir, filePrefix=jobName+"subHadd_"))
    
    
        dag_config.append(condor_jobs)
    
    else:
        babySit(haddCommands, o.execute)
    
    
    
    
    
    ###
    ###  copy the combined files to eos
    ###
    ##cpCommands = []
    ##for s in outputFiles:
    ##    for f in outputFiles[s]:
    ##        cmd = "xrdcp "+f+" "+o.xrootdCopyPrefix+o.inputPath+"/"+f
    ##        cpCommands.append(cmd)
    ##
    ##babySit(cpCommands, execute)
    
    
    #
    #  Hadd the combined files
    #
    condor_jobs = []
    fileList = []
    for s in outputFiles:
        for f in outputFiles[s]:
            #fileList.append(o.xrootdPrefix + o.inputPath +"/"+f)
            fileList.append(f)
    
    haddCMDsCombined, outputsCombined = getHaddCommands(fileList,"All",o.inputPath)
    
    
    if o.condor:
        for icmd, cmd in enumerate(haddCMDsCombined):
            condor_jobs.append(makeCondorFile(cmd, "None", str(icmd), outputDir=outputDir, filePrefix=jobName+"hadd_"))        
        
        dag_config.append(condor_jobs)
    else:
        babySit(haddCMDsCombined, o.execute)
    
    
    if o.condor:
        execute("rm "+outputDir+jobName+"All.dag",  o.execute)
        execute("rm "+outputDir+jobName+"All.dag.*", o.execute)
    
        dag_file = makeDAGFile(jobName+"All.dag",dag_config, outputDir=outputDir)
        cmd = "condor_submit_dag "+dag_file
        execute(cmd, o.execute)
    
    
    ##
    ##  copy the combined file to eos
    ##
    #cpCommands = []
    #for f in outputsCombined:
    #    cmd = "xrdcp "+f+" "+o.xrootdCopyPrefix+o.inputPath+"/"+f
    #    cpCommands.append(cmd)
    #
    #babySit(cpCommands, execute)
    #
    #
    ##
    ##  Remove the local files
    ##
    #cpCommands = []
    #for f in outputsCombined:
    #    cmd = "rm -rf "+f
    #    cpCommands.append(cmd)
    #
    #babySit(cpCommands, execute)
