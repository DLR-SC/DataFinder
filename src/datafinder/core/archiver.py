#
# Created: 02.03.2010 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: archiver.py 4613 2010-04-16 14:26:17Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the main archiving process.
"""


import os
import logging
from tempfile import NamedTemporaryFile
from StringIO import StringIO

from datafinder.core.configuration.properties.constants import ARCHIVE_ROOT_COLLECTION_ID, \
                                                               ARCHIVE_PART_INDEX_ID, ARCHIVE_PART_COUNT_ID
from datafinder.core.item.data_persister.constants import ITEM_STATE_ARCHIVED, ITEM_STATE_ARCHIVED_MEMBER, \
                                                          ITEM_STATE_ARCHIVED_READONLY, ITEM_STATE_NULL
from datafinder.core.item.visitor.importer import Importer
from datafinder.core.error import ItemError, CoreError
from datafinder.persistence.error import PersistenceError


__version__ = "$LastChangedRevision: 4613 $"


_log = logging.getLogger()

_STOP_TRAVERSAL_STATES = [ITEM_STATE_ARCHIVED, ITEM_STATE_ARCHIVED_READONLY]
_STOP_PROCESSING_STATES = [ITEM_STATE_ARCHIVED_MEMBER]

_ARCHIVE_SUFFIX = " Archive"


class Archiver(object):
    """ Implements the archiving process. """
     
    def __init__(self, repository, repositoryManager):
        """ Constructor. """
        
        self._repository = repository
        self._repositoryManager = repositoryManager
     
    def create(self, sourceCollection, parentCollection, properties=None):
        """
        Initially creates a new archive. 
        
        @param sourceCollection: Identifies the collection which should be archived.
        @type sourceCollection: L{ItemCollection<datafinder.core.item.collection.ItemCollection>}
        @param parentCollection: Identifies the collection which later contains the created archive.
        @type parentCollection: L{ItemCollection<datafinder.core.item.collection.ItemCollection>}
        @param properties: Optional list of properties of the newly created archive root collection. Default: C{None}
        @type properties: C{list} of L{Property<datafinder.core.item.property.Property>}
        
        @raise ItemError: Indicating errors during creation of the archive.
        """
        
        if properties is None:
            properties = list()
        self._checkPreConditions(sourceCollection, properties)

        archiveRoot = self._createArchiveRoot(sourceCollection, parentCollection, properties)
        try:
            self._storeArchiveData(sourceCollection, archiveRoot)
            self._performPostArchivingActions(sourceCollection, archiveRoot)
        except ItemError, error:
            try:
                archiveRoot.delete()
            except ItemError:
                if archiveRoot.properties[ARCHIVE_PART_COUNT_ID].value == 0:
                    archiveRoot.delete(True)
                else:
                    archiveRoot.refresh()
            raise error
    
    def _checkPreConditions(self, sourceItem, properties):
        """ Sanity checks before the archive process starts. """
        
        if not sourceItem.capabilities.canArchive:
            raise ItemError("The item '%s' cannot be archived." %  sourceItem.path)
        
        missingPropertyIds = list()
        for property_ in properties:
            if not property_.propertyDefinition in self._repository.configuration.defaultArchivePropertyDefinitions:
                missingPropertyIds.append(property_.propertyDefinition.identifier)
        if len(missingPropertyIds) > 0:
            errorMessage = "The following properties are missing:"
            for propertyId in missingPropertyIds:
                errorMessage += "\n" + propertyId
            raise ItemError(errorMessage)

    def _createArchiveRoot(self, sourceItem, targetCollection, properties):
        """ Determines the target archive item. """
        
        if self._repository.configuration.isManagedRepository:
            name = self._repository.determineUniqueItemName(sourceItem.name + _ARCHIVE_SUFFIX, targetCollection)
            properties += sourceItem.properties.values()
            properties.append(self._repository.createProperty(ARCHIVE_PART_COUNT_ID, 0))
            archiveRoot = self._repository.createCollection(name, targetCollection)
        else:
            name = self._repository.determineUniqueItemName(sourceItem.name + ".zip", targetCollection)
            archiveRoot = self._repository.createLeaf(name, targetCollection)
        
        try:
            archiveRoot.create(properties)
        except CoreError, error:
            try:
                archiveRoot.delete(True)
            except ItemError:
                raise error
            raise error
        else:
            return archiveRoot
    
    def _storeArchiveData(self, sourceCollection, archiveRoot):
        """ Collects data which has to be archived and stores it. """
        
        importedLeafs = list()
        temporaryFilePath = self._determineTemporaryFilePath()
        try:
            # put everything in a temporary file
            cwr = self._repositoryManager.workingRepository
            archiveRepository = self._repositoryManager.connectRepository("arch:" + temporaryFilePath)
            try:
                importer = Importer(_STOP_TRAVERSAL_STATES, _STOP_PROCESSING_STATES)
                for item in sourceCollection.getChildren():
                    importer.performImport(item, archiveRepository.root, ignoreLinks=True)
                    importedLeafs += importer.importedLeafs
            finally:
                self._repositoryManager.disconnectRepository(archiveRepository)
                self._repositoryManager.workingRepository = cwr

            # store it - when necessary
            if len(importedLeafs) > 0:
                try:
                    archiveRoot.dataPersister.storeData(open(temporaryFilePath, "rb")) 
                except (OSError, IOError):
                    raise ItemError("Unable to access temporary created archive data.")
        finally:
            try:
                os.remove(temporaryFilePath)
            except OSError:
                _log.debug("Cannot remove temporary file '%s'" % temporaryFilePath)
        return importedLeafs
                    
    @staticmethod
    def _determineTemporaryFilePath():
        """ Determines a temporary file path and returns it. """
        
        try:
            tmpFile = NamedTemporaryFile()
            tmpFile.close()
        except (OSError, IOError):
            raise ItemError("Cannot determine temporary file name.")
        else:
            return tmpFile.name

    def _performPostArchivingActions(self, sourceItem, targetItem):
        """ Performs post archiving actions. """
        
        if self._repository.configuration.isManagedRepository:
            properties = [self._repository.createProperty(ARCHIVE_ROOT_COLLECTION_ID, targetItem.path),
                          self._repository.createProperty(ARCHIVE_PART_INDEX_ID, 0)]
            failedCopiedItems = list()
            importer = Importer(_STOP_TRAVERSAL_STATES, _STOP_PROCESSING_STATES)
            for sourceItem in sourceItem.getChildren():
                try:
                    importer.performImport(sourceItem, targetItem, defaultProperties=properties, 
                                           copyData=False, ignoreLinks=True)
                except CoreError, error:
                    failedCopiedItems.append((sourceItem, error.message))
            
            if len(failedCopiedItems) > 0:
                errorMessage = "Problems occurred while performing post archiving action." \
                               + "The following items could not be copied:"
                for sourceItem, message in failedCopiedItems:
                    errorMessage += "\n" + sourceItem.path + " Reason: " + message
                raise ItemError(errorMessage)
            else:
                targetItem.refresh()
            
    def commit(self, archiveRoot):
        """ 
        Commits an existing archive. 

        @param archiveRoot: Identifies the archive root collection. Only collections with the associated state C{ITEM_STATE_ARCHIVED}
                            can be committed.
        @type archiveRoot: L{ItemCollection<datafinder.core.item.collection.ItemCollection>}
        
        @raise ItemError: Indicating errors during commit of the given archive.
        """
        
        if not archiveRoot.state in (ITEM_STATE_ARCHIVED, ITEM_STATE_ARCHIVED_READONLY):
            raise ItemError("Archive '%s' cannot be committed as it is no archive or a read-only archive." % archiveRoot.path)

        importedLeafs = self._storeArchiveData(archiveRoot, archiveRoot)

        # Update properties of newly added archive members
        partIndex = archiveRoot.properties[ARCHIVE_PART_COUNT_ID].value - 1
        if partIndex < 0:
            partIndex = 0
        properties = [self._repository.createProperty(ARCHIVE_ROOT_COLLECTION_ID, archiveRoot.path),
                      self._repository.createProperty(ARCHIVE_PART_INDEX_ID, partIndex)]
            
        for importedLeaf in importedLeafs:
            try:
                if importedLeaf.fileStorer == importedLeaf.dataPersister.fileStorer:
                    importedLeaf.storeData(StringIO("")) # When data is not stored on an external storage then it is set to "0"
                else:
                    importedLeaf.dataPersister.delete()
                importedLeaf.updateProperties(properties)
                parent = importedLeaf.parent
                while not parent is None and parent.state == ITEM_STATE_NULL: # is a true collection
                    parent.updateProperties(properties)
                    parent = parent.parent
            except (CoreError, ItemError, PersistenceError), error:
                _log.error("Cannot update item '%s'. Reason: '%s'" % error.message)
                continue
        archiveRoot.refresh()
