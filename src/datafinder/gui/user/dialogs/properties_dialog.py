#
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#
#modification, are permitted provided that the following conditions are
#met:
#
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
This class contains all classes that are necessary for the displaying of the properties editing dialog.
"""


from PyQt4 import QtCore, QtGui

from datafinder.core.error import PropertyError
from datafinder.gui.user.models.properties import PropertiesModel
from datafinder.gui.gen.user import properties_dialog_ui


__version__ = "$Revision-Id:$" 


class PropertiesDialog(QtGui.QDialog, properties_dialog_ui.Ui_propertiesDialog):
    """
    The properties dialog is responsible for the editing of the resource properties.
    """

    def __init__(self, model, parent=None):
        """
        Constructor.

        @param model: Model representing a set of properties.
        @type model: L{PropertiesModel<datafinder.gui.user.models.properties.PropertiesModel>}
        @param parent: The parent object of the property dialog.
        @type parent: L{QWidget<PyQt4.QtGui.QWidget>}
        """

        QtGui.QDialog.__init__(self, parent)
        properties_dialog_ui.Ui_propertiesDialog.__init__(self)
        self.setupUi(self)

        self._model = model
        self.propertyWidget.model = model
        self.setWindowTitle(self.tr("Edit properties of %1").arg(self._model.itemName))
        
        self.connect(self.applyButton, QtCore.SIGNAL("clicked()"), self._applyClickedSlot)
        self.connect(self, QtCore.SIGNAL("accepted()"), self._acceptedSlot)
        self.connect(self._model, QtCore.SIGNAL(PropertiesModel.PROPERTY_STATE_CHANGED_SIGNAL), 
                     self._propertyStateChangedSlot)
        
    def _propertyStateChangedSlot(self):
        """
        Slot is called when the model has changed.
        """

        self.applyButton.setEnabled(self._model.dirty and self._model.isConsistent)

    def _applyClickedSlot(self):
        """
        Slot is called when the apply button was clicked.
        """

        self.applyButton.setEnabled(False)
        try:
            self._model.save()
        except PropertyError:
            QtGui.QMessageBox.critical(self,
                                       "Error applying changes", 
                                       "Failed to validate input. Please correct it."
                                        )
            self.applyButton.setEnabled(True)
        
    def _acceptedSlot(self):
        """
        Slot is called when the OK button was clicked.
        """

        if self._model.dirty and self._model.isConsistent:
            self._applyClickedSlot()
