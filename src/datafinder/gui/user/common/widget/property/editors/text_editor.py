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
The module provides a text editor.
"""


from PyQt4 import QtGui, QtCore
from PyQt4.Qt import Qt

from datafinder.gui.gen.user.text_editor_dialog_ui import Ui_textEditorDialog


__version__ = "$Revision-Id:$" 


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
