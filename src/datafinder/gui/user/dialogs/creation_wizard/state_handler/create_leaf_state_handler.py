#
# Created: 24.11.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: create_leaf_state_handler.py 4592 2010-04-09 11:50:10Z schlauch $ 
# 
# Copyright (c) 2009, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Handles leaf creation.
"""


from datetime import datetime
        
from datafinder.core.configuration.properties.constants import CONTENT_CREATION_DATETIME_PROPERTY_ID, CONTENT_MODIFICATION_DATETIME_ID, \
                                                               CONTENT_SIZE_ID, DATA_FORMAT_ID, DATAMODEL_PROPERTY_CATEGORY
from datafinder.gui.user.dialogs.creation_wizard.constants import DATASTORE_PAGE_ID, PROPERTY_PAGE_ID, SOURCE_PAGE_ID, \
                                                                  OFFLINE_DATASTORE_MODE
from datafinder.gui.user.dialogs.creation_wizard.state_handler.base_state_handler import BaseStateHandler
from datafinder.gui.user.models.repository.filter.leaf_filter import LeafFilter


__version__ = "$LastChangedRevision: 4592 $"


class CreateLeafHandler(BaseStateHandler):
    """ Handles leaf creation. """
    
    WINDOW_TITLE = "New Leaf"
    _PAGEID_TITLE_SUBTITLE_MAP = {SOURCE_PAGE_ID: ("Leaf", "Creates a new leaf."),
                                  DATASTORE_PAGE_ID: ("Storage Location", "Please select the destination location."),
                                  PROPERTY_PAGE_ID: ("Leaf Properties", "Please attach additional information to the leaf.")}
    _ITEMNAME_LABEL_TEXT = "Leaf name:"

    def __init__(self, wizard):
        """ Constructor. """
        
        BaseStateHandler.__init__(self, wizard)
        self._repositoryModel = wizard.sourceRepositoryModel
        self.lockIndex = None # Redefining it because check-in pylint wants it
        
    def checkPreConditions(self):
        """ Checks the preconditions. """
        
        result = None
        if self._repositoryModel.initialized and self._repositoryModel.isManagedRepository:
            if len(self._repositoryModel.repository.configuration.offlineDatastores) == 0:
                result = "There are no off-line storage locations configured. Please contact your administrator."
        return result
    
    def nextId(self):
        """ Returns the identifier of the next page. """
        
        nextId = -1
        if self._repositoryModel.isManagedRepository \
           and self._wizard.currentId() == SOURCE_PAGE_ID:
            nextId = DATASTORE_PAGE_ID
        elif self._repositoryModel.hasCustomMetadataSupport \
           and self._wizard.currentId() == DATASTORE_PAGE_ID:
            nextId = PROPERTY_PAGE_ID
        return nextId

    def initializePage(self, identifier):
        """ Performs initialization actions for the wizard page with the given identifier. """
        
        if identifier == SOURCE_PAGE_ID:
            self._wizard.configureSourceItemPage(LeafFilter(self._repositoryModel), 
                                                 [self._repositoryModel.activeIndex],
                                                 self._ITEMNAME_LABEL_TEXT)
        elif identifier == DATASTORE_PAGE_ID:
            self._wizard.configureDataStorePage(OFFLINE_DATASTORE_MODE, self._repositoryModel)
        else:
            initialProperties = self._determineInitialProperties()
            self._wizard.configurePropertyPage(self._repositoryModel, False, initialProperties=initialProperties)
    
    def _determineInitialProperties(self):
        """ Determines the initial properties for the property page. """
        
        properties = list()
        if self._repositoryModel.isManagedRepository:
            contentCreation = self._repositoryModel.repository.createProperty(CONTENT_CREATION_DATETIME_PROPERTY_ID, datetime.now())
            contentCreation.propertyDefinition.category = DATAMODEL_PROPERTY_CATEGORY
            properties.append(contentCreation)
            
            contentModification = self._repositoryModel.repository.createProperty(CONTENT_MODIFICATION_DATETIME_ID, datetime.now())
            contentModification.propertyDefinition.category = DATAMODEL_PROPERTY_CATEGORY
            properties.append(contentModification)
            
            contentSize = self._repositoryModel.repository.createProperty(CONTENT_SIZE_ID, 0)
            contentSize.propertyDefinition.category = DATAMODEL_PROPERTY_CATEGORY
            properties.append(contentSize)
        return properties

    def prepareFinishSlot(self):
        """ Performs the finish slot preparation. """
        
        self.lockIndex = self._wizard.sourceIndexes[0]
        self._repositoryModel.lock([self.lockIndex])
        
    def finishSlotCallback(self):
        """ Unlocks the lock index. """
        
        self._repositoryModel.unlock(self.lockIndex)
        self._repositoryModel.activeIndex = self.lockIndex
    
    def finishSlot(self):
        """ Performs specific actions when the user commits his parameters. """

        properties = list()
        if self._repositoryModel.hasCustomMetadataSupport:
            properties = self._wizard.properties
            dataFormatValue = self._repositoryModel.repository.configuration.determineDataFormat(baseName=self._wizard.sourceItemName)
            dataFormat = self._repositoryModel.repository.createProperty(DATA_FORMAT_ID, dataFormatValue.name)
            properties.append(dataFormat)
            
        self._repositoryModel.createLeaf(self._wizard.sourceItemName, 
                                         self.lockIndex,
                                         properties)
