# $Filename$ 
# $Authors$
#
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
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
Contains wrapper class around the item representation used in the core package.
"""


from datafinder.core.error import ItemError
from datafinder.script_api.error import ItemSupportError


__version__ = "$Revision-Id:$" 
 

class ItemDescription(object):
    """ 
    Wrapper around the internal item representation giving restricted access to
    the relevant parameters.
    All instance variables are read-only.
    """
    
    
    def __init__(self, item):
        """ 
        Constructor. 
        
        @param item: The item.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        self.__item = item
        self.__capabilities = item.capabilities
    
    @property
    def name(self):
        """
        Returns the name of the item.
        """   
    
        return self.__item.name

    @property
    def path(self):
        """
        Returns the path of the item.
        """   
    
        return self.__item.path

    @property
    def linkTargetPath(self):
        """
        Returns the path of the link target. If it is no link None is returned.
        """   
        
        linkTargetPath = self.__item.linkTargetPath
        if self.isLink and linkTargetPath == None:
            raise ItemSupportError("Broken Link. Target does not exist.")       
        return linkTargetPath
    
    @property
    def isRoot(self):
        """
        Indicates whether it is the root item or not.
        """   
    
        return self.__item.isRoot
         
    @property
    def isCollection(self):
        """
        Indicates whether it is a collection or not.
        """   
    
        return self.__item.isCollection
    
    @property
    def isLeaf(self):
        """
        Indicates whether the item is a leaf or not.
        """
        
        return self.__item.isLeaf
    
    @property
    def isLink(self):
        """
        Indicates whether the item is a link or not.
        """
        
        return self.__item.isLink
    
    @property
    def state(self):
        """
        Retrieve the data state associated with
        L{NullDataPersister<datafinder.core.item.data_persister.persisters.NullDataPersister>} of this item.
        
        @return: The data state.
        @rtype: C{unicode} @see L{datafinder.core.item.data_persister.constants}
        """
        
        return self.__item.state

    @property
    def dataUri(self):
        """
        Returns the URI of the associated file object.
        """
        
        try:
            return self.__item.dataUri
        except ItemError, error:
            raise ItemSupportError("%s" % error.message)

    @property
    def uri(self):
        """
        Returns the URI of the item.
        """
        
        return self.__item.uri
    
    @property
    def isManaged(self):
        """
        Flag indicating whether the item belongs to managed repository or not.
        """
        
        return self.__item.isManaged

    @property
    def canAddChildren(self):
        """
        Convenience method to check whether an item can be created below.
        """
        
        return self.__capabilities.canAddChildren
    
    @property
    def canDelete(self):
        """
        Convenience method to check whether an item can be deleted.
        """
        
        return self.__capabilities.canDelete
    
    @property
    def canCopy(self):
        """
        Convenience method to check whether an item can be copied.
        """
        
        return self.__capabilities.canCopy
    
    @property
    def canMove(self):
        """
        Convenience method to check whether an item can be moved.
        """
        
        return self.__capabilities.canMove
    
    @property
    def canStoreData(self):
        """
        Convenience method to check whether the associated data can be stored using this item.
        """
        
        return self.__capabilities.canStoreData
    
    @property
    def canRetrieveData(self):
        """
        Convenience method to check whether the associated data can be retrieved using this item.
        """
        
        return self.__capabilities.canRetrieveData
    
    @property
    def canArchive(self):
        """
        Convenience method to check whether an item can be archived.
        """
        
        return self.__capabilities.canArchive
    
    @property
    def canSearch(self):
        """
        Convenience method to check whether an item can be searched.
        @note: The sanity checks are run again when this method is called.
        """
        
        return self.__capabilities.canSearch
    
    @property
    def canRetrieveProperties(self):
        """
        Convenience method to check whether an item`s properties can be retrieved.
        """
        
        return self.__capabilities.canRetrieveProperties

    @property
    def canStoreProperties(self):
        """
        Convenience method to check whether an item`s properties can be written.
        """
        
        return self.__capabilities.canStoreProperties

    def __str__(self):
        """ String representation. """
        
        return "URI: " + self.uri + " isManaged: " + str(self.isManaged) \
               + " isRoot: " + str(self.isRoot) + " isCollection: " + str(self.isCollection) \
               + " isLeaf: " + str(self.isLeaf) + " isLink: " + str(self.isLink) + " " + str(self.__item.linkTargetPath)
