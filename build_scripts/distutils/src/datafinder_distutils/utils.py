#
# Created: 04.08.2008 schlauch <Tobias.schlauch@dlr.de>
# Changed: $Id: utils.py 4616 2010-04-18 10:41:05Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
This module provides common functionality used in different build targets.
"""


__version__ = "$LastChangedRevision: 4616 $"


def setVersion(versionString):
    """ Sets the version name within the DataFinder ..."""
    
    relativeVersionFilePath = "src/datafinder/core/configuration/constants.py" # Path Relative to project root
    fileHandle = open(relativeVersionFilePath, "r")
    content = fileHandle.readlines()
    fileHandle.close()
    newContent = []
    for line in content:
        if "VERSION" in line:
            line = "VERSION = \"%s\"\n" % versionString
        newContent.append(line)
    
    fileHandle = open(relativeVersionFilePath, "w")
    fileHandle.writelines(newContent)
    fileHandle.close()
