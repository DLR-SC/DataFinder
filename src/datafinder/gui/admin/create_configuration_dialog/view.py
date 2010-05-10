#
# Created: 06.11.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: view.py 3669 2009-01-07 08:18:44Z mohr_se $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder/
#


"""
Creates a default configuration on the specific location.
"""


from qt import QMessageBox, SIGNAL

from datafinder.gui.gen import create_configuration_dialog


__version__ = "$LastChangedRevision: 3669 $"


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
