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
Handles link creation.
"""


from PyQt4 import QtGui

from datafinder.gui.user.dialogs.creation_wizard.constants import SOURCE_PAGE_ID, TARGET_PAGE_ID
from datafinder.gui.user.dialogs.creation_wizard.state_handler.base_state_handler import BaseStateHandler
from datafinder.gui.user.models.repository.filter.leaf_filter import LeafFilter
from datafinder.gui.user.models.repository.filter.property_filter import PropertyFilter


__version__ = "$Revision-Id:$" 


class CreateLinkHandler(BaseStateHandler):
    """ Handles link creation. """
    
    WINDOW_TITLE = "New Link"
    _PAGEID_TITLE_SUBTITLE_MAP = {SOURCE_PAGE_ID: ("Source Items", "Please select the link sources."),
                                  TARGET_PAGE_ID: ("Target Collection", "Please select the destination location.")}

    def __init__(self, wizard):
        """ Constructor. """
        
        BaseStateHandler.__init__(self, wizard)
        self._repositoryModel = wizard.sourceRepositoryModel
        self._sourceIndexes = None
        self.lockIndex = None # Redefining it because check-in pylint wants it
        
    def nextId(self):
        """ Returns the identifier of the next page. """
        
        nextId = -1
        if self._wizard.currentId() == SOURCE_PAGE_ID:
            nextId = TARGET_PAGE_ID
        return nextId

    def initializePage(self, identifier):
        """ Performs initialization actions for the wizard page with the given identifier. """
        
        if identifier == SOURCE_PAGE_ID:
            preSelectedSourceItems = self._wizard.preSelectedSourceItems
            if preSelectedSourceItems is None:
                preSelectedSourceItems = [self._repositoryModel.activeIndex]
            self._wizard.configureSourceItemPage(PropertyFilter(self._repositoryModel, 
                                                                itemSelectionMode=PropertyFilter.ALL_SELECTION_MODE), 
                                                 preSelectedSourceItems,
                                                 disableItemNameSpecification=True,
                                                 selectionMode=QtGui.QAbstractItemView.MultiSelection,
                                                 itemCheckFunction=lambda _: True)
        elif identifier == TARGET_PAGE_ID:
            self._wizard.configureTargetItemPage(LeafFilter(self._repositoryModel), 
                                                 [self._repositoryModel.activeIndex],
                                                 disableItemNameSpecification=True)
    
    def prepareFinishSlot(self):
        """ Performs the finish slot preparation. """
        
        self.lockIndex = self._wizard.targetIndexes[0]
        self._sourceIndexes = self._wizard.sourceIndexes
        self._repositoryModel.lock([self.lockIndex])
        
    def finishSlotCallback(self):
        """ Unlocks the lock index. """
        
        self._repositoryModel.unlock(self.lockIndex)
        self._repositoryModel.activeIndex = self.lockIndex

    def finishSlot(self):
        """ Performs specific actions when the user commits his parameters. """

        for sourceIndex in self._sourceIndexes:
            sourceItem = self._repositoryModel.nodeFromIndex(sourceIndex)
            self._repositoryModel.createLink(sourceItem.name,
                                             self.lockIndex,
                                             sourceIndex,
                                             self._wizard.properties)
