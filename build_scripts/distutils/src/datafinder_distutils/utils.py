# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#
#modification, are permitted provided that the following conditions are
#met:
#
# * Redistributions of source code must retain the above copyright 
#   notice, this list of conditions and the following disclaimer. 
#
# * Redistributions in binary form must reproduce the above copyright 
#   notice, this list of conditions and the following disclaimer in the 
#   documentation and/or other materials provided with the 
#   distribution. 
#
# * Neither the name of the German Aerospace Center nor the names of
#   its contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
#LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 
#A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
#OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
#SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
#LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
#DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
#THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  


""" 
This module provides common functionality used in different build targets.
"""


import os


__version__ = "$Revision-Id:$" 


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
