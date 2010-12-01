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
Module documentation string. 
"""


from PyQt4 import QtCore


__version__ = "$Revision-Id:$" 


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
