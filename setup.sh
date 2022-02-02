# Absolute path to this script. 
THISDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ -z "$PYTHONPATH" ]
then
    export PYTHONPATH=$HOME
fi


PYTHONPATH=$PYTHONPATH:$THISDIR:$THISDIR/../:$THISDIR/iPlot:$THISDIR/iPlot/models:$THISDIR/scripts


alias iPlot='python -i ${THISDIR}/iPlot/iPlot.py'
