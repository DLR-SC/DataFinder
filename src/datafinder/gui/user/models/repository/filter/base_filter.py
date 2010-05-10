#
# Created: 13.11.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: base_filter.py 4423 2010-02-01 14:52:21Z schlauch $ 
# 
# Copyright (c) 2009, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements a common base class for models filtering the repository model.
"""


__version__ = "$LastChangedRevision: 4423 $"


class BaseRepositoryFilter(object):
    """ Define a basic interface for models filtering the repository model. """

    def __init__(self, repositoryModel):
        """
        Constructor.
        
        @param repositoryModel: Repository model.
        @type repositoryModel: L{RepositoryModel<datafinder.gui.user.models.repository.repository.RepositoryModel>}
        """
        
        self._repositoryModel = repositoryModel

    def mapFromSource(self, index):
        """
        Maps index in terms of the source model to an index in terms of the filter model.
        
        @param index: Index in terms of the source model.
        @type proxyIndex: L{index<PyQt4.QtCore.QAbstractItemModel.index>}
        
        @return: Index in terms of the filter model.
        @rtype: L{index<PyQt4.QtCore.QAbstractItemModel.index>}
        """
        
        pass
    
    def mapToSource(self, index):
        """
        Maps index in terms of the filter model to an index in terms of the source model.
        
        @param index: Index in terms of the filter model.
        @type proxyIndex: L{index<PyQt4.QtCore.QAbstractItemModel.index>}
        
        @return: Index in terms of the source model.
        @rtype: L{index<PyQt4.QtCore.QAbstractItemModel.index>}
        """

        pass
    
    def indexFromPath(self, path):
        """
        @see: L{indexFromPath<datafinder.gui.user.models.repository.repository.indexFromPath>}
        """
        
        return self.mapFromSource(self._repositoryModel.indexFromPath(path))

    def nodeFromIndex(self, proxyIndex):
        """
        @see: L{nodeFromIndex<datafinder.gui.user.models.repository.repository.RepositoryModel.nodeFromIndex>}
        
        @param proxyIndex: Index in terms of the filter model.
        @type proxyIndex: L{index<PyQt4.QtCore.QAbstractItemModel.index>}
        """
        
        index = self.mapToSource(proxyIndex)
        return self._repositoryModel.nodeFromIndex(index)

    @property
    def repositoryModel(self):
        """ 
        Getter for the underlying repository model. 
        
        @param repositoryModel: Repository model.
        @type repositoryModel: L{RepositoryModel<datafinder.gui.user.models.repository.repository.RepositoryModel>}
        """
        
        return self._repositoryModel
        
    def _getIndex(self):
        """
        @see: L{_getIndex<datafinder.gui.user.models.repository.history.HistoryModel._getIndex>}
        """

        return self.mapFromSource(self._repositoryModel.activeIndex)

    def _setIndex(self, index):
        """
        @see: L{_setIndex<datafinder.gui.user.models.repository.history.HistoryModel._setIndex>}
        """

        self._repositoryModel.activeIndex = self.mapToSource(index)

    activeIndex = property(_getIndex, _setIndex)
