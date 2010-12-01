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
Manages the icons of a specific data repository.
"""


from datafinder.common.logger import getDefaultLogger
from datafinder.core.configuration.icons.constants import LARGE_ICONFILENAME_SUFFIX, SMALL_ICONFILENAME_SUFFIX
from datafinder.core.configuration.icons.icon import parseIconDirectory, Icon
from datafinder.core.error import ConfigurationError
from datafinder.persistence.metadata.constants import MODIFICATION_DATETIME
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.factory import createFileStorer


__version__ = "$Revision-Id:$" 


class IconHandler(object):
    """ Implements icon management for a specific repository. """

    __logger = getDefaultLogger()

    def __init__(self, iconRegistry, sourceFileStorer, targetFileStorer):
        """
        Constructor.
        
        @param iconRegistry: Global registry for icons.
        @type iconRegistry: L{IconRegistry<datafinder.core.configuration.icons.registry.IconRegistry>}
        @param sourceFileStorer: Represents the source directory containing icon files.
        @type sourceFileStorer: L{FileStorer<datafinder.persistence.factory.FileStorer>}
        @param targetFileStorer: Represents the target directory for the icon files.
        @type targetFileStorer: L{FileStorer<datafinder.persistence.factory.FileStorer>}
        """

        self._iconRegistry = iconRegistry
        self._location = targetFileStorer.identifier
        self._sourceFileStorer = sourceFileStorer
        self._targetFileStorer = targetFileStorer
        
    @property
    def allIcons(self):
        """ Getter for all defined icons. """
        
        return self._iconRegistry.icons
    
    @property
    def icons(self):
        """ Getter for handler-specific icons. """
        
        return self._iconRegistry.getIcons(self._location)
    
    @property
    def localIconFilePath(self):
        """ Getter for the local icon file path. """
        
        return self._location
        
    def load(self):
        """
        Stores the icons in the target directory and register corresponding icons.
        
        @raise ConfigurationError: Indicating problems.
        """

        self.__logger.info("Loading icons...")
        try:
            if not self._targetFileStorer.exists():
                self._targetFileStorer.createCollection(True)
        except PersistenceError, error:
            raise ConfigurationError("Cannot prepare target icon location.\nReason: '%s'" % error.message)
        else:
            numberOfDownloadedIcons = 0
            try:
                children = self._sourceFileStorer.getChildren()
            except PersistenceError, error:
                raise ConfigurationError("Cannot retrieve icons.\nReason: '%s'" % error.message)
            else:
                for source in children:
                    target = self._targetFileStorer.getChild(source.name)
                    updateRequired = self._isUpdateRequired(source, target)
                    if updateRequired:
                        try:
                            self._copy(source, target)
                            numberOfDownloadedIcons += 1
                        except PersistenceError, error:
                            self.__logger.error("Cannot retrieve icon file '%s'. Reason '%s'" % (source.name, error.message))
                self._iconRegistry.register(self._location, parseIconDirectory(self._targetFileStorer))
                if numberOfDownloadedIcons > 0:
                    self.__logger.info("Retrieved %i icons files." % numberOfDownloadedIcons)
    
    @staticmethod
    def _isUpdateRequired(source, target):
        """ Checks whether an update of an existing target icons is required. """
        
        updateRequired = False
        try:
            sourceModificationDatetime = source.retrieveMetadata([MODIFICATION_DATETIME])[MODIFICATION_DATETIME].value
            targetModificationDatetime = target.retrieveMetadata([MODIFICATION_DATETIME])[MODIFICATION_DATETIME].value
            if sourceModificationDatetime is None or targetModificationDatetime is None:
                updateRequired = True
            else:
                if sourceModificationDatetime > targetModificationDatetime:
                    updateRequired = True
        except PersistenceError:
            updateRequired = True
        return updateRequired
            
    def create(self):
        """ 
        Creates icon location of the repository. 
        
        @raise ConfigurationError: Indicating problems on creation.
        """
    
        try:
            self._sourceFileStorer.createCollection()
        except PersistenceError, error:
            raise ConfigurationError("Cannot create icon collection. Reason: '%s'" % error.message)
    
    def getIcon(self, baseName):
        """
        Returns an icon for the given logical name or C{None}.
        
        @param baseName: Logical name of the icon.
        @type baseName: C{unicode}
        
        @return: Icon.
        @rtype: C{Icon}
        """
        
        icon = self._iconRegistry.getIcon(baseName, self._location)
        if icon is None:
            icon = self._iconRegistry.getIcon(baseName)
        return icon
    
    def addIcon(self, iconBaseName, localBaseDirectoryPath):
        """
        Adds a new icon.

        @param iconBaseName: Base name of the new icon.
        @type iconBaseName: C{unicode}
        @param localBaseDirectoryPath: Path to the base directory for small and large icon representation.
        @type localBaseDirectoryPath: C{unicode} 
        
        @raise ConfigurationError: Indicating problems on icon importing.
        """

        try:
            str(iconBaseName)
        except UnicodeEncodeError:
            raise ConfigurationError("Currently only icon file names in ASCII encoding are supported.")
        else:
            try:
                baseDirectoryFileStorer = createFileStorer("file:///" + localBaseDirectoryPath)
                smallIconFileName = iconBaseName + SMALL_ICONFILENAME_SUFFIX
                largeIconFileName = iconBaseName + LARGE_ICONFILENAME_SUFFIX
                smallIconFileStorer = baseDirectoryFileStorer.getChild(smallIconFileName)
                largeIconFileStorer = baseDirectoryFileStorer.getChild(largeIconFileName)
    
                if not smallIconFileStorer.exists():
                    raise ConfigurationError("The small icon file '%s' cannot be found." % smallIconFileName)
                if not largeIconFileStorer.exists():
                    raise ConfigurationError("The large icon file '%s' cannot be found." % largeIconFileName)
                
                for smallIconDestination in [self._sourceFileStorer, self._targetFileStorer]:
                    smallIconDestinationFileStorer = smallIconDestination.getChild(smallIconFileName)
                    self._copy(smallIconFileStorer, smallIconDestinationFileStorer)
                for largeIconDestination in [self._sourceFileStorer, self._targetFileStorer]:
                    largeIconDestinationFileStorer = largeIconDestination.getChild(largeIconFileName)
                    self._copy(largeIconFileStorer, largeIconDestinationFileStorer)
                    
                self._iconRegistry.register(self._location, [Icon(iconBaseName, smallIconFileName, 
                                                                  largeIconFileName, localBaseDirectoryPath)])
            except PersistenceError, error:
                raise ConfigurationError("Cannot add icon '%s'. Reason: '%s'" % (iconBaseName, error.message))
    
    @staticmethod
    def _copy(source, destination):
        """ Transfers data from source to destination. """
        
        if not destination.exists():
            destination.createResource()
        fileObj = source.readData()
        destination.writeData(fileObj)
            
    def removeIcon(self, icon):
        """
        Removes an icon.

        @param icon: Icon to remove.
        @type icon: C{Icon}
        """

        try:
            smallIconFileStorer = self._targetFileStorer.getChild(icon.smallName)
            if smallIconFileStorer.exists():
                smallIconFileStorer.delete()
            largeIconFileStorer = self._targetFileStorer.getChild(icon.largeName)
            if largeIconFileStorer.exists():
                largeIconFileStorer.delete()
            self._iconRegistry.unregister(self._location, icon)
            
            smallIconFileStorer = self._sourceFileStorer.getChild(icon.smallName)
            if smallIconFileStorer.exists():
                smallIconFileStorer.delete()
            largeIconFileStorer = self._sourceFileStorer.getChild(icon.largeName)
            if largeIconFileStorer.exists():
                largeIconFileStorer.delete()
        except PersistenceError, error:
            raise ConfigurationError("Cannot remove icon '%s'. Reason: '%s'" % (icon.baseName, error.message))
        
    def hasIcon(self, iconBaseName):
        """ 
        Checks whether the specific icon is already imported. 
        
        @param iconBaseName: Logical name of the icon.
        @type iconBaseName: C{unicode}
        
        @return: Flag indicating existence.
        @rtype: C{bool}
        """
        
        return self._iconRegistry.hasIcon(iconBaseName, self._location)
