#
# Created: 25.01.2008 lege_ma <malte.legenhausen@dlr.de>
# Changed:
#
# Copyright (C) 2003-2007 DLR/SISTEC, Germany
#
# All rights reserved
#
# http://www.dlr.de/datafinder
#


"""
Controller of the property view.
"""


from PyQt4 import QtCore

from datafinder.gui.user.common.delegate import AbstractDelegate
from datafinder.gui.user.common import util
from datafinder.gui.user.common.controller import AbstractController


__version__ = "$LastChangedRevision: 4475 $"


class PropertiesController(AbstractController):
    """
    Controls the property view.
    """

    def __init__(self, mainWindow, parentController):
        """
        Constructor.
        """

        AbstractController.__init__(self, mainWindow.serverAttributeTableView, mainWindow, parentController=parentController)
        
        self.horizontalHeader().setSortIndicator(0, QtCore.Qt.AscendingOrder)

        self._delegates = [_PropertiesDelegate(self)]
        

class _PropertiesDelegate(AbstractDelegate):
    """
    This delegate is responsible for all user interaction with the view.
    """

    def __init__(self, controller):
        """
        Constructor.
        """

        AbstractDelegate.__init__(self, controller)

    @util.immediateConnectionDecorator("widget", "modelUpdateSignal")
    def _setSortingEnabled(self):
        """ Enables the sorting behavior. """

        self._controller.setSortingEnabled(True)
   
    @util.immediateConnectionDecorator(["serverTableSelectionModel", "serverTreeSelectionModel"],
                                        "currentChanged(QModelIndex, QModelIndex)")
    def _propertySelectionSlot(self, index, __):
        """
        Slot is called when a item was selected in the tree/table or list view.

        @param index: The selected index.
        @type index: L{QModelIndex<PyQt4.QtCore.QModelIndex>}
        """

        if index.isValid():
            try:
                index = index.model().mapToSource(index)
            except AttributeError:
                index = index
            node = index.model().nodeFromIndex(index)
            self._controller.model.itemIndex = index
            self._mainWindow.serverPropertiesDockWidget.setWindowTitle("Properties of %s" % node.name)
        else:
            self._mainWindow.serverPropertiesDockWidget.setWindowTitle("Properties")

    @util.immediateConnectionDecorator("model", "modelReset()")
    def _modelResetSlot(self):
        """ Handles the reset signal of the property model. """
        
        self._mainWindow.serverPropertiesDockWidget.setWindowTitle("Properties")
