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


"""
Module that contains the collection item type.
"""


import logging

from datafinder.core.configuration.properties.constants import DATATYPE_ID
from datafinder.core.item.base import ItemBase
from datafinder.core.error import ItemError
from datafinder.persistence.error import PersistenceError


__version__ = "$Revision-Id:$" 


class ItemCollection(ItemBase):
    """
    Representation of a class that can contain child items.
    """

    _logger = logging.getLogger()
    
    def __init__(self, name=None, fileStorer=None):
        """ L{ItemBase.__init__<datafinder.core.item.base.ItemBase.__init__>} """
        
        ItemBase.__init__(self, name, fileStorer)
        self._isCollection = True
        self._children = None
        self._childrenPopulated = False
        self._dataType = None
        
    def refresh(self, itemStateOnly=False):
        """ 
        L{ItemBase.refresh<datafinder.core.item.base.ItemBase.refresh>} 
        Extends the refresh behavior so the children are refreshed as well. 
        """
        
        self._dataType = None
        if not itemStateOnly:
            if self.childrenPopulated:
                children = self._children[:]
                for child in children:
                    child.invalidate()
            self._children = None
            self._childrenPopulated = False
        ItemBase.refresh(self, itemStateOnly)
        
    def create(self, properties):
        """ @see: L{ItemBase.create<datafinder.core.item.base.ItemBase.create>} """

        ItemBase.create(self, properties)
        self.itemFactory.checkDatamodelConsistency(self.parent.dataType, self.dataType, self.parent.isRoot)
        
        try:
            if not self.fileStorer.exists():
                self.fileStorer.createCollection()
                self.updateProperties(properties)
                self.dataPersister.create()
                self._refreshProperties()
        except PersistenceError, error:
            raise ItemError("Unable to create collection item.\nReason:'%s'" % error.message)
        else:
            self._created = True
    
    def getChildren(self):
        """ @see: L{ItemBase.getChildren<datafinder.core.item.base.ItemBase.getChildren>} """
        
        if self._children is None:
            self._children = list()
            try:
                try:
                    children = self.fileStorer.getChildren()
                except PersistenceError, error:
                    self._childrenPopulated = True
                    raise ItemError(error.args)
                else:
                    for fileStorer in children:
                        try:
                            self._createItem(fileStorer)
                        except ItemError:
                            continue
            finally:
                self._childrenPopulated = True
        return self._children

    def addChild(self, item):
        """ @see: L{ItemBase.addChild<datafinder.core.item.base.ItemBase.addChild>} """

        if not item is None:
            if not self.hasChild(item.name):
                self.getChildren().append(item)
                item.parent = self
        
    def removeChild(self, item):
        """ @see: L{ItemBase.removeChild<datafinder.core.item.base.ItemBase.removeChild>} """
        
        if not item is None:
            try:
                self.getChildren().remove(item)
            except ValueError:
                pass
            else:
                item.parent = None

    def hasChild(self, name, isCaseSensitive=False):
        """ @see: L{ItemBase.hasChild<datafinder.core.item.base.ItemBase.hasChild>} """
        
        for child in self.getChildren():
            if not isCaseSensitive:
                if child.name == name:
                    return True
            else:
                if child.name.lower() == name.lower():
                    return True
        return False
    
    def copy(self, item):
        """ @see: L{copy<datafinder.core.item.base.ItemBase.copy>}"""
        
        self.itemFactory.checkDatamodelConsistency(item.parent.dataType, self.dataType, item.parent.isRoot)
        ItemBase.copy(self, item)
        
    def move(self, item):
        """ @see: L{move<datafinder.core.item.base.ItemBase.move>}"""
        
        self.itemFactory.checkDatamodelConsistency(item.parent.dataType, self.dataType, item.parent.isRoot)
        ItemBase.move(self, item)
        
    def _createItem(self, fileStorer):
        """ Initializes an item. """
        
        return self.itemFactory.create(None, self, fileStorer)
        
    @property
    def dataType(self):
        """ @see: L{dataType<datafinder.core.item.base.ItemBase.dataType>} """
    
        if self._dataType is None:
            if DATATYPE_ID in self.properties:
                self._dataType = self.itemFactory.getDataType(self.properties[DATATYPE_ID].value)
        return self._dataType
    

class ItemRoot(ItemCollection):
    """ Represent the item root. """
    
    def __init__(self, name=None, fileStorer=None):
        """ L{ItemBase.__init__<datafinder.core.item.base.ItemBase.__init__>} """
        
        ItemCollection.__init__(self, name, fileStorer)
        self._isRoot = True
