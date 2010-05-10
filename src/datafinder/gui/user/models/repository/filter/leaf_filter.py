#
# Created: 18.02.2008 lege_ma <malte.legenhausen@dlr.de>
# Changed: $Id: leaf_filter.py 4464 2010-02-18 21:04:07Z schlauch $ 
# 
# Copyright (C) 2003-2008 DLR/SISTEC, Germany
# 
# All rights reserved
# 
# http://www.dlr.de/datafinder/
#


""" 
Filters the original item model.
"""


from PyQt4 import QtCore, QtGui

from datafinder.gui.user.models.repository.filter.base_filter import BaseRepositoryFilter


__version__ = "$LastChangedRevision: 4464 $"


class LeafFilter(BaseRepositoryFilter, QtGui.QSortFilterProxyModel):
    """
    This Model wraps the L{RepositoryModel<datafinder.gui.user.models.repository.repository.RepositoryModel>}.
    It filters files and links.
    """

    def __init__(self, repositoryModel):
        """
        Constructor.

        @param repositoryModel: Repository model.
        @type repositoryModel: L{RepositoryModel<datafinder.gui.user.models.repository.repository.RepositoryModel>}
        """

        BaseRepositoryFilter.__init__(self, repositoryModel)
        QtGui.QSortFilterProxyModel.__init__(self, None)
        
        self._columnCount = 1
        self.setSourceModel(self._repositoryModel)
        
        self.connect(self._repositoryModel, QtCore.SIGNAL("updateSignal"), self._emitActiveIndexChangedSignal)
     
    def columnCount(self, _=QtCore.QModelIndex()):
        """
        @see: L{columnCount<PyQt4.QtGui.QSortFilterProxyModel.columnCount>}
        """

        return self._columnCount
    
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

    def filterAcceptsRow(self, row, parent):
        """
        @see: L{filterAcceptsRow<PyQt4.QtGui.QSortFilterProxyModel.filterAcceptsRow>}
        """

        index = self._repositoryModel.index(row, 0, parent) 
        item = self._repositoryModel.nodeFromIndex(index)
        acceptsRow = False
        if not item is None:
            acceptsRow = item.isCollection
        return acceptsRow
    
    def _emitActiveIndexChangedSignal(self, index):
        """
        Signals change of the active index.
        """

        index = self.mapFromSource(index)
        self.emit(QtCore.SIGNAL("updateSignal"), index)
