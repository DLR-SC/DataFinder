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
Dialog to configure default data stores.
"""


from PyQt4 import QtCore, QtGui

from datafinder.gui.gen.user.datastores_dialog_ui import Ui_datastoresDialog


__version__ = "$Revision-Id:$" 


class DataStoresPreferencesDialog(QtGui.QDialog, Ui_datastoresDialog):
    """
    Dialog to configure default data stores.
    """

    _DEFAULT_STORE_NAME = ""
    
    def __init__(self, parent=None):
        """
        @param parent: Parent window of this L{QtGui.QDialog}
        @type parent: C{QtGui.QWidget}
        """

        QtGui.QDialog.__init__(self, parent)
        Ui_datastoresDialog.__init__(self)

        self.setupUi(self)

        self._generalStores = list()
        self._archiveStores = list()
        self._offlineStores = list()
        
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"), self.reject)
        self.connect(self.okButton, QtCore.SIGNAL("clicked()"), self.accept)

    def _getDefaultDataStore(self):
        """
        Returns the currently selected default data store.
        """
        
        return unicode(self.defaultDataStoreComboBox.currentText())

    def _setDefaultDataStore(self, name):
        """
        Sets the default data store selection.
        """
        
        if not name in self._generalStores:
            name = self._DEFAULT_STORE_NAME
        self.defaultDataStoreComboBox.setCurrentIndex(self.defaultDataStoreComboBox.findText(name))
        
    defaultDataStore = property(_getDefaultDataStore, _setDefaultDataStore)
    
    def _getDefaultArchiveStore(self):
        """
        Returns the currently selected default archive store.
        """
        
        return unicode(self.defaultArchiveStoreComboBox.currentText())

    def _setDefaultArchiveStore(self, name):
        """
        Sets the default archive store selection.
        """
        
        if not name in self._archiveStores:
            name = self._DEFAULT_STORE_NAME
        self.defaultArchiveStoreComboBox.setCurrentIndex(self.defaultArchiveStoreComboBox.findText(name))
        
    defaultArchiveStore = property(_getDefaultArchiveStore, _setDefaultArchiveStore)

    def _getDefaultOfflineStore(self):
        """
        Returns the currently selected default off-line store.
        """
        
        return unicode(self.defaultOfflineStoreComboBox.currentText())

    def _setDefaultOfflineStore(self, name):
        """
        Sets the default archive store selection.
        """
        
        if not name in self._offlineStores:
            name = self._DEFAULT_STORE_NAME
        self.defaultOfflineStoreComboBox.setCurrentIndex(self.defaultOfflineStoreComboBox.findText(name))
        
    defaultOfflineStore = property(_getDefaultOfflineStore, _setDefaultOfflineStore)
    
    def load(self, generalStores, archiveStores, offlineStores):
        """
        Fills the list of data stores with the given values.
        
        @param generalStores: List of general purpose store names.
        @type generalStores: C{list} of C{unicode}
        @param archiveStores: List of archive store names.
        @type archiveStores: C{list} of C{unicode}
        @param offlineStores: List of off-line store names.
        @type offlineStores: C{list} of C{unicode}
        """

        self._generalStores = generalStores[:]
        generalStores.insert(0, self._DEFAULT_STORE_NAME)
        self._archiveStores = archiveStores[:]
        archiveStores.insert(0, self._DEFAULT_STORE_NAME)
        self._offlineStores = offlineStores[:]
        offlineStores.insert(0, self._DEFAULT_STORE_NAME)
        
        self.defaultArchiveStoreComboBox.clear()
        self.defaultDataStoreComboBox.clear()
        self.defaultOfflineStoreComboBox.clear()
        self.defaultDataStoreComboBox.addItems(generalStores)
        self.defaultArchiveStoreComboBox.addItems(archiveStores)
        self.defaultOfflineStoreComboBox.addItems(offlineStores)
