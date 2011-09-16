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
Implements the meta data search dialog including results view.
"""


import bisect

from PyQt4 import QtCore, QtGui

from datafinder.common.logger import getDefaultLogger
from datafinder.core import search_restriction
from datafinder.gui.gen.user.search_dialog_ui import Ui_searchDialog
from datafinder.gui.user.common.controller import AbstractController
from datafinder.gui.user.common import util
from datafinder.gui.user.common.item_selection_dialog import ItemSelectionDialog
from datafinder.gui.user.controller.output.searchresults import SearchResultController
from datafinder.gui.user.models.repository.filter.leaf_filter import LeafFilter
from datafinder.gui.user.models.repository.filter.search_filter import SearchFilter
from datafinder.gui.user.dialogs.search_dialog.utils import KeywordSearchQueryConverter
from datafinder.gui.user.dialogs.search_dialog.search_query_editor import Completer, SearchSyntaxHighlighter
from datafinder.gui.user.dialogs.search_dialog.utils import SearchQueryAnalyzer


__version__ = "$Revision-Id:$" 


class SearchDialog(QtGui.QDialog, Ui_searchDialog):
    """
    This class implements the search dialog.
    """

    _logger = getDefaultLogger()
        
    def __init__(self, repositoryModel, parentWidget, itemActionController):
        """
        Constructor.
        
        @param repositoryModel: Reference on the repository model.
        @type repositoryModel: L{RepositoryModel<datafinder.gui.user.models.repository.repository.RepositoryModel>}
        @param parentWidget: Parent widget of this dialog.
        @type parentWidget: L{QWidget<PyQt4.QtGui.QWidget>}
        """

        QtGui.QDialog.__init__(self, parentWidget)
        Ui_searchDialog.__init__(self)
        self.setupUi(self)
        
        self._collectionSearchDialog = None
        self._parser = search_restriction.SearchRestrictionParser()
        
        self.__model = repositoryModel
        self._worker = None
        self._initialSearchQuery = ""
        
        self.__searchQueryAnalyzer = SearchQueryAnalyzer(self._parser, self._preparePropertyDefinitionToolTips())
        self._initSearchQueryEditor()
        self.__highlighter = SearchSyntaxHighlighter(self.__searchQueryAnalyzer, self.restrictionTextEdit)
        self.__searchResultController = SearchResultController(self.resultsTableView, parentWidget, self, itemActionController)
        self.__searchResultController.model = SearchFilter(self.__model)
        self.__storedSearchesController = _SearchStorerController(self.searchesListView, self)
        self.__storedSearchesController.model = _ServerSearchStoreModel(repositoryModel.preferences)
        self._keywordSearchQueryConverter = KeywordSearchQueryConverter(self.__model.repository.configuration.registeredPropertyDefinitions)
        
        self.storedSearchesPushButton.setChecked(True)
        self._activateSimpleMode()
        self._connectSlots()

    def show(self):
        """ @see: L{QDialog<PyQt4.QtGui.QDialog>}"""
        
        self.startLineEdit.setText(self.__model.activePath or "/")
        QtGui.QDialog.show(self)

    def _initSearchQueryEditor(self):
        """ Initializes the search query editor. """
        
        self.restrictionTextEdit.searchQueryAnalyzer = self.__searchQueryAnalyzer
        propertyNameCompleter = Completer(self._preparePropertyDefinitionToolTips(), True)
        self.restrictionTextEdit.registerCompleter(propertyNameCompleter, SearchQueryAnalyzer.PROPERTY_TYPE)
        
        comparisionOperatorCompleter = QtGui.QCompleter(self._parser.comparisonTokens)
        comparisionOperatorCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.restrictionTextEdit.registerCompleter(comparisionOperatorCompleter, SearchQueryAnalyzer.COMPARISON_TYPE)

        conjunctionOperatorCompleter = QtGui.QCompleter(self._parser.conjunctionTokens)
        conjunctionOperatorCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.restrictionTextEdit.registerCompleter(conjunctionOperatorCompleter, SearchQueryAnalyzer.CONJUNCTION_TYPE)
        
        completions = {u"''": u"Empty Value.", 
                       u"'DD.MM.YYYY'": u"Date Format Value.",
                       u"'DD.MM.YYYY HH:MM:SS'": u"Date Time Format Value."}
        valueStateCompleter = Completer(completions)
        self.restrictionTextEdit.registerCompleter(valueStateCompleter, SearchQueryAnalyzer.LITERAL_TYPE)
        self.restrictionTextEdit.state = SearchQueryAnalyzer.PROPERTY_TYPE
        
    def _preparePropertyDefinitionToolTips(self):
        """ Prepares a dictionary containing the tool tips of existing property definitions. """
        
        result = dict()
        for propDef in self.__model.repository.configuration.registeredPropertyDefinitions.values():
            result[propDef.identifier] = util.determinePropertyDefinitionToolTip(propDef)
        return result
    
    def _connectSlots(self):
        """ Connects signals and slots. """
        
        self.connect(self.startSelectionButton, QtCore.SIGNAL("clicked()"), self._showSelectionClickedSlot)
        self.connect(self.closeButton, QtCore.SIGNAL("clicked()"), self._closeClickedSlot)
        self.connect(self.searchesListView, QtCore.SIGNAL("doubleClicked(QModelIndex)"), self._storedSearchClickedSlot)
        self.connect(self.expertModePushButton, QtCore.SIGNAL("clicked(bool)"), self._searchModeChanged)
        self.connect(self.storedSearchesPushButton, QtCore.SIGNAL("clicked(bool)"), self._storedSearchesModeChanged)
        self.connect(self.saveSearchButton, QtCore.SIGNAL("clicked()"), self._handleSearchStored)
        
    def _handleSearchStored(self):
        """ Reacts on when saving a search. """
        
        self._initialSearchQuery = self.restrictionTextEdit.toPlainText()
        
    def _showSelectionClickedSlot(self):
        """ 
        Slot is called when the start selection button was clicked. 
        """

        leafFilterModel = LeafFilter(self.__model)
        self._collectionSearchDialog = ItemSelectionDialog(leafFilterModel, self)
        self._collectionSearchDialog.selectedIndex = self.__model.indexFromPath(unicode(self.startLineEdit.text()))
        if self._collectionSearchDialog.exec_() == QtGui.QDialog.Accepted:
            item = self.__model.nodeFromIndex(self._collectionSearchDialog.selectedIndex)
            self.startLineEdit.setText(item.path or "/")

    def _closeClickedSlot(self):
        """ 
        Slot is called when the close button was clicked. 
        """

        if self._proceedWithUnsavedChanges():
            self.__storedSearchesController.model.save()
            self.close()

    def _expertSearchClickedSlot(self):
        """ 
        Slot is called when the search button was clicked and the dialog is in
        the expert mode. 
        """

        self.resultsGroupBox.show()
        self.setEnabled(False)
        path = unicode(self.startLineEdit.text())
        query = unicode(self.restrictionTextEdit.toPlainText())
        self._worker = util.startNewQtThread(self.__model.search,
                                             self._searchFinishedSlot, 
                                             self.__model.indexFromPath(path),
                                             query)
        
    def _searchFinishedSlot(self):
        """
        Slot is called when the search thread finished its work 
        and the dialog is in expert mode.
        """
        
        if not self._worker.error is None:
            QtGui.QMessageBox.critical(self, "Search Error", self._worker.error.message)
        self.setEnabled(True)
        
    def _simpleSearchClickedSlot(self):
        """
        Slot is called when the search button was clicked and the dialog is in the simple
        search mode.
        """
        
        self.splitter_2.show()
        self.resultsGroupBox.show()
        self.setEnabled(False)
        text = unicode(self.keywordLineEdit.text())
        path = unicode(self.startLineEdit.text())
        query = self._keywordSearchQueryConverter.convert(text)
        self._worker = util.startNewQtThread(self.__model.search,
                                             self._searchFinishedSlot, 
                                             self.__model.indexFromPath(path),
                                             query)
            
    def _storedSearchClickedSlot(self, index):
        """ Slot is called when a search was selected from the stored searches. """

        if self._proceedWithUnsavedChanges():
            self.__storedSearchesController.searchSelectedSlot(index)
            restriction = self.__storedSearchesController.model.restrictionFromIndex(index)
            self._initialSearchQuery = restriction
            self.restrictionTextEdit.setText(restriction)
        else:
            self.searchesListView.clearSelection()
            
    def _searchModeChanged(self, expertMode):
        """
        Slot is called when the state of the expertModePushButton changed.
        """
        
        if expertMode:
            self._activateExpertMode()
        else:
            if self._proceedWithUnsavedChanges():
                self._activateSimpleMode()
            else:
                self.expertModePushButton.setChecked(True)
            
    def _proceedWithUnsavedChanges(self):
        """ 
        Checks for unsaved changes of the search restrictions 
        and asks the user how to proceed. 
        """
        
        continue_ = True
        if self._initialSearchQuery != self.restrictionTextEdit.toPlainText():
            answer = QtGui.QMessageBox.question(self, "Unsaved Changes", "Some changes of the search restrictions "\
                                                      + "have not yet been saved and may be lost when you proceed."\
                                                      + "\nDo you want to continue?",
                                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if answer == QtGui.QMessageBox.No:
                continue_ = False
        return continue_
    
    def _storedSearchesModeChanged(self, storedSearches):
        """
        Slot is called when the state of the storedSearchesPushButton changed.
        """
        
        self.storedSearchGroupBox.setVisible(bool(storedSearches))
    
    def _activateSimpleMode(self):
        """
        Activates the simple mode. It hides all expert mode's widgets and
        sets all simple mode's widgets visible. It also manages the signal slot
        connections. 
        """
        
        self.disconnect(self.__searchQueryAnalyzer, QtCore.SIGNAL(SearchQueryAnalyzer.VALIDATION_SIGNAL), self.searchButton.setEnabled)
        self.disconnect(self.__searchQueryAnalyzer, QtCore.SIGNAL(SearchQueryAnalyzer.VALIDATION_SIGNAL), 
                        self.__storedSearchesController.validationSlot)
        self.disconnect(self.searchButton, QtCore.SIGNAL("clicked()"), self._expertSearchClickedSlot)
        self.connect(self.keywordLineEdit, QtCore.SIGNAL("textChanged(const QString &)"), self._handleKeywordLineEditTextChanged)
        self.connect(self.searchButton, QtCore.SIGNAL("clicked()"), self._simpleSearchClickedSlot)

        self.splitter_2.hide()
        self.resultsGroupBox.hide()
        self.optionsGroupBox.hide()
        self.storedSearchGroupBox.hide()
        
        self.simpleSearchGroupBox.show()
        self.searchButton.show()
        self.storedSearchesPushButton.hide()
        
        self.resize(self.minimumSize().width(), self.sizeHint().height())
        
        self._handleKeywordLineEditTextChanged(self.keywordLineEdit.text())
        
    def _handleKeywordLineEditTextChanged(self, newText):
        """ Handles changes of the keyword line editor. """
        
        isEmpty = len(unicode(newText).strip()) == 0
        self.searchButton.setEnabled(not isEmpty)
        
    def _activateExpertMode(self):
        """
        Activates the expert mode. It hides all simple mode's widgets and
        sets all expert mode's widgets visible. It also manages the signal slot
        connections. 
        """
        
        self.disconnect(self.searchButton, QtCore.SIGNAL("clicked()"), self._simpleSearchClickedSlot)
        self.disconnect(self.keywordLineEdit, QtCore.SIGNAL("textChanged(const QString &)"), self._handleKeywordLineEditTextChanged)
        
        self.optionsGroupBox.show()

        self.storedSearchGroupBox.setVisible(self.storedSearchesPushButton.isChecked())

        self.connect(self.searchButton, QtCore.SIGNAL("clicked()"), self._expertSearchClickedSlot)
        self.connect(self.__searchQueryAnalyzer, QtCore.SIGNAL(SearchQueryAnalyzer.VALIDATION_SIGNAL), self.searchButton.setEnabled)
        self.connect(self.__searchQueryAnalyzer, QtCore.SIGNAL(SearchQueryAnalyzer.VALIDATION_SIGNAL), 
                     self.__storedSearchesController.validationSlot)

        self.startLabel.hide()
        self.startSelectionButton.hide()
        self.splitter_2.show()
        self.simpleSearchGroupBox.hide()
        self.storedSearchesPushButton.show()
        query = self._keywordSearchQueryConverter.convert(unicode(self.keywordLineEdit.text()))
        self._initialSearchQuery = query
        self.restrictionTextEdit.setText(query)


class _SearchStorerController(AbstractController):
    """
    Class controls the storage and retrieval of stored searches.
    """

    def __init__(self, listView, parentController):
        """
        Constructor.
        """

        AbstractController.__init__(self, listView, parentController=parentController)

        self.__valid = False

        self.connect(self.widget, QtCore.SIGNAL("modelUpdateSignal"), self.__modelUpdateSlot)
        self.connect(self.parentController.saveSearchButton,
                     QtCore.SIGNAL("clicked()"),
                     self.saveSearchClickedSlot)
        self.connect(self.parentController.deleteSearchButton,
                     QtCore.SIGNAL("clicked()"),
                     self.deleteSearchClickedSlot)
        self.connect(self.parentController.searchNameLineEdit,
                     QtCore.SIGNAL("textChanged(QString)"),
                     self.searchNameTextChanged)

    def __modelUpdateSlot(self, _):
        """
        Slot is called when the model has changed.
        """
        
        self.connect(self.selectionModel(),
                     QtCore.SIGNAL("currentChanged(QModelIndex, QModelIndex)"),
                     self.searchSelectedSlot)

        self.connect(self.selectionModel(),
                     QtCore.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"),
                     self.__deleteButtonEnableSlot)

    def __saveButtonEnableCheck(self):
        """
        Checks if the restriction text is valid and the search name lint edit isn't empty.
        """
        
        searchSaveName = unicode(self.parentController.searchNameLineEdit.text()).strip()
        self.parentController.saveSearchButton.setEnabled(self.__valid and len(searchSaveName) > 0)

    def __deleteButtonEnableSlot(self):
        """
        Checked if an item is selected in the L{QtGui.QListView} and enables or disables the delete button.
        """

        self.parentController.deleteSearchButton.setEnabled(self.selectionModel().hasSelection())

    def deleteSearchClickedSlot(self):
        """
        Deletes the selected search from the model.
        """

        if self.selectionModel().hasSelection():
            index = self.selectionModel().selectedIndexes()[0]
            self.model.remove(index)

    def saveSearchClickedSlot(self):
        """
        Slot is called when a new search has to be added to the search storer view.
        """

        name = unicode(self.parentController.searchNameLineEdit.text())
        restriction = unicode(self.parentController.restrictionTextEdit.toPlainText())

        index = self.model.set(name, restriction)
        self.selectionModel().setCurrentIndex(index, QtGui.QItemSelectionModel.ClearAndSelect)

    def validationSlot(self, valid):
        """
        Slot is called when the validation of the restriction text edit has changed.

        @param valid: The information if the restriction is valid.
        @type valid: C{bool}
        """

        self.__valid = valid
        self.__saveButtonEnableCheck()

    def searchNameTextChanged(self):
        """
        Slot is called when the name of the save name line edit changed.
        """

        self.__saveButtonEnableCheck()

    def searchSelectedSlot(self, index):
        """
        Slot is called when a stored search was selected.

        @param index: The index of the selected stored search.
        @type index: C{QtCore.QModelIndex}
        """

        if index.isValid():
            self.parentController.searchNameLineEdit.setText(self.model.data(index).toString())
        else:
            self.parentController.searchNameLineEdit.setText("")


class _ServerSearchStoreModel(QtCore.QAbstractTableModel):
    """
    The SearchStorerModel contains all stored searches. The class is responsible for holding
    the data structure and the management of it.
    """

    def __init__(self, preferences):
        """
        Constructor.

        @param preferences: Object containing application preferences.
        @type preferences: L{PreferencesHandler<datafinder.core.configuration.preferences.PreferencesHandler>}
        """

        QtCore.QAbstractTableModel.__init__(self, None)

        self._preferences = preferences
        self._dirty = False
        self._columnCount = 1
        self._storedSearchQueries = list()
        
        for searchQuery in preferences.searchQueries:
            self._insert(searchQuery.name, searchQuery.query)

    def _insert(self, name, restriction):
        """
        Insert the given arguments at the right position of the this list.
        After the insert the internal list is still sorted.
        """

        if not name is None and not restriction is None:
            toolTip = self._determineRestrictionToolTip(restriction)
            bisectList = util.BisectColumnHelper(self._storedSearchQueries, 0)
            row = bisect.bisect_left(bisectList, name.lower())
            self.beginInsertRows(QtCore.QModelIndex(), row, row)
            self._storedSearchQueries.insert(row, [name, restriction, toolTip])
            self.endInsertRows()
            return row
        
    @staticmethod
    def _determineRestrictionToolTip(restriction):
        """ Determines the tool tip of the given restrictions. """
        
        toolTip = restriction
        toolTipLength = len(toolTip)
        for counter in range(1, (toolTipLength / 60) + 1):
            toolTip = toolTip[:(counter * 60)] + "\n" + toolTip[(counter * 60):]
        return toolTip

    def rowCount(self, _=QtCore.QModelIndex()):
        """
        @see: L{rowCount<PyQt4.QtCore.QAbstractTableModel.rowCount>}
        """

        return len(self._storedSearchQueries)

    def columnCount(self, _=QtCore.QModelIndex()):
        """
        @see: L{columnCount<PyQt4.QtCore.QAbstractTableModel.columnCount>}
        """

        return self._columnCount

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """
        @see: L{data<PyQt4.QtCore.QAbstractTableModel.data>}
        """

        row = index.row()
        variant = QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            variant = QtCore.QVariant(self._storedSearchQueries[row][index.column()])
        elif role == QtCore.Qt.ToolTipRole:
            variant = QtCore.QVariant(self._storedSearchQueries[row][2])
        return variant

    def set(self, name, restriction):
        """
        Add a new line or edit an existing line in the stored searches.

        @param name: Name of the new search.
        @type name: C{unicode}
        @param restriction: Restriction that has to be saved under the given name.
        @type restriction: C{unicode}

        @return: The index of the new created search item.
        @rtype: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """

        name = unicode(name)
        restriction = unicode(restriction)

        try:
            row = [item[0] for item in self._storedSearchQueries].index(name)
        except ValueError:
            row = self._insert(name, restriction)
        else:
            self._storedSearchQueries[row][1] = restriction
            self._storedSearchQueries[row][2] = self._determineRestrictionToolTip(restriction)

        self._dirty = True
        return self.createIndex(row, 0, self._storedSearchQueries[row][0])

    def remove(self, index):
        """
        Deletes the search under the given index.

        @param index: The index that has to be deleted.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """

        row = index.row()
        self.beginRemoveRows(QtCore.QModelIndex(), row, row)
        del self._storedSearchQueries[row]
        self.endRemoveRows()
        self._dirty = True

    def save(self, force=False):
        """
        Save all searches in the preferences.

        @param force: Force the save process even no data has changed.
        @type force: C{boolean}
        """

        if self._dirty or force:
            self._preferences.clearSearchQueries()
            for name, query, _ in self._storedSearchQueries:
                self._preferences.addSearchQuery(name, query)
        self._dirty = False

    def restrictionFromIndex(self, index):
        """
        Returns the restriction from the given index.

        @param index: The index from which the restriction has to be returned.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}

        @return: The restriction for the given index.
        @rtype: C{unicode}
        """

        if index.isValid():
            return unicode(self._storedSearchQueries[index.row()][1])
        return ""
