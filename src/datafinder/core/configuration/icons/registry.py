#
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#Redistribution and use in source and binary forms, with or without
#
#modification, are permitted provided that the following conditions are
#
#met:
#
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


""" Initialization and administration of DataFinder images. """


from copy import copy

from datafinder.core.configuration.constants import LOCAL_INSTALLED_ICONS_DIRECTORY_PATH
from datafinder.core.configuration.icons.icon import parseIconDirectory
from datafinder.core.error import ConfigurationError
from datafinder.persistence.factory import createFileStorer
from datafinder.persistence.error import PersistenceError


__version__ = "$Revision-Id:$" 


class IconRegistry(object):
    """ Global registry for image configurations. """
    
    def __init__(self):
        """ Constructor. """
        
        self._registeredIcons = dict()

    def load(self):
        """ Initializes everything with the installed icons. """
        
        try:
            directoryFileStorer = createFileStorer("file:///" + LOCAL_INSTALLED_ICONS_DIRECTORY_PATH)
        except PersistenceError, error:
            raise ConfigurationError("Cannot parse local icon directory.\nReason:'%s'", error.message)
        else:
            icons = parseIconDirectory(directoryFileStorer)
            self._registeredIcons.clear()
            self.register(LOCAL_INSTALLED_ICONS_DIRECTORY_PATH, icons)
    
    @property
    def icons(self):
        """ Getter for all existing icons. """
        
        result = list()
        for locationsIcons in self._registeredIcons.values():
            for icon in locationsIcons.values():
                result.append(copy(icon))
        return result
    
    def getIcons(self, location=LOCAL_INSTALLED_ICONS_DIRECTORY_PATH):
        """ 
        Determines the icons for the specific location. 
        
        @param location: Identifies the icon location.
        @type location: C{unicode}
        
        @return: List of icons of the location.
        @rtype: C{list} of C{Icon}
        """
        
        result = list()
        if location in self._registeredIcons:
            for icon in self._registeredIcons[location].values():
                result.append(copy(icon))
        return result
    
    def register(self, location, icons):
        """ 
        Registers an icon location. 
        
        @param location: Represents the scope / location of the icons.
        @type location: C{unicode}
        @param icons: List of icons that a registered.
        @type icons: C{list} of C{Icon}
        """
        
        if not location in self._registeredIcons:
            self._registeredIcons[location] = dict()
        for icon in icons:
            self._registeredIcons[location][icon.baseName] = icon

    def unregister(self, location, icon):
        """ 
        Unregisters the given icon.
        
        @param icon: The icon to unregister.
        @type icon: C{Icon}
        """
        
        if location in self._registeredIcons:
            if icon.baseName in self._registeredIcons[location]:
                del self._registeredIcons[location][icon.baseName]

    def hasIcon(self, baseName, location=LOCAL_INSTALLED_ICONS_DIRECTORY_PATH):
        """ Checks whether the specific icons exists. """
        
        return not self.getIcon(baseName, location) is None
        
    def getIcon(self, baseName, location=LOCAL_INSTALLED_ICONS_DIRECTORY_PATH):
        """ Returns the icon for the given location. """
        
        result = None
        if location in self._registeredIcons:
            if baseName in self._registeredIcons[location]:
                result = copy(self._registeredIcons[location][baseName])
        return result
