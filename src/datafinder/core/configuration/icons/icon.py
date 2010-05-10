#
# Created: 09.04.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: icon.py 4430 2010-02-03 15:38:57Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Represents a single icon.
"""


import os
import sys

from datafinder.core.configuration.icons.constants import LARGE_ICONFILENAME_SUFFIX, SMALL_ICONFILENAME_SUFFIX
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError


__version__ = "$LastChangedRevision: 4430 $"


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
