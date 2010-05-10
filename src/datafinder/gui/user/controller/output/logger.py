#
# Created: 21.01.2008 lege_ma <malte.legenhausen@dlr.de>
# Changed:
#
# Copyright (C) 2003-2007 DLR/SISTEC, Germany
#
# All rights reserved
#
# http://www.dlr.de/datafinder
#


"""
This module contains all classes that are necessary for the use of the standard Python
logging mechanism in the DataFinder GUI components.
"""


import logging
import functools

from PyQt4 import QtCore, QtGui

from datafinder.gui.user.common.controller import AbstractController


__version__ = "$LastChangedRevision: 4475 $"


class LoggingTableController(AbstractController):
    """
    The LoggingController presents logging messages.
    """

    def __init__(self, widget, parentController):
        """
        Constructor.

        @param widget: The L{QtGui.QTableView} that has to be used for the presentation.
        @type widget: L{QTableView<PyQt4.QtGui.QTableView>}
        @param parentController: Parent controller of this one.
        @type parentController: L{AbstractController<datafinder.gui.user.common.controller.AbstractController>}
        """

        AbstractController.__init__(self, widget, parentController=parentController)

        self.horizontalHeader().setSortIndicator(1, QtCore.Qt.DescendingOrder)

        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)

        self.connect(self.widget, QtCore.SIGNAL("modelUpdateSignal"), self.__modelUpdateSlot)
        self.connect(self.widget,
                     QtCore.SIGNAL("customContextMenuRequested(QPoint)"),
                     self.showContextMenuSlot)

    def __modelUpdateSlot(self, model):
        """ Slot is called when the model had changed. """

        self.setSortingEnabled(True)
        self.connect(model, QtCore.SIGNAL("rowsInserted(QModelIndex, int, int)"), self.rowsInsertedSlot)

    def showContextMenuSlot(self):
        """ Shows the table context menu at the current cursor position. """

        menu = QtGui.QMenu(self.widget)
        for level in (logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG):
            action = menu.addAction(logging.getLevelName(level))
            action.setCheckable(True)
            action.setChecked(not self.model.isFiltered(level))
            action.connect(action, QtCore.SIGNAL("triggered(bool)"),
                           functools.partial(self.filterLevelSlot, level))
        menu.addSeparator()
        action = menu.addAction(menu.tr("Clear"))
        action.connect(action, QtCore.SIGNAL("triggered()"), self.model.flush)
        action.setEnabled(self.model.rowCount() > 0)
        menu.exec_(QtGui.QCursor.pos())

    def filterLevelSlot(self, level, shown):
        """
        Slot is called when the given level has to be added or removed from the filter list.

        @param level: Level that has to be added or removed.
        @type level: C{int}
        @param shown: Indicated if the given level has to be shown.
        @type shown: C{bool}
        """

        if shown:
            self.model.removeFilter(level)
        else:
            self.model.addFilter(level)

    def rowsInsertedSlot(self, _, __, ___):
        """
        Slot is called when a row was inserted.

        @param parent: The index in that where added new rows.
        @type parent: C{QtCore.QModelIndex}
        @param start: The start index where rows where inserted.
        @type start: C{int}
        @param end: The end index where rows where inserted.
        @type end: C{int}
        """

        header = self.horizontalHeader()
        if header.sortIndicatorSection() == 1:
            if header.sortIndicatorOrder() == QtCore.Qt.AscendingOrder:
                self.scrollToBottom()
            else:
                self.scrollToTop()
