# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
# All rights reserved.
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
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
Module that contains the repository class.
"""


from pyparsing import ParseException

from datafinder.core import search_restriction
from datafinder.core.archiver import Archiver
from datafinder.core.error import CoreError
from datafinder.core.item.factory import ItemFactory
from datafinder.core.item.privileges.principal import Principal
from datafinder.core.item.property import Property
from datafinder.core.item.visitor.importer import Importer
from datafinder.core.item.visitor.walker import ItemTreeWalker
from datafinder.persistence.error import PersistenceError
from datafinder.common.event_observer import Observable


__version__ = "$Revision-Id:$" 


class Repository(object):
    """
    The repository represents the container for the items.
    """
    
    # The root repository node.
    root = None
    
    
    def __init__(self, fileSystem, configuration, repositoryManager):
        """
        Constructor.
        """

        self._repositoryManager = repositoryManager
        self._configuration = configuration
        self._fileStorerFactory = fileSystem
        self._itemFactory = ItemFactory(self._fileStorerFactory, self._configuration)
        self._identifierPattern = None
        self._customMetadataSupport = None
        self._metadataSearchSupport = None
        self._privilegeSupport = None
        self._archiver = Archiver(self, repositoryManager)
    
        self.root = self._itemFactory.create("/")
        connection = self._configuration.preferences
        self._luceneSearchSupport = False
        if not connection is None:
            self._luceneSearchSupport = connection.useLucene
 
    @Observable
    @staticmethod
    def performImport(sourceItem, targetCollection, targetItemName=None, 
                      defaultProperties=None, copyData=True, ignoreLinks=False, determinePropertiesCallback=None):
        """ 
        Import the given item into the repository.
        
        @raise ItemError: Indicating problems on import.
        @see: L{performImport<datafinder.core.item.visitor.importer.Importer.performImport>}
              for details on parameters.
        """
        
        importer = Importer()
        if not defaultProperties is None:
            defaultProperties = defaultProperties[:]
        importer.performImport(sourceItem, targetCollection, targetItemName, defaultProperties, 
                               copyData, ignoreLinks, determinePropertiesCallback)
        
    @staticmethod
    def walk(item):
        """
        Walks through the subtree starting with given item and
        returns the items found in pre-order.
        
        @param item: Item idnetfying the starting point.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        
        @return: List of items in pre-order.
        @rtype: C{list} of L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        return ItemTreeWalker().walk(item)
        
    def determineUniqueItemName(self, proposedName, targetCollection):
        """ 
        Makes the proposed name unique so it can be used to as a child name
        for the collection identified by C{targetCollection}. In addition, invalid characters
        are replaced by "_".
        
        @param proposedName: Name of the new child item.
        @type proposedName: C{unicode}
        @param targetCollection: Parent collection.
        @type targetCollection: L{ItemCollection<datafinder.core.item.collection.ItemCollection>}
        
        @return: The unique name.
        @rtype: C{unicode}
        """
        
        proposedName = self._itemFactory.determineValidItemName(proposedName)
        uniqueName = proposedName
        appendPosition = uniqueName.rfind(".")
        if appendPosition == -1:
            appendPosition = len(uniqueName)

        if targetCollection.isCollection:
            counter = 1
            while targetCollection.hasChild(uniqueName):
                offset = 0
                if counter > 1:
                    offset = 3
                uniqueName = uniqueName[:appendPosition] + "_%i_" % counter + uniqueName[appendPosition + offset:]
                counter += 1
        return uniqueName
        
    def createArchive(self, sourceCollection, parentCollection, properties=None):
        """ Just a delegate method. @see: L{create<datafinder.core.archiver.Archiver.create>} """
        
        return self._archiver.create(sourceCollection, parentCollection, properties)
            
    def commitArchive(self, archiveRoot):
        """ Just a delegate method. @see: L{commit<datafinder.core.archiver.Archiver.commit>} """
        
        self._archiver.commit(archiveRoot)
        
    def release(self):
        """ Disconnects from the current repository. """
        
        self._configuration.release()
        self._fileStorerFactory.release()
        
    def getItem(self, path):
        """ @see: L{ItemFactory.create<datafinder.core.item.factory.ItemFactory.create>}"""
                
        return self._itemFactory.create(path)

    def createCollection(self, name, parent=None):
        """ @see: L{ItemFactory.createCollection<datafinder.core.item.factory.ItemFactory.createCollection>}"""
        
        return self._itemFactory.createCollection(name, parent)
    
    def createLeaf(self, name, parent=None):
        """ @see: L{ItemFactory.createLeaf<datafinder.core.item.factory.ItemFactory.createLeaf>}"""
        
        return self._itemFactory.createLeaf(name, parent)

    def createLink(self, name, linkTarget=None, parent=None):
        """ @see: L{ItemFactory.createLink<datafinder.core.item.factory.ItemFactory.createLink>}"""
        
        return self._itemFactory.createLink(name, linkTarget, parent)
    
    def createProperty(self, name, value, namespace=None):
        """ Creates a property for the given name and value. """
        
        propertyDefinition = self._configuration.getPropertyDefinition(name, namespace)
        return Property(propertyDefinition, value)
    
    @staticmethod
    def createPropertyFromDefinition(propertyDefinition, value):
        """ Creates a property for the given property definition and value. """
        
        return Property(propertyDefinition, value)
    
    def searchPrincipal(self, pattern, searchMode):
        """ Triggers a search for principals. 
        
        @param pattern: Name pattern to match corresponding principals.
        @type pattern: C{unicode}
        @param searchMode: Determines type of search.
        @type searchMode: C{int}
        """
        
        try:
            principals = self._fileStorerFactory.searchPrincipal(pattern, searchMode)
        except PersistenceError, error:
            raise CoreError(error.message)
        else:
            mappedPrincipals = list()
            for principal in principals:
                mappedPrincipals.append(Principal.create(principal))
            return mappedPrincipals
        
    def search(self, restrictions):
        """ Triggers a search.
        
        @param restrictions: The search restrictions.
        @type restrictions: C{unicode}
        """
        
        parser = search_restriction.SearchRestrictionParser()
        try:
            parsedRestrictions = parser.parseString(restrictions).asList()
        except ParseException, error:
            raise CoreError(str(error))
        else:
            result = list()
            try:
                fileStorers = self._fileStorerFactory.search(parsedRestrictions)
                for fileStorer in fileStorers:
                    result.append(self._itemFactory.create(fileStorer.identifier, fileStorer=fileStorer))
            except PersistenceError, error:
                print error
                raise CoreError(str(error))
            return result
            
    def isValidIdentifier(self, identifier):
        """ 
        Checks whether the given string describes a valid identifier.
        
        @param identifier: String describing the identifier.
        @type identifier: C{unicode}
        
        @return: C{True},C{None} if it is valid, otherwise C{False}, position
        @rtype: C{tuple} of C{bool}, C{int}
        """
        
        return self._fileStorerFactory.isValidIdentifier(identifier)
        
    def isValidPropertyIdentifier(self, identifier):
        """ 
        Checks whether the given string describes a valid property identifier.
        
        @param identifier: String describing the property identifier.
        @type identifier: C{unicode}
        
        @return: C{True} if it is valid, otherwise C{False}
        @rtype: C{bool}
        """
        
        return self._configuration.isValidPropertyIdentifier(identifier)

    @property
    def hasCustomMetadataSupport(self):
        """ Checks whether it is allowed to store custom meta data or not. """
        
        if self._customMetadataSupport is None:
            self._customMetadataSupport = self._fileStorerFactory.hasCustomMetadataSupport
        return self._customMetadataSupport

    @property
    def hasMetadataSearchSupport(self):
        """ Checks whether a meta data search is supported. """
        
        if self._metadataSearchSupport is None:
            self._metadataSearchSupport = self._fileStorerFactory.hasMetadataSearchSupport
        return self._metadataSearchSupport
    
    @property
    def hasLuceneSearchSupport(self):
        """ Checks whether a lucene search is supported. """
        
        return self._luceneSearchSupport
    
    @property
    def hasPrivilegeSupport(self):
        """ Checks whether privilege setting is supported. """
        
        if self._privilegeSupport is None:
            self._privilegeSupport = self._fileStorerFactory.hasPrivilegeSupport
        return self._privilegeSupport

    @property
    def configuration(self):
        """
        Returns the corresponding configuration of the repository.
                
        @return: Repository configuration instance.
        @rtype: L{RepositoryConfiguration<datafinder.core.configuration.configuration.RepositoryConfiguration>}
        """
        
        return self._configuration

