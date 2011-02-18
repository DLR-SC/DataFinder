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
Some general GUI related mocks.
"""


import os

from PyQt4.QtGui import QStandardItem, QStandardItemModel
from PyQt4.QtCore import QModelIndex


__version__ = "$Revision-Id$" 


class BaseRepositoryMock(QStandardItemModel):
    """ Base mock of GUI specific repository model. """
    
    def __init__(self, availableItems):
        """ Initializes the model with the given items. """
        
        QStandardItemModel.__init__(self)
        
        self.activeIndex = QModelIndex()
        
        # Determine all nested items
        self._parentChildMap = dict()
        self._allItems = dict()
        root = None
        for item in availableItems:
            self._parentChildMap[item.path] = list()
            currentItem = item
            while not currentItem is None:
                self._parentChildMap[item.path].append(currentItem)
                if currentItem.parent is None:
                    root = currentItem
                    self._parentChildMap[item.path].reverse()
                currentItem = currentItem.parent
        self._parentChildMap[root.path] = [root]
        
        # Initializing the model
        sRoot = self.invisibleRootItem()
        sRoot.item = root
        root.sItem = sRoot
        self._allItems[root.path] = root
        for items in self._parentChildMap.values():
            parent = sRoot
            for item in items:
                if root != item:
                    sItem = QStandardItem(item.name)
                    sItem.item = item
                    item.sItem = sItem
                    self._allItems[item.path] = item
                    parent.appendRow(sItem)
                    parent = sItem

    def nodeFromIndex(self, index):
        """ Mocks the item retrieval operation of the original
        repository model. """
        
        sItem = self.itemFromIndex(index)
        if sItem is None:
            sItem = self._allItems["/"].sItem
        return sItem.item
 
    def nodeFromPath(self, path):
        """ Mocks the item form path retrieval method. """
        
        return self.nodeFromIndex(self.indexFromPath(path))
    
    def indexFromPath(self, path):
        """ Mocks the index from path retrieval method. """
        
        if path in self._allItems:
            item = self._allItems[path]
            return self.indexFromItem(item.sItem)
        else:
            return QModelIndex()


class BaseItemMock(object):
    """ Used to mock an item. The parent items are created recursively. """
    
    def __init__(self, path):
        """ Constructor. """
        
        self.childrenPopulated = True
        self.path = path
        self.name = os.path.basename(path)
        self._parent = None

    @property
    def parent(self):
        """ Determines the parent item using the path attribute. """
        
        if self._parent is None:
            if self.path != "/":
                # It is ensured that the parent is from the same base class
                # as the item itself. This makes creation of more specific
                # sub classed items easier.
                self._parent = self.__class__(os.path.dirname(self.path))
        return self._parent
