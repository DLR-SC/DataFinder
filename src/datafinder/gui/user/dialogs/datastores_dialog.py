#
# Created: 28.01.2008 wend_he <heinrich.wendel@dlr.de>
# Changed: $Id: datastores_dialog.py 4450 2010-02-09 16:30:51Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


"""
Dialog to configure local default data stores.
"""


from PyQt4 import QtCore, QtGui

from datafinder.gui.gen.user.datastores_dialog_ui import Ui_datastoresDialog


__version__ = "$LastChangedRevision: 4450 $"


class DatastoresDialog(QtGui.QDialog, Ui_datastoresDialog):
    """
    Dialog to configure connection preferences, currently only LDAP.
    """

    _DEFAULT_STORE_NAME = ""
    
    def __init__(self, parent=None):
        """
        Constructor.

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
