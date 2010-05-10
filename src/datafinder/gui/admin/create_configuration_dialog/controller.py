#
# Created: 06.11.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: controller.py 3919 2009-04-07 15:52:01Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Controller component of the create configuration dialog.
"""


import sys
import threading

from qt import QApplication, qApp

from datafinder.common import logger
from datafinder.core.error import ConfigurationError
from datafinder.gui.admin.create_configuration_dialog.view import CreateConfigurationView
from datafinder.gui.admin.create_configuration_dialog.model import CreateConfigurationModel


__version__ = "$LastChangedRevision: 3919 $"


class CreateConfigurationController(object):
    """ Controller component of the create configuration dialog. """
    
    _logger = logger.getDefaultLogger()
    
    def __init__(self, repositoryManager):
        """ Constructor. """
        
        self.__errorMessage = None
        self.__view = CreateConfigurationView(self)
        self.__model = CreateConfigurationModel(repositoryManager)
        self.__view.show()
        
    def createConfiguration(self, hostUri, username, password, configurationPath, dataPath):
        """ Delegates the call to the model. """
        
        self.__errorMessage = None
        self.__view.createPushButton.setEnabled(False)
        thread = threading.Thread(target=self.__prepare, args=(hostUri, configurationPath, dataPath, username, password))
        thread.start()
        while thread.isAlive():
            qApp.processEvents()
        self.__view.createPushButton.setEnabled(True)
        
        if not self.__errorMessage is None:
            self._logger.error(self.__errorMessage)
            self.__view.showErrorMessage(self.__errorMessage)
        else:
            createConfiguration = True
            if self.__model.exists:
                createConfiguration = self.__view.showQuestion("The configuration path does already exist. Overwrite it?")
            self.__view.createPushButton.setEnabled(False)
            thread = threading.Thread(target=self.__performConfigurationCreation, args=(createConfiguration, ))
            thread.start()
            while thread.isAlive():
                qApp.processEvents()
            if not self.__errorMessage is None:
                self._logger.error(self.__errorMessage)
                self.__view.showErrorMessage(self.__errorMessage)
            self.__view.createPushButton.setEnabled(True)
    
    def __prepare(self, hostUri, configurationPath, dataPath, username, password):
        """ Performs basic checks in thread. """
        
        try:
            self.__model.prepareConfiguration(hostUri, configurationPath, dataPath, username, password)
        except ConfigurationError, error:
            self.__errorMessage = error.message

    def __performConfigurationCreation(self, overwrite):
        """ Performs the configuration creation and handles errors. """
        
        try:
            self.__model.createConfiguration(overwrite)
        except ConfigurationError, error:
            self.__errorMessage = error.message

    def __getView(self):
        """ Returns the generated view class. """
        
        return self.__view.view

    view = property(__getView)


# simple self-test
if __name__ == "__main__":
    application = QApplication(sys.argv)
    controller = CreateConfigurationController()
    application.setMainWidget(controller.view)
    application.exec_loop()  
