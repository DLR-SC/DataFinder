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
Controller component of the create configuration dialog.
"""


import sys
import threading

from qt import QApplication, qApp

from datafinder.common import logger
from datafinder.core.error import ConfigurationError
from datafinder.gui.admin.create_configuration_dialog.view import CreateConfigurationView
from datafinder.gui.admin.create_configuration_dialog.model import CreateConfigurationModel


__version__ = "$Revision-Id:$" 


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
