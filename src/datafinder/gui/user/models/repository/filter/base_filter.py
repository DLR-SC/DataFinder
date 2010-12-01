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
Implements a common base class for models filtering the repository model.
"""


__version__ = "$Revision-Id:$" 


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
