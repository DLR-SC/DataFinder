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


import os


__version__ = "$LastChangedRevision: 4616 $"


def setVersion(versionString):
    """ Sets the version name within the DataFinder ..."""
    
    relativeVersionFilePath = "src/datafinder/core/configuration/constants.py" # Path Relative to project root
    fileHandle = open(relativeVersionFilePath, "r")
    content = fileHandle.readlines()
    fileHandle.close()
    newContent = list()
    for line in content:
        if "VERSION" in line:
            line = "VERSION = \"%s\"\n" % versionString
        newContent.append(line)
    
    fileHandle = open(relativeVersionFilePath, "w")
    fileHandle.writelines(newContent)
    fileHandle.close()


def regenerateFile(sourceFilePath, targetFilePath):
    """ 
    Returns C{True} if the target file (C{targetFilePath}) needs to regenerated 
    from the source file (C{targetFilePath}). The target file is created if:
    - The target file does not exist
    - The modification date of the source file is new than the one of the target file
    """

    regenerateFile = True
    if os.path.exists(targetFilePath):
        if os.path.getmtime(sourceFilePath) < os.path.getmtime(targetFilePath):
            regenerateFile = False
    return regenerateFile
