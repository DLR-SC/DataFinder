# pylint: disable=R0902, C0302
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
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
Main window of DataFinder administration client.
"""


import sys
import os

from qt import QPixmap, QIconSet, QMessageBox, QLabel
from qt import SIGNAL, QApplication
from qt import QGridLayout, PYSIGNAL, QListViewItem, QFileDialog
from qt import QPoint, SLOT

from datafinder.core.repository_manager import RepositoryManager
from datafinder.common.logger import getDefaultLogger
from datafinder.core.configuration.datamodel.constants import ROOT_RELATION_NAME
from datafinder.core.error import ConfigurationError
from datafinder.gui.gen.AdminMainWindowForm import AdminWindow
from datafinder.gui.admin import about_dialog
from datafinder.gui.admin import login_dialog
from datafinder.gui.admin.common import logger_handler
from datafinder.gui.admin.common import utils
from datafinder.gui.admin.datamodel_iconview import canvas_view
from datafinder.gui.admin import script_selection_dialog
from datafinder.gui.admin import icon_selection_dialog
from datafinder.gui.admin.datastore_configuration_wizard.controller import DataStoreConfigurationWizardController
from datafinder.gui.admin import relation_type_dialog
from datafinder.gui.admin import data_type_dialog
from datafinder.gui.admin.create_configuration_dialog.controller import CreateConfigurationController


__version__ = "$Revision-Id:$" 


class AdminMain(AdminWindow):
    """ Implements the administration client functionality. """

    __tabDataTypesTitle = "Data Types"
    __tabRelationTypesTitle = "Relation Types"
    __tabDataStoresTitle = "Data Stores"

    __baseCaption = "DataFinder Administration Client - Server: "
    __errorMessageCaption = "DataFinder Administration Client: Error"
    __informationMessageCaption = "DataFinder Administration Client: Information"

    __logger = getDefaultLogger()

    def __init__(self, repositoryManager):
        """ Constructor. """

        # Init GUI
        AdminWindow.__init__(self)
        
        # set icon in window-title:
        self.setIcon(QPixmap.fromMimeSource("DF_Logo_24x24.png"))
        iconSet = QIconSet(QPixmap.fromMimeSource("dataType16.png"))
        self.dataNavigator.setTabIconSet(self.dataTypes, iconSet)
        iconSet = QIconSet(QPixmap.fromMimeSource("relationType16.png"))
        self.dataNavigator.setTabIconSet(self.relationTypes, iconSet)
        iconSet = QIconSet(QPixmap.fromMimeSource("dataStore16.png"))
        self.dataNavigator.setTabIconSet(self.dataStores, iconSet)

        logger_handler.installGuiLoggingHandler(self.__logger, self.logList)

        self.myStatusBar = self.statusBar()
        self.statusLabel1 = QLabel("DataFinder", self.myStatusBar)
        self.statusLabel2 = QLabel("OK", self.myStatusBar)

        self.myStatusBar.addWidget(self.statusLabel1, 80)
        self.myStatusBar.addWidget(self.statusLabel2, 20)

        self.statusLabel1.show()
        self.statusLabel2.show()
        self.myStatusBar.show()

        # prepare "About"-dialog:
        self.dfAboutDialog = about_dialog.AboutDialog()
        self.dfAboutDialog.setPixmap(QPixmap.fromMimeSource("about_datafinder_admin.png"))

        # Login-dialog:
        self.dfLoginDialog = login_dialog.LoginDialog(repositoryManager.preferences, parent=self, showurl=True)

        # IconView:
        propertyPanelLayout = QGridLayout(self.propertyPanel, 1, 1, 2, 6, "propertyPanelLayout")

        self.iconView = canvas_view.CanvasView(self.propertyPanel, self, "iconView", 0)
        propertyPanelLayout.addWidget(self.iconView, 0, 0)

        self.iconViewCanvas = self.iconView.canvas()

        self.connect(self.dfLoginDialog.okPushButton,
                     PYSIGNAL("updateWebdavServerView"),
                     self.updateWebdavServerSlot)
        self.connect(self.dataTypeBrowser, SIGNAL("doubleClicked(QListViewItem*)"), self.__addDataTypeIconSlot)
        self.connect(self.relationTypeBrowser, SIGNAL("doubleClicked(QListViewItem*)"), self.__addRelationTypeIconSlot)
        self.connect(self.dataStoreBrowser, SIGNAL("clicked(QListViewItem*)"), self.iconView.updateCanvasView)
        self.connect(self.dataStoreBrowser, SIGNAL("doubleClicked(QListViewItem*)"), self.editSlot)
        
        # Init model
        self._repositoryManager = repositoryManager
        self.repositoryConfiguration = None
        self._preferences = self._repositoryManager.preferences
        self._lastUploadDirectory = os.path.expanduser("~")

        self._dataTypes = list()
        self._relationTypes = list()
        self._dataStores = list()

        self.__setConnectionState(False)

    def __setConnectionState(self, isConnected):
        """
        Sets the enabled state of the actions in accordance to
        successful or unsuccessful connection.
        """

        self.iconView.clear()
        self.__setActionEnabledState(isConnected)
        
        if isConnected:
            self.setCaption(self.__baseCaption + unicode(self.repositoryConfiguration.repositoryConfigurationUri))
            iconPath = self.repositoryConfiguration.localIconFilePath
            if sys.platform == "win32" and iconPath.startswith("/"):
                iconPath = iconPath[1:]
            utils.addQtImagePath(iconPath)
        else:
            self.repositoryConfiguration = None
            enableActions = [self.fileConnectAction, self.fileExitAction,
                             self.fileCreateConfigurationAction, self.editPreferencesAction,
                             self.helpAboutAction]
            for action in enableActions:
                action.setEnabled(True)
            self.setCaption(self.__baseCaption + "<not connected>")

        self.updateDataTypes()
        self.updateRelationTypes()
        self.updateDataStores()

    def __setActionEnabledState(self, isEnabled):
        """ Sets the enabled state of all actions. """

        self.datamodelExportAction.setEnabled(isEnabled)
        self.datamodelImportAction.setEnabled(isEnabled)
        self.datamodelNewDataTypeAction.setEnabled(isEnabled)
        self.datamodelNewRelationTypeAction.setEnabled(isEnabled)
        self.deleteAction.setEnabled(isEnabled)
        self.editAction.setEnabled(isEnabled)
        self.editPreferencesAction.setEnabled(isEnabled)
        self.fileConnectAction.setEnabled(isEnabled)
        self.fileCreateConfigurationAction.setEnabled(isEnabled)
        self.fileDeleteConfigurationAction.setEnabled(isEnabled)
        self.fileExitAction.setEnabled(isEnabled)
        self.helpAboutAction.setEnabled(isEnabled)
        self.reloadConfigurationAction.setEnabled(isEnabled)
        self.storeExportAction.setEnabled(isEnabled)
        self.storeImportAction.setEnabled(isEnabled)
        self.storeNewAction.setEnabled(isEnabled)
        self.utilDeleteIconAction.setEnabled(isEnabled)
        self.utilDeleteScriptAction.setEnabled(isEnabled)
        self.utilUploadIconAction.setEnabled(isEnabled)
        self.utilUploadScriptAction.setEnabled(isEnabled)

    def __configureDatastore(self, datastore=None):
        """ Shows the Data Store configuration wizard to add a new Data Store. """

        DataStoreConfigurationWizardController(self, self.repositoryConfiguration.dataStoreHandler, 
                                               self.repositoryConfiguration.iconHandler, datastore)

    def changeIconPixmap(self, icon, oldLabel, newLabel):
        """ Changes the icon (node) pixmap. """

        changedTitle = oldLabel
        if not oldLabel == newLabel and not self._getIconFromLabel(newLabel) == None:
            result = self.__showQuestion("DataFinder: Confirm Overwrite", "A Node of the same name \"" + unicode(newLabel) + \
                                          "\" already exists.\nBefore renaming, please close that node.")
            return changedTitle
        if not oldLabel == newLabel and self._isTypeExisting(newLabel):
            result = self.__showQuestion("DataFinder: Confirm Overwrite", "Overwrite existing \"" + unicode(newLabel) + "\"?")
            if result:
                return changedTitle

        iconItem = self._getIconFromLabel(oldLabel)
        if not iconItem is None:
            if icon is None:
                iconItem.setIconLabel(newLabel)
            else:
                iconItem.setIconLabel(newLabel)
                iconItem.setIconPixmap(icon.pixmap())
            changedTitle = newLabel
            self.iconView.updateCanvasView()

    def _isNodeExisting(self, title):
        """
        Check if the node with title does already exist.

        @param title: Title of the node.
        @type title: C{string}
        """

        returnValue = True
        if self._getIconFromLabel(title) is None:
            returnValue = False
        return returnValue

    def _isTypeExisting(self, newName):
        """ Checks if the type exists. """

        returnValue = False
        if not self.repositoryConfiguration.getDataType(newName) is None:
            returnValue = True
        elif not self.repositoryConfiguration.getRelation(newName) is None:
            returnValue = True
        return returnValue

    def _getIconFromLabel(self, searchLabel):
        """
        Returns the icon specified by searchLabel.

        @param searchLabel: the label of the icon.
        @type searchLabel: C{String}

        @rtype: L{PrototypeIcon}
        """

        return self.iconView.getIcon(searchLabel)

    def updateWebdavServerSlot(self, url, username, password):
        """ Reconnect to WebDAV server. """

        # update preferences
        if self.dfLoginDialog.savePasswordCheckBox.isChecked():
            self._preferences.addConnection(url, username, password)
        else:
            self._preferences.addConnection(url, username, None)
        self._preferences.store()

        try:
            if not self.repositoryConfiguration is None:
                self.repositoryConfiguration.release()
            repositoryConfiguration = None
            repositoryConfiguration = self._repositoryManager.getRepositoryConfiguration(url, username, password)
            repositoryConfiguration.load()
        except ConfigurationError, error:
            if not repositoryConfiguration is None:
                repositoryConfiguration.release()
            self.__showErrorMessage("Cannot connect to specified server. Reason: '%s'" % error.message \
                                    + "Please try again or create a new configuration.")
            self.__setConnectionState(False)
        else:
            self.repositoryConfiguration = repositoryConfiguration
            self.__setConnectionState(True)

    def updateDataTypes(self):
        """ Updates list of data types. """

        self.dataTypeBrowser.clear()
        self._dataTypes = list()
        if not self.repositoryConfiguration is None:
            self._dataTypes = self.repositoryConfiguration.datatypes
        for dataType in self._dataTypes:
            item = QListViewItem(self.dataTypeBrowser, None)
            if not dataType.name is None:
                item.setText(0, unicode(dataType.name))
            pixmap = utils.getPixmapForImageName(dataType.iconName)
            item.setPixmap(0, pixmap)

    def updateRelationTypes(self):
        """ Updates the displayed list of relation types. """

        self.relationTypeBrowser.clear()
        self._relationTypes = list()
        if not self.repositoryConfiguration is None:
            self._relationTypes = self.repositoryConfiguration.relations
        for relationType in self._relationTypes:
            item = QListViewItem(self.relationTypeBrowser, None)
            if not relationType.name is None:
                item.setText(0, relationType.name)
            pixmap = utils.getPixmapForImageName(relationType.iconName)
            item.setPixmap(0, pixmap)

    def updateDataStores(self):
        """ Updates the displayed list of Data Stores. """

        self.dataStoreBrowser.clear()
        self._dataStores = list()
        if not self.repositoryConfiguration is None:
            self._dataStores = self.repositoryConfiguration.datastores
        for dataStore in self._dataStores:
            item = QListViewItem(self.dataStoreBrowser, None)
            if not dataStore.name is None:
                item.setText(0, dataStore.name)
            if dataStore.isDefault:
                item.setText(1, "Yes")
            pixmap = utils.getPixmapForImageName(dataStore.iconName)
            item.setPixmap(0, pixmap)

    def editSlot(self):
        """ Edits the selected item (data type, relation, or data store). """

        currentTabLabel = str(self.dataNavigator.tabLabel(self.dataNavigator.currentPage()))
        if currentTabLabel == AdminMain.__tabDataTypesTitle:
            item = self.dataTypeBrowser.selectedItem()
            if not item is None:
                title = unicode(item.text(0))
                dataTypeController = data_type_dialog.DataTypeController(self, title, self.repositoryConfiguration)
                dataTypeController.show()
        elif currentTabLabel == AdminMain.__tabRelationTypesTitle:
            item = self.relationTypeBrowser.selectedItem()
            if not item is None:
                title = unicode(item.text(0))
                relationTypeController = relation_type_dialog.RelationTypeController(self, title, self.repositoryConfiguration)
                relationTypeController.show()
        elif currentTabLabel == AdminMain.__tabDataStoresTitle:
            item = self.dataStoreBrowser.selectedItem()
            if not item is None:
                datastore = self.repositoryConfiguration.getDataStore(unicode(item.text(0)))
                self.__configureDatastore(datastore)

    def __addDataTypeIconSlot(self):
        """ Edits the selected data type. """

        item = self.dataTypeBrowser.selectedItem()
        if not item is None:
            dataType = self.repositoryConfiguration.getDataType(unicode(item.text(0)))
            title = dataType.name
            iconSet = QIconSet(utils.getPixmapForImageName(dataType.iconName))
            if not self._isNodeExisting(title):
                iconSet = QIconSet(utils.getPixmapForImageName(dataType.iconName))
                self.iconView.addDataTypeIcon(title, iconSet)
                self.__logger.info("Data Type %s was successfully loaded." % title)
            else:
                self.iconView.markDataTypeIcon(title)

    def __addRelationTypeIconSlot(self):
        """ Edits the selected relation type. """

        item = self.relationTypeBrowser.selectedItem()
        if not item is None:
            relationType = self.repositoryConfiguration.getRelation(unicode(item.text(0)))
            title = relationType.name
            iconSet = QIconSet(utils.getPixmapForImageName(relationType.iconName))
            if not self._isNodeExisting(title):
                iconSet = QIconSet(utils.getPixmapForImageName(relationType.iconName))
                self.iconView.addRelationIcon(relationType, title, iconSet)
                self.__logger.info("Relation Type %s was successfully loaded." % title)
            else:
                self.iconView.markRelationIcon(title)

    def deleteSlot(self):
        """ Deletes the selected data type. """

        currentTabLabel = unicode(self.dataNavigator.tabLabel(self.dataNavigator.currentPage()))
        try:
            if currentTabLabel == AdminMain.__tabDataTypesTitle:
                self.deleteSelectedDataType()
            elif currentTabLabel == AdminMain.__tabRelationTypesTitle:
                self.deleteSelectedRelationType()
            elif currentTabLabel == AdminMain.__tabDataStoresTitle:
                self.__deleteSelectedDataStore()
        except ConfigurationError, error:
            errorMessage = "Cannot delete the specific item. Reason: '%s'" % error.message
            self.__showErrorMessage(errorMessage)
            self.__logger.error(errorMessage)

    def deleteSelectedDataType(self):
        """ Deletes the selected data type. """

        item = self.dataTypeBrowser.selectedItem()
        if not item is None:
            title = unicode(item.text(0))
            dtype = self.repositoryConfiguration.getDataType(title)
            if not dtype is None:
                result = self.__showQuestion("DataFinder: Confirm Delete", "Delete Data Type \"" + title + "\"?")
                if result:
                    self.repositoryConfiguration.removeDataType(dtype.name)
                    self.repositoryConfiguration.dataModelHandler.store()
                    self.updateDataTypes()
                    self.iconView.markDataTypeIcon(title)
                    self.iconView.removeIcon()
            else:
                self.__logger.warning("Data Type not found in configuration.")

    def deleteSelectedRelationType(self):
        """ Deletes the selected relation type. """

        item = self.relationTypeBrowser.selectedItem()
        if not item is None:
            title = unicode(item.text(0))
            if title == ROOT_RELATION_NAME:
                self.__showErrorMessage("The the root relations cannot be removed.")
            else:
                rtype = self.repositoryConfiguration.getRelation(title)
                if not rtype is None:
                    result = self.__showQuestion("DataFinder: Confirm Delete", "Delete Relation Type \"" + title + "\"?")
                    if result:
                        self.repositoryConfiguration.removeRelation(rtype.name)
                        self.repositoryConfiguration.dataModelHandler.store()
                        self.updateRelationTypes()
                        self.iconView.markRelationIcon(title)
                        self.iconView.removeIcon()
        else:
            self.__logger.warning("Relation Type not found in configuration.")

    def __deleteSelectedDataStore(self):
        """ Deletes the selected Data Store. """

        item = self.dataStoreBrowser.selectedItem()
        if not item is None:
            title = unicode(item.text(0))
            stype = self.repositoryConfiguration.getDataStore(title)
            if not stype is None:
                result = self.__showQuestion("DataFinder: Confirm Delete", "Delete Data Store \"" + title + "\"?")
                if result:
                    self.repositoryConfiguration.removeDataStore(stype.name)
                    self.repositoryConfiguration.dataStoreHandler.store()
                    self.updateDataStores()
            else:
                self.__logger.warning("Data Store was not found in configuration.")

    def addDataTypeSlot(self):
        """ Adds a new data type. """

        data_type_dialog.DataTypeController(self, None, self.repositoryConfiguration, False).show()

    def addRelationTypeSlot(self):
        """ Adds a new relation type. """

        relation_type_dialog.RelationTypeController(self, None, self.repositoryConfiguration, False).show()

    def addDataStoreSlot(self):
        """ Configures a new data store. """

        self.__configureDatastore()

    def exportDatamodelSlot(self):
        """ Exports the current data model to the local file system. """

        proposedName = "datamodel.xml"
        targetFilePath = unicode(QFileDialog.getSaveFileName(os.path.join(self._lastUploadDirectory, proposedName),
                                                              "*.xml", self, "Export data model...", "Choose a file" ))
        if len(targetFilePath) > 0:
            self._lastUploadDirectory = os.path.dirname(targetFilePath)
            try:
                self.repositoryConfiguration.exportDatamodel(targetFilePath)
            except ConfigurationError, error:
                self.__showErrorMessage("Cannot export data model to '%s'. Reason: '%s'" % (targetFilePath, error.message))
            else:
                self.__logger.info("Successfully exported the current data model to '%s'." % targetFilePath)

    def importDatamodelSlot(self):
        """ Imports the current data model with the one read from the local file system. """

        targetFilePath = unicode(QFileDialog.getOpenFileName(self._lastUploadDirectory, "*.xml",
                                                             self, "Import data model...", "Choose a file" ))
        if os.path.isfile(targetFilePath):
            self._lastUploadDirectory = os.path.dirname(targetFilePath)
            try:
                self.repositoryConfiguration.importDatamodel(targetFilePath)
                self.repositoryConfiguration.dataModelHandler.store()
            except ConfigurationError, error:
                self.__showErrorMessage("Cannot import data model from '%s'. Reason: '%s'" \
                                        % (targetFilePath, error.message))
            else:
                self.updateDataTypes()
                self.updateRelationTypes()
                self.__logger.info("Successfully imported the data model.")

    def exportDataStoresSlot(self):
        """ Exports the current data model to the local file system. """

        proposedName = "datastores.xml"
        targetFilePath = unicode(QFileDialog.getSaveFileName(os.path.join(self._lastUploadDirectory, proposedName),
                                                              "*.xml", self, "Export data store configuration...", "Choose a file" ))
        if len(targetFilePath) > 0:
            self._lastUploadDirectory = os.path.dirname(targetFilePath)
            try:
                self.repositoryConfiguration.exportDataStores(targetFilePath)
            except ConfigurationError, error:
                self.__showErrorMessage("Cannot export data store configuration to '%s'. \nReason: '%s'" \
                                        % (targetFilePath, error.message))
            else:
                self.__logger.info("Successfully exported the current data store configurations to '%s'." % targetFilePath)

    def importDataStoresSlot(self):
        """ Imports the current data model with the one read from the local file system. """

        targetFilePath = unicode(QFileDialog.getOpenFileName(self._lastUploadDirectory, "*.xml",
                                                             self, "Import data store configuration...", "Choose a file" ))
        if len(targetFilePath) > 0:
            self._lastUploadDirectory = os.path.dirname(unicode(targetFilePath))
            try:
                self.repositoryConfiguration.importDataStores(targetFilePath)
                self.repositoryConfiguration.dataStoreHandler.store()
            except ConfigurationError, error:
                self.__showErrorMessage("Cannot import data store configuration from '%s'. Reason: '%s'" \
                                        % (targetFilePath, error.message))
            else:
                self.updateDataStores()
                self.__logger.info("Successfully imported data store configurations.")

    def __showErrorMessage(self, errorMessage):
        """ Display the given error message. """

        QMessageBox.critical(self, self.__errorMessageCaption, errorMessage)
        self.__logger.error(errorMessage)

    def __showQuestion(self, caption, question):
        """ Ask the user a question and returns the result. """

        result = False
        answer = QMessageBox.warning(self, caption, question, QMessageBox.No, QMessageBox.Yes)
        if answer == QMessageBox.Yes:
            result = True
        return result

    def __showInformation(self, information):
        """ Shows the given information. """

        QMessageBox.information(self, self.__informationMessageCaption, information, QMessageBox.Ok)

    def fileConnectSlot(self):
        """ Displays the login dialog. """

        self.dfLoginDialog.presetUrlList()
        self.dfLoginDialog.show()

    def createConfigurationSlot(self):
        """ Creates a new configuration. """

        self.__logger.debug("Display dialog for creation of a new configuration.")
        CreateConfigurationController(self._repositoryManager)

    def reloadConfigurationSlot(self):
        """ Reloads data types, relations and data stores. """

        try:
            self.repositoryConfiguration.load()
        except ConfigurationError, error:
            self.__showErrorMessage(error.message)
            self.__setConnectionState(False)
        else:
            self.__setConnectionState(True)
            
    def deleteConfigurationSlot(self):
        """ Deletes the current configuration. """

        question = "Do you really want to delete this configuration?\n" \
                 + "Warning: The complete content of collection '%s' is removed, too." \
                 % self.repositoryConfiguration.repositoryConfigurationUri
        result = self.__showQuestion("Confirm delete", question)
        if result:
            try:
                self.repositoryConfiguration.delete()
            except ConfigurationError, error:
                errorMessage = "Unable to delete configuration.\n Reason: '%s'" % error.message
                self.__showErrorMessage(errorMessage)
            else:
                self.repositoryConfiguration.release()
                self.__setConnectionState(False)

    def fileExitSlot(self):
        """ Exits the administration client. """

        try:
            self._repositoryManager.savePreferences()
        except ConfigurationError, error:
            self.__logger.error(error.message)
        QApplication.exit(0)

    def showAboutDialogSlot(self):
        """ Shows the about dialog. """

        self.dfAboutDialog.exec_loop()

    def uploadIconSlot(self):
        """
        Upload icon(s) to WebDAV-server Images collection.
        """

        filePaths = list(QFileDialog.getOpenFileNames("Image Files (*16.png)",
                                                      self._lastUploadDirectory,
                                                      self,
                                                      "open file dialog",
                                                      "Choose files" ))
        if len(filePaths) > 0:
            self._lastUploadDirectory = os.path.dirname(unicode(filePaths[0]))
            for filePath in filePaths:
                iconName = os.path.basename(unicode(filePath))[0:-6]
                iconPath = os.path.dirname(unicode(filePath))

                # Check if icon size (named) 24 is available
                iconPath24Pixel = os.path.join(iconPath, iconName + "24.png")
                if not os.path.exists(iconPath24Pixel):
                    errorMessage = "Icon '%s24.png' does not exist!" % iconName
                    self.__logger.error(errorMessage)
                else:
                    performIconImport = True
                    if self.repositoryConfiguration.hasIcon(iconName):
                        questionMessage = u"Icon '%s' already exists!\n\n Overwrite?" % iconName
                        performIconImport = self.__showQuestion("Icon Import", questionMessage)
                    if performIconImport:
                        try:
                            self.repositoryConfiguration.addIcon(iconName, iconPath)
                        except ConfigurationError, error:
                            self.__logger.error(error.message)

    def deleteIconSlot(self):
        """ Delete icon from server. """

        icons = self.repositoryConfiguration.icons
        if len(icons) == 0:
            self.__showInformation("No icons have been found on server.")
        else:
            selectDialog = icon_selection_dialog.SelectUserIconDialog(multiSelection=True)
            iconsToRemove = selectDialog.getIconName(icons)
            for icon in iconsToRemove:
                self.repositoryConfiguration.removeIcon(self.repositoryConfiguration.getIcon(icon))

    def uploadScriptSlot(self):
        """ Upload script(s) to WebDAV-server Scripts collection. """

        filePaths = list(QFileDialog.getOpenFileNames("DataFinder Script Files (*.py *.tar)",
                                                      self._lastUploadDirectory,
                                                      self,
                                                      "open file dialog",
                                                      "Choose files" ))
        if len(filePaths) > 0:
            self._lastUploadDirectory = os.path.dirname(unicode(filePaths[0]))
            for filePath in filePaths:
                filePath = unicode(filePath)
                performScriptImport = True
                if self.repositoryConfiguration.hasScript(os.path.basename(filePath)):
                    question = "Script '%s' already exists!\n\n Overwrite?" % os.path.basename(filePath)
                    performScriptImport = self.__showQuestion("Script Upload", question)
                if performScriptImport:
                    try:
                        self.repositoryConfiguration.addScript("file:///" + filePath)
                    except ConfigurationError, error:
                        errorMessage = "Cannot add script.\n Reason: '%s'" % error.message
                        self.__showErrorMessage(errorMessage)

    def deleteScriptSlot(self):
        """
        Delete script from server.
        """

        scripts = self.repositoryConfiguration.scripts
        if len(scripts) == 0:
            self.__showInformation("No scripts have been found on server.")
        else:
            selectDialog = script_selection_dialog.SelectScriptDialog()
            selectDialog.setScripts(scripts)
            scriptsToRemove = selectDialog.getScriptToRemove()
            for script in scriptsToRemove:
                try:
                    self.repositoryConfiguration.removeScript(script)
                except ConfigurationError, error:
                    errorMessage = "Cannot remove script.\n Reason: '%s'" % error.message
                    self.__showErrorMessage(errorMessage)


def main():
    """ Start function. """

    application = QApplication(sys.argv)
    splashScreen = utils.showSplash("splash_datafinder_admin.png")
    splashScreen.show()
    repositoryManager = RepositoryManager()
    repositoryManager.load()
    adminMainWindow = AdminMain(repositoryManager)
    application.connect(application, SIGNAL("lastWindowClosed()"), application, SLOT("quit()"))
    application.setMainWidget(adminMainWindow)
    screen = QApplication.desktop().screenGeometry()
    adminMainWindow.move(QPoint(screen.center().x() - adminMainWindow.width() / 2, screen.center().y() - adminMainWindow.height() / 2))
    adminMainWindow.show()
    splashScreen.close(True)
    adminMainWindow.fileConnectSlot()
    application.exec_loop()


if __name__ == "__main__":
    main()
