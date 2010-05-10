#
# Created: 24.11.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: create_collection_state_handler.py 4525 2010-03-06 12:13:44Z schlauch $ 
# 
# Copyright (c) 2009, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Handler for create collection wizard.
"""


from datafinder.gui.user.dialogs.creation_wizard.constants import PROPERTY_PAGE_ID, SOURCE_PAGE_ID
from datafinder.gui.user.dialogs.creation_wizard.state_handler.base_state_handler import BaseStateHandler
from datafinder.gui.user.models.repository.filter.leaf_filter import LeafFilter


__version__ = "$LastChangedRevision: 4525 $"


class CreateCollectionHandler(BaseStateHandler):
    """ Handles collection creation. """
    
    WINDOW_TITLE = "New Collection"
    _PAGEID_TITLE_SUBTITLE_MAP = {SOURCE_PAGE_ID: ("Collection", "Creates a new collection."),
                                  PROPERTY_PAGE_ID: ("Collection Properties", "Please attach additional information to the collection.")}
    _ITEMNAME_LABEL_TEXT = "Collection name:"

    def __init__(self, wizard):
        """ Constructor. """
        
        BaseStateHandler.__init__(self, wizard)
        self._repositoryModel = wizard.sourceRepositoryModel
        self._currentSourceIndex = None
        self.lockIndex = None # Redefining it because check-in pylint wants it
        
    def nextId(self):
        """ Returns the identifier of the next page. """
        
        nextId = -1
        if self._repositoryModel.hasCustomMetadataSupport \
           and self._wizard.currentId() == SOURCE_PAGE_ID:
            nextId = PROPERTY_PAGE_ID
        return nextId

    def initializePage(self, identifier):
        """ Performs initialization actions for the wizard page with the given identifier. """
        
        if identifier == SOURCE_PAGE_ID:
            self._wizard.configureSourceItemPage(LeafFilter(self._repositoryModel), 
                                                 [self._repositoryModel.activeIndex],
                                                 self._ITEMNAME_LABEL_TEXT,
                                                 self._repositoryModel.isManagedRepository)
        else:
            indexChanged = self._currentSourceIndex != self._wizard.sourceIndexes[0]
            self._currentSourceIndex = self._wizard.sourceIndexes[0]
            
            self._wizard.configurePropertyPage(self._repositoryModel, True, self._currentSourceIndex, indexChanged)
    
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
        
        self._repositoryModel.createCollection(self._wizard.sourceItemName, 
                                               self.lockIndex,
                                               self._wizard.properties)
