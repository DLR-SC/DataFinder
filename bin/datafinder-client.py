#!python
# pylint: disable-msg=C0103,W1010
# Created: 30.07.2003 Guy Kloss <Guy.Kloss@dlr.de>
# Changed: $Id: datafinder-client.py 4523 2010-03-05 12:24:19Z schlauch $
#
# Version: $Revision: 4523 $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
# http://www.dlr.de/datafinder/
#


"""
Operating system independent start script (Win32 and UN*X)
for the DataFinder application.
"""


import os
import locale
import sys


__version__ = "$LastChangedRevision: 4523 $"


dfHome  = os.environ.get('DF_HOME')
dfStart = os.environ.get('DF_START')
profile = os.environ.get('PROFILE')
debug = os.environ.get('DEBUG_DATAFINDER')

# set the encoding
encoding = "UTF-8"
if not locale.getdefaultlocale()[1] is None:
    encoding = locale.getdefaultlocale()[1]
try:
    sys.setdefaultencoding(encoding)
except AttributeError:
    if sys.getdefaultencoding() == "ascii":
        print "It is required to correctly set default encoding. Please see site.py for further details."

if not dfStart:
    print 'Sorry, you will have to set the environment variable "DF_START"'
    print 'properly in order to start the DataFinder.'
    raise SystemExit

if not dfHome: # assume that this script is in df_home/bin/
    dfHome = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
    os.environ['DF_HOME'] = dfHome

if dfHome and os.path.exists(dfHome):
    # modify the PYTHONPATH internally
    sys.path.append(os.path.join(dfHome, 'lib', 'src'))
    sys.path.append(os.path.join(dfHome, 'src'))

    # OK, and now do it ...
    from datafinder.gui.user import application
    
    if profile:
        import cProfile
        cProfile.run('application.main()', sort='cumulative')
    else:
        if debug is None:
            debug = False
        else:
            debug = True
        application.main(dfStart, debug)
    
else:
    print 'Sorry, you will have to set the environment variable "DF_HOME"'
    print 'properly in order to start the DataFinder.'
    print 'Usually the path of the variable is one level below the'
    print 'current directory ("bin") that contains this script.'
    raise SystemExit
