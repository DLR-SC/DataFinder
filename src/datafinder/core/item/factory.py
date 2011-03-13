# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
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
Factory module for the creating of new items.
"""


from datafinder.core.error import ItemError
from datafinder.core.item.collection import ItemCollection, ItemRoot
from datafinder.core.item.leaf import ItemLeaf
from datafinder.core.item.link import ItemLink
from datafinder.core.item.data_persister.factory import DataPersisterFactory
from datafinder.core.item.visitor.checks import ActionCheckTreeWalker, ItemCapabilityChecker
from datafinder.persistence.error import PersistenceError

__version__ = "$Revision-Id:$" 

class ItemFactory(object):
    """ Factory for the item creation. """
    
    def __init__(self, fileSytem, configuration):
        """
        Constructor.

        @param fileSytem: Generic file system used for file storer creation.
        @type fileSytem: L{FileSystem<datafinder.persistence.factory.FileSystem>} 
        @param configuration: The configuration of the data repository.
        @type configuration: L{RepositoryConfiguration<datafinder.core.configuration.configuration.RepositoryConfiguration>} 
        """
        
        self._fileSystem = fileSytem
        self._configuration = configuration
        self._dataPersisterFactory = DataPersisterFactory(self._configuration)
        self._itemCache = dict()
                
    def createFileStorer(self, path):
        """ 
        Creates file storer for the given path.
        
        @param path: Identifier of the item.
        @type path: C{unicode}
        
        @return: File storer.
        @rtype: L{FileStorer<datafinder.persistence.factory.FileStorer>}
        """
        
        return self._fileSystem.createFileStorer(path)
    
    def createActionCheckTreeWalker(self):
        """
        Returns a capability checker for a item subtree.
        
        @return: Capability checker for a item subtree.
        @rtype: L{ActionCheckTreeWalker<ActionCheckTreeWalker>}
        """
        
        return ActionCheckTreeWalker(False,
                                     self._fileSystem.hasCustomMetadataSupport,
                                     self._fileSystem.hasMetadataSearchSupport)
    
    def createItemCapabilityChecker(self, item):
        """
        Returns a capability checker for the given item.
        
        @param item: Item to check.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        
        @return: Capability checker.
        @rtype: L{ItemCapabilityChecker<datafinder.core.item.visitor.checks.ItemCapabilityChecker>}
        """
        
        return ItemCapabilityChecker(item, 
                                     self._fileSystem.hasCustomMetadataSupport,
                                     self._fileSystem.hasMetadataSearchSupport)
    
    def createDataPersister(self, item):
        """
        Creates data persister for the given item.
        
        @param item: The item for which the data persister is required.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        return self._dataPersisterFactory.createDataPersister(item)
        
    def getPropertyDefinition(self, propertyId, namespace=None):
        """
        Retrieves the property definition for the given property identifier.
        
        @param propertyId: Identifier of the property definition.
        @type propertyId: C{unicode}
        
        @return: Property definition / type.
        @rtype: L{PropertyDefinition<datafinder.core.configuration.properties.property_definition.PropertyDefinition>}
        """
        
        return self._configuration.getPropertyDefinition(propertyId, namespace)
        
    def getDefaultPropertyDefinitions(self, item):
        """ 
        Returns a list of property definitions that are by the item.
        
        @param item: The item the default property definitions are required for.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        defaultPropertyDefinitions = list()
        if item.isCollection:
            defaultPropertyDefinitions = self._configuration.defaultCollectionPropertyDefinitions
        elif item.isLeaf:
            defaultPropertyDefinitions = self._configuration.defaultResourcePropertyDefinitions
        return defaultPropertyDefinitions
        
    def createLink(self, name, linkTarget=None, parent=None):
        """
        Returns an item representing a symbolic link for the given name. 
        When a parent item is supplied the created item is initialized 
        with this item as parent.
        The item is expected to be non-existing.
        
        @param name: Name of item. E.g. "c".
        @type name: C{unicode}
        @param linkTarget: : An item the link is pointing to.
        @type linkTarget: L{ItemBase<datafinder.core.item.base.ItemBase>}
        
        @return: An item.
        @rtype: L{ItemLink<datafinder.core.item.link.ItemLink>}
        """
        
        item = self._createItem(ItemLink, None, name, parent)
        item.linkTarget = linkTarget
        return item 
        
    def createLeaf(self, name, parent=None):
        """
        Returns an item representing a leaf for the given name. When a parent item is
        supplied the created item is initialized with this item as parent.
        The item is expected to be non-existing.
        
        @param name: Name of item. E.g. "c".
        @type name: C{unicode}
        
        @return: An item.
        @rtype: L{ItemLeaf<datafinder.core.item.leaf.ItemLeaf>}
        """
        
        return self._createItem(ItemLeaf, None, name, parent)
    
    def createCollection(self, name, parent=None, fileStorer=None):
        """
        Returns an item representing a collection for the given name. 
        When a parent item is supplied the created item is initialized 
        with this item as parent.
        The item is expected to be non-existing.
        
        @param name: Name of item. E.g. "c".
        @type name: C{unicode}
        
        @return: An item.
        @rtype: L{ItemCollection<datafinder.core.item.collection.ItemCollection>}
        """
        
        return self._createItem(ItemCollection, fileStorer, name, parent)
    
    def create(self, path, parent=None, fileStorer=None):
        """
        Returns an item for the given path. If it does not exist
        an error is raised.
        
        @param path: Path relative to the root item. E.g. "/a/b/c".
        @type path: C{unicode}
        
        @return: An item.
        @rtype: L{ItemBase<datafinder.core.item.base.ItemBase>}
        
        @raise ItemError: Raised when the item does not exist.
        """
        
        try:
            if fileStorer is None \
            and path not in self._itemCache:
                fileStorer = self._fileSystem.createFileStorer(path)
            elif fileStorer is not None:
                path = fileStorer.identifier
            if path in self._itemCache:
                item = self._itemCache[path]
                if not parent is None:
                    item.parent = parent
                return item
            
            if path == "/":
                item = self._createItem(ItemRoot, fileStorer, None, parent)
            else:
                if fileStorer.isCollection:
                    item = self._createItem(ItemCollection, fileStorer, None, parent)
                elif fileStorer.isLink:
                    item = self._createItem(ItemLink, fileStorer, None, parent)
                elif fileStorer.isLeaf:
                    item = self._createItem(ItemLeaf, fileStorer, None, parent)
                else:
                    raise ItemError("No valid item representation found for '%s'" % path)
        except PersistenceError, error:
            raise ItemError("Problem accessing item '%s'. Reason: '%s'", (path, error.message))
        else:
            item._created = True
            self._itemCache[path] = item
            return item

    def _createItem(self, itemClass, fileStorer=None, name=None, parent=None):
        """ Creates the concrete item. """
        
        item = itemClass(name, fileStorer)
     
       
        item.itemFactory = self
        if not parent is None:
            if parent.hasChild(item.name):
                raise ItemError("The item '%s' already has a child '%s'." % (parent.path, item.name))
            item.parent = parent
        item._created = False
        if not parent is None:
            item._ignoreChecks = parent.ignoreChecks
        self._itemCache[item.path] = item

        return item 

    
    def invalidate(self, path):
        """ Invalidate an entry from the item cache. """
        
        if path in self._itemCache:
            del self._itemCache[path]
        for itemPath in self._itemCache.keys()[:]:
            if itemPath.startswith(path):
                del self._itemCache[itemPath]

    def getDataType(self, dataTypeName):
        """ Retrieves the data type for the given name. """
        
        dataType = None
        if self._configuration.isManagedRepository:
            dataType = self._configuration.getDataType(dataTypeName)
        return dataType

    def getDataFormat(self, dataFormatName=None, mimeType=None, baseItemName=None):
        """ Retrieves the data format for the given name. """

        return self._configuration.determineDataFormat(dataFormatName, mimeType, baseItemName)

    def _existsConnection(self, sourceDataType, targetDataType):
        """ Checks whether a connection / relation exists between both data types. """
        
        if sourceDataType is None:
            sourceDataTypeName = None
        else:
            sourceDataTypeName = sourceDataType.name
        return self._configuration.existsConnection(sourceDataTypeName, targetDataType.name)
        
    def checkDatamodelConsistency(self, parentDataType, childDataType, isRoot=False):
        """ Checks the data model consistency of both items. """
        
        if self._configuration.isManagedRepository:
            if childDataType is None:
                raise ItemError("Data type is invalid.")
            if parentDataType is None and not isRoot:
                raise ItemError("Data type is invalid.")
            if not self._existsConnection(parentDataType, childDataType):
                raise ItemError("Cannot perform action because no relation between " \
                                + "both data types is defined by the underlying data model.")

    @property
    def isManaged(self):
        """ Returns a flag indicating whether the factory belongs to a managed repository or not. """
        
        return self._configuration.isManagedRepository
    
    @property
    def hasCustomMetadataSupport(self):
        """ Returns a flag indicating whether the factory belongs to a managed repository or not. """
        
        return self._fileSystem.hasCustomMetadataSupport
