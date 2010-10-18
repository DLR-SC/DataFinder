#!python
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

from datafinder.gui.admin import admin_application


__version__ = "$LastChangedRevision: 4607 $"


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

admin_application.main()
