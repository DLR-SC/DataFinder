# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#
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
This is the main controller component of the wizard
"""


from PyQt4 import QtGui, QtCore

from datafinder.common.logger import getDefaultLogger
from datafinder.gui.gen.user.creation_wizard_ui import Ui_Wizard
from datafinder.gui.user.common.progress_dialog import ProgressDialog
from datafinder.gui.user.dialogs.creation_wizard import constants
from datafinder.gui.user.dialogs.creation_wizard.error_handler import ErrorHandler
from datafinder.gui.user.dialogs.creation_wizard.pages.item_selection_page import ItemSelectionWizardPage
from datafinder.gui.user.dialogs.creation_wizard.state_handler.create_archive_state_handler import CreateArchiveHandler
from datafinder.gui.user.dialogs.creation_wizard.state_handler.create_collection_state_handler import CreateCollectionHandler
from datafinder.gui.user.dialogs.creation_wizard.state_handler.create_link_state_handler import CreateLinkHandler
from datafinder.gui.user.dialogs.creation_wizard.state_handler.create_leaf_state_handler import CreateLeafHandler
from datafinder.gui.user.dialogs.creation_wizard.state_handler.export_state_handler import ExportHandler
from datafinder.gui.user.dialogs.creation_wizard.state_handler.import_state_handler import ImportHandler


__version__ = "$Revision-Id:$" 


class CreationWizard(QtGui.QWizard, Ui_Wizard):
    """ Main controller of the wizard. """
    
    ARCHIVE_STATE = 0
    COLLECTION_STATE = 1
    EXPORT_STATE = 2
    IMPORT_STATE = 3
    LEAF_STATE = 4
    LINK_STATE = 5
    
    _stateWizardHandlerMap = {ARCHIVE_STATE: CreateArchiveHandler,
                              COLLECTION_STATE: CreateCollectionHandler,
                              EXPORT_STATE: ExportHandler,
                              IMPORT_STATE: ImportHandler,
                              LEAF_STATE: CreateLeafHandler,
                              LINK_STATE: CreateLinkHandler}
    
    _logger = getDefaultLogger()
    
    
    def __init__(self, sourceBaseRepositoryModel, targetBaseRepositoryModel, parent=None, preSelectedSourceItems=None):
        """
        Constructor.
        
        @param sourceBaseRepositoryModel: Reference on the not filtered source repository model.
        @type sourceBaseRepositoryModel: L{RepositoryModel<datafinder.gui.user.models.repository.repository.RepositoryModel>}
        @param targetBaseRepositoryModel: Reference on the not filtered target repository model.
        @type targetBaseRepositoryModel: L{RepositoryModel<datafinder.gui.user.models.repository.repository.RepositoryModel>}
        @param parent: Parent widget of this dialog.
        @type parent: L{QWidget<PyQt4.QtGui.QWidget>}
        """

        QtGui.QWizard.__init__(self, parent)
        Ui_Wizard.__init__(self)
        self.setupUi(self)
        
        self._sourceBaseRepositoryModel = sourceBaseRepositoryModel
        self._targetBaseRepositoryModel = targetBaseRepositoryModel
        self.preSelectedSourceItems = preSelectedSourceItems
        
        self._stateHandler = None
        self._progressDialog = None
        self._errorHandler = ErrorHandler(self)
        
    def start(self, state):
        """ 
        Initializes and starts the wizard. 
        
        @param state: Constant specifying the state of the wizard.
        @type state: C{int}
        """

        self._stateHandler = self._stateWizardHandlerMap[state](self)
        result = self._stateHandler.checkPreConditions()
        if not result is None:
            QtGui.QMessageBox.critical(self.parent(), self._stateHandler.WINDOW_TITLE, result)
        else:
            self.setWindowTitle(self._stateHandler.WINDOW_TITLE)
            self.connect(self.button(QtGui.QWizard.FinishButton), 
                         QtCore.SIGNAL("clicked()"), 
                         self._finishSlot)
            self.sourceChoserWizardPage.pageMode = ItemSelectionWizardPage.SOURCE_ITEM_PAGE
            self.targetChoserWizardPage.pageMode = ItemSelectionWizardPage.TARGET_ITEM_PAGE
            self.propertyWidget.deactivateRefreshButton()
            self.exec_()

    def _finishSlot(self):
        """ Returns function including error handling for the specific creation action. """
        
        self._progressDialog = ProgressDialog(self._stateHandler.WINDOW_TITLE, "", parent=self.parent())
        self._stateHandler.prepareFinishSlot()
        self._progressDialog._cb = self._stateHandler.finishSlotCallback
        self._progressDialog.start(self._stateHandler.finishSlot)

    def nextId(self):
        """ @see: L{nextId<PyQt4.QtGui.QWizard.nextId>} """
        
        try:
            return self._stateHandler.nextId()
        except KeyError:
            return -1
    
    def initializePage(self, identifier):
        """ @see: L{initializePage<PyQt4.QtGui.QWizard.initializePage>} """

        page = self.page(identifier)
        page.errorHandler = self.errorHandler
        self._stateHandler.initializePage(identifier)
        page.setTitle(self._stateHandler.currentTitle)
        page.setSubTitle(self._stateHandler.currentSubTitle)
        self.errorHandler.udpateErrorDisplay()
        
    def cleanupPage(self, identifier):
        """ @see: L{cleanupPage<PyQt4.QtGui.QWizard.cleanupPage>} """
        
        self._stateHandler.cleanupPage(identifier)
        self.errorHandler.clear()

    def configureSourceItemPage(self, filteredRepositoryModel, preSelectedIndexes, itemNameLabelText="", 
                                checkTargetDataTypesExistence=False, disableItemNameSpecification=False,
                                selectionMode=QtGui.QAbstractItemView.SingleSelection, itemCheckFunction=None):
        """ Prepares the source item wizard page. """

        
        if itemCheckFunction is None:
            itemCheckFunction = self.sourceChoserWizardPage.itemCheckFunction
        self._configureItemChoserPage(self.sourceChoserWizardPage, filteredRepositoryModel, preSelectedIndexes, itemNameLabelText, 
                                      checkTargetDataTypesExistence, disableItemNameSpecification, selectionMode, None, itemCheckFunction)
        
    @staticmethod
    def _configureItemChoserPage(choserWizardPage, filteredRepositoryModel, preSelectedIndexes, itemNameLabelText="", 
                                 checkTargetDataTypesExistence=False, disableItemNameSpecification=False,
                                 selectionMode=QtGui.QAbstractItemView.SingleSelection, targetIndex=None, 
                                 itemCheckFunction=None):
        """ Prepares the item wizard page. """

        choserWizardPage.filteredRepositoryModel = filteredRepositoryModel
        choserWizardPage.preSelectedIndexes = preSelectedIndexes
        choserWizardPage.itemNameLabelText = itemNameLabelText
        choserWizardPage.checkTargetDataTypesExistence = checkTargetDataTypesExistence
        choserWizardPage.disableItemNameSpecification = disableItemNameSpecification
        choserWizardPage.selectionMode = selectionMode
        choserWizardPage.targetIndex = targetIndex
        choserWizardPage.itemCheckFunction = itemCheckFunction
        choserWizardPage.configure()

    def configureTargetItemPage(self, filteredRepositoryModel, preSelectedIndexes, itemNameLabelText="", 
                                checkTargetDataTypesExistence=False, disableItemNameSpecification=False,
                                selectionMode=QtGui.QAbstractItemView.SingleSelection, targetIndex=None):
        """ Prepares the target item wizard page. """
        
        self._configureItemChoserPage(self.targetChoserWizardPage, filteredRepositoryModel, preSelectedIndexes, itemNameLabelText, 
                                      checkTargetDataTypesExistence, disableItemNameSpecification, selectionMode, targetIndex)
        
    def configureDataStorePage(self, dataStoreMode, baseRepositoryModel):
        """ Prepares the source item wizard page. """

        self.datastoreChoserWizardPage.dataStoreMode = dataStoreMode
        self.datastoreChoserWizardPage.iconProvider = baseRepositoryModel.iconProvider
        self.datastoreChoserWizardPage.dataStoreHandler = baseRepositoryModel.repository.configuration.dataStoreHandler
        self.datastoreChoserWizardPage.preferences = baseRepositoryModel.repository.configuration.preferences
        self.datastoreChoserWizardPage.configure()
    
    def configurePropertyPage(self, baseRepositoryModel, isDataTypeSelectionEnabled, index=QtCore.QModelIndex(), 
                              indexChanged=True, initialProperties=None):
        """ Prepares the source item wizard page. """
        
        self.propertyChoserWizardPage.baseRepositoryModel = baseRepositoryModel
        self.propertyChoserWizardPage.isDataTypeSelectionEnabled = isDataTypeSelectionEnabled
        self.propertyChoserWizardPage.index = index
        self.propertyChoserWizardPage.indexChanged = indexChanged
        self.propertyChoserWizardPage.initialProperties = initialProperties
        self.propertyChoserWizardPage.configure()
        
    @property
    def sourceItemName(self):
        """ Returns the specified item name or C{None}. """
        
        return self._getItemName(constants.SOURCE_PAGE_ID, self.sourceItemNameLineEdit)
    
    @property
    def targetItemName(self):
        """ Returns the specified item name or C{None}. """
        
        return self._getItemName(constants.TARGET_PAGE_ID, self.targetItemNameLineEdit)
    
    def _getItemName(self, pageId, lineEdit):
        """ Retrieves the item name. """
        
        itemName = None
        if self.hasVisitedPage(pageId) \
           and not self.page(pageId).disableItemNameSpecification:
            itemName = unicode(lineEdit.text())
            itemName.strip()
        return itemName
    
    @property
    def sourceIndexes(self):
        """ Returns the specified source indexes or C{None}. """
        
        sourceIndexes = None
        if self.hasVisitedPage(constants.SOURCE_PAGE_ID):
            sourceIndexes = self.sourceSelectItemWidget.selectedIndexes
        return sourceIndexes
    
    @property
    def targetIndexes(self):
        """ Returns the specified target indexes or C{None}. """
        
        targetIndexes = None
        if self.hasVisitedPage(constants.TARGET_PAGE_ID):
            targetIndexes = self.targetSelectItemWidget.selectedIndexes
        return targetIndexes

    @property
    def properties(self):
        """ Returns the specified properties or C{None}. """
        
        properties = None
        if self.hasVisitedPage(constants.PROPERTY_PAGE_ID):
            propertyModel = self.propertyWidget.model
            properties = propertyModel.properties
        return properties

    @property
    def dataStoreName(self):
        """ Returns the specified data store or C{None}. """
        
        dataStoreName = None
        if self.hasVisitedPage(constants.DATASTORE_PAGE_ID):
            dataStoreName = unicode(self.dataStoreComboBox.currentText())
        return dataStoreName
    
    @property
    def dataStoreConfiguration(self):
        """ Returns the specified data store configuration or C{None}. """
        
        dataStoreConfiguration = None
        if self.hasVisitedPage(constants.DATASTORE_PAGE_ID):
            dataStoreConfiguration = self.page(constants.DATASTORE_PAGE_ID).selectedDataStoreConfiguration
        return dataStoreConfiguration
    
    @property
    def sourceRepositoryModel(self):
        """ Getter of the source repository. """
        
        return self._sourceBaseRepositoryModel

    @property
    def targetRepositoryModel(self):
        """ Getter of the target repository. """
        
        return self._targetBaseRepositoryModel

    @property
    def errorHandler(self):
        """ Getter of the central error handler instance. """
        
        return self._errorHandler

    @property
    def currentSubTitle(self):
        """ Returns the current default sub title of the create collection wizard. """
        
        return self._stateHandler.currentSubTitle

    @property
    def currentTitle(self):
        """ Returns the current default title of the create collection wizard. """
        
        return self._stateHandler.currentTitle
