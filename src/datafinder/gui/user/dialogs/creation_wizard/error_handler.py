#
# Created: 22.01.2010 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: error_handler.py 4533 2010-03-07 17:24:29Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Module documentation string. 
"""


from PyQt4 import QtCore


__version__ = "$LastChangedRevision: 4533 $"


class ErrorHandler(object):
    """ Class handles display of wizard error messages. """
    
    __ERROR_TEMPLATE = "<p><img src=':icons/icons/cross16.png' />   %s</p>"
    
    def __init__(self, creationWizard):
        """
        Constructor.
        
        @param creationWizard: Reference to the creation wizard instance.
        @type creationWizard: L{CreationWizard<datafinder.gui.user.dialogs.creation_wizard.main.CreationWizard>}
        """
        
        self._creationWizard = creationWizard
        
        self._errors = dict()
        
    def appendError(self, errorType, errorMessage):
        """
        Displays the given error message as page sub title and prevents the 
        continuation with the next wizard page.
        
        @param errorType: Constant specifying the error type.
        @type errorType: C{int}
        @param errorMessage: error messages to display.
        @type errorMessage: C{unicode}
        """
        
        self._errors[errorType] = errorMessage
        self.udpateErrorDisplay()
        
    def udpateErrorDisplay(self):
        """ Updates the current displayed errors. """
        
        currentPage = self._creationWizard.currentPage()
        if not currentPage is None:
            currentPage.setTitle(self._creationWizard.currentTitle)
            if len(self._errors) > 0:
                errorMessage = self.__ERROR_TEMPLATE % self._errors.values()[0]
                currentPage.setSubTitle(errorMessage)
            else:
                currentPage.setSubTitle(self._creationWizard.currentSubTitle)
            currentPage.emit(QtCore.SIGNAL("completeChanged()"))

    def removeError(self, errorType):
        """
        Removes the specified error type and the according message.
        If no error type exists, the corresponding navigation buttons 
        will be activated again.
        
        @param errorType: Constant specifying the error type.
        @type errorType: C{int}
        """
        
        if errorType in self._errors:
            del self._errors[errorType]
            self.udpateErrorDisplay()

    def clear(self):
        """ Clear all errors which useful when going one page back. """
           
        self._errors.clear()
        self.udpateErrorDisplay()

    @property
    def hasErrors(self):
        """ Returns whether errors exist or not. """
        
        return len(self._errors) > 0
