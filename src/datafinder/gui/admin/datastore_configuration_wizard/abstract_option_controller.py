# pylint: disable=R0921
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
Defines an abstract controller component for the different option
pages of the wizard.
"""


__version__ = "$Revision-Id:$" 


# error message for missing implementation of abstract methods.
_implementationErrorMessage = "You have to provide a suitable implementation."


class AbstractOptionController(object):
    """ Abstract class that defines the interface of the form controller classes. """
        
    def __init__(self, wizardView, wizardController, pageType):
        """
        Constructor.
        
        @param wizardView: The wizard class.
        @type wizardView: instance of L{view.DataStoreConfigurationWizardView}
        @param wizardController: The main controller class.
        @type wizardController: instance of L{view.DataStoreConfigurationWizardController}
        @param pageType: category of the displayed options (e.g. storage, authentication, ...)
        @type pageType: C{string}
        """
        
        self.wizardView = wizardView
        self.wizardController = wizardController
        self.errorDictionary = {}
        self.pageType = pageType
        self.wizardView.showCurrentErrorLabels(False, pageType)
        
    def showModelPart(self):
        """ Initializes the according form elements from the DataStore model. """       
        
        raise NotImplementedError(_implementationErrorMessage)
    
    def setDatastoreProperty(self, myProperty, value, source=None):
        """ Validate and set the given property of the DataStore. """
        
        try:
            setattr(self.wizardController.datastore, myProperty, value)
            if self.errorDictionary.has_key(myProperty):
                del self.errorDictionary[myProperty]
                self.wizardView.showErrorSource(source, False)
        except ValueError, valueError:
            self.errorDictionary[myProperty] = unicode(valueError)
            self.wizardView.showErrorSource(source, True)
        self.checkErrorMessageDisplaying()
        
    def checkErrorMessageDisplaying(self):
        """ Checks if it is necessary to display an error message. """
        
        errorCount = len(self.errorDictionary)
        if errorCount == 0:
            self.wizardView.transitionEnabled(True)
            self.wizardView.showCurrentErrorLabels(False,
                                                   self.pageType)
        else:
            self.wizardView.transitionEnabled(False)
            errorValues = self.errorDictionary.values()
            self.wizardView.showCurrentErrorLabels(True, 
                                                   self.pageType,
                                                   errorValues[errorCount - 1])
