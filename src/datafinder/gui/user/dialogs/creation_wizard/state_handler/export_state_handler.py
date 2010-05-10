#
# Created: 24.11.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: export_state_handler.py 4599 2010-04-12 13:12:11Z schlauch $ 
# 
# Copyright (c) 2009, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Handler for export of item to the unmanaged repository.
"""


from PyQt4 import QtGui

from datafinder.gui.user.dialogs.creation_wizard.constants import SOURCE_PAGE_ID, TARGET_PAGE_ID
from datafinder.gui.user.dialogs.creation_wizard.state_handler.base_state_handler import BaseStateHandler
from datafinder.gui.user.models.repository.filter.leaf_filter import LeafFilter
from datafinder.gui.user.models.repository.filter.property_filter import PropertyFilter


__version__ = "$LastChangedRevision: 4599 $"


class ExportHandler(BaseStateHandler):
    """ Handles importing of items. """
    
    WINDOW_TITLE = "Export Items"
    _PAGEID_TITLE_SUBTITLE_MAP = {SOURCE_PAGE_ID: ("Export", "Exports items."),
                                  TARGET_PAGE_ID: ("Destination", "Please select the destination collection.")}

    def __init__(self, wizard):
        """ Constructor. """
        
        BaseStateHandler.__init__(self, wizard)
        self._sourceRepositoryModel = wizard.sourceRepositoryModel
        self._targetRepositoryModel = wizard.targetRepositoryModel
        self._currentSourceIndex = None
        self.lockIndex = None # Redefining it because check-in pylint wants it
        
    def checkPreConditions(self):
        """ Checks the preconditions. """
        
        if self._sourceRepositoryModel is None or self._targetRepositoryModel is None:
            return "Both repository models are not set. This should not happen."
        if not self._targetRepositoryModel.initialized:
            return "Please connect the shared data repository to import items."
        if self._targetRepositoryModel.isManagedRepository:
            return "The export is defined from the shared data repository into the local data repository."
        
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
                preSelectedSourceItems = [self._sourceRepositoryModel.activeIndex]
            self._wizard.configureSourceItemPage(PropertyFilter(self._sourceRepositoryModel, 
                                                                itemSelectionMode=PropertyFilter.ALL_SELECTION_MODE), 
                                                 preSelectedSourceItems, "",
                                                 False, True, QtGui.QAbstractItemView.MultiSelection,
                                                 itemCheckFunction=lambda item: item.capabilities.canRetrieveData \
                                                                                or item.isCollection and item.capabilities.canArchive)
        else:
            self._wizard.configureTargetItemPage(LeafFilter(self._targetRepositoryModel),
                                                 [self._targetRepositoryModel.activeIndex], "", False, True)

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
                                                  self.lockIndex)
