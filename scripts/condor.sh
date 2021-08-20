#!/bin/bash
echo "Starting job on " `date` #Date/time of start of job
echo "Running on: `uname -a`" #Condor job is running on this node
echo "System software: `cat /etc/redhat-release`" #Operating System on that node
CMSSW=$1
EOSOUTDIR=$2
TARBALL=$3
CMD=(${@})
unset CMD[0]
unset CMD[1]
unset CMD[2]

# bring in the tarball you created before with caches and large files excluded:
echo "xrdcp -s ${TARBALL} ."
xrdcp -s ${TARBALL} .
echo "source /cvmfs/cms.cern.ch/cmsset_default.sh"
source /cvmfs/cms.cern.ch/cmsset_default.sh 
echo "tar -xf ${CMSSW}.tgz"
tar -xf ${CMSSW}.tgz
rm ${CMSSW}.tgz
echo "cd ${CMSSW}/src/"
cd ${CMSSW}/src/
scramv1 b ProjectRename # this handles linking the already compiled code - do NOT recompile
eval `scramv1 runtime -sh` # cmsenv is an alias not on the workers
echo $CMSSW_BASE "is the CMSSW we have on the local worker node"
#cd ${_CONDOR_SCRATCH_DIR}
pwd

echo "${CMD[*]}"
eval "${CMD[*]}"
CMDEXIT=$?
echo
if [[ $CMDEXIT -ne 0 ]]; then
    echo "command exit code $CMDEXIT"
    exit $CMDEXIT
fi

# if [ $EOSOUTDIR == "None" ]
# then
#     echo "Done"
if [ $EOSOUTDIR != "None" ]
then
    pwd
    echo "List all root files:"
    ls *.root
    countROOT=`ls -1 *.root 2>/dev/null | wc -l`
    echo "List all h5 files:"
    ls *.h5
    countH5=`ls -1 *.h5 2>/dev/null | wc -l`
    echo "List all files:"
    ls -alh

    if [ $countROOT == 0 ] && [ $countH5 == 0 ]
    then
	echo "failed to produce either *.root or *.h5"
	echo "Throwing error"
	exit 1
    fi

    if [ $countROOT != 0 ]
    then 
	echo "*******************************************"
	echo "xrdcp ROOT output for condor to:"
	echo $EOSOUTDIR
	for FILE in *.root
	do
	    echo "xrdcp -f ${FILE} ${EOSOUTDIR}/${FILE}"
	    xrdcp -f ${FILE} ${EOSOUTDIR}/${FILE} 2>&1
	    XRDEXIT=$?
	    if [[ $XRDEXIT -ne 0 ]]; then
		rm *.root
		echo "exit code $XRDEXIT, failure in xrdcp root"
		exit $XRDEXIT
	    fi
	    rm ${FILE}
	done
    fi

    if [ $countH5 != 0 ]
    then 
	echo "*******************************************"
	echo "xrdcp H5 output for condor to:"
	echo $EOSOUTDIR
	for FILE in *.h5
	do
	    echo "xrdcp -f ${FILE} ${EOSOUTDIR}/${FILE}"
	    xrdcp -f ${FILE} ${EOSOUTDIR}/${FILE} 2>&1
	    XRDEXIT=$?
	    if [[ $XRDEXIT -ne 0 ]]; then
		rm *.h5
		echo "exit code $XRDEXIT, failure in xrdcp h5"
		exit $XRDEXIT
	    fi
	    rm ${FILE}
	done
    fi
fi

