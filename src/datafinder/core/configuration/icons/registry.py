# pylint: disable-msg=W0201,C0103
#
# Initialization and administration of DataFinder images.
#
# Created: Heinrich Wendel (heinrich.wendel@dlr.de)
#
# Version: $Id: registry.py 4430 2010-02-03 15:38:57Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder
#


""" Initialization and administration of DataFinder images. """


from copy import copy

from datafinder.core.configuration.constants import LOCAL_INSTALLED_ICONS_DIRECTORY_PATH
from datafinder.core.configuration.icons.icon import parseIconDirectory
from datafinder.persistence.factory import createFileStorer


__version__ = "$LastChangedRevision: 4430 $"


class IconRegistry(object):
    """ Global registry for image configurations. """
    
    def __init__(self):
        """ Constructor. """
        
        self._registeredIcons = dict()

    def load(self):
        """ Initializes everything with the installed icons. """
        
        directoryFileStorer = createFileStorer("file:///" + LOCAL_INSTALLED_ICONS_DIRECTORY_PATH)
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
