# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#
#Redistribution and use in source and binary forms, with or without
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
Represents a single icon.
"""


import os
import sys

from datafinder.core.configuration.icons.constants import LARGE_ICONFILENAME_SUFFIX, SMALL_ICONFILENAME_SUFFIX
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError


__version__ = "$Revision-Id:$" 


def parseIconDirectory(directoryFileStorer):
    """
    Parses the given directory for icon files.
    
    @param directoryFileStorer: Allows access to the directory containing the icons.
    @type directoryFileStorer: L{FileStorer<datafinder.persistence.factory.FileStorer>}
    
    @return: List of icons.
    @rtype: C{list} of C{Icon}
    """
    
    try:
        result = list()
        children = directoryFileStorer.getChildren()
        childrenNames = [child.name for child in children]
        smallSuffixLength = len(SMALL_ICONFILENAME_SUFFIX)
        for fileStorer in children:
            if fileStorer.name.endswith(SMALL_ICONFILENAME_SUFFIX):
                baseName = fileStorer.name[:len(fileStorer.name) - smallSuffixLength]
                largeIconFileName = baseName + LARGE_ICONFILENAME_SUFFIX
                if largeIconFileName in childrenNames:
                    result.append(Icon(baseName, fileStorer.name, largeIconFileName, directoryFileStorer.identifier))
                else:
                    result.append(Icon(baseName, fileStorer.name, fileStorer.name, directoryFileStorer.identifier))
        return result
    except PersistenceError, error:
        raise ConfigurationError("Cannot load the local installed icons. Reason: '%s'" % error.message)


class Icon(object):
    """ Defines an image representation. """
    
    def __init__(self, baseName, smallName, largeName, localBaseDirectoryFilePath):
        """ 
        Constructor. 
        
        @param baseName: Logical name of the icon.
        @type baseName: C{unicode}
        @param smallName: Complete file name of the concrete small icon representation.
        @type smallName: C{unicode}
        @param largeName: Complete file name of the concrete large icon representation.
        @type largeName: C{unicode}
        @param localBaseDirectoryFilePath: Local file path of the directory the icon is located.
        @type localBaseDirectoryFilePath: C{unicode}
        """
        
        self.baseName = baseName
        self.smallName = smallName
        self.largeName = largeName
        self._localBaseDirectoryFilePath = localBaseDirectoryFilePath
        if not self._localBaseDirectoryFilePath is None and sys.platform == "win32":
            self._localBaseDirectoryFilePath = self._localBaseDirectoryFilePath[1:]

    @property
    def smallIconLocalPath(self):
        """ Returns the local path to the small icon file path. """
        
        return os.path.join(self._localBaseDirectoryFilePath, self.smallName)
   
    @property
    def largeIconLocalPath(self):
        """ Returns the local path to the small icon file path. """
        
        return os.path.join(self._localBaseDirectoryFilePath, self.largeName)
   
    def __cmp__(self, other):
        """ Compares to instances. """
        
        try:
            return cmp(self.baseName, other.baseName)
        except AttributeError:
            return 1

    def __repr__(self):
        """ Representation of the icon. """
        
        return self.baseName
