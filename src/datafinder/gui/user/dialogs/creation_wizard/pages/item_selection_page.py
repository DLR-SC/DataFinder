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
Implements the specific of the source item page.
"""


from PyQt4 import QtCore, QtGui

from datafinder.core.error import ItemError
from datafinder.gui.user.dialogs.creation_wizard import constants
from datafinder.gui.user.dialogs.creation_wizard.pages.base_page import BaseWizardPage
from datafinder.gui.user.dialogs.creation_wizard.pages.utils import determineTargetDataTypes, dataTypesCompatible


__version__ = "$Revision-Id:$" 


class ItemSelectionWizardPage(BaseWizardPage):
    """ Implements the specific of the source item page. """

    SOURCE_ITEM_PAGE = 0
    TARGET_ITEM_PAGE = 1

    def __init__(self):
        """ Constructor. """
        
        BaseWizardPage.__init__(self)
        
        self._filteredRepositoryModel = None
        self._baseRepositoryModel = None
        self._itemNameValidator = None
        self._itemNameLabel = None
        self._itemNameLineEdit = None
        self._selectItemWidget = None
        self._pageMode = None
        
        self.preSelectedIndexes = list()
        self.itemNameLabelText = "File name:"
        self.checkTargetDataTypesExistence = False
        self.disableItemNameSpecification = False
        self.targetIndex = None
        self.itemCheckFunction = lambda item: item.capabilities.canAddChildren
        self.selectionMode = QtGui.QAbstractItemView.SingleSelection

    def configure(self):
        """ Configures the source item wizard page. """
        
        self._selectItemWidget.selectionMode = self.selectionMode
        self._selectItemWidget.repositoryModel = self._filteredRepositoryModel
        self._selectItemWidget.selectedIndexes = self.preSelectedIndexes
        
        if not self.disableItemNameSpecification:
            self._itemNameLabel.show()
            self._itemNameLineEdit.show()
            self._itemNameLabel.setText(self.itemNameLabelText)
            if self.preSelectedIndexes > 0:
                firstSelectedIndex = self.preSelectedIndexes[0]
            else:
                firstSelectedIndex = QtCore.QModelIndex()
            self._itemNameValidator = _ItemNameValidator(self._baseRepositoryModel, self.wizard().errorHandler,
                                                         self.checkTargetDataTypesExistence)
            self.connect(self._selectItemWidget, 
                         QtCore.SIGNAL(self._selectItemWidget.SELECTED_INDEX_CHANGED_SIGNAL),
                         self._itemNameValidator.handleCurrentIndexChanged)
            self._itemNameLineEdit.setValidator(self._itemNameValidator)
            self._itemNameValidator.handleCurrentIndexChanged(firstSelectedIndex)
        else:
            self.connect(self._selectItemWidget, 
                         QtCore.SIGNAL(self._selectItemWidget.SELECTION_CHANGED),
                         self._handleSelectionChanges)
            self._itemNameLabel.hide()
            self._itemNameLineEdit.hide()
            self._handleSelectionChanges()
            
    def _handleSelectionChanges(self):
        """ Handles selection changes when used in multiple selection mode. """
        
        selectedIndexes = self._selectItemWidget.selectedIndexes
        if len(selectedIndexes) == 0:
            errorMessage = "At least you have to chose one item."
            self._errorHandler.appendError(constants.MISSING_SELECTION, errorMessage)
        else:
            self._errorHandler.removeError(constants.MISSING_SELECTION)
            
            if not self.itemCheckFunction is None:
                childrenNotUsable = False
                for selectedIndex in selectedIndexes: 
                    item = self._baseRepositoryModel.nodeFromIndex(selectedIndex)
                    if not self.itemCheckFunction(item):
                        childrenNotUsable = True
                        break
                if childrenNotUsable:
                    errorMessage = "One of the chosen items can not be used to perform the specific action."
                    self._errorHandler.appendError(constants.CHILDREN_NOT_ADDABLE_ERROR_TYPE, errorMessage)
                else:
                    self._errorHandler.removeError(constants.CHILDREN_NOT_ADDABLE_ERROR_TYPE)
        
            if not self.targetIndex is None:
                if not dataTypesCompatible(self._baseRepositoryModel, self.targetIndex, selectedIndexes[0]):
                    errorMessage = "The selected item cannot be used as new parent as both data types are incompatible."
                    self._errorHandler.appendError(constants.INCOMPATIBLE_DATA_TYPES, errorMessage)
                else:
                    self._errorHandler.removeError(constants.INCOMPATIBLE_DATA_TYPES)

    
    def _setFilteredRepositoryModel(self, filteredRepositoryModel):
        """ Sets the repository (filtered or not) and determines the corresponding underlying repository instance. """
        
        self._filteredRepositoryModel = filteredRepositoryModel
        try:
            self._baseRepositoryModel = filteredRepositoryModel.repositoryModel
        except AttributeError:
            self._baseRepositoryModel = filteredRepositoryModel

    filteredRepositoryModel = property(None, _setFilteredRepositoryModel)

    def _getPageMode(self):
        """ Getter of the page mode. """
        
        return self._pageMode
    
    def _setPage(self, pageMode):
        """ Setter of the page mode. """
        
        self._pageMode = pageMode
        if self._pageMode == self.SOURCE_ITEM_PAGE:
            self._itemNameLabel = self.wizard().sourceItemNameLabel
            self._itemNameLineEdit = self.wizard().sourceItemNameLineEdit
            self._selectItemWidget = self.wizard().sourceSelectItemWidget
        else:
            self._itemNameLabel = self.wizard().targetItemNameLabel
            self._itemNameLineEdit = self.wizard().targetItemNameLineEdit
            self._selectItemWidget = self.wizard().targetSelectItemWidget

    pageMode = property(_getPageMode, _setPage)


class _ItemNameValidator(QtGui.QValidator):
    """ Custom validator for item name checking. """
    
    def __init__(self, baseRepositoryModel, errorHandler, 
                 checkTargetDataTypesExistence=False):
        """
        Constructor. 
        
        @param baseRepositoryModel: The not filtered repository model.
        @type baseRepositoryModel: L{RepositoryModel<datafinder.gui.user.models.repository.repository.RepositoryModel>}
        @param errorHandler: Reference to the error handler instance.
        @type errorHandler: L{ErrorHandler<datafinder.gui.user.dialogs.creation_wizard.error_handler.ErrorHandler>}
        @param checkTargetDataTypesExistence: Flag indicating that availability of data types is checked. Default: C{False}
        @type checkTargetDataTypesExistence: C{bool}
        """
        
        QtGui.QValidator.__init__(self, None)

        self._baseRepositoryModel = baseRepositoryModel
        self._errorHandler = errorHandler
        self._checkTargetDataTypesExistence = checkTargetDataTypesExistence
        
        self._item = None
        self._currentItemName = ""
        
    def validate(self, itemName, position):
        """ Overwrites the default implementation. """
        
        self._currentItemName = unicode(itemName)
        self._performItemNameValidation()
        return (QtGui.QValidator.Acceptable, position)

    def handleCurrentIndexChanged(self, index):
        """ Handles selection of a new index when used in single selection mode. """
        
        self._item = self._baseRepositoryModel.nodeFromIndex(index)
        if not self._item.capabilities.canAddChildren:
            errorMessage = "Below the chosen item no further items can be added."
            self._errorHandler.appendError(constants.CHILDREN_NOT_ADDABLE_ERROR_TYPE, errorMessage)
        else:
            self._errorHandler.removeError(constants.CHILDREN_NOT_ADDABLE_ERROR_TYPE)
    
        if self._checkTargetDataTypesExistence:
            dataTypes = determineTargetDataTypes(self._baseRepositoryModel, index)
            if len(dataTypes) == 0:
                errorMessage = "Data model defines no usable data types below the selected item."
                self._errorHandler.appendError(constants.MISSING_TARGET_DATA_TYPES_ERROR_TYPE, errorMessage)
            else:
                self._errorHandler.removeError(constants.MISSING_TARGET_DATA_TYPES_ERROR_TYPE)
        
        self._performItemNameValidation()

    def _performItemNameValidation(self):
        """ Performs the validation of the currently used item name. """
        
        if not self._item is None:
            itemName = self._currentItemName
            errorMessage = None
            try:
                hasChild = self._item.hasChild(itemName, True)
            except ItemError:
                hasChild = False
            if not hasChild:
                isValid = self._baseRepositoryModel.isValidIdentifier(itemName)
                if not isValid[0]:
                    if isValid[1] is None:
                        errorMessage = "The item name is empty."
                    else:
                        errorMessage = "'%s' is no valid character." % itemName[isValid[1]]
            else:
                errorMessage = "An item with this name already exists below the selected collection."
            
            if errorMessage is None:
                self._errorHandler.removeError(constants.INVALID_NAME_ERROR_TYPE)
            else:
                self._errorHandler.appendError(constants.INVALID_NAME_ERROR_TYPE, errorMessage)
