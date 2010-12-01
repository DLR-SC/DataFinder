# pylint: disable=R0201, R0904, R0902, C0302
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
# All rights reserved.
#met:
#
#
#
# * Redistributions of source code must retain the above copyright 
#   notice, this list of conditions and the following disclaimer. 
#
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
Module for the base item declaration.
"""


import logging

from datafinder.core.configuration.properties.constants import UNMANAGED_SYSTEM_PROPERTY_CATEGORY, \
                                                               MANAGED_SYSTEM_PROPERTY_CATEGORY
from datafinder.core.error import ItemError, PrivilegeError, PropertyError
from datafinder.core.item.property import Property
from datafinder.core.item.privileges.acl import AccessControlList
from datafinder.core.item.privileges.privilege import getPrivilege
from datafinder.persistence.error import PersistenceError


__version__ = "$Revision-Id:$" 


_logger = logging.getLogger()
    
    
class ItemBase(object):
    """ Base class for all item implementations. """

    def __init__(self, name=None, fileStorer=None):
        """
        Constructor.
        
        @param name: Name of the item.
        @type name: C{unicode}
        @param fileStorer: File storer object representing the item.
        @type fileStorer: L{FileStorer<datafinder.persistence.factory.FileStorer>}
        @raise ItemError: If both C{name} and C{fileStorer} are not specified.
        """
        
        if name is None and fileStorer is None:
            raise ItemError("Either name or a file storer has to be specified on initialization.")
        
        self.name = name
        self.path = None
        self.linkTarget = None
        self._fileStorer = fileStorer
        if not fileStorer is None:
            self.path = fileStorer.identifier
            self.name = fileStorer.name
        self._parent = None
        
        self._dataPersister = None
        self.itemFactory = None
        
        self._isRoot = False
        self._isCollection = False
        self._childrenPopulated = True
        self._isLeaf = False
        self._isLink = False
        self._created = False
        self._acl = None
        self._privileges = None
        self._properties = None
        self._ignoreChecks = False
        
    def refresh(self, itemStateOnly=False):
        """ 
        Resets the state of the item so that 
        its information is reloaded when accessed.
        
        @param itemStateOnly: If set it indicates that only the item 
                              state is refreshed but no structural information. Default is C{False}
        @type itemStateOnly: C{bool}
        """
        
        if not itemStateOnly: 
            self._parent = None
            self._dataPersister = None
            self._fileStorer = None
        self._acl = None
        self._properties = None
        self._privileges = None
            
    def create(self, properties):
        """ 
        Interface for the creation of the concrete item. 
        
        @param properties: Optional properties parameter for specifying meta data.
        @type properties: C{list} of L{Property<datafinder.core.item.properties.Property>}
        """
        
        self._checkCreationProperties(properties)
        
        if not self.parent.capabilities.canAddChildren:
            raise ItemError("No child item can be created below parent item '%s'" % self.parent.path)
        
    def _checkCreationProperties(self, properties):
        """ Checking whether the given properties are sufficient for item creation. """
        
        self._properties = dict()
        if self.itemFactory.hasCustomMetadataSupport:
            for property_ in properties:
                if self.isManaged or property_.propertyDefinition.category != MANAGED_SYSTEM_PROPERTY_CATEGORY:
                    self._properties[property_.identifier] = property_
        
        missingProperties = list()
        requiredPropertyDefinitions = self.requiredPropertyDefinitions
        availablePropertyDefinitions = [property_.propertyDefinition for property_ in properties]
        
        for requiredPropertyDefinition in requiredPropertyDefinitions:
            isAvailable = requiredPropertyDefinition in availablePropertyDefinitions
            if not isAvailable and requiredPropertyDefinition.notNull:
                missingProperties.append(requiredPropertyDefinition.displayName)
            elif not isAvailable:
                property_ = Property(requiredPropertyDefinition, requiredPropertyDefinition.defaultValue)
                properties.append(property_)
                
        if len(missingProperties) > 0:
            self._properties = None
            errorMessage = "The following required properties are missing.\n%s" % "\n".join(missingProperties)
            raise ItemError(errorMessage)
    
    def delete(self, ignoreStorageLocation=False):
        """ Deletes the item. """

        if not ignoreStorageLocation:
            checker = self.itemFactory.createActionCheckTreeWalker()
            if not checker.canDelete(self):
                raise ItemError("The item '%s' cannot be deleted." % self.path)
    
            for affectedItem in checker.affectedItems:
                try:
                    affectedItem.dataPersister.delete()
                except PersistenceError, error:
                    raise ItemError("Unable to delete item '%s'.\nReason:'%s'" % (self.path, error.message))
            self.dataPersister.delete()
                
        try:
            self.fileStorer.delete()
        except (AttributeError, PersistenceError), error:
            raise ItemError("Unable to delete item '%s'.\nReason:'%s'" % (self.path, error.message))
        else:
            self.invalidate()
    
    def copy(self, item):
        """
        Copy the this item to the given item.
        
        @param item: The target item that represents the copied item.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
            
        checker = self.itemFactory.createActionCheckTreeWalker()
        if not checker.canCopy(self):
            raise ItemError("The item '%s' cannot be copied." % self.path)
        
        if not item.parent.capabilities.canAddChildren:
            raise ItemError("Cannot copy to target item.")
        
        try:
            self.fileStorer.copy(item.fileStorer)
            item._created = True
            self.dataPersister.copy(item)
            for affectedItem in checker.affectedItems:
                targetPath = item.path + affectedItem.path[len(self.path):]
                targetItem = self.itemFactory.create(targetPath)
                affectedItem.dataPersister.copy(targetItem)
        except (AttributeError, PersistenceError, ItemError), error:
            raise ItemError("Cannot copy item. Reason:'%s'" % error.message)
        else:
            item.refresh(True)
    
    def move(self, item):
        """
        Moves this item to the given item location.
        
        @param item: The target item for this item.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        self._created = False
        checker = self.itemFactory.createActionCheckTreeWalker()
        if not checker.canMove(self):
            self._created = True
            raise ItemError("The item '%s' cannot be moved." % self.path)
        
        if not item.parent.capabilities.canAddChildren:
            self._created = True
            raise ItemError("Cannot move to target item.")

        try:
            self.fileStorer.move(item.fileStorer)
            item._created = True
            self.dataPersister.move(item)
            for affectedItem in checker.affectedItems:
                targetPath = item.path + affectedItem.path[len(self.path):]
                targetItem = self.itemFactory.create(targetPath)
                affectedItem.dataPersister.move(targetItem)
        except (AttributeError, PersistenceError, ItemError), error:
            self._created = True
            raise ItemError("Cannot move item. Reason:'%s'" % error.message)
        else:
            self.invalidate()
            item.refresh(True)
            
    def retrieveData(self):
        """
        Receives the data associated with this item.
        @return: Readable file-like object.
        """

        if not self.capabilities.canRetrieveData:
            raise ItemError("This item does not allow data retrieval.")
        else:
            try:
                return self.dataPersister.retrieveData()
            except PersistenceError, error:
                raise ItemError("Cannot read item data. Reason: '%s'" % error.message)

    def getTemporaryFileObject(self, deleteOnClose=True):
        """ 
        Returns a named local temporary file object allowing access to the binary content.
        
        @param deleteOnClose: Automatically deletes the temporary file object when its closed. Default: C{True}
        @type deleteOnClose: C{bool}
        
        @return: Tuple consisting of local file path and opened temporary file object.
        @rtype: C{tuple} of C{unicode}, C{object} implementing file protocol
        """

        if self.dataPersister.fileStorer is None:
            raise ItemError("This item does not allow data retrieval.")
        else:
            try:
                return self.dataPersister.fileStorer.getTemporaryFileObject(self.name, deleteOnClose)
            except PersistenceError, error:
                raise ItemError("Cannot retrieve temporary file object. Reason: '%s'" % error.message)

    def storeData(self, fileObj):
        """
        Stores the data that has to be associated with this item.
        
        @param fileObj: File-like object that can be read from.
        """
        
        if not self.capabilities.canStoreData:
            raise ItemError("This item does not allow data storage.")
        else:
            try:
                self.dataPersister.storeData(fileObj)
            except PersistenceError, error:
                raise ItemError("Cannot write item data. Reason: '%s'" % error.message)
    
    def search(self, restrictions):
        """
        Search from this item the whole subtree.

        @param restrictions: The search restrictions.
        @type restrictions: C{unicode}
        """
        
        if not self.parent is None:
            return self.parent.search(restrictions)

    def getChildren(self):
        """
        Returns the children for this item.
        
        @return: The children of this item.
        @rtype: C{list}
        """
        
        return list()

    def addChild(self, item):
        """
        Adds a child item to this item. This method has to be implemented by 
        subclasses.
        
        @param item: The item that has to be added to the item.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        pass
        
    def removeChild(self, item):
        """
        Removes the given item from the child list.
        
        @param item: The child item that has to be removed.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        pass

    def hasChild(self, name, isCaseSensitive=False):
        """
        Determines whether the item has a child with the given name.
        
        @param name: Name of the child.
        @type name: C{unicode}
        @param isCaseSensitive: Flag indicating whether the check is performed case sensitive. Default is C{False}.
        @type isCaseSensitive: C{bool}

        @return: Flag indicating existence.
        @rtype: C{bool}
        """
        
        pass

    def invalidate(self):
        """ Invalidates the item. """
        
        self.parent = None
        self.itemFactory.invalidate(self.path)
        self.path = None
        self._fileStorer = None

    @property
    def properties(self):
        """ Retrieves the properties and maps them to the correct representation. """
        
        if self._properties is None:
            if self.isCreated:
                self._refreshProperties()
            else:
                return dict()
        return self._properties

    def _refreshProperties(self):
        """ Updates the item properties with current information of the persistence backend. """
        
        self._properties = dict()
        try:
            metadata = self.fileStorer.retrieveMetadata()
        except PersistenceError, error:
            _logger.error(error.message)
        except AttributeError:
            self._properties = dict()
        else:
            propertyNamespace = self._determinePropertyNamespace(metadata)
            for metadataId, persistedValue in metadata.iteritems():
                propertyDefinition = self.itemFactory.getPropertyDefinition(metadataId, propertyNamespace)
                try:
                    property_ = Property.create(propertyDefinition, persistedValue)
                except PropertyError, error:
                    message = "Invalid value for property '%s' of item '%s' " % (propertyDefinition.identifier, self.path)\
                              + "has been found."
                    _logger.warning(message)
                else:
                    self._properties[propertyDefinition.identifier] = property_

    def _determinePropertyNamespace(self, metadata):
        """ Allows determination of the name space used identify property definitions. """

        pass
    
    def updateProperties(self, properties):
        """ 
        Adds/Updates the given properties to the item.
        
        @param properties: Properties to add.
        @type properties: C{list} of L{Property<datafinder.core.item.property.Property>}
        """
        
        propertiesToStore = dict()
        if self._properties is not None:
            currentProperties = self._properties.copy()
        else:
            currentProperties = list()
        for property_ in properties:
            if property_.propertyDefinition.category != UNMANAGED_SYSTEM_PROPERTY_CATEGORY:
                if self.isManaged or property_.propertyDefinition.category != MANAGED_SYSTEM_PROPERTY_CATEGORY:
                    if property_.identifier in self.properties:
                        try:
                            self.properties[property_.identifier].value = property_.value
                        except PropertyError:
                            continue
                    else:
                        propertyNamespace = None
                        if not self.dataType is None:
                            propertyNamespace = self.dataType.name
                        propDef = self.itemFactory.getPropertyDefinition(property_.identifier, propertyNamespace)
                        try:
                            self.properties[property_.identifier] = Property(propDef, property_.value)
                        except PropertyError:
                            continue
                    propertiesToStore[property_.identifier] = property_.value
        try:
            self.fileStorer.updateMetadata(propertiesToStore)
        except (AttributeError, PersistenceError), error:
            _logger.error(error.message)
            self._properties = currentProperties
            
    def deleteProperties(self, propertyIdentifiers):
        """ 
        Deletes the given properties from the item properties.
        
        @param propertyIdentifiers: List of property identifiers.
        @type propertyIdentifiers: C{list} of C{unicode}
        """
        
        try:
            self.fileStorer.deleteMetadata(propertyIdentifiers)
        except (AttributeError, PersistenceError), error:
            _logger.error(error.message)
        else:     
            for propertyIdentifier in propertyIdentifiers:
                if propertyIdentifier in self.properties:
                    del self.properties[propertyIdentifier]
    
    @property
    def acl(self):
        """ Retrieves the access control list. """
        
        if self._acl is None:
            try:
                persistedAcl = self.fileStorer.retrieveAcl()
            except (AttributeError, PersistenceError), error:
                _logger.error(error.message)
                self._acl = AccessControlList()
            else:
                try:
                    self._acl = AccessControlList.create(persistedAcl)
                except PrivilegeError, error:
                    _logger.error(error.message)
                    self._acl = AccessControlList()

    def updateAcl(self, acl):
        """ Stores access control list. """
        
        try:
            self.fileStorer.updateAcl(self._acl.toPersistenceFormat())
        except (AttributeError, PersistenceError), error:
            _logger.error(error.message)
        else:
            self._acl = acl
    
    @property
    def fileStorer(self):
        """ Returns the file storer. """
        
        if self._fileStorer is None and not self.path is None:
            self._fileStorer = self.itemFactory.createFileStorer(self.path)
        return self._fileStorer

    @property
    def dataType(self):
        """ Getter for the data type attribute. """

        pass
    
    @property
    def dataFormat(self):
        """ Getter for the data format attribute. """

        pass
        
    @property
    def dataPersister(self):
        """ Lazy instantiation of the data persister. """
        
        if self._dataPersister is None:
            self._dataPersister = self.itemFactory.createDataPersister(self)
        return self._dataPersister
    
    @property
    def isRoot(self):
        """ Indicates whether it is the root item or not. """   
    
        return self._isRoot
         
    @property
    def isCollection(self):
        """ Indicates whether it is a collection or not. """   
    
        return self._isCollection
    
    @property
    def childrenPopulated(self):
        """ Indicates whether the children are already retrieved. """
        
        return self._childrenPopulated
    
    @property
    def isLeaf(self):
        """ Indicates whether the item is a leaf or not. """
        
        return self._isLeaf
    
    @property
    def isLink(self):
        """ Indicates whether the item is a link or not. """
        
        return self._isLink
    
    @property
    def linkTargetPath(self):
        """ Getter for the link target path. """
        
        return None
    
    @property
    def state(self):
        """
        Retrieve the data state associated with
        L{NullDataPersister<datafinder.core.item.data_persister.persisters.NullDataPersister>} of this item.
        
        @return: The data state.
        @rtype: C{unicode} @see L{datafinder.core.item.data_persister.constants}
        """
        
        return self.dataPersister.state

    @property
    def privileges(self):
        """ Getter for the granted privileges on the specific item. """
        
        if self._privileges is None:
            self._privileges = list()
            if not self.fileStorer is None:
                try:
                    privileges = self.fileStorer.retrievePrivileges()
                except PersistenceError, error:
                    raise PrivilegeError("Cannot determine privileges.\nReason: '%s'" % error.message)
                for privilege in privileges:
                    self._privileges.append(getPrivilege(privilege))
        return self._privileges

    def _setParent(self, parent):
        """ Setter for the parent item. """
        
        if not parent is None:
            if parent.isLeaf or parent.isLink:
                raise ItemError("Given parent is a leaf.")
            parent.addChild(self)
            oldPath = self.path
            if parent.path.endswith("/"):
                self.path = parent.path + self.name
            else:
                self.path = parent.path + "/" + self.name
            if oldPath != self.path:
                self._fileStorer = None
            self._dataPersister = None

        if not self._parent is None:
            if self._parent != parent:
                self._parent.removeChild(self)
        self._parent = parent
        
    def _getParent(self):
        """ Returns the parent of this item. """
        
        if self._parent is None and not self.isRoot and not self.fileStorer is None:
            parentFileStorer = self.fileStorer.parent
            self._parent = self.itemFactory.create(parentFileStorer.identifier, fileStorer=parentFileStorer)
        return self._parent
    parent = property(_getParent, _setParent)

    @property
    def capabilities(self):
        """ Property holding the direct capabilities. """
        
        return self.itemFactory.createItemCapabilityChecker(self)

    @property
    def dataUri(self):
        """ Returns the URI of the associated file object. """
        
        if self.dataPersister.fileStorer is None:
            raise ItemError("This item does not allow data retrieval.")
        return self.dataPersister.fileStorer.uri

    @property
    def uri(self):
        """ Returns the URI of the item. """
        
        return self.fileStorer.uri
    
    @property
    def isManaged(self):
        """ Flag indicating whether the item belongs to managed repository or not. """
        
        return self.itemFactory.isManaged

    @property
    def isCreated(self):
        """ Flag indicating whether the item has been already created or not. """
        
        return self._created

    @property
    def requiredPropertyDefinitions(self):
        """ Determines the required property definitions. """
        
        requiredPropertyDefinitions = self.itemFactory.getDefaultPropertyDefinitions(self)
        if not self.dataType is None:
            requiredPropertyDefinitions += self.dataType.propertyDefinitions
        if not self.dataFormat is None:
            requiredPropertyDefinitions += self.dataFormat.propertyDefinitions
        return requiredPropertyDefinitions
