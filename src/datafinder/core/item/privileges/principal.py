#
# Created: 29.01.2009 mohr_se <steven.mohr@dlr.de>
# Changed: $Id: new_module_template.xml 3460 2008-10-31 11:23:52Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Principal module 
"""


__version__ = "$LastChangedRevision: 3460 $"


class Principal(object):
    """
    representation of a principal
    """
    
    def __init__(self, identifier, displayName):
        """
        @param identifier: identifier of the principal
        @type identifier: string
        @param displayName: display name of the principal
        @type displayName: string
        """
        self._identifier = identifier
        self._displayName = displayName 
        
    def __cmp__(self, other):
        """
        Allows comparision of two comparision
        """
        if self._identifier == other.identifier:
            return 0
        else:
            return 1
        
        
    def _getDisplayName(self):
        """
        Getter method for displayName
        """
        
        return self._displayName
    
    def _setDisplayName(self, name):
        """
        Setter method for displayName
        """
        
        self._displayName = name
    
    def _getIdentifier(self):
        """
        Getter method for identifier
        """
        
        return self._identifier
    
    def _setIdentifier(self, identifier):
        """
        Setter method for identifier
        """
        
        self._identifier = identifier
    
    displayName = property(_setDisplayName, _getDisplayName,
                           doc = "Display name of the principal")
    identifier  = property(_getIdentifier, _setIdentifier,
                           doc = "identifier of the principal")