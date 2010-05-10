# pylint: disable-msg=R0901
#
# properties_dialog.py
#
# Created: 05.02.2008 lege_ma <malte.legenhausen@dlr.de>
# Changed:
#
# Copyright (C) 2003-2007 DLR/SISTEC, Germany
#
# All rights reserved
#
# http://www.dlr.de/datafinder
#


"""
This class contains all classes that are necessary for the displaying of the properties editing dialog.
"""


from PyQt4 import QtCore, QtGui

from datafinder.core.error import PropertyError
from datafinder.gui.user.models.properties import PropertiesModel
from datafinder.gui.gen.user import properties_dialog_ui


__version__ = "$LastChangedRevision: 4479 $"


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
