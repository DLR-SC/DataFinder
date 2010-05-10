# pylint: disable-msg=W0201, R0201
# W0201: The parent attribute is defined in the base class. The pylint checker cannot see this on commit time.
# R0201: Have to do this to correctly overwrite template implementation of the ItemBase class.
#
# Created: Malte Legenhausen (mail to malte.legenhausen@dlr.de)
#
# Version: $Id: collection.py 4554 2010-03-21 11:58:03Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder
#


"""
Module that contains the collection item type.
"""


import logging

from pyparsing import ParseException

from datafinder.core.configuration.properties.constants import DATATYPE_ID
from datafinder.core.item.base import ItemBase
from datafinder.core.item import search_restriction
from datafinder.core.error import CoreError, ItemError
from datafinder.persistence.error import PersistenceError


__version__ = "$LastChangedRevision: 4554 $"


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
            
    def search(self, restrictions):
        """ @see: L{ItemBase.search<datafinder.core.item.base.ItemBase.search>} """
        
        parser = search_restriction.SearchRestrictionParser()
        try:
            parsedRestrictions = parser.parseString(restrictions).asList()
        except ParseException, error:
            raise CoreError(str(error))
        else:
            result = list()
            try:
                fileStorers = self.fileStorer.metadataSearch(parsedRestrictions)
                for fileStorer in fileStorers:
                    result.append(self.itemFactory.create(None, fileStorer=fileStorer))
            except PersistenceError, error:
                self._logger.error(error.message)
                raise CoreError(str(error))
            return result
    
    def getChildren(self):
        """ @see: L{ItemBase.getChildren<datafinder.core.item.base.ItemBase.getChildren>} """
        
        if self._children is None:
            self._children = list()
            try:
                try:
                    children = self.fileStorer.getChildren()
                except PersistenceError, error:
                    self._childrenPopulated = True
                    raise ItemError(error.message)
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
        
    def _determinePropertyNamespace(self, metadata): # R0201
        """ Determines the property name space. """
        
        propertyNamespace = None
        if DATATYPE_ID in metadata:
            propertyNamespace = metadata[DATATYPE_ID].value
        return propertyNamespace
    
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
