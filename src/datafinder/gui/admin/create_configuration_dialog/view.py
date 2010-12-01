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
Creates a default configuration on the specific location.
"""


from qt import QMessageBox, SIGNAL

from datafinder.gui.gen import create_configuration_dialog


__version__ = "$Revision-Id:$" 


_creationErrorMessage = "Problems on configuration creation..."
_creationQuestionMessage = "Question..."

class CreateConfigurationView(object):
    """ View component of the create configuration dialog. """

    def __init__(self, controller):
        """ Constructor. """

        self.__generatedDialog = create_configuration_dialog.CreateConfigurationDialog()
        self.__controller = controller

        self.connect(self.createPushButton, SIGNAL("clicked()"), self.__createSlot)
        self.connect(self.cancelPushButton, SIGNAL("clicked()"), self.cancelDialog)
        self.connect(self.authenticationRequiredCheckBox, SIGNAL("toggled(bool)"), self.__authenticationRequiredSlot)

    def __createSlot(self):
        """ Triggers the creation of the configuration. """

        hostName = unicode(self.hostNameLineEdit.text())
        userName = None
        password = None
        if self.authenticationRequiredCheckBox.isChecked():
            userName = unicode(self.userNameLineEdit.text())
            password = unicode(self.passwordLineEdit.text())
        configurationPath = unicode(self.configurationPathLineEdit.text())
        dataPath = unicode(self.dataPathLineEdit.text())
        self.__controller.createConfiguration(hostName, userName, password, configurationPath, dataPath)

    def __authenticationRequiredSlot(self, isChecked):
        """ Enables or disables the user name, password line edits. """

        self.userNameLineEdit.setEnabled(isChecked)
        self.passwordLineEdit.setEnabled(isChecked)

    def showErrorMessage(self, errorMessage):
        """ Displays the given error message. """

        QMessageBox.critical(self.__generatedDialog, _creationErrorMessage, errorMessage)

    def showQuestion(self, question):
        """ Displays the given question and returns the answer. """

        answer = QMessageBox.question(self.__generatedDialog, _creationQuestionMessage, question,
                                      QMessageBox.No, QMessageBox.Yes)
        result = False
        if answer == QMessageBox.Yes:
            result = True
        return result

    def cancelDialog(self):
        """ Closes the dialog. """

        self.close()

    def __getView(self):
        """ Returns the generated Qt instance. """

        return self.__generatedDialog

    view = property(__getView)

    def __getattr__(self, name):
        """ Redirecting calls to generated dialog. """

        return getattr(self.__generatedDialog, name)
