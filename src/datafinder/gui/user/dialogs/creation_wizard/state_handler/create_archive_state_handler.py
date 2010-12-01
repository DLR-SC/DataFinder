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


""" Module implementing a wizard handler for archive creation. """


from datetime import datetime, timedelta

from datafinder.core.configuration.properties.constants import DATASTORE_NAME_ID, \
                                                               ARCHIVE_RETENTION_EXCEEDED_DATETIME_ID
from datafinder.gui.user.dialogs.creation_wizard import constants
from datafinder.gui.user.dialogs.creation_wizard.state_handler.base_state_handler import BaseStateHandler
from datafinder.gui.user.models.repository.filter.leaf_filter import LeafFilter


__version__ = "$Revision-Id:$" 


class CreateArchiveHandler(BaseStateHandler):
    """ Handles collection creation. """
    
    WINDOW_TITLE = "New Archive"
    
    _PAGEID_TITLE_SUBTITLE_MAP = {constants.SOURCE_PAGE_ID: ("Archive Collection", "Please select the collection that should be archived."),
                                  constants.TARGET_PAGE_ID: ("Target Collection",
                                                             "Select the collection where the archive should be stored."),
                                  constants.DATASTORE_PAGE_ID: ("Storage Location", "Please select the storage location of your archive.")}

    def __init__(self, wizard):
        """ Constructor. """
        
        BaseStateHandler.__init__(self, wizard)
        self._repositoryModel = wizard.sourceRepositoryModel
        self._sourceIndex = None
        self.lockIndex = None # Redefining it because check-in pylint wants it
        
    def checkPreConditions(self):
        """ Checks the preconditions. """
        
        result = None
        if self._repositoryModel.initialized and self._repositoryModel.isManagedRepository:
            if len(self._repositoryModel.repository.configuration.archiveDatastores) == 0:
                result = "There are no archive storage locations configured. Please contact your administrator."
        return result
    
    def nextId(self):
        """ Returns the identifier of the next page. """
        
        currentId = self._wizard.currentId()
        nextId = -1
        if currentId == constants.SOURCE_PAGE_ID:
            nextId = constants.TARGET_PAGE_ID
        elif currentId == constants.TARGET_PAGE_ID \
             and self._repositoryModel.repository.configuration.isManagedRepository:
            nextId = constants.DATASTORE_PAGE_ID
        return nextId

    def initializePage(self, identifier):
        """ Performs initialization actions for the wizard page with the given identifier. """
        
        if identifier == constants.SOURCE_PAGE_ID:
            preSelectedSourceItems = self._wizard.preSelectedSourceItems
            if preSelectedSourceItems is None or len(preSelectedSourceItems) == 0:
                preSelectedSourceItems = [self._repositoryModel.activeIndex]
            self._wizard.configureSourceItemPage(LeafFilter(self._repositoryModel), preSelectedSourceItems,
                                                 disableItemNameSpecification=True, 
                                                 itemCheckFunction=lambda item: item.capabilities.canArchive)
        elif identifier == constants.TARGET_PAGE_ID:
            self._wizard.configureTargetItemPage(LeafFilter(self._repositoryModel), [self._wizard.sourceIndexes[0].parent()],
                                                 disableItemNameSpecification=True, checkTargetDataTypesExistence=True,
                                                 targetIndex=self._wizard.sourceIndexes[0])
        else:
            self._wizard.configureDataStorePage(constants.ARCHIVE_DATASTORE_MODE, self._repositoryModel)
    
    def prepareFinishSlot(self):
        """ Performs the finish slot preparation. """
        
        self.lockIndex = self._wizard.targetIndexes[0]
        self._sourceIndex = self._wizard.sourceIndexes[0]
        self._repositoryModel.lock([self.lockIndex])
        
    def finishSlotCallback(self):
        """ Unlocks the lock index. """
        
        self._repositoryModel.unlock(self.lockIndex)
        self._repositoryModel.activeIndex = self.lockIndex
    
    def finishSlot(self):
        """ Performs specific actions when the user commits his parameters. """

        properties = None
        if self._repositoryModel.isManagedRepository:
            properties = list()
            dataStoreConfiguration = self._wizard.dataStoreConfiguration
            dataStoreProperty = self._repositoryModel.repository.createProperty(DATASTORE_NAME_ID, dataStoreConfiguration.name)
            properties.append(dataStoreProperty)
            try:
                rententionPeriod = dataStoreConfiguration.retentionPeriod or 1
                exeededDate = datetime.now() + timedelta(rententionPeriod)
            except (OverflowError, AttributeError):
                exeededDate = datetime.now() + timedelta(1)
                
            exeededDateProperty = self._repositoryModel.repository.createProperty(ARCHIVE_RETENTION_EXCEEDED_DATETIME_ID, exeededDate)
            properties.append(exeededDateProperty)

        self._repositoryModel.createArchive(self._sourceIndex, self.lockIndex, properties)
