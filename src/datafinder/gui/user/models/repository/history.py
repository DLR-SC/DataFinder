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
This module contains the HistoryModel.
"""


from PyQt4 import QtCore


__version__ = "$Revision-Id:$" 


class HistoryModel(QtCore.QAbstractItemModel):
    """
    The History model implements a mechanism to store and restore L{QModelIndex<PyQt4.QtCore.QModelIndex>} objects.
    That is necessary for the built-in history functionality. That allows to navigate forward
    and backwards through the L{QModelIndex<PyQt4.QtCore.QModelIndex>} objects.
    """

    def __init__(self, parent=None, maximumLength=20):
        """
        Constructor.

        @param parent: Parent object.
        @type parent: L{QObject<PyQt4.QtCore.QObject>}
        @param maximumLength: Maximum length of the history.
        @type maximumLength: C{int}
        """

        QtCore.QAbstractItemModel.__init__(self, parent)

        self._sortedColumn = 0
        self._sortedOrder = QtCore.Qt.AscendingOrder
        
        self.__pathIndex = 0
        self.__pathCurrent = ""
        self.__pathForwardList = list()
        self.__pathBackwardList = list()

        self.maximumLength = maximumLength

    def __pushHistories(self, loadList, storeList, steps=1):
        """
        Move all entries according to the step count from the load list to the store list.

        @param loadList: The load list contains all entries that will move to C{storeList}.
        @type loadList: C{list}
        @param storeList: The store list stores all entries from the C{loadList}.
        @type storeList: C{list}

        @param steps: The step count that has to been moved forward in the history.
        @type steps: C{int}
        """

        index = steps - 1
        loadList = loadList[::-1]
        if index < len(loadList):
            storeList.append(self.__pathCurrent)
            storeList += loadList[:index]
            self.__pathCurrent = loadList[index]
            loadList = loadList[steps:]

        return loadList[::-1], storeList

    def _getIndex(self):
        """
        Getter for the current index.

        @return: Current model index.
        @rtype: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """

        return self._index(self.__pathCurrent)

    def _setIndex(self, index):
        """
        Setter for the new selected index.

        @param index: Index of a valid directory.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """

        node = self.nodeFromIndex(index)
        if not node is None and node != self._placeHolderCollection and node != self._placeHolderLeaf:
            if not node.isCollection:
                parentIndex = index.parent()
                node = self.nodeFromIndex(parentIndex)
            if not node is None:
                if node.isCollection:
                    self.__pathForwardList = list()
                    if len(self.__pathBackwardList) == 0 or self.__pathCurrent != self.__pathBackwardList[-1]:
                        if len(node.path) > 0 and node.path != self.__pathCurrent:
                            self.__pathBackwardList.append(self.__pathCurrent)
                            self.__pathBackwardList = self.__pathBackwardList[:self.maximumLength]
                    self.__pathCurrent = node.path
                    self.sort(self._sortedColumn, self._sortedOrder)
                    self.updateSignal(index)

    def _getPath(self):
        """
        Returns the current path of the model.

        @return: Current path.
        @rtype: C{unicode}
        """

        return self.__pathCurrent

    def _setPath(self, path):
        """
        Setter for the current path.
        When the given path is a file it will be executed.

        @param path: Path that has to been set to the current path.
        @type path: C{unicode}
        """

        self.activeIndex = self._index(path)

    @property
    def history(self):
        """
        Returns the list of the last stored histories.

        @return: List of index elements.
        @rtype: C{list}, C{list}
        """

        return self.__pathBackwardList[::-1], self.__pathForwardList[::-1]

    def _setRelativeHistoryIndex(self, index):
        """
        Set the current path to the given relative index in the history.
        Positive index will move forward in the history, negative will move backward.

        @param index: Relative index in the history that has to been selected.
        @type index: C{int}
        """

        if index > 0:
            result = self.__pushHistories(self.__pathForwardList,
                                          self.__pathBackwardList,
                                          index)
            self.__pathForwardList, self.__pathBackwardList = result
        elif index < 0:
            result = self.__pushHistories(self.__pathBackwardList,
                                          self.__pathForwardList,
                                          index*-1)
            self.__pathBackwardList, self.__pathForwardList = result
        if index != 0:
            self.updateSignal(self.activeIndex)

    def clear(self):
        """
        Clears the history and emits the update signal.
        """

        self.__pathIndex = 0
        self.__pathCurrent = ""
        self.__pathForwardList = list()
        self.__pathBackwardList = list()

        self.updateSignal()

    def updateSignal(self, index=QtCore.QModelIndex()):
        """
        Emits the update signal to all connected views.

        @param index: The index where a change has happened.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """
        
        self.emit(QtCore.SIGNAL("updateSignal"), index)
        
    def itemDataChangedSignal(self, index=QtCore.QModelIndex()):
        """
        Emits the item data changed signal to all connected views.

        @param index: The index where a change has happened.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """
        
        self.emit(QtCore.SIGNAL("itemDataChanged"), index)
        
    def searchResultChangedSignal(self, items):
        """
        Emits the search result changed signal to all connected views.

        @param items: List of items representing the search result.
        @type index: C{list}
        """
        
        self.emit(QtCore.SIGNAL("searchResultChangedSignal"), items)


    activeIndex = property(_getIndex, _setIndex)

    activePath = property(_getPath, _setPath)

    relativeHistoryIndex = property(fset=_setRelativeHistoryIndex)
