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
Defines interface and default implementation for data-related actions.
"""


from StringIO import StringIO


__version__ = "$Revision-Id:$" 


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
        
        self = self # silent pylint
        return None
    
    @property
    def isLink(self):
        """
        Determines whether the associated item is a symbolic link or not.
        If it is a link the link target can be retrieved using the C{getChildren} method.
        
        @return: Flag indicating whether it is a link or not.
        @rtype: C{bool}
        """
        
        self = self # silent pylint
        return False
    
    @property
    def isCollection(self):
        """
        Determines whether the associated item is an item container or not.
        
        @return: Flag indicating whether it is an item container or not.
        @rtype: C{bool}
        """
        
        self = self # silent pylint
        return False
    
    @property
    def isLeaf(self):
        """
        Determines whether the associated item is a leaf node or not.
        
        @return: Flag indicating whether it is a leaf node or not.
        @rtype: C{bool}
        """
        
        self = self # silent pylint
        return False

    @property
    def canAddChildren(self):
        """
        Determines whether it is possible to add new items below this item.
        
        @return: Flag indicating the possibility of adding new items below.
        @rtype: C{bool}
        """
           
        self = self # silent pylint
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
        
        self = self # silent pylint
        return list()
    
    def exists(self):
        """ 
        Checks whether the item does already exist.
        
        @return: Flag indicating the existence of the item.
        @rtype: C{bool}
        """
        
        self = self # silent pylint
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
        
        self = self # silent pylint
        return StringIO("")
    
    def writeData(self, data):
        """ 
        Writes data of the associated item.
        
        @param data: Associated data.
        @type data: C{object} implementing the file protocol.
        """
        
        pass
