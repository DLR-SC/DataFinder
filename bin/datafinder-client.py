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

from datafinder.gui.user import application


__version__ = "$LastChangedRevision: 4523 $"


dfStart = os.environ.get("DF_START")
profile = os.environ.get("DF_PROFILE")
debug = os.environ.get("DF_DEBUG")

# set the encoding
encoding = "UTF-8"
if not locale.getdefaultlocale()[1] is None:
    encoding = locale.getdefaultlocale()[1]
try:
    sys.setdefaultencoding(encoding)
except AttributeError:
    if sys.getdefaultencoding() == "ascii":
        print("It is required to correctly set default encoding. " + \
              "Please see site.py for further details.")
    
if profile:
    import cProfile
    cProfile.run("application.main()", sort="cumulative")
else:
    application.main(dfStart, bool(debug))
