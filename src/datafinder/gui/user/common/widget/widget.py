# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#
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
This module contains all custom widgets for the datafinder guis.
"""


import functools

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt


__version__ = "$Revision-Id:$" 


class _Tab(object):
    """
    Tab class to store tab informations.
    Only used in the L{datafinder.gui.user.ouput.decorator.TabWidgetDecorator}.
    """

    def __init__(self, tabText, tabToolTip, tabWhatsThis, tabIcon, widget, shown = True):
        """
        Constructor.

        @param tabText: Text of the tab.
        @type tabText: C{string}
        @param tabToolTip: ToolTip of the tab.
        @type tabToolTip: C{string}
        @param tabWhatsThis: Whats this text of the tab.
        @type tabWhatsThis: C{string}
        @param tabIcon: Icon of the tab.
        @type tabIcon: C{QtGui.QIcon}
        @param widget: Widget of the tab.
        @type widget: C{QtGui.QWidget}
        @param shown: True = The tab is visible, False = the tab is removed.
        @type shown: C{bool}
        """

        self.text = tabText
        self.toolTip = tabToolTip
        self.whatsThis = tabWhatsThis
        self.icon = tabIcon
        self.widget = widget
        self.shown = shown


class HideableTabWidget(QtGui.QTabWidget):
    """
    Decorator for the QTabWidget class to change the visibility of tab items.
    """

    def __init__(self, parent=None):
        """
        Constructor.

        @param tabWidget: TabWidget that you want to decorate.
        @type tabWidget: C{QtGui.QTabWidget}

        @param parent: Parent of this L{QtCore.QObject}.
        @type parent: C{QtCore.QObject}
        """

        QtGui.QTabWidget.__init__(self, parent)

        self.__tabs = list()
        
        self.tabBar().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        QtCore.QObject.connect(self.tabBar(),
                               QtCore.SIGNAL("customContextMenuRequested(QPoint)"),
                               self.showTabBarContextMenuSlot)

    def fetchTabs(self, index=0):
        """
        Fetch all tab informations and stores them in an internal list.
        Necessary cause it is not possible to hide tabs without loss of tab informations.
        Has to be called after setting up new tabs that have to get the hiding ability.
        
        @param index: The index at which the tab was inserted.
        @type index: C{int}
        """
        
        count = self.count()
        self.__tabs = self.__tabs[:index]
        for i in range(index, count):
            tab = _Tab(self.tabText(i), self.tabToolTip(i), self.tabWhatsThis(i), self.tabIcon(i), self.widget(i))
            self.__tabs.append(tab)

    def setTabShown(self, tab, shown):
        """
        Show or hide a widget at the given index.

        @param index: Index of the tab.
        @type index: C{int}

        @param shown: True = show, False = hide.
        @type shown: C{bool}
        """

        index = tab
        #Index correction.
        for i in range(tab):
            if not self.__tabs[i].shown:
                index -= 1

        #Set the tab visible.
        if shown is True:
            self.insertTab(index,
                           self.__tabs[tab].widget,
                           self.__tabs[tab].icon,
                           self.__tabs[tab].text)
            self.setTabToolTip(index, self.__tabs[tab].toolTip)
            self.setTabWhatsThis(index, self.__tabs[tab].whatsThis)
            self.setCurrentIndex(index)
        #Hide the tab.
        else:
            self.removeTab(index)
        #Set the tab visibility status.
        self.__tabs[tab].shown = shown

        #Hide the tabwidget if there is no tab anymore.
        shown = self.count() > 0
        #Sending signal on visibility change.
        if self.isHidden() == shown:
            self.emit(QtCore.SIGNAL("shownChangedSignal(bool)"), shown)
        self.setShown(shown)
        
    def showTabBarContextMenuSlot(self):
        """
        Slot is called when a context menu request was emitted.
        """
        
        menu = QtGui.QMenu(self)
        for i, tab in enumerate(self.__tabs):
            action = menu.addAction(tab.icon, tab.text)
            action.setCheckable(True)
            action.setChecked(tab.shown)
            self.connect(action, QtCore.SIGNAL("triggered(bool)"), 
                         functools.partial(self.setTabShown, i))
        menu.exec_(QtGui.QCursor.pos())


class DefaultTreeView(QtGui.QTreeView):
    """
    Customized the given L{QtGui.QTreeView}.
    """
    
    def __init__(self, parent=None):
        """
        Constructor.
        
        @param widget: The tree view that has to be customized.
        @type widget: C{QtGui.QWidget}
        """
        
        QtGui.QTreeView.__init__(self, parent)
        
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.setEditTriggers(QtGui.QAbstractItemView.SelectedClicked |
                             QtGui.QAbstractItemView.EditKeyPressed)
        self.header().hide()
        self.header().setSortIndicator(0, QtCore.Qt.AscendingOrder)
        self.setSortingEnabled(True)
        
        self.connect(self, QtCore.SIGNAL("expanded(QModelIndex)"), self._resizeColumnsSlot)
        self.connect(self, QtCore.SIGNAL("collapsed(QModelIndex)"), self._resizeColumnsSlot)
        
    def _resizeColumnsSlot(self, index):
        """
        Resize the given columns on expand or collapse.

        @param index: Index with the column which have to be resized.
        @type index: C{QtCore.QModelIndex}
        """

        if index.isValid():
            self.resizeColumnToContents(index.column())
    

class DefaultTableView(QtGui.QTableView):
    """
    Customized the given L{QtGui.QTableView}.
    """
    
    def __init__(self, parent=None):
        """
        Constructor.
        
        @param widget: The table view that has to be customized.
        @type widget: C{QtGui.QTableView}
        """
        
        QtGui.QTableView.__init__(self, parent)
        
        self.__gridStyles = [(self.tr('Solid'), QtCore.Qt.SolidLine),
                             (self.tr('Dashed'), QtCore.Qt.DashLine),
                             (self.tr('Dotted'), QtCore.Qt.DotLine),
                             (self.tr('Dashed Dotted'), QtCore.Qt.DashDotLine)]           
        
        
        self.verticalHeader().hide()
        self.verticalHeader().setDefaultSectionSize(22)
        
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().setClickable(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.horizontalHeader().setMovable(True)
        self.horizontalHeader().setHighlightSections(False)
        
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setGridStyle(QtCore.Qt.DotLine)
        
        self.connect(self.horizontalHeader(),
                     QtCore.SIGNAL("customContextMenuRequested(QPoint)"),
                     self.showHeaderMenu)
        
    def keyPressEvent(self, keyEvent):
        """ Signals that the return key is pressed and provides the specific the current model index. """
        
        if keyEvent.key() == Qt.Key_Return:
            self.emit(QtCore.SIGNAL("returnPressed"), self.selectionModel().currentIndex())
        QtGui.QTableView.keyPressEvent(self, keyEvent)
        
    def showHeaderMenu(self, _):
        """
        Shows the header content menu at the current cursor position.
        """

        #Generates the menu for changing the visibility of the headers.
        menu = QtGui.QMenu(self)
        lastCheckedAction = None
        numberOfCheckActions = 0
        for section in range(self.model().columnCount(QtCore.QModelIndex())):
            text = self.model().headerData(section, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole).toString()
            action = menu.addAction(text)
            action.setCheckable(True)
            if self.isColumnHidden(section):
                action.setChecked(False)
                action.connect(action, QtCore.SIGNAL("triggered(bool)"), 
                               functools.partial(self.showColumn, section))
            else:
                action.setChecked(True)
                action.connect(action, QtCore.SIGNAL("triggered(bool)"), 
                               functools.partial(self.hideColumn, section))
                lastCheckedAction = action
                numberOfCheckActions += 1
            action.setEnabled(True)
        if not lastCheckedAction is None and numberOfCheckActions == 1:
            lastCheckedAction.setEnabled(False) 
        
        #Generates the menu for the grid style.
        gridMenu = QtGui.QMenu(self.tr('Grid'), menu)
        styleGroup = QtGui.QActionGroup(menu)
        for name, style in self.__gridStyles:
            action = gridMenu.addAction(name)
            action.setCheckable(True)
            action.setChecked(style == self.gridStyle())
            action.setEnabled(self.showGrid())
            styleGroup.addAction(action)
            self.connect(action, QtCore.SIGNAL("triggered(bool)"), 
                         functools.partial(self.setGridStyle, style))
        gridMenu.addSeparator()
        action = gridMenu.addAction(self.tr('Show'))
        action.setCheckable(True)
        action.setChecked(self.showGrid())
        self.connect(action, QtCore.SIGNAL("triggered(bool)"), self.setShowGrid)
        
        menu.addSeparator()
        menu.addMenu(gridMenu)
        
        menu.exec_(QtGui.QCursor.pos())
        

class DefaultListView(QtGui.QListView):
    """
    Customize the given L{QtGui.QListView}.
    """
    
    def __init__(self, parent=None):
        """
        Constructor.
        
        @param widget: The widget that has to be wrapped by this class.
        @type widget: C{QtGui.QWidget}
        """
        
        QtGui.QListView.__init__(self, parent)
        
        self.__verticalOffset = 0
    
    def keyPressEvent(self, keyEvent):
        """ Signals that the return key is pressed and provides the specific the current model index. """
        
        if keyEvent.key() == Qt.Key_Return:
            self.emit(QtCore.SIGNAL("returnPressed"), self.selectionModel().currentIndex())
        QtGui.QListView.keyPressEvent(self, keyEvent)
    
    def setViewMode(self, mode):
        """
        @see: QtGui.QListView#setViewMode
        """
        
        size = QtCore.QSize(-1, -1)
        self.__verticalOffset = 0
        if mode == QtGui.QListView.IconMode:
            size = QtCore.QSize(115, 80)
            self.__verticalOffset = -10
        self.setGridSize(size)
        QtGui.QListView.setViewMode(self, mode)
    
    def visualRect(self, index):
        """
        @see: QtCore.QAbstractItemView#visualRect
        """
        
        rect = self.rectForIndex(index)
        
        dx = -1 * self.horizontalOffset()
        dy = -1 * self.verticalOffset() - self.__verticalOffset
        rect.adjust(dx, dy, dx, dy)
        return rect


class ActionTooltipMenu(QtGui.QMenu):
    """ Implements a menu which shows the tool tip of the active action. """
    
    def __init__(self, parent=None):
        """ Constructor. """
        
        QtGui.QMenu.__init__(self, parent)
        
    def event(self, event):
        """ 
        @see: L{event<PyQt4.QtGui.QWidget.event>}
        Used displaying token dependent tool tips.
        """
        
        if event.type() == QtCore.QEvent.ToolTip:
            if not self.activeAction() is None:
                QtGui.QToolTip.showText(event.globalPos(), self.activeAction().toolTip())
            else:
                QtGui.QToolTip.hideText()
        return QtGui.QMenu.event(self, event)
