#
# Created: 30.01.2010 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: property_filter.py 4624 2010-04-20 08:29:40Z schlauch $ 
# 
# Copyright (C) 2003-2008 DLR/SISTEC, Germany
# 
# All rights reserved
# 
# http://www.dlr.de/datafinder/
#


""" 
Configurable filter component to restrict displayed properties
"""


from PyQt4 import QtCore, QtGui

from datafinder.gui.user.models.repository.filter.base_filter import BaseRepositoryFilter


__version__ = "$LastChangedRevision: 4624 $"


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
