# Absolute path to this script. 
THISDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

PYTHONPATH=$PYTHONPATH:$THISDIR:$THISDIR/../:$THISDIR/iPlot/models

