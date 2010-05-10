# 
# Contains constants to be used by DataFinder classes.
# 
# Created: 05.09.2003 Guy Kloss <Guy.Kloss@dlr.de>
# Changed: $Id: constants.py 4616 2010-04-18 10:41:05Z schlauch $
# 
# Version: $Revision: 4616 $
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
# 


"""
Contains constants to be used by DataFinder classes.
"""


import os


__version__ = "$LastChangedRevision: 4616 $"


DATAMODEL_FILENAME = "datamodel.xml"
DATASTORE_FILENAME = "datastores.xml"
ICON_DIRECTORYNAME = "icons"
SCRIPT_DIRECTORYNAME = "scripts"

# Homedir for the user
USER_HOME = os.path.join(os.path.expanduser("~"), ".datafinder")

# DataFinder install directory
INSTALLATION_HOME = os.environ.get("DF_HOME")

# Installed image files
if not INSTALLATION_HOME is None:
    LOCAL_INSTALLED_ICONS_DIRECTORY_PATH = os.path.abspath(os.path.join(INSTALLATION_HOME, "resources", "images"))
else:
    LOCAL_INSTALLED_ICONS_DIRECTORY_PATH = ""

# version number
VERSION = ""
