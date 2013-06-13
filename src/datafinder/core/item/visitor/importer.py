# $Filename$ 
# $Authors$
#
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
# All rights reserved.
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


""" This module provides a tree walker that copies all items from one repository to another. """


from datafinder.common import logger
from datafinder.core.configuration.properties.constants import CONTENT_CREATION_DATETIME_PROPERTY_ID, \
                                                               CREATION_DATETIME_ID, DATA_FORMAT_ID, SIZE_ID, \
                                                               CONTENT_SIZE_ID, CONTENT_MODIFICATION_DATETIME_ID, \
                                                               MODIFICATION_DATETIME_ID
from datafinder.core.error import CoreError, ItemError
from datafinder.core.item.collection import ItemCollection, ItemRoot
from datafinder.core.item.link import ItemLink
from datafinder.core.item.leaf import ItemLeaf
from datafinder.core.item.property import Property
from datafinder.core.item.visitor.base import ItemTreeWalkerBase, VisitSlot


__version__ = "$Revision-Id:$" 


class Importer(ItemTreeWalkerBase, object): # inherit from object to make pylint happy, but this is a pylint issue
    """
    This class uses the L{ItemTreeWalkerBase<datafinder.core.item.visitor.base.ItemTreeWalkerBase>}
    protocol to implement a recursive copy algorithm between two repositories. It is assumed
    (but NOT checked) that the repository configurations are compatible.
    """
    
    
    _log = logger.getDefaultLogger()
    
    
    def __init__(self, stopTraversalStates=None, stopProcessStates=None):
        """ 
        @param stopTraversalStates: List of states that are used to prevent traversal of specific collections. Default: C{None}
        @type stopTraversalStates: C{list} of C{unicode}
        @param stopProcessStates: List of states that are used to prevent processing a specific items. Default: C{None}
        @type stopProcessStates: C{list} of C{unicode}
        """
        
        super(Importer, self).__init__(-1, stopTraversalStates, stopProcessStates)

        self._pwd = None
        self._deferredLinks = None
        self._destinationRootPath = None
        self._itemFactory = None
        self._newSourceName = None
        self._defaultProperties = None
        self._source = None
        self._copyData = True
        self._ignoreLinks = False
        self._determinePropertiesCallback = None
        self.importedLeafs = None
        
    def performImport(self, source, targetCollection, newSourceName=None, 
                      defaultProperties=None, copyData=True, ignoreLinks=False, determinePropertiesCallback=None):
        """
        This method initiates the copy process and starts walking the source creating a
        new node in the destination tree for each item it passes.
        
        @param source: The item that should be imported.
        @type source: L{ItemBase<datafinder.core.item.base.ItemBase>}
        @param targetCollection: The collection that should afterwards contain the copy.
        @type targetCollection: L{ItemCollection<datafinder.core.item.collection.ItemCollection>}
        @param newSourceName: Optional new name of the source item. Default: C{None}
        @type newSourceName: C{unicode}
        @param defaultProperties: Optional list of properties which are set for every item. Default: C{None}
        @type defaultProperties: C{list} of L{Property<datafinder.core.item.property.Property>}
        @param copyData: Flag indicating whether data has to be copied or not.
        @type copyData: C{bool}
        @param ignoreLinks: Flag indicating the links are ignored during import. Default: C{False}
        @type ignoreLinks: C{bool}
        @param determinePropertiesCallback: Function determining properties used when importing a specific item.
        @type: determinePropertiesCallback: C{callable} using an item description as input and returns a dictionary
                                            describing the properties.
    
        
        @raise ItemError: Indicating errors during import.
        """
        
        self._pwd = targetCollection
        self._deferredLinks = list()
        self._destinationRootPath = targetCollection.path
        self._itemFactory = targetCollection.itemFactory
        self._newSourceName = newSourceName
        self._defaultProperties = defaultProperties
        self._source = source
        self._copyData = copyData
        self.importedLeafs = list()
        self._ignoreLinks = ignoreLinks
        self._determinePropertiesCallback = determinePropertiesCallback
        
        self.walk(source)
        
        missingDefferedLinkPaths = list()
        for source, importName, destinationParent in self._deferredLinks:
            try:
                self._copyLink(source, importName, destinationParent)
            except ItemError:
                missingDefferedLinkPaths.append(source.path)
        
        if len(missingDefferedLinkPaths) > 0:
            errorMessage = "The following links could not be imported:"
            for linkPath in missingDefferedLinkPaths:
                errorMessage += "\n" + linkPath
            raise ItemError(errorMessage)
    
    def walk(self, node):
        """
        @see: L{walk<datafinder.core.item.visitor.base.ItemTreeWalkerBase.walk>} method to add further post-processing.
        """

        super(Importer, self).walk(node)
        if node.isCollection:
            if not node.state in self._stopTraversalStates:
                self._pwd = self._pwd.parent
    
    def _copyLink(self, source, importName, destinationParent):
        """ Copies a link item. """
        
        baseDestinationPath = self._destinationRootPath 
        if not baseDestinationPath.endswith("/"):
            baseDestinationPath += "/"
        baseDestinationPath += (self._newSourceName or self._source.name)
        destinationLinkTargetPath = baseDestinationPath + source.linkTarget.path[len(self._source.path):]
        destinationLinkTarget = self._itemFactory.create(destinationLinkTargetPath)
        link = self._itemFactory.createLink(importName, destinationLinkTarget, destinationParent)
        properties = source.properties.values()[:]
        if not self._determinePropertiesCallback is None:
            properties.extend(self._determinePropertiesCallback(source))
        if not self._defaultProperties is None:
            properties.extend(self._defaultProperties)
        try:
            link.create(properties)
        except CoreError, error:
            link.invalidate()
            raise error
        
    def _importLink(self, link):
        """ Imports a link item. Not resolvable links are processed at the end. """

        if not self._ignoreLinks:
            importName = self._determineImportName(link)
            if not link.linkTarget is None \
               and link.linkTarget.path.startswith(self._source.path):
                try:
                    self._copyLink(link, importName, self._pwd)
                except ItemError:
                    self._deferredLinks.append((link, importName, self._pwd))

    def _determineImportName(self, item):
        """ Determines the name used importing the given item. """
        
        importName = item.name
        if item == self._source and not self._newSourceName is None:
            importName = self._newSourceName
        importName = self._itemFactory.determineValidItemName(importName)
        if importName != item.name:
            self._log.warning("Imported '%s' using different name: '%s'." % (item.path, importName))
        return importName

    def _importLeaf(self, leaf):
        """ Retrieves the content of a leaf item. """
        
        if leaf.capabilities.canRetrieveData:
            importName = self._determineImportName(leaf)
            importedLeaf = self._itemFactory.createLeaf(importName, self._pwd)
            properties = self._determineLeafProperties(leaf)
            try:
                importedLeaf.create(properties)
            except CoreError, error:
                self._handleLeafCreationError(importedLeaf, error)
            else:
                if self._copyData:
                    try:
                        importedLeaf.storeData(leaf.retrieveData())
                    except CoreError, error:
                        self._handleLeafCreationError(importedLeaf, error)
                    else:
                        self.importedLeafs.append(leaf)
                        
    def _handleLeafCreationError(self, leaf, error):
        self._log.error(error.args)
        try:
            leaf.delete(ignoreStorageLocation=True)
        except CoreError, error_:
            leaf.invalidate()
            self._log.info(error_.args)
        raise error
                        
    def _determineLeafProperties(self, leaf):
        """ Determines the properties when importing a leaf item. """
        
        properties = leaf.properties.values()[:]
        if not leaf.isManaged:
            contentCreationPropertyDefinition = self._itemFactory.getPropertyDefinition(CONTENT_CREATION_DATETIME_PROPERTY_ID) 
            properties.append(Property(contentCreationPropertyDefinition, leaf.properties[CREATION_DATETIME_ID].value))
            contentModificationPropertyDefinition = self._itemFactory.getPropertyDefinition(CONTENT_MODIFICATION_DATETIME_ID) 
            properties.append(Property(contentModificationPropertyDefinition, leaf.properties[MODIFICATION_DATETIME_ID].value))
            contentSizeDefinition = self._itemFactory.getPropertyDefinition(CONTENT_SIZE_ID) 
            properties.append(Property(contentSizeDefinition, leaf.properties[SIZE_ID].value))
            dataFormatPropertyDefinition = self._itemFactory.getPropertyDefinition(DATA_FORMAT_ID) 
            properties.append(Property(dataFormatPropertyDefinition, leaf.dataFormat.name))
        if not self._determinePropertiesCallback is None:
            properties.extend(self._determinePropertiesCallback(leaf))
        if not self._defaultProperties is None:
            properties.extend(self._defaultProperties)
        return properties
    
    def _importCollection(self, collection):
        """ Retrieves the content of a collection. """
        
        importName = self._determineImportName(collection)
        importedCollection = self._itemFactory.createCollection(importName, self._pwd)
        
        properties = collection.properties.values()[:]
        if not self._determinePropertiesCallback is None:
            properties.extend(self._determinePropertiesCallback(collection))
        if not self._defaultProperties is None:
            properties.extend(self._defaultProperties)
        try:
            importedCollection.create(properties)
        except CoreError, error:
            importedCollection.invalidate()
            raise error
        self._pwd = importedCollection
    
    handle = VisitSlot((_importLink, [ItemLink]), 
                       (_importLeaf, [ItemLeaf]), 
                       (_importCollection, [ItemCollection]), 
                       (lambda self, _: None, [ItemRoot]))
