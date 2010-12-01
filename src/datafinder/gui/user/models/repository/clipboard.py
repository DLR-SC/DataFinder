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
This module provides a simple clip-board for internal
copy-cut-paste actions.
"""


from datafinder.gui.user.models import constants


__version__ = "$Revision-Id:$" 


class ItemClipboard(object):
    """ Implements the clip-board. """

    def __init__(self, repositoryModel):
        """
        Constructor.

        @param repositoryModel: The repository model.
        @type repositoryModel: L{RepositoryModel<datafinder.gui.user.models.repository.RepsitoryModel>}
        """
        
        self._clipboard = None
        self.clear()
        self._repositoryModel = repositoryModel
    
    def setCopyIndexes(self, itemIndexes):
        """
        Sets the given item indexes for copying purpose.
        
        @param itemIndexes: List of item indexes marked for the given purpose.
        @type itemIndexes: C{list} of L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """
        
        self._setItemIndexes(constants.CLIPBOARD_STATE_COPY, itemIndexes)
    
    def setCutIndexes(self, itemIndexes):
        """
        Sets the given item indexes for cut purpose.
        
        @param itemIndexes: List of item indexes marked for the given purpose.
        @type itemIndexes: C{list} of L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """
        
        self._setItemIndexes(constants.CLIPBOARD_STATE_CUT, itemIndexes)

    def setCopyPropertiesIndex(self, itemIndex):
        """
        Sets the given item index for copying of its properties.
        
        @param itemIndexes: Item index marked for the given purpose.
        @type itemIndexes: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """
        
        self._setItemIndexes(constants.CLIPBOARD_STATE_COPY_PROPERTIES, [itemIndex])
        
    def _setItemIndexes(self, state, itemIndexes):
        """
        Sets the given item indexes for the purpose specified with C{state}.
        
        @param state: Specifies the purpose (copy or cut) of the temporarily store.
        @type state: L{constants<datafinder.gui.user.common.constants>} 
        @param itemIndexes: List of item indexes marked for the given purpose.
        @type itemIndexes: C{list} of L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """
        
        if state in self._clipboard:
            self.clear()
            self._clipboard[state] = list()
            for index in itemIndexes:
                if index.isValid():
                    item = self._repositoryModel.nodeFromIndex(index)
                    self._clipboard[state].append(item.path)
    
    @property
    def state(self):
        """ 
        Read-only property for the state of the clip-board.
        This can be used to determine whether items for copying or moving
        have been put into the clip-board.
        
        @see L{constants<datafinder.gui.user.models.constants>} 
        """
        
        state = constants.CLIPBOARD_STATE_EMPTY
        for key in self._clipboard:
            if len(self._clipboard[key]) > 0:
                return key
        return state

    @property
    def indexes(self):
        """ Returns the current set of item indexes in the clip-board. """
        
        itemIndexes = list()
        state = self.state
        if state in self._clipboard:
            invalidPaths = list()
            for path in self._clipboard[state]:
                index = self._repositoryModel.indexFromPath(path)
                if index.isValid():
                    itemIndexes.append(index)
                else:
                    invalidPaths.append(path)
            for path in invalidPaths:
                self._clipboard[state].remove(path)
        return itemIndexes
    
    @property
    def isEmpty(self):
        """ Convenience read-only flag to check whether the clip-board is empty. """

        return self.state == constants.CLIPBOARD_STATE_EMPTY
    
    def clear(self):
        """ Clears the content of the clip-board. """
        
        self._clipboard = {constants.CLIPBOARD_STATE_COPY: list(),
                           constants.CLIPBOARD_STATE_CUT: list(),
                           constants.CLIPBOARD_STATE_COPY_PROPERTIES: list()}
