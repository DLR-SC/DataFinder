#
# Created: 10.11.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: controller.py 4561 2010-03-23 17:02:05Z ney_mi $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Controller component of the data store configuration wizard.
"""


from qt import SIGNAL, QFileDialog

from datafinder.common.logger import getDefaultLogger
from datafinder.core.configuration import datastores
from datafinder.core.error import ConfigurationError
from datafinder.gui.admin.datastore_configuration_wizard.constants import authenticationOptionsPage, \
                                                                          performanceOptionsPage, \
                                                                          securityOptionsPage, \
                                                                          standardOptionsPage, \
                                                                          storageOptionsPage, \
                                                                          wizardCaptionTemplate
from datafinder.gui.admin.datastore_configuration_wizard import default
from datafinder.gui.admin.datastore_configuration_wizard import ftp
from datafinder.gui.admin.datastore_configuration_wizard import gridftp
from datafinder.gui.admin.datastore_configuration_wizard import offline
from datafinder.gui.admin.datastore_configuration_wizard import tsm
from datafinder.gui.admin.datastore_configuration_wizard import view
from datafinder.gui.admin.datastore_configuration_wizard import webdav
#from datafinder.gui.admin.datastore_configuration_wizard import s3


__version__ = "$LastChangedRevision: 4561 $"


# default for all datastores
_defaultForAllDataStores = "Default"

# dictionary that contains the wizard page sequence for every datastore type 
_pageSequenceDictionary = {
datastores.GRIDFTP_STORE: [standardOptionsPage, storageOptionsPage,
                           securityOptionsPage, performanceOptionsPage], 
datastores.WEBDAV_STORE: [standardOptionsPage, storageOptionsPage, 
                          authenticationOptionsPage], 
datastores.FILE_STORE: [standardOptionsPage, storageOptionsPage, 
                       authenticationOptionsPage], 
datastores.FTP_STORE: [standardOptionsPage, storageOptionsPage, 
                      authenticationOptionsPage], 
datastores.OFFLINE_STORE: [standardOptionsPage, storageOptionsPage], 
datastores.DEFAULT_STORE: [standardOptionsPage],
datastores.TSM_CONNECTOR_STORE: [standardOptionsPage, storageOptionsPage,
                                authenticationOptionsPage]
#datastores.S3_STORE: [standardOptionsPage, storageOptionsPage,
#                                authenticationOptionsPage]
}


class DataStoreConfigurationWizardController(object):    
    """
    Controls the DataStoreWizardView. Delegates the control of the specific from
    to the according subclass of AbstractoptionComntroller.
    """


    _logger = getDefaultLogger()

    
    def __init__(self, parentFrame, dataStoreHandler, iconHandler, datastore=None):
        """
        Constructor.
        """
        
        self.parent = parentFrame
        self._dataStoreHandler = dataStoreHandler
        # create main view
        self.wizardView = view.DataStoreConfigurationWizardView(parentFrame)
        # init model
        if not datastore is None:
            self.datastore = datastore
        else:
            self.datastore = self._dataStoreHandler.createDataStore()
        
        # add control logic of the displayed forms 
        self.lastPageTitle = standardOptionsPage
        self.currentFormHandler = default.base_option_controller.BaseOptionController(self.wizardView, self, standardOptionsPage, 
                                                                                      dataStoreHandler, iconHandler)
        self.formControllerDict = {
         standardOptionsPage: {
           _defaultForAllDataStores: self.currentFormHandler
         },
         storageOptionsPage: {
           datastores.OFFLINE_STORE: 
            offline.storage_option_controller.StorageOptionController(self.wizardView, self, storageOptionsPage),
           datastores.TSM_CONNECTOR_STORE: 
            tsm.storage_option_controller.StorageOptionController(self.wizardView, self, storageOptionsPage),
#           datastores.S3_STORE:
#            s3.storage_option_controller.StorageOptionController(self.wizardView, self, storageOptionsPage),
           _defaultForAllDataStores:
            default.storage_option_controller.StorageOptionController(self.wizardView, self, storageOptionsPage)
         },
         securityOptionsPage: {
           datastores.GRIDFTP_STORE: 
            gridftp.security_option_controller.SecurityOptionController(self.wizardView, self, securityOptionsPage),
         },
         authenticationOptionsPage: {
           datastores.FTP_STORE: 
            ftp.authentication_option_controller.AuthenticationOptionController(self.wizardView, self, authenticationOptionsPage),
           datastores.WEBDAV_STORE: 
            webdav.authentication_option_controller.AuthenticationOptionController(self.wizardView, self, authenticationOptionsPage),
           datastores.TSM_CONNECTOR_STORE: 
            tsm.authentication_option_controller.AuthenticationOptionController(self.wizardView, self, authenticationOptionsPage),
#            datastores.S3_STORE:
#            s3.authentication_option_controller.AuthenticationOptionController(self.wizardView, self, authenticationOptionsPage)
           _defaultForAllDataStores: 
            default.authentication_option_controller.AuthenticationOptionController(self.wizardView, self, authenticationOptionsPage)
         },
         performanceOptionsPage: {
           datastores.GRIDFTP_STORE: 
            gridftp.performance_option_controller.PerformanceOptionController(self.wizardView, self, performanceOptionsPage)
         }
        }
        
        # show wizard
        self.wizardView.setCaption(wizardCaptionTemplate % (self.datastore.storeType, self.datastore.name))
        self.wizardView.show()
        self.wizardView.adjustSize()
        self.currentFormHandler.showModelPart()
        self.setPageSequence()
        # connect slots
        self.wizardView.connect(self.wizardView, SIGNAL("selected(const QString&)"), self._wizardPageChangedSlot)
        self.wizardView.connect(self.wizardView.finishButton(), SIGNAL("clicked()"), self._finishedSlot)
        
    def _finishedSlot(self):
        """ 
        Method to overwrite standard behavior of the QWizard class if the
        button "finished" is used. This method validates the user input, saves 
        the DataStore object and continues closes the wizard.
        """
        
        self._dataStoreHandler.addDataStore(self.datastore)
        try:
            self._dataStoreHandler.store()
        except ConfigurationError, error:
            self._logger.error(error.message)
        else:
            self.parent.updateDataStores()
            
    def _wizardPageChangedSlot(self, currentTitleQString):
        """
        Slot that saves the current form values and initializes the next form.
        """
        
        actualPageTitle = unicode(currentTitleQString)
        if not actualPageTitle == self.lastPageTitle:
            self.lastPageTitle = actualPageTitle
            self.wizardView.transitionEnabled(True)
            pageType = unicode(currentTitleQString)
            try:
                self.currentFormHandler = self.formControllerDict[pageType][self.datastore.storeType]
            except KeyError:
                self.currentFormHandler = self.formControllerDict[pageType][_defaultForAllDataStores]
            self.currentFormHandler.showModelPart()

    def setPageSequence(self):
        """ Adapts the current wizard page sequence. """
        
        pageSequenceList = _pageSequenceDictionary[self.datastore.storeType]
        self.wizardView.setPageSequence(pageSequenceList)   
        self.wizardView.transitionEnabled(True)
        
    def getFileHandleFromDialog(self):
        """ Returns a file handle to the selected file. """
        
        fileName = unicode(QFileDialog.getSaveFileName("",
                                                       "All Files (*)",
                                                       self.wizardView,
                                                       "Save file dialog",
                                                       "Choose a file name"))
        fileHandle = None
        if fileName:
            try:
                fileHandle = open (fileName, "rb")
            except IOError:
                fileHandle = None
        return fileHandle
