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
Factory for input methods within a dialog.
"""


from datetime import datetime
        
from PyQt4 import QtGui, QtCore

from datafinder.core.configuration.properties import constants
from datafinder.gui.user.common.util import extractPyObject
from datafinder.gui.user.common.widget.property.editors.list_editor import ListEditor
from datafinder.gui.user.common.widget.property.editors.text_editor import TextEditor


__version__ = "$Revision-Id:$" 


class EditorFactory(object):
    """
    This factory produces adequate widgets for editing Qt data types.
    """
    
    def __init__(self):
        """ Constructor. """
        
        self._handlingMethods = {constants.STRING_TYPE: self._createStringEditor,
                                 constants.DATETIME_TYPE: self._createDateTimeEditor,
                                 constants.NUMBER_TYPE: self._createDecimalEditor,
                                 constants.LIST_TYPE: self._createListEditor,
                                 constants.BOOLEAN_TYPE: self._createBooleanEditor}
    
    def createEditor(self, parent, objectType, restrictions=dict(), initState=None):
        """
        Creates an editor for given object and initializes it correctly.
        
        @param parent: parent of the new editor
        @type parent: L{QWidget<PyQt4.QtGui.QWidget>}
        @param objectType: string that specifies the editor to create
        @type object: C{unicode}
        @param restrictions: restrictions that should be set for the editor
        @type restrictions: C{dict}: string -> int or string
        @param initState: a valid init state for an editor (f.e. string for a line edit)
        
        @return: An initialized editor widget
        @rtype: L{QWidget<PyQt4.QtGui.QWidget>}
        """
        
        restrictions = restrictions or dict()
        try:
            editor = self._handlingMethods[unicode(objectType)](restrictions, initState, parent)
        except TypeError:
            editor = self._handlingMethods[unicode(objectType)](restrictions, None, parent)
        except KeyError:
            editor = self._createStringEditor(restrictions, initState, parent)
            editor.setEnabled(False)
        return editor
        
    def _createStringEditor(self, restriction, initData, parent):
        """
        Creates an adequate editor for text.
        
        @param restriction: restriction for the input
        @type restriction: C{dict}
        @param parent: parent of the new editor
        @type parent: L{QWidget<PyQt4.QtGui.QWidget>}
        """
        
        editor = TextEditor(initData, parent)
        if constants.OPTIONS in restriction:
            options = [QtCore.QString(item) for item in restriction[constants.OPTIONS]]
            editor = self._createSelectionBox(None, options, parent)
            return editor
        
        if constants.MAXIMUM_LENGTH in restriction:
            editor.setMaxLength(restriction[constants.MAXIMUM_LENGTH])
        
        if constants.PATTERN in restriction:
            regEx = QtCore.QString(unicode(restriction[constants.PATTERN]))
            regExValidator = QtGui.QRegExpValidator(editor)
            regExValidator.setRegExp(QtCore.QRegExp(regEx))
            editor.setValidator(regExValidator)
        return editor
    
    @staticmethod
    def _createSelectionBox(_, listItems, parent):
        """
        Creates a combination box.
        
        @param listItems: items of the combination box
        @type listItems: C{list} of QString
        @param parent: Parent of the new editor
        @type parent: L{QWidget<PyQt4.QtGui.QWidget>}
        """
        
        editor = QtGui.QComboBox(parent)
        editor.addItems(listItems)
        return editor
        
    @staticmethod
    def _createDateTimeEditor(restriction, _, parent):
        """
        Creates an adequate editor for a list 
        @param restriction: restriction for the input
        @type restriction: C{dict}
        @param parent: Parent of the new editor
        @type parent: L{QWidget<PyQt4.QtGui.QWidget>}
        """
        
        editor = QtGui.QDateTimeEdit(parent)
        editor.setCalendarPopup(True)
        if constants.MINIMUM_VALUE in restriction:
            editor.setMinimumDateTime(restriction[constants.MINIMUM_VALUE])
        if constants.MAXIMUM_VALUE in restriction:
            editor.setMaximumDateTime(restriction[constants.MAXIMUM_VALUE])
        editor.setDateTime(datetime.now())
        return editor    
    @staticmethod
    def _createDecimalEditor(restriction, _, parent):
        """
        Creates an adequate editor for a decimal  
        @param restriction: restriction for the input
        @type restriction: C{dict}
        @param parent: Parent of the new editor
        @type parent: L{QWidget<PyQt4.QtGui.QWidget>}
        """
        
        editor = QtGui.QDoubleSpinBox(parent)
        if constants.MINIMUM_VALUE in restriction:
            editor.setMinimum(restriction[constants.MINIMUM_VALUE])
        
        if constants.MAXIMUM_VALUE in restriction:
            editor.setMaximum(restriction[constants.MAXIMUM_VALUE])
            
        if constants.MAXIMUM_NUMBER_OF_DECIMAL_PLACES in restriction:
            editor.setDecimals(restriction[constants.MAXIMUM_NUMBER_OF_DECIMAL_PLACES])
        else:
            editor.setDecimals(12)
            editor.setRange(-9999999999, 9999999999)
        return editor
    
    def _createListEditor(self, restrictions, listItems, parent=None):
        """
        Creates an adequate editor for a list 
        
        @param restriction: restriction for the input
        @type restriction: C{dict}
        @param listItems: values to be edited
        @type listItems: C{list} of plain python types
        @param parent: Parent of the new editor
        @type parent: L{QWidget<PyQt4.QtGui.QWidget>}
        """
        
        listItems = listItems or list()
        return ListEditor(restrictions, self, listItems, parent)
    
    @staticmethod
    def _createBooleanEditor(_, __, parent):
        """
        Creates an adequate editor for a boolean value
        
        @param parent: Parent of the new editor
        @type parent: L{QWidget<PyQt4.QtGui.QWidget>} 
        """
        
        checkbox =  QtGui.QCheckBox(parent)
        checkbox.setAutoFillBackground(True)
        return checkbox
    
    @staticmethod
    def getValueFromEditor(editor):
        """
        Returns the current value of the editor
        @param editor: Editor to get value from
        @type editor: L{QWidget<PyQt4.QtGui.QWidget>}
        """

        returnValue = None
        if type(editor)  == QtGui.QDateTimeEdit:
            returnValue = editor.dateTime()
        elif type(editor) == QtGui.QDoubleSpinBox:
            returnValue = editor.value()
        elif type(editor) == QtGui.QCheckBox:
            returnValue = editor.isChecked()
        elif type(editor) == QtGui.QComboBox:
            returnValue = editor.currentText()
        elif type(editor) == ListEditor:
            returnValue = editor.value
        elif isinstance(editor, QtGui.QLineEdit):
            currentText = editor.text()
            if len(currentText) > 0:
                returnValue = currentText
        return returnValue
    
    @staticmethod
    def setEditorValue(editor, value):
        """
        Sets the value of the editor.
        """
        
        value = extractPyObject(value)
        
        if value is None:
            return value
        
        try:
            if isinstance(editor, QtGui.QLineEdit):
                editor.setText(value)
            elif type(editor)  == QtGui.QDateTimeEdit:
                editor.setDateTime(value)
            elif type(editor) == QtGui.QDoubleSpinBox:
                editor.setValue(value)
            elif type(editor) == QtGui.QCheckBox:
                editor.setChecked(value)
        except TypeError:
            return
