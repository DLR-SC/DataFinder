# pylint: disable-msg=R0201
# R0201 is disabled for provision of a default implementation.
#
# Created: 17.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: datastorer.py 4394 2010-01-18 13:40:39Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Defines interface and default implementation for data-related actions.
"""


from StringIO import StringIO


__version__ = "$LastChangedRevision: 4394 $"


class NullDataStorer(object):
    """ 
    Null pattern / default implementation of the data-related interface.
    
    @note: Real implementations of this interface are raising errors of
           type L{PersistenceError<datafinder.persistence.error.PersistenceError>}
           to indicate problems.
    """

    def __init__(self, identifier):
        """ 
        Constructor. 
        
        @param identifier: The logical identifier of the associated item. 
                           This is usually the path relative to a root.
        @type identifier: C{unicode}
        """
        
        self.identifier = identifier
    
    @property
    def linkTarget(self):
        """ 
        Getter for the logical identifier of the item the link is pointing to or C{None}.
        
        @return: Link target identifier.
        @rtype: C{unicode} or C{None}
        """
        
        return None
    
    @property
    def isLink(self):
        """
        Determines whether the associated item is a symbolic link or not.
        If it is a link the link target can be retrieved using the C{getChildren} method.
        
        @return: Flag indicating whether it is a link or not.
        @rtype: C{bool}
        """
        
        return False
    
    @property
    def isCollection(self):
        """
        Determines whether the associated item is an item container or not.
        
        @return: Flag indicating whether it is an item container or not.
        @rtype: C{bool}
        """
        
        return False
    
    @property
    def isLeaf(self):
        """
        Determines whether the associated item is a leaf node or not.
        
        @return: Flag indicating whether it is a leaf node or not.
        @rtype: C{bool}
        """
        
        return False

    @property
    def canAddChildren(self):
        """
        Determines whether it is possible to add new items below this item.
        
        @return: Flag indicating the possibility of adding new items below.
        @rtype: C{bool}
        """
           
        return False
    
    def createCollection(self, recursively):
        """ 
        Creates a collection.
        
        @param recursively: If set to C{True} all missing collections are created as well.
        @type recursively: C{bool}
        """
        
        pass
    
    def createResource(self):
        """ 
        Creates a resource. 
        """
    
        pass
    
    def createLink(self, destination):
        """ 
        Creates a symbolic link to the specified destination.
        
        @param destination: Identifies the item that the link is pointing to.
        @type destination: C{object} implementing the C{NullDataStorer} interface.
        """
    
        pass
    
    def getChildren(self):
        """ 
        Retrieves the logical identifiers of the child items. 
        In case of a symbolic link the identifier of the link target is returned.
        
        @return: List of the child item identifiers.
        @rtype: C{list} of C{unicode} 
        """
        
        return list()
    
    def exists(self):
        """ 
        Checks whether the item does already exist.
        
        @return: Flag indicating the existence of the item.
        @rtype: C{bool}
        """
        
        return False
    
    def delete(self):
        """ 
        Deletes the item. 
        """
        
        pass
    
    def copy(self, destination):
        """ 
        Copies the associated item.
        
        @param destination: Identifies the copy of the item.
        @type destination: C{object} implementing the C{NullDataStorer} interface. 
        """
        
        pass
    
    def move(self, destination):
        """ 
        Moves the associated item.
        
        @param destination: Identifies the moved item.
        @type destination: C{object} implementing the C{NullDataStorer} interface. 
        """
        
        pass 
    
    def readData(self):
        """ 
        Returns the associated data.
        
        @return: Associated data.
        @rtype: C{object} implementing the file protocol.
        """
        
        return StringIO("")
    
    def writeData(self, data):
        """ 
        Writes data of the associated item.
        
        @param data: Associated data.
        @type data: C{object} implementing the file protocol.
        """
        
        pass
