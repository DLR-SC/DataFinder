#
# Created: 13.11.2009 schlauch <Tobias.Schlauch@dlrde>
# Changed: $Id: select_item.py 4479 2010-03-02 21:55:09Z schlauch $ 
# 
# Copyright (c) 2009, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements a widget allowing selection of an item in a specific repository
with a tree view.
"""


from PyQt4 import QtGui, QtCore

from datafinder.gui.gen.widgets.select_item_widget_ui import Ui_selectItemWidget


__version__ = "$LastChangedRevision: 4479 $"


class SelectItemWidget(QtGui.QWidget, Ui_selectItemWidget):
    """ 
    Implements a widget allowing selection of an item in a 
    specific repository with a tree view.
    """

    SELECTED_INDEX_CHANGED_SIGNAL = "SelectedIndexChanged"
    SELECTION_CHANGED = "SelectionChanged"
    
    def __init__(self, parent):
        """ @see: L{QWidget<PyQt4.QtGui.QWidget>} """
        
        QtGui.QWidget.__init__(self, parent)
        Ui_selectItemWidget.__init__(self)
                
        self._repositoryModel = None
        self._isSingleSelectionMode = True
        
        self.setupUi(self)

    def hidePathEditor(self):
        """ Hides the path editor. """
        
        self._isSingleSelectionMode = False
        self.pathEditLabel.hide()
        self.pathLineEdit.hide()
        self.disconnect(self.pathLineEdit, QtCore.SIGNAL("editingFinished()"), self._pathLineEditTextEditingFinishedSlot)

    def showPathEditor(self):
        """ Hides the path editor. """
        
        self._isSingleSelectionMode = True
        self.pathEditLabel.show()
        self.pathLineEdit.show()
        self.connect(self.pathLineEdit, QtCore.SIGNAL("editingFinished()"), self._pathLineEditTextEditingFinishedSlot)

    def _pathLineEditTextEditingFinishedSlot(self):
        """ Handles changes of the path line edit. """
        
        index = self._repositoryModel.indexFromPath(unicode(self.pathLineEdit.text()))
        self.selectedIndex = index
                
    def _selectedIndexChangedSlot(self, currentIndex, _):
        """ Sets the path of the selected item. """
        
        if not currentIndex.model() is None:
            item = currentIndex.model().nodeFromIndex(currentIndex)
        else:
            item = self._repositoryModel.nodeFromIndex(currentIndex)
        if self._isSingleSelectionMode:
            self.pathLineEdit.setText(item.path or "")

        if item.childrenPopulated:
            self._ensureChildrenFetching(currentIndex)
        self.emit(QtCore.SIGNAL(self.SELECTED_INDEX_CHANGED_SIGNAL), self._getSelectedIndex())

    def _ensureChildrenFetching(self, index):
        """ 
        A little workaround as on sometimes not all children are correctly
        displayed in the tree view (only the first place holder item) when
        using the arrow key for collection expansion.
        """

        if index.isValid():
            self._repositoryModel.fetchMore(index)

    def _selectionChangedSlot(self, _, __):
        """ Propagates selection changes of the tree view. """
        
        self.emit(QtCore.SIGNAL(self.SELECTION_CHANGED))
        
    def _setRepositoryModel(self, repositoryModel):
        """ 
        Sets the underlying repository model. 
        
        @param repositoryModel: The underlying repository model.
        @type repositoryModel: L{AbstractRepositoryModelFilter<datafinder.gui.user.models.filter.AbstractRepositoryModelFilter>}
        """
        
        self._repositoryModel = repositoryModel
        self.repositoryTreeView.setModel(self._repositoryModel)
        self.connect(self.repositoryTreeView.selectionModel(), 
                     QtCore.SIGNAL("currentChanged(QModelIndex, QModelIndex)"), 
                     self._selectedIndexChangedSlot)
        self.connect(self.repositoryTreeView.selectionModel(), 
                     QtCore.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"), 
                     self._selectionChangedSlot)
        
    repositoryModel = property(None, _setRepositoryModel)

    def _setSelectedIndexes(self, indexes):
        """
        Selects the given indexes.
        
        @param indexes: List of index in terms of the source repository model.
        @type indexes: C{list} of L{QModelIndex<PyQt4.QtCore.QModelIndex>} 
        """
        
        for index in indexes:
            if index.isValid() and index.model() != self._repositoryModel: # think of this
                index = self._repositoryModel.mapFromSource(index)
            if self._isSingleSelectionMode:
                item = self._repositoryModel.nodeFromIndex(index)
                self.pathLineEdit.setText(item.path)
                self.repositoryTreeView.setCurrentIndex(index)
            else:
                self.repositoryTreeView.scrollTo(index)
                self.repositoryTreeView.selectionModel().select(index, QtGui.QItemSelectionModel.Select)
                
    def _getSelectedIndexes(self):
        """
        Returns the selected indexes in terms of the source repository model.
        
        @return: List of indexes in terms of the source repository model.
        @rtype: C{list} of L{QModelIndex<PyQt4.QtCore.QModelIndex>} 
        """
        
        selectedIndexes = list()
        if self._isSingleSelectionMode:
            try:
                selectedIndexes.append(self._repositoryModel.mapToSource(self.repositoryTreeView.currentIndex()))
            except AttributeError:
                selectedIndexes.append(self.repositoryTreeView.currentIndex())
        else:
            for index in self.repositoryTreeView.selectionModel().selectedRows():
                try:
                    if self._repositoryModel.flags(index) & QtCore.Qt.ItemIsSelectable:
                        selectedIndexes.append(self._repositoryModel.mapToSource(index))
                except AttributeError:
                    selectedIndexes.append(index)
        return selectedIndexes
    
    selectedIndexes = property(_getSelectedIndexes, _setSelectedIndexes)

    def _setSelectedIndex(self, index):
        """ Selects the given index. """
        
        self._setSelectedIndexes([index])
    
    def _getSelectedIndex(self):
        """ Returns the selected index in terms of the source repository model. """
        
        try:
            return self._getSelectedIndexes()[0]
        except IndexError:
            return QtCore.QModelIndex()
    
    selectedIndex = property(_getSelectedIndex, _setSelectedIndex)

    def _setSelectionMode(self, selectionMode):
        """ Sets the selection mode of the tree view. """
        
        self.repositoryTreeView.setSelectionMode(selectionMode)
        if selectionMode == QtGui.QAbstractItemView.MultiSelection:
            self.hidePathEditor()
        else:
            self.showPathEditor()
    
    selectionMode = property(None, _setSelectionMode)

    @property
    def hasEmptySelection(self):
        """ Determines whether anything at all has been selected. """
        
        return len(self.selectedIndexes) == 0
