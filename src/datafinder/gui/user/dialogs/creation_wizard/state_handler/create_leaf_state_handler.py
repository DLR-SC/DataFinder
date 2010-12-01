# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
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
Handles leaf creation.
"""


from datetime import datetime
        
from datafinder.core.configuration.properties.constants import CONTENT_CREATION_DATETIME_PROPERTY_ID, CONTENT_MODIFICATION_DATETIME_ID, \
                                                               CONTENT_SIZE_ID, DATA_FORMAT_ID, DATAMODEL_PROPERTY_CATEGORY
from datafinder.gui.user.dialogs.creation_wizard.constants import DATASTORE_PAGE_ID, PROPERTY_PAGE_ID, SOURCE_PAGE_ID, \
                                                                  OFFLINE_DATASTORE_MODE
from datafinder.gui.user.dialogs.creation_wizard.state_handler.base_state_handler import BaseStateHandler
from datafinder.gui.user.models.repository.filter.leaf_filter import LeafFilter


__version__ = "$Revision-Id:$" 


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
