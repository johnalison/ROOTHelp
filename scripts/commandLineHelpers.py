import time
import textwrap
import os, re
import sys
import subprocess
import shlex
import optparse
import numpy as np
from threading import Thread
try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty  # python 2.x

ON_POSIX = 'posix' in sys.builtin_module_names

def getCMSSW():
    return os.getenv('CMSSW_VERSION')

def getUSER():
    return os.getenv('USER')


DEFAULTCMSSW   = getCMSSW()
USER           = getUSER()

DEFAULTCMSSW   = getCMSSW()
USER           = getUSER()
try:
    DEFAULTTARBALL = "root://cmseos.fnal.gov//store/user/"+USER+"/condor/"+DEFAULTCMSSW+".tgz"
except:
    DEFAULTTARBALL = None


def enqueue_output(out, queue, logFile):
    for line in iter(out.readline, b''):
        if logFile: logFile.write(line)
        queue.put(line)
        if queue.qsize()>1: queue.get_nowait()

        
    out.close()


def execute(command, execute=True): # use to run command like a normal line of bash
    print command
    if execute: os.system(command)


def watch(command, execute=True, stdout=None, doPrint=True, logFile=None): # use to run a command and keep track of the thread, ie to run something when it is done
    if doPrint: print command
    if execute:
        p = subprocess.Popen(shlex.split(command), stdout=stdout, universal_newlines=(True if stdout else False), bufsize=1, close_fds=ON_POSIX)
        if stdout:
            q = Queue()
            t = Thread(target=enqueue_output, args=(p.stdout, q, logFile))
            t.daemon = True
            t.start()
            return (command, p, q)
        return (command, p)


# \033[<L>;<C>H # Move the cursor to line L, column C
# \033[<N>A     # Move the cursor up N lines
# \033[<N>B     # Move the cursor down N lines
# \033[<N>C     # Move the cursor forward N columns
# \033[<N>D     # Move the cursor backward N columns
# \033[2J       # Clear the screen, move to (0,0)
# \033[K        # Erase to end of line
def placeCursor(L,C):
    print '\033['+str(L)+';'+str(C)+'H',
def moveCursorUp(N=''):
    print '\r\033['+str(N)+'A',
def moveCursorDown(N=''):
    print '\r\033['+str(N)+'B',


def babySit(commands, execute, maxAttempts=1, maxJobs=3, logFiles=None):
    attempts={}
    nCommands = len(commands)
    jobs=[]
    logs=[]
    outs=[]
    waiting=[]
    waitinglogs=[]
    done=[]
    for c in range(nCommands):
        command = commands[c]
        attempts[command] = 1
        done.append(0)
        print "# ",c
        if len(jobs)<maxJobs:
            logs.append(open(logFiles[c],"w") if (logFiles and execute) else None)
            jobs.append(watch(command, execute, stdout=subprocess.PIPE,logFile=logs[-1]))
                
            outs.append("LAUNCHING")
        else:
            print command
            waiting.append(command)
            waitinglogs.append(open(logFiles[c],"w") if (logFiles and execute) else None)
            outs.append("IN QUEUE")

    if not execute: return
    
    nDone = 0
    while nDone < nCommands:
        time.sleep(0.2)
        failure=False
        nJobs = len(jobs)
        nDone = sum(done)
        nToLaunch = 0
        for j in range(nJobs):
            code = jobs[j][1].poll()
            #if code == None: # job is still running
            #    done=False
            if code==0: # job finished
                if done[j]==0: nToLaunch += 1
                done[j] = 1
            elif code: # job crashed, try resubmitting
                moveCursorDown(1000)
                outs[j] = "CRASHED AT <"+outs[j]+">"
                crash = ["",
                         "# "+"-"*200,
                         "# "+jobs[j][0],
                         "# "+outs[j],
                         "# Exited with: "+str(code),
                         "# Attempt: "+str(attempts[jobs[j][0]]),
                         "# "+"-"*200,
                         ""]
                time.sleep(1)
                for line in crash: print line
                if attempts[jobs[j][0]] > maxAttempts: 
                    if done[j]==0: nToLaunch += 1
                    done[j] = 1
                    continue # don't resubmit, already tried maxAttempts times
                attempts[jobs[j][0]] += 1
                time.sleep(10)
                #done=False
                jobs[j] = watch(jobs[j][0], execute, stdout=subprocess.PIPE, logFile=logs[j])

        nWaiting = len(waiting)
        for w in range(nJobs, nJobs+min(nToLaunch, nWaiting)):
            jobs.append(watch(waiting.pop(0), execute, stdout=subprocess.PIPE, doPrint=False,logFile=waitinglogs.pop(0)))
            outs[w] = "LAUNCHING"

        nJobs = len(jobs)
        nLines = 1+nCommands#3
        print "\033[K"
        for c in range(nCommands):
            if c < nJobs:
                try:          
                    outs[c]=jobs[c][2].get_nowait().replace('\n','').replace('\r','')
                except Empty: 
                    outs[c]=outs[c]
            print "\033[K# "+str(c).rjust(2)+" >>",outs[c]

        moveCursorUp(nLines)
    moveCursorDown(1000)
            

def waitForJobs(jobs,failedJobs):
    for job in jobs:
        code = job[1].wait()
        if code: failedJobs.append(job)
    return failedJobs

def relaunchJobs(jobs, execute=True):
    print "# "+"-"*200
    print "# RELAUNCHING JOBS"
    newJobs = []
    for job in jobs: newJobs.append(watch(job[0], execute))
    return newJobs

def mkdir(directory, execute=True):
    if not os.path.isdir(directory):
        print "mkdir",directory
        if execute: os.mkdir(directory)
    else:
        print "#",directory,"already exists"

def rmdir(directory, execute=True):
    if not execute: 
        print "rm -r",directory
        return
    if "*" in directory:
        execute("rm -r "+directory)
        return
    if os.path.isdir(directory):
        execute("rm -r "+directory)
    elif os.path.exists(directory):
        execute("rm "+directory)
    else:
        print "#",directory,"does not exist"


def makeTARBALL(doRun, debug=False):
    base=os.getenv('CMSSW_BASE')
    base=base.replace(getCMSSW(),"")

    TARBALL   = "root://cmseos.fnal.gov//store/user/"+getUSER()+"/condor/"+getCMSSW()+".tgz"

    if os.path.exists(base+getCMSSW()+".tgz"):
        print "TARBALL already exists, skip making it"
        return
    cmd  = 'tar -C '+base+' -zcf '+base+getCMSSW()+'.tgz '+getCMSSW()
    if debug:
        cmd  = 'tar -C '+base+' -zcvf '+base+getCMSSW()+'.tgz '+getCMSSW()
    cmd += ' --exclude="*.pdf" --exclude="*.jdl" --exclude="*.stdout" --exclude="*.stderr" --exclude="*.log"  --exclude="log_*" --exclude="*.stdout" --exclude="*.stderr"'
    cmd += ' --exclude=".git" --exclude="PlotTools" --exclude="madgraph" --exclude="*.pkl" --exclude="*.root"  --exclude="*.h5"   --exclude=data*hemis*.tgz  --exclude=plotsWith*  --exclude=plotsNoFvT*  '
    cmd += " --exclude=Signal*hemis*.tgz "
    cmd += ' --exclude="closureTests/OLD" '
    #cmd += ' --exclude="closureTests/nominal" '                                                                                                                                                            
    cmd += ' --exclude=plotsRW* '
    cmd += ' --exclude="tmp" --exclude="combine" --exclude="genproductions" --exclude-vcs --exclude-caches-all'
    execute(cmd, doRun)
    cmd  = 'ls '+base+' -alh'
    execute(cmd, doRun)
    cmd = "xrdfs root://cmseos.fnal.gov/ mkdir /store/user/"+getUSER()+"/condor"
    execute(cmd, doRun)
    cmd = "xrdcp -f "+base+getCMSSW()+".tgz "+TARBALL
    execute(cmd, doRun)



class jdl:
    def __init__(self, cmd=None, CMSSW=DEFAULTCMSSW, EOSOUTDIR="None", TARBALL=DEFAULTTARBALL, fileName=None, logPath = './', logName = ''):
        self.randName = str(np.random.uniform())[2:]
        self.humanReadableName = ''
        self.fileName = fileName if fileName else self.randName+".jdl"
        if cmd:
            fileList = [c for c in cmd.split() if '.txt' in c]
            if fileList:
                self.humanReadableName = fileList[0].split('/')[-1].replace('.txt','')
                if not fileName: self.fileName = '%s_%s.jdl'%(self.humanReadableName, self.randName)
            if 'hadd' in cmd:
                self.humanReadableName = cmd.replace('-f','').split()[1].split('/')[-2]
                if not fileName: self.fileName = 'hadd_%s_%s.jdl'%(self.humanReadableName, self.randName)
        print('#', self.fileName, cmd)

        if self.humanReadableName and not logName:
            logName = 'condor_log_%s_$(Cluster)_$(Process)'%self.humanReadableName            
        elif not logName:
            logName = 'condor_log_$(Cluster)_$(Process)'

        self.CMSSW = CMSSW
        self.EOSOUTDIR = EOSOUTDIR # specify this to have condor.sh manually xrdcp command output to an EOS location
        self.TARBALL = TARBALL

        self.universe = "vanilla"
        self.use_x509userproxy = "true"
        self.Executable = "ROOTHelp/scripts/condor.sh"
        #self.x509userproxy = "x509up_forCondor"
        self.should_transfer_files = "YES"
        self.when_to_transfer_output = "ON_EXIT"
        self.Output = logPath+logName+".stdout"
        self.Error = logPath+logName+".stderr"
        self.Log = logPath+logName+".log"
        self.Arguments = CMSSW+" "+EOSOUTDIR+" "+TARBALL+" "+cmd
        self.Queue = "1" # no equals sign in .jdl file
        
        self.made = False

    def make(self):
        attributes=["universe",
                    "use_x509userproxy",
                    "Executable",
                    #"x509userproxy",
                    "should_transfer_files",
                    "when_to_transfer_output",
                    "Output",
                    "Error",
                    "Log",
                    "Arguments",
                ]
        f=open(self.fileName,'w')
        for attr in attributes:
            f.write(attr+" = "+str(getattr(self, attr))+"\n")

        f.write('+DesiredOS="SL7"\n')
        f.write("Queue "+str(self.Queue)+"\n")    
        f.close()

        self.made = True



def makeCondorFile(cmd,eosOutDir,eosSubdir, outputDir, filePrefix):
    jdlFileName = filePrefix+eosSubdir
    TARBALL = "root://cmseos.fnal.gov//store/user/"+getUSER()+"/condor/"+getCMSSW()+".tgz"
    EOSOUTDIR = "None" if eosOutDir == "None" else eosOutDir+eosSubdir
    thisJDL = jdl(CMSSW=getCMSSW(), EOSOUTDIR=EOSOUTDIR, TARBALL=TARBALL, cmd=cmd, fileName=outputDir+jdlFileName+".jdl", logPath=outputDir, logName=jdlFileName)
    thisJDL.make()
    return thisJDL.fileName




def makeDAGFile(dag_file, dag_config, outputDir):
    fileName = outputDir+"/"+dag_file
    f=open(fileName,'w')

    dependencies = []

    if len(dag_config) > 25:
        print "ERROR Too many subjobs ", len(dag_config)
        sys.exit(-1)

    from string import ascii_uppercase

    # Name the JOB and collect the JOB names                                                                                                                                                                
    for node_itr, node_list in enumerate(dag_config):
        dependencies.append([])
        for job_itr, job in enumerate(node_list):
            jobID = ascii_uppercase[node_itr]+str(job_itr)
            line = "JOB "+jobID+" "+job
            f.write(line+"\n")
            dependencies[-1].append(jobID)

    # derive the structure in terms of JOB names (assume each JOB at higher level depends on all jobs below it)                                                                                             
    for dep_itr in range(1,len(dependencies)):
        parents = dependencies[dep_itr-1]

        for child in dependencies[dep_itr]:
            line = "PARENT "
            for p in parents: line += p+" "
            line += " CHILD " + child
            f.write(line+"\n")

    f.close()
    return fileName
