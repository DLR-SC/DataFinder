# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#
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
Configurable filter component to restrict displayed properties
"""


from PyQt4 import QtCore, QtGui

from datafinder.gui.user.models.repository.filter.base_filter import BaseRepositoryFilter


__version__ = "$Revision-Id:$" 


class PropertyFilter(BaseRepositoryFilter, QtGui.QSortFilterProxyModel):
    """
    This Model wraps the L{RepositoryModel<datafinder.gui.user.models.repository.repository.RepositoryModel>}.
    It filters specific sets of properties of displayed items.
    """


    ALL_PROPERTIES_FILTER = 0
    
    ALL_SELECTION_MODE = 0
    LEAF_SELECTION_MODE = 1
    COLLECTION_SELECTION_MODE = 2
    

    def __init__(self, repositoryModel, filterMode=ALL_PROPERTIES_FILTER, 
                 itemSelectionMode=LEAF_SELECTION_MODE, allowedItemNameSuffixes=None):
        """
        Constructor.

        @param repositoryModel: Repository model.
        @type repositoryModel: L{RepositoryModel<datafinder.gui.user.models.repository.repository.RepositoryModel>}
        @param filterMode: Determines the set of properties which is filtered.
        @type filterMode: C{int}
        @param itemSelectionMode: Determines the items which can be selected.
        @type itemSelectionMode: C{int}
        @param allowedItemNameSuffixes: When set to a list of strings only items ending on 
                                      one of these strings are shown.
        @type allowedItemNameSuffixes: C{list} of C{unicode}
        """

        BaseRepositoryFilter.__init__(self, repositoryModel)
        QtGui.QSortFilterProxyModel.__init__(self, None)
        
        self._filterMode = filterMode
        self._itemSelectionMode = itemSelectionMode
        self._allowedItemNameSuffixes = allowedItemNameSuffixes
        self.setSourceModel(self._repositoryModel)
        
        self.connect(self._repositoryModel, QtCore.SIGNAL("updateSignal"), self._emitActiveIndexChangedSignal)
     
    def mapFromSource(self, index):
        """
        @see: L{mapFromSource<datafinder.gui.user.models.filter.BaseRepositoryFilter.mapFromSource>}
        Re-implemented to resolve name clash.
        """

        return QtGui.QSortFilterProxyModel.mapFromSource(self, index)

    def mapToSource(self, index):
        """
        @see: L{mapToSource<datafinder.gui.user.models.filter.BaseRepositoryFilter.mapToSource>}
        Re-implemented to resolve name clash.
        """

        return QtGui.QSortFilterProxyModel.mapToSource(self, index)

    def filterAcceptsColumn(self, column, _):
        """ @see: L{filterAcceptsColumn<PyQt4.QtGui.QSortFilterProxyModel.filterAcceptsColumn>} """

        accepted = True
        if self._filterMode == self.ALL_PROPERTIES_FILTER:
            if column != 0:
                accepted = False
        return accepted
    
    def filterAcceptsRow(self, row, parent):
        """ @see: L{filterAcceptsColumn<PyQt4.QtGui.QSortFilterProxyModel.filterAcceptsRow>} """

        accepted = True
        if not self._allowedItemNameSuffixes is None:
            index = self._repositoryModel.index(row, 0, parent) 
            item = self._repositoryModel.nodeFromIndex(index)
            if self._itemSelectionMode == self.ALL_SELECTION_MODE \
               or (self._itemSelectionMode == self.LEAF_SELECTION_MODE and (item.isLeaf or item.isLink)) \
               or (self._itemSelectionMode == self.COLLECTION_SELECTION_MODE and item.isCollection):
                accepted = False
                for allowedItemNameSuffix in self._allowedItemNameSuffixes:
                    if item.name.endswith(allowedItemNameSuffix):
                        accepted = True
                        break
        return accepted

    def _emitActiveIndexChangedSignal(self, index):
        """ Signals change of the active index. """

        index = self.mapFromSource(index)
        self.emit(QtCore.SIGNAL("updateSignal"), index)

    def flags(self, index):
        """ @see: L{flags<PyQt4.QtCore.QAbstractItemModel.flags>}"""

        flags = self._repositoryModel.flags(self.mapToSource(index))
        item = self.nodeFromIndex(index)
        if self._itemSelectionMode == self.LEAF_SELECTION_MODE:
            if item.isCollection or item.isLink:
                flags ^= QtCore.Qt.ItemIsSelectable
        elif self._itemSelectionMode == self.COLLECTION_SELECTION_MODE:
            if not item.isCollection:
                flags ^= QtCore.Qt.ItemIsSelectable
        if item.path is None:
            return QtCore.Qt.NoItemFlags
        return flags
