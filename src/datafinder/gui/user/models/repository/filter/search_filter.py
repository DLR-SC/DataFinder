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
Provides search model implementation.
"""


from PyQt4 import QtCore

from datafinder.gui.user.models.repository.filter.base_filter import BaseRepositoryFilter


__version__ = "$Revision-Id:$" 


class SearchFilter(BaseRepositoryFilter, QtCore.QAbstractTableModel):
    """
    The search model enables the support for displaying a search result.
    """

    def __init__(self, repositoryModel):
        """
        Constructor.

        @param repositoryModel: Repository model.
        @type repositoryModel: L{RepositoryModel<datafinder.gui.user.models.repository.repository.RepositoryModel>
        """

        BaseRepositoryFilter.__init__(self, repositoryModel)
        QtCore.QAbstractTableModel.__init__(self, None)

        self._result = list()
        self._sortedColumn = 0
        self._sortOrder = QtCore.Qt.AscendingOrder
        self._emptyModelIndex = QtCore.QModelIndex()
        
        self.connect(self._repositoryModel, QtCore.SIGNAL("searchResultChangedSignal"), self._searchResultChangedSlot)
        self.connect(self._repositoryModel, QtCore.SIGNAL("modelReset()"), self.clear)
        self.connect(self._repositoryModel, QtCore.SIGNAL("rowsRemoved(const QModelIndex & , int, int)"), self._handleRemovedRows)

    def _handleRemovedRows(self, _, __, ___):
        """ Handles removal of rows of the source model. """
        
        self._removeInvalidItems()
        
    def _searchResultChangedSlot(self, items):
        """ Handles changes of the search result. """
        
        self._result = items[:]
        self._removeInvalidItems()
        self._updateSignal()

    def _removeInvalidItems(self):
        """ Removes invalid items (removed from source model) from the current result. """
        
        invalids = list()
        counter = 0
        for item_ in self._result:
            path = item_.path
            item = self._repositoryModel.nodeFromPath(path)
            if item is None:
                invalids.append(item_)
            elif not item.path == path:
                invalids.append(item_)
            counter += 1
        if len(invalids) > 0:
            invalids.reverse()
            for invalid in invalids:
                self._result.remove(invalid)
        self.reset()  
        
    def data(self, index, role):
        """
        @see: L{data<datafinder.gui.user.models.repository.repository.data>}
        Extends the implementation by provision of the path as tool tip.
        """
        
        if role == QtCore.Qt.ToolTipRole and index.row() < len(self._result):
            return QtCore.QVariant(self._result[index.row()].path)
        else:
            try:
                index = self.mapToSource(index)
            except AttributeError:
                self._removeInvalidItems()
                self._updateSignal()
                return QtCore.QVariant()
            return self._repositoryModel.data(index, role)
        
    def rowCount(self, _=QtCore.QModelIndex()):
        """
        @see: L{rowCount<PyQt4.QtCore.QAbstractTableModel.rowCount>}
        """
        
        rowCount = len(self._result)
        return rowCount
    
    def parent(self, _):
        """
        @see: L{parent<PyQt4.QtCore.QAbstractTableModel.parent>}
        """
        
        return self._emptyModelIndex
    
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """
        @see: L{headerData<PyQt4.QtCore.QAbstractTableModel.headerData>}
        """
        
        return self._repositoryModel.headerData(section, orientation, role)
    
    def index(self, row, column, _):
        """
        @see: L{index<PyQt4.QtCore.QAbstractTableModel.index>}
        """
        
        return self.createIndex(row, column, None)
    
    def columnCount(self, _=QtCore.QModelIndex()):
        """
        @see: L{columnCount<PyQt4.QtCore.QAbstractTableModel.columnCount>}
        """
        
        return self._repositoryModel.columnCount(QtCore.QModelIndex())
    
    def mapFromSource(self, _):
        """
        @see: L{mapFromSource<datafinder.gui.user.models.filter.BaseRepositoryFilter.mapFromSource>}
        """
        
        proxyIndex = self._emptyModelIndex
        item = self._repositoryModel.nodeFromIndex()
        for item_ in self._result:
            if item.path == item_.path:
                return self._repositoryModel.indexFromPath(item.path) 
        return proxyIndex
    
    def mapToSource(self, proxyIndex):
        """
        @see: L{mapToSource<datafinder.gui.user.models.filter.BaseRepositoryFilter.mapToSource>}
        """

        sourceIndex = self._emptyModelIndex
        if proxyIndex.isValid():
            try:
                path = self._result[proxyIndex.row()].path
                sourceIndex = self._repositoryModel.indexFromPath(path, proxyIndex.column())
            except IndexError:
                sourceIndex = self._emptyModelIndex
        return sourceIndex
    
    @staticmethod
    def flags(_):
        """ L{flags<QtCore.QAbstractItemModel.flags>} """
        
        flags = QtCore.Qt.ItemIsSelectable
        flags |= QtCore.Qt.ItemIsEnabled
        return flags
    
    def sort(self, column, order=QtCore.Qt.AscendingOrder):
        """
        @see: L{sort<PyQt4.QtCore.QAbstractTableModel.sort>}
        """

        self._sortedColumn = column
        self._sortOrder = order
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self._repositoryModel.sortItems(self._result, column, order)
        self.emit(QtCore.SIGNAL("layoutChanged()"))

    def clear(self):
        """
        Removes all results from the model.
        """

        self._result = list()
        self.reset()

    def _updateSignal(self):
        """
        Signal is emitted when the data of the model has changed.
        """

        self.emit(QtCore.SIGNAL("updateSignal"))

    @property
    def sortProperties(self):
        """
        Returns how the model is sorted.

        @return: Tuple describing column count and sorting order.
        @rtype: C{tuple} C{int}, C{int}
        """

        return self._sortedColumn, self._sortOrder
