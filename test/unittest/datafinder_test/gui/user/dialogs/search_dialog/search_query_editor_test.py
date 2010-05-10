#
# Created: 19.08.2009 Steven Mohr <steven.mohr@dlr.de>
# Changed: $Id: search_query_editor_test.py 4314 2009-10-19 12:38:25Z schlauch $ 
# 
# Copyright (c) 2009, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Test for the automatic completion text editor.
"""


import unittest, sys

from PyQt4 import QtCore, QtGui

from datafinder.core.item.search_restriction import SearchRestrictionParser
from datafinder.gui.user.dialogs.search_dialog.search_query_editor import SearchQueryEditor, SearchQueryAnalyzer


__version__ = "$LastChangedRevision: 4314 $"


class SearchQueryEditorTestCase(unittest.TestCase): 
    """ 
    Tests the auto completion text edit module.
    """
    
    _availableProperties = ["Content", "Date time", "Content type descriptor"]
    _availableComparisonOperators = ["=", "<", ">", ">=", "<=", "is"]
    _availableConjuntionsOperators = ["AND", "OR"]
    _application = QtGui.QApplication(sys.argv)
    
    def setUp(self):
        """ Setups the test fixture. """
        
        self.autoComplEdit = SearchQueryEditor(None)

        self.autoComplEdit.registerCompleter(QtGui.QCompleter(self._availableProperties), 
                                             SearchQueryAnalyzer.PROPERTY_TYPE)
        completer = QtGui.QCompleter(self._availableComparisonOperators)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.autoComplEdit.registerCompleter(completer, SearchQueryAnalyzer.COMPARISON_TYPE)
        completer = QtGui.QCompleter(self._availableConjuntionsOperators)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.autoComplEdit.registerCompleter(completer, SearchQueryAnalyzer.CONJUNCTION_TYPE)
        self.autoComplEdit.registerCompleter(QtGui.QCompleter(["''"]), 
                                             SearchQueryAnalyzer.LITERAL_TYPE)
        
        self._searchQueryAnalyzer = SearchQueryAnalyzer(SearchRestrictionParser(), dict())
        self.autoComplEdit._searchQueryAnalyzer = self._searchQueryAnalyzer
    
    def testPropertyCompletion(self):
        """ Tests auto completion for property names. """
        
        self.autoComplEdit.setText("Con")
        self._requestAutocompletionAtPosition(3)
        self.assertEquals(self.autoComplEdit.completer().currentCompletion(), "Content")
        
        self.autoComplEdit.setText("Conz")
        self._requestAutocompletionAtPosition(4)
        self.assertEquals(self.autoComplEdit.completer().currentCompletion(), "")
        
    def _requestAutocompletionAtPosition(self, position):
        """ Sets the cursor position in the text editor. """
        
        textCursor = self.autoComplEdit.textCursor()
        textCursor.setPosition(position)
        self.autoComplEdit.setTextCursor(textCursor)
        self._searchQueryAnalyzer.analyze(unicode(self.autoComplEdit.toPlainText()))
        self.autoComplEdit.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Space, QtCore.Qt.ControlModifier))
        
    def testConjunctionCompletion(self):
        """ Tests the completion of conjunction operators. """
        
        self.autoComplEdit.setText("Content = 'tada' ")
        self._requestAutocompletionAtPosition(17)
        self.assertEquals(self.autoComplEdit.completer().currentCompletion(), "AND")
        
    def testComparisonCompletion(self):
        """ Tests the completion of comparison operators. """
        
        self.autoComplEdit.setText("Content >")
        self._requestAutocompletionAtPosition(9)
        completions = list()
        i = 0
        while self.autoComplEdit.completer().setCurrentRow(i):
            completions.append(self.autoComplEdit.completer().currentCompletion())
            i += 1

        self.assertEquals(completions, [">", ">="])
        
    def testPropertyCompletionAfterConjunction(self):
        """ Tests auto completion for property names after a conjunction. """
        
        self.autoComplEdit.setText("Content = 'tada' and C")
        self._requestAutocompletionAtPosition(22)
        self.assertEquals(self.autoComplEdit.completer().currentCompletion(), "Content")
        
    def testMultipleCompletion(self):
        """ Tests the multiple use of auto completion in one query. """
        
        self.autoComplEdit.setText("")
        self._requestAutocompletionAtPosition(0)
        self.autoComplEdit.insertCompletion(self.autoComplEdit.completer().currentCompletion())
        self.assertEquals(self.autoComplEdit.toPlainText(), "Content ")

        self._requestAutocompletionAtPosition(7)
        self.autoComplEdit.insertCompletion(self.autoComplEdit.completer().currentCompletion())
        self.assertEquals(self.autoComplEdit.toPlainText(), "Content ")
        
        self._requestAutocompletionAtPosition(8)
        self.autoComplEdit.insertCompletion(self.autoComplEdit.completer().currentCompletion())
        self.assertEquals(self.autoComplEdit.toPlainText(), "Content = ")
        
        self._requestAutocompletionAtPosition(10)
        self.autoComplEdit.insertCompletion(self.autoComplEdit.completer().currentCompletion())
        self.assertEquals(self.autoComplEdit.toPlainText(), "Content = '' ")

        self._requestAutocompletionAtPosition(0)
        self.autoComplEdit.insertCompletion(self.autoComplEdit.completer().currentCompletion())
        self.assertEquals(self.autoComplEdit.toPlainText(), "Content = '' ")

        self._requestAutocompletionAtPosition(4)
        self.assertEquals(self.autoComplEdit.completer().currentCompletion(), "Content")
        self.autoComplEdit.insertCompletion(self.autoComplEdit.completer().currentCompletion())
        self.assertEquals(self.autoComplEdit.toPlainText(), "Content = '' ")

        self.autoComplEdit.setText("Content  = '' ")
        self._requestAutocompletionAtPosition(8)
        self.autoComplEdit.insertCompletion(self.autoComplEdit.completer().currentCompletion())
        self.assertEquals(self.autoComplEdit.toPlainText(), "Content =  = '' ")
        
    def testConjunctionRecognition(self):
        """ Tests the recognition of conjunction terms when already a character is typed. """
        
        self.autoComplEdit.setText("Content = 'Peter hhg' o")
        self._requestAutocompletionAtPosition(23)
        self.assertEquals(self.autoComplEdit.completer().currentCompletion(), "OR")
        
    def testConjunctionRecognitionWithNoTokenUnderCursor(self):
        """ Tests the recognition of conjunction terms with no token under the cursor. """
        
        self.autoComplEdit.setText("Content = 'Peter hhg'  AND Content = 'Peter hhg'")
        self._requestAutocompletionAtPosition(22)
        self.assertEquals(self.autoComplEdit.completer().currentCompletion(), "AND")

    def testConjunctionRecognitionWithTokenUnderCursor(self):
        """ Tests the recognition of conjunction terms with token under the cursor. """
        
        self.autoComplEdit.setText("Content = 'Peter hhg' AND NOT Content = 'Peter hhg'")
        self._requestAutocompletionAtPosition(24)
        self.assertEquals(self.autoComplEdit.completer().currentCompletion(), "AND")
