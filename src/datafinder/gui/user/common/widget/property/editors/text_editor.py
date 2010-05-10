#
# Created: 20.04.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: text_editor.py 4340 2009-11-17 16:32:30Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
The module provides a text editor.
"""


from PyQt4 import QtGui, QtCore
from PyQt4.Qt import Qt

from datafinder.gui.gen.user.text_editor_dialog_ui import Ui_textEditorDialog


__version__ = "$LastChangedRevision: 4340 $"


class TextEditor(QtGui.QLineEdit):
    """
    This widget widget is a specialized line editor which allows 
    text editing in a separated dialog.
    """
    
    def __init__(self, initData="", parent=None):
        """
        Constructor.

        @param initData: Initial list data.
        @type initData: C{unicode}
        @param parent: Parent widget of the dialog.
        @type parent: L{QWidget<PyQt4.QtGui.QWidget>}
        """

        QtGui.QLineEdit.__init__(self, parent)
        
        self.value = initData or ""
        self.setText(self.value)
        
        self._editButton = QtGui.QPushButton("...", self)
        self._editButton.setCursor(Qt.ArrowCursor)
        self._editButton.setMaximumSize(QtCore.QSize(20, 20))
        
        self.setStyleSheet("QLineEdit { padding-right: 0px; } ")
        
        self.connect(self._editButton, QtCore.SIGNAL("clicked()"), self._showEditorSlot)
        
    def resizeEvent(self, _):
        """ Ensures that the edit button is in the right corner of the line editor. """
        
        size = self._editButton.maximumSize()
        self._editButton.move(self.rect().right() - size.width(),
                             (self.rect().bottom() + 1 - size.height()) / 2)

        
    def _showEditorSlot(self):
        """ Slot which shows the list editor. """
        
        self.value = self.text()
        textEditor = _TextEditorDialog(self.value, self)
        textEditor.exec_()
        self.setText(self.value)
        self.setFocus(Qt.OtherFocusReason)


class _TextEditorDialog(QtGui.QDialog, Ui_textEditorDialog):
    """
    This dialog shows the content of a list property and supports the editing the property.
    """
    
    def __init__(self, initData, parent=None):
        """
        Constructor.

        @param initData: Initial list data.
        @type initData: C{unicode}
        @param parent: Parent widget of the dialog.
        @type parent: L{QWidget<PyQt4.QtGui.QWidget>}
        """
        
        QtGui.QDialog.__init__(self, parent)
        Ui_textEditorDialog.__init__(self)
        self.setupUi(self)
        
        self.textEdit.setText(initData or "")
        
        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accepted)

    def accepted(self):
        """ This slot is called when the user clicks OK. It returns the entered text. """
        
        self.parent().value = self.textEdit.toPlainText()
        QtGui.QDialog.accept(self)
