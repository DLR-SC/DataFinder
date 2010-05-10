# pylint: disable-msg=C0103,W1010
# Created: 11.08.2003 Matthias Wagner <Matthias.Wagner@dlr.de>
# Changed: $Id: datafinder-admin-client.py 4607 2010-04-14 13:27:38Z schlauch $ 
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


__version__ = "$LastChangedRevision: 4607 $"


dfHome = os.environ.get('DF_HOME')

# set the encoding
encoding = "UTF-8"
if not locale.getdefaultlocale()[1] is None:
    encoding = locale.getdefaultlocale()[1]
try:
    sys.setdefaultencoding(encoding)
except AttributeError:
    if sys.getdefaultencoding() == "ascii":
        print "It is required to correctly set default encoding. Please see site.py for further details."

if not dfHome: # assume that this script is in df_home/bin/
    dfHome = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
    os.environ['DF_HOME'] = dfHome

if dfHome and os.path.exists(dfHome):
    # modify the PYTHONPATH internally
    sys.path.append(os.path.join(dfHome, 'lib', 'src'))
    sys.path.append(os.path.join(dfHome, 'src'))

    from datafinder.gui.admin import admin_application
    # OK, and now do it ...
    admin_application.main()
else:
    print 'Sorry, you will have to set the environment variable "DF_HOME"'
    print 'properly in order to start the DataFinder.'
    print 'Usually the path of the variable is one level below the'
    print 'current directory ("bin") that contains this script.'
    raise SystemExit
