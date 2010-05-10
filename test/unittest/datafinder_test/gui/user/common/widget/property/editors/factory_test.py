#
# Created: 07.03.2009 mohr_se <steven.mohr@dlr.de>
# Changed: $Id: factory_test.py 4552 2010-03-16 12:28:19Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Tests for the property editor factory.
"""


import unittest, sys, datetime

from PyQt4 import QtGui, QtCore

from datafinder.core.configuration.properties import constants
from datafinder.core.configuration.properties.property_type import PROPERTY_TYPE_NAMES
from datafinder.gui.user.common.widget.property.editors.factory import EditorFactory
from datafinder.gui.user.common.widget.property.editors.list_editor import ListEditor


__version__ = "$LastChangedRevision: 4552 $"


class EditorFactoryTest(unittest.TestCase): 
    """
    Tests for the property editor factory.
    """
    
    def setUp(self):
        """ Creates object under test. """
        
        self._editorFactory = EditorFactory()
        self._app = QtGui.QApplication(sys.argv)
    
    def testGetEditorForPropTypes(self):
        """
        Tests the getEditor method. It checks if every property type has a corresponding
        editor.
        """
        
        propTypes = PROPERTY_TYPE_NAMES[:]
        propTypes.remove(u'Any')
        for propType in propTypes:
            self._editorFactory.createEditor(None, propType)
    
    def testGetCorrectEditor(self):
        """
        Checks that the correct editor type is returned corresponding to the input type.
        """
        
        self.assertTrue(type(self._editorFactory.createEditor(None, 'Number')) == QtGui.QDoubleSpinBox)
        self.assertTrue(type(self._editorFactory.createEditor(None, 'Boolean')) == QtGui.QCheckBox)
        self.assertTrue(type(self._editorFactory.createEditor(None, 'Date Time')) == QtGui.QDateTimeEdit)
        self.assertTrue(isinstance(self._editorFactory.createEditor(None, 'String'), QtGui.QLineEdit))
        self.assertTrue(type(self._editorFactory.createEditor(None, 'List')) == ListEditor)
        
    def testGetValueFromEditor(self):
        """
        Tests the mapping from editor to return type
        """
        
        lineEdit = QtGui.QLineEdit()
        lineEdit.setText(QtCore.QString(u"TestValue"))
        self.assertEquals(self._editorFactory.getValueFromEditor(lineEdit), u"TestValue")
        
        lineEdit = QtGui.QLineEdit()
        lineEdit.setText(QtCore.QString(u""))
        self.assertEquals(self._editorFactory.getValueFromEditor(lineEdit), None)
        
        spinBox = QtGui.QDoubleSpinBox()
        spinBox.setValue(23.04)
        self.assertEquals(self._editorFactory.getValueFromEditor(spinBox), 23.04)
        
        checkBox = QtGui.QCheckBox()
        checkBox.setChecked(True)
        self.assertTrue(self._editorFactory.getValueFromEditor(checkBox))
        
        comboBox = QtGui.QComboBox()
        comboBox.addItems([u"test1"])
        self.assertEquals(self._editorFactory.getValueFromEditor(comboBox), u"test1")
        
        listEditor = ListEditor(self._editorFactory, ["test"])
        self.assertEquals(self._editorFactory.getValueFromEditor(listEditor), ["test"])
        
        listEditor = ListEditor(self._editorFactory)
        self.assertEquals(self._editorFactory.getValueFromEditor(listEditor), list())
        
    def testEditorRestrictionsStringInt(self):
        """
        Tests restrictions for integer and string editors
        """
        
        restrictions = {constants.MAXIMUM_LENGTH: 12,
                        constants.MAXIMUM_VALUE: 500,
                        constants.MINIMUM_VALUE: 10,
                        constants.MAXIMUM_NUMBER_OF_DECIMAL_PLACES: 5,
                        constants.MINIMUM_NUMBER_OF_DECIMAL_PLACES: 1,
                        constants.PATTERN : 'A.B*C'
                        }
        
        lineEdit = self._editorFactory.createEditor(None, "String", restrictions)
        self.assertTrue(type(lineEdit.validator()) == QtGui.QRegExpValidator)
        self.assertTrue(lineEdit.maxLength() == restrictions[constants.MAXIMUM_LENGTH])
        
        spinBox = self._editorFactory.createEditor(None, "Number", restrictions)
        self.assertTrue(spinBox.maximum() == restrictions[constants.MAXIMUM_VALUE])
        self.assertTrue(spinBox.minimum() == restrictions[constants.MINIMUM_VALUE])
        self.assertTrue(spinBox.decimals() == restrictions[constants.MAXIMUM_NUMBER_OF_DECIMAL_PLACES])
        
    def testEditorRestrictionsDateTime(self):
        """
        Tests restrictions for the date time editor
        """
        
        restrictions = {
                        constants.MINIMUM_VALUE: datetime.datetime(1950, 1, 1, 0, 15),
                        constants.MAXIMUM_VALUE: datetime.datetime(2010, 1, 1, 0, 15),
                        }        
        dateTimeEdit = self._editorFactory.createEditor(None, "Date Time", restrictions)
        self.assertTrue(dateTimeEdit.maximumDateTime().toPyDateTime() == restrictions[constants.MAXIMUM_VALUE])
        self.assertTrue(dateTimeEdit.minimumDateTime().toPyDateTime() == restrictions[constants.MINIMUM_VALUE])
        
    def testEditorRestrictionOption(self):
        """
        Tests the OPTIONS restriction for Strings
        """
        
        restrictions = {constants.OPTIONS: ""}
        comboBox = self._editorFactory.createEditor(None, "String", restrictions)
        self.assertTrue(type(comboBox) == QtGui.QComboBox)
        
    def testSetEditorValue(self):
        """
        Tests the setEditorValue method
        """
        
        lineEdit = QtGui.QLineEdit()
        self._editorFactory.setEditorValue(lineEdit, u"Test")
        self.assertTrue(lineEdit.text() == u"Test" )
        
        spinBox = QtGui.QDoubleSpinBox()
        self._editorFactory.setEditorValue(spinBox, 2.05)
        self.assertTrue(spinBox.value() == 2.05)
        
        checkBox = QtGui.QCheckBox()
        self._editorFactory.setEditorValue(checkBox, True)
        self.assertTrue(checkBox.isChecked() == True)
        
    def tearDown(self):
        """ Cleans up the test environment. """
        
        self._app.quit()
        self._app.deleteLater()
