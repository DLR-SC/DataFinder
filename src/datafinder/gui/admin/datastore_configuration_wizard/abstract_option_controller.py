# pylint: disable-msg=R0921
#
# Created: 10.11.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: abstract_option_controller.py 3603 2008-12-01 13:26:31Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Defines an abstract controller component for the different option
pages of the wizard.
"""


__version__ = "$LastChangedRevision: 3603 $"


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
