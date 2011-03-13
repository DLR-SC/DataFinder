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
Implements the editor for search queries.
"""


from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

from datafinder.gui.user.dialogs.search_dialog.utils import SearchQueryAnalyzer


__version__ = "$Revision-Id:$" 

    
class SearchQueryEditor(QtGui.QTextEdit):
    """
    Implement an editor for search queries.    
    """
    
    def __init__(self, parent=None):
        """
        @param parent: parent widget
        @type parent: L{QWidget <PyQt4.QtGui.QWidget>}
        """
        
        QtGui.QTextEdit.__init__(self, parent)
        
        self._completers = dict()
        self._activeTokenType = SearchQueryAnalyzer.PROPERTY_TYPE
        self._stateChangeTrigger = dict()
        self._searchQueryAnalyzer = None
        self._cursorPositionAnalysisResults = None # tuple of current token, token before, completion prefix
        
    def event(self, event):
        """ 
        @see: L{event<PyQt4.QtGui.QWidget.event>}
        Used displaying token dependent tool tips.
        """
        
        if event.type() == QtCore.QEvent.ToolTip:
            if not self._searchQueryAnalyzer is None:
                position = self.cursorForPosition(event.pos()).position()
                token = self._searchQueryAnalyzer.token(position)
                toolTip = None
                if not token is None:
                    toolTip = token.toolTip
                if not toolTip is None:
                    QtGui.QToolTip.showText(event.globalPos(), toolTip)
                else:
                    QtGui.QToolTip.hideText()
        return QtGui.QTextEdit.event(self, event)
    
    def _handleValidationSignal(self, valid):
        """ Highlights the invalid parts of the search restrictions. """
        
        if len(self.toPlainText()) > 0:
            format_ = QtGui.QTextCharFormat()
            format_.setFontUnderline(not valid)
            startPosition = 0
            if valid:
                format_.setUnderlineStyle(QtGui.QTextCharFormat.NoUnderline)
            else:
                startPosition = self._searchQueryAnalyzer.errorResult[0]
                format_.setUnderlineColor(QtCore.Qt.red)
                format_.setUnderlineStyle(QtGui.QTextCharFormat.WaveUnderline)
                
            textCursor = self.textCursor()
            textCursor.setPosition(startPosition)
            textCursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.KeepAnchor)
            
            extraSelection = QtGui.QTextEdit.ExtraSelection()
            extraSelection.cursor = textCursor
            extraSelection.format = format_
            self.setExtraSelections([extraSelection])
        
    def registerCompleter(self, completer, tokenType):
        """
        Registers completer for the given token type.
       
        @param completer: completer to be registered
        @type completer: L{QCompleter <PyQt4.QtGui.QCompleter>}
        @param tokenType: For constant definitions see 
                          L{SearchQueryAnalyzer<datafinder.gui.user.dialogs.search_dialog.utils.SearchQueryAnalyzer>}.
        @type tokenType: C{int}
        """
        
        self._completers[tokenType] = completer
            
    def _setActiveTokenType(self, tokenType):
        """
        Setter method for token type. 
        It disconnects the QCompleter of the old token type and connects the new one.
        """
        
        if not self._completers[self._activeTokenType] is None:
            self.disconnect(self._completer, QtCore.SIGNAL("activated(QString)"), self.insertCompletion)
            self._completer.popup().hide()
        self._activeTokenType = tokenType
        self._completers[tokenType].setWidget(self)
        self.connect(self._completers[tokenType], QtCore.SIGNAL("activated(QString)"), self.insertCompletion)
        
    state = property(None, _setActiveTokenType)
    
    def completer(self):
        """
        @see: L{completer <PyQt4.QtGui.QLineEdit.completer>}
        """
        
        return self._completer
            
    def insertCompletion(self, completion):
        """
        Inserts the chosen completion in the text editor.
        """
        
        completion = unicode(completion)
        textCursor = self.textCursor()
        currentToken = self._cursorPositionAnalysisResults[0]
        
        if not currentToken is None:
            textCursor.beginEditBlock()
            textCursor.setPosition(currentToken.start)
            textCursor.setPosition(currentToken.end, QtGui.QTextCursor.KeepAnchor)
            textCursor.deleteChar()
            textCursor.insertText(completion)
            textCursor.endEditBlock()
        else:
            textCursor.insertText(completion + " ")
        self.setTextCursor(textCursor)
        
    def _analyzeCurrentCursorPosition(self):
        """ 
        Analyzes the current position of the cursor 
        and finds out which tokens are placed around the cursor. 
        """
        
        textCursor = self.textCursor()
        position = textCursor.position()
        
        currentToken, tokenBefore = self._searchQueryAnalyzer.tokenAround(position)

        completionPrefix = ""
        if not currentToken is None:
            completionPrefix = currentToken.token[:(position - currentToken.start)]
        self._cursorPositionAnalysisResults = currentToken, tokenBefore, completionPrefix
        return self._cursorPositionAnalysisResults
    
    def _updateActiveTokenType(self):
        """
        Updates the used completer. It decides based on the types of the 
        tokens around the current cursor position which completer should be used.
        """
        
        currentToken, tokenBefore, completionPrefix = self._analyzeCurrentCursorPosition()

        newState = SearchQueryAnalyzer.PROPERTY_TYPE
        if not currentToken is None:
            newState = currentToken.type
        if not tokenBefore is None:
            newState = self._searchQueryAnalyzer.nextTokenType(tokenBefore.type)
        self.state = newState
        return completionPrefix
    
    def keyPressEvent(self, keyEvent):
        """
        Slot that is called when a key is pressed. It checks whether a completion exist in its own
        completion model and presents a popup with all possibilities if available.
        @see: L{keyPressEvent <PyQt4.QtGui.QTextEdit.keyPressEvent>}
        """
        
        if not self._completer is None and self._completer.popup().isVisible():
            if keyEvent.key() in [Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab]:
                keyEvent.ignore()
                return

        if keyEvent.key() == Qt.Key_Space and keyEvent.modifiers() & Qt.ControlModifier:
            keyEvent.ignore()
            completionPrefix = self._updateActiveTokenType()
            self._completer.setCompletionPrefix(completionPrefix)
            self._completer.popup().setCurrentIndex(self._completer.completionModel().index(0, 0))
     
            cursorRect = self.cursorRect()
            cursorRect.setWidth(self._completer.popup().sizeHintForColumn(0)
                                + self._completer.popup().verticalScrollBar().sizeHint().width())
            self._completer.complete(cursorRect)
        else:
            QtGui.QTextEdit.keyPressEvent(self, keyEvent)
        
    @property
    def _completer(self):
        """
        Active completer.
        """
        
        return self._completers[self._activeTokenType]

    def _setSearchQueryAnalyzer(self, searchQueryAnalyzer):
        """ Sets the analyzer instance and connects the validation signal. """
        
        self._searchQueryAnalyzer = searchQueryAnalyzer
        self.connect(self._searchQueryAnalyzer, QtCore.SIGNAL(SearchQueryAnalyzer.VALIDATION_SIGNAL), self._handleValidationSignal)
        
    searchQueryAnalyzer = property(None, _setSearchQueryAnalyzer)
        

class Completer(QtGui.QCompleter):
    """ Custom completer allowing displaying completions and tool tips for them in a list view. """
    
    def __init__(self, completions, sortCompletions=False):
        """
        Constructor.
        
        @param completions: Completions and specific tool tips explaining them.
        @type completions: C{dict} of C{unicode}, C{unicode}
        @param sortCompletions: Flag indicating whether completions should be sorted.
        @type sortCompletions: C{bool}
        """
        
        QtGui.QCompleter.__init__(self)

        self._model = QtGui.QStandardItemModel(len(completions), 0)
        counter = 0
        keys = completions.keys()
        if sortCompletions:
            keys.sort(key=unicode.lower)
        for name in keys:
            item = QtGui.QStandardItem(name)
            item.setToolTip(completions[name])
            self._model.setItem(counter, 0, item)
            counter += 1
        self.setModel(self._model)
        
        self.setPopup(self._CustomListView())

    class _CustomListView(QtGui.QListView):
        """ Custom list view. """
        
        def __init__(self):
            """ Constructor. """
            
            QtGui.QListView.__init__(self)
            
        def event(self, event):
            """ 
            This re-implementation is required because 
            when the list view is popped up the method C{viewportEvent} 
            - handling item specific tool tips - is no called.
            """
            
            if event.type() == QtCore.QEvent.ToolTip:
                return self.viewportEvent(event)
            else:
                return QtGui.QListView.event(self, event)


class SearchSyntaxHighlighter(QtGui.QSyntaxHighlighter):
    """
    This class enables syntax highlighting in the criteria window of the search dialog.
    """

    def __init__(self, searchQueryAnalyzer, parent=None):
        """
        Constructor.

        @param parent: Parent object of this class.
        @type parent: L{QObject<PyQt4.QtCore.QObject>}
        """

        QtGui.QSyntaxHighlighter.__init__(self, parent)
        self._parent = parent
        self._searchQueryAnalyzer = searchQueryAnalyzer
        self._searchQueryAnalyzer._matchHook = self._highlightToken
        
        literalFormat = QtGui.QTextCharFormat()
        literalFormat.setForeground(QtCore.Qt.darkGreen)

        comparisonFormat = QtGui.QTextCharFormat()
        comparisonFormat.setForeground(QtCore.Qt.blue)
        
        conjunctionFormat = QtGui.QTextCharFormat()
        conjunctionFormat.setForeground(QtCore.Qt.blue)
        conjunctionFormat.setFontWeight(QtGui.QFont.Bold)

        propertyFormat = QtGui.QTextCharFormat()
        propertyFormat.setForeground(QtCore.Qt.darkMagenta)
        
        self._typeFormatMap = {SearchQueryAnalyzer.LITERAL_TYPE: literalFormat,
                               SearchQueryAnalyzer.CONJUNCTION_TYPE: conjunctionFormat,
                               SearchQueryAnalyzer.COMPARISON_TYPE: comparisonFormat,
                               SearchQueryAnalyzer.PROPERTY_TYPE: propertyFormat}
        self._paragraphStartPosition = 0
                
    def highlightBlock(self, currentText):
        """
        @see: L{highlightBlock<PyQt4.QtGui.QSyntaxHighlighter.highlightBlock>}
        """

        text = unicode(self._parent.toPlainText())
        currentText = unicode(currentText)
        if len(text.strip()) > 0:
            splittedText = text.split("\n")
            self._paragraphStartPosition = 0
            if len(splittedText) > 1:
                self._paragraphStartPosition = self._determineParagraphStartPosition(splittedText, currentText)
            self._searchQueryAnalyzer.analyze(text)
        else:
            self._searchQueryAnalyzer.clearParsingResults()
            
    @staticmethod
    def _determineParagraphStartPosition(splittedText, currentText):
        """ Finds out the start of the paragraph that is currently changed. """
        
        begin = 0
        for paragraph in splittedText:
            if paragraph != currentText:
                begin += len(paragraph) + 1
            else:
                break
        return begin
            
    def _highlightToken(self, tokenDescriptor):
        """ Set the format of the given token. """
        
        if tokenDescriptor.start - self._paragraphStartPosition >= 0: 
            self.setFormat(tokenDescriptor.start - self._paragraphStartPosition, tokenDescriptor.end - tokenDescriptor.start, 
                           self._typeFormatMap[tokenDescriptor.type])
