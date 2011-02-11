# $Filename$$
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
Implements a filter which just allows access to a specific item and its predecessors.
"""


from PyQt4.QtCore import QModelIndex
from PyQt4.QtGui import QSortFilterProxyModel

from datafinder.gui.user.models.repository.filter.base_filter import BaseRepositoryFilter


__version__ = "$Revision-Id:$" 


class PathFilter(BaseRepositoryFilter, QSortFilterProxyModel):
    """
    This Model wraps the L{RepositoryModel<datafinder.gui.user.models.repository.
    repository.RepositoryModel>}. It just provides access to the given item and its 
    predecessors. If no item is is provided the model is empty. 
    """

    def __init__(self, repositoryModel, item=None):
        """
        Constructor.

        @param repositoryModel: Repository model.
        @type repositoryModel: L{RepositoryModel<datafinder.gui.user.models.repository.
        repository.RepositoryModel>}
        @param item: Item to which the filter restricts the access.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """

        BaseRepositoryFilter.__init__(self, repositoryModel)
        QSortFilterProxyModel.__init__(self, None)
        
        self._allowedItems = list()
        self.item = item
        
        self._columnCount = 1
        self.setSourceModel(self._repositoryModel)
        
    def _setItem(self, item):
        """ Sets the item and determines the allowed parents. """
        
        self.reset()
        if item is None:
            self._allowedItems = list() 
        else:
            self._allowedItems = [item]
            currentItem = item.parent
            while not currentItem is None:
                self._allowedItems.append(currentItem)
                currentItem = currentItem.parent
    item = property(None, _setItem)
        
    def columnCount(self, _=QModelIndex()):
        """
        @see: L{columnCount<PyQt4.QtGui.QSortFilterProxyModel.columnCount>}
        """

        return self._columnCount
    
    def mapFromSource(self, index):
        """
        @see: L{mapFromSource<datafinder.gui.user.models.filter.BaseRepositoryFilter.mapFromSource>}
        Re-implemented to resolve name clash.
        """

        return QSortFilterProxyModel.mapFromSource(self, index)

    def mapToSource(self, index):
        """
        @see: L{mapToSource<datafinder.gui.user.models.filter.BaseRepositoryFilter.mapToSource>}
        Re-implemented to resolve name clash.
        """

        return QSortFilterProxyModel.mapToSource(self, index)

    def filterAcceptsRow(self, row, parent):
        """
        @see: L{filterAcceptsRow<PyQt4.QtGui.QSortFilterProxyModel.filterAcceptsRow>}
        """

        index = self._repositoryModel.index(row, 0, parent) 
        item = self._repositoryModel.nodeFromIndex(index)
        return item in self._allowedItems
