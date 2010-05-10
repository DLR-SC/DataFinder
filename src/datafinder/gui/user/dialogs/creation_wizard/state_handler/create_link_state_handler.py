#
# Created: 24.11.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: create_link_state_handler.py 4599 2010-04-12 13:12:11Z schlauch $ 
# 
# Copyright (c) 2009, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Handles link creation.
"""


from PyQt4 import QtGui

from datafinder.gui.user.dialogs.creation_wizard.constants import SOURCE_PAGE_ID, TARGET_PAGE_ID
from datafinder.gui.user.dialogs.creation_wizard.state_handler.base_state_handler import BaseStateHandler
from datafinder.gui.user.models.repository.filter.leaf_filter import LeafFilter
from datafinder.gui.user.models.repository.filter.property_filter import PropertyFilter


__version__ = "$LastChangedRevision: 4599 $"


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
