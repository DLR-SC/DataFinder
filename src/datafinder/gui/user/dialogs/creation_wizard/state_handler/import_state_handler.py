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
Handles import of item from a unmanaged repository.
"""


from PyQt4 import QtGui

from datafinder.gui.user.dialogs.creation_wizard.constants import DATASTORE_PAGE_ID, PROPERTY_PAGE_ID, SOURCE_PAGE_ID, \
                                                                  TARGET_PAGE_ID, ONLINE_DATASTORE_MODE
from datafinder.gui.user.dialogs.creation_wizard.state_handler.base_state_handler import BaseStateHandler
from datafinder.gui.user.models.repository.filter.leaf_filter import LeafFilter
from datafinder.gui.user.models.repository.filter.property_filter import PropertyFilter


__version__ = "$Revision-Id:$" 


class ImportHandler(BaseStateHandler):
    """ Handles import of items. """
    
    WINDOW_TITLE = "Import Items"
    _PAGEID_TITLE_SUBTITLE_MAP = {SOURCE_PAGE_ID: ("Import", "Imports a new files."),
                                  TARGET_PAGE_ID: ("Destination", "Please select the destination collection."),
                                  DATASTORE_PAGE_ID: ("Storage Location", "Please select the destination storage location."),
                                  PROPERTY_PAGE_ID: ("Item Properties", "Please attach additional information to the items.")}

    def __init__(self, wizard):
        """ Constructor. """
        
        BaseStateHandler.__init__(self, wizard)
        self._sourceRepositoryModel = wizard.sourceRepositoryModel
        self._targetRepositoryModel = wizard.targetRepositoryModel
        self._currentSourceIndex = None
        self.lockIndex = None # Redefining it because check-in pylint wants it
        
    def checkPreConditions(self):
        """ Checks the preconditions. """
        
        result = None
        if self._sourceRepositoryModel is None or self._targetRepositoryModel is None:
            result = "Both repository models are not set. This should not happen."
        if not self._targetRepositoryModel.initialized:
            result = "Please connect the shared data repository to import items."
        if not self._targetRepositoryModel.isManagedRepository:
            result = "The import is defined from the local data repository into the shared data repository."
        else:
            if len(self._targetRepositoryModel.repository.configuration.onlineDatastores) == 0:
                result = "There are no storage locations configured. Please contact your administrator."
        return result
        
    def nextId(self):
        """ Returns the identifier of the next page. """
        
        nextId = -1
        if self._wizard.currentId() == SOURCE_PAGE_ID:
            nextId = TARGET_PAGE_ID
        elif self._wizard.currentId() == TARGET_PAGE_ID:
            nextId = DATASTORE_PAGE_ID
        elif self._wizard.currentId() == DATASTORE_PAGE_ID:
            nextId = PROPERTY_PAGE_ID
        return nextId

    def initializePage(self, identifier):
        """ Performs initialization actions for the wizard page with the given identifier. """
        
        if identifier == SOURCE_PAGE_ID:
            preSelectedSourceItems = self._wizard.preSelectedSourceItems
            if preSelectedSourceItems is None:
                preSelectedSourceItems = [self._sourceRepositoryModel.activeIndex]
            self._wizard.configureSourceItemPage(PropertyFilter(self._sourceRepositoryModel), 
                                                 preSelectedSourceItems, "",
                                                 False, True, QtGui.QAbstractItemView.MultiSelection)
        elif identifier == TARGET_PAGE_ID:
            self._wizard.configureTargetItemPage(LeafFilter(self._targetRepositoryModel),
                                                 [self._targetRepositoryModel.activeIndex], "", False, True,
                                                 itemCheckFunction=lambda item: item.capabilities.canAddChildren)
        elif identifier == DATASTORE_PAGE_ID:
            self._wizard.configureDataStorePage(ONLINE_DATASTORE_MODE, self._targetRepositoryModel)
        else:
            self._wizard.configurePropertyPage(self._targetRepositoryModel, False)
    
    def prepareFinishSlot(self):
        """ Performs the finish slot preparation. """
        
        self.lockIndex = self._wizard.targetIndexes[0]
        self._targetRepositoryModel.lock([self.lockIndex])
        
    def finishSlotCallback(self):
        """ Unlocks the lock index. """
        
        self._targetRepositoryModel.unlock(self.lockIndex)
        self._targetRepositoryModel.activeIndex = self.lockIndex
    
    def finishSlot(self):
        """ Performs specific actions when the user commits his parameters. """

        self._targetRepositoryModel.performImport(self._wizard.sourceIndexes, 
                                                  self.lockIndex, 
                                                  self._wizard.properties)
