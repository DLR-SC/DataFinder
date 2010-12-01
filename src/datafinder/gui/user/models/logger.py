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
Implements the model for logging messages.
"""


import os
import sys
import time
import logging

from PyQt4 import QtCore, QtGui


__version__ = "$Revision-Id:$" 


_DATETIME_FORMAT = "%d.%m.%y %X"


class LoggingModel(QtCore.QAbstractTableModel, logging.Handler):
    """
    The LoggingModel implements a model for the DataFinder.
    It implements the L{QtCore.QAbstractTableModel} to present the logging records in a L{QtGui.QTableView}.
    With the implementation of the L{logging.Handler} class it is possible to add this model to the
    standard Python logger.
    """

    _LEVEL_NAME = "levelname"
    _NAME = "name"
    _PATH_NAME = "pathname"
    _FUNC_NAME = "funcName"
    _LINE_NO = "lineno"
    _MESSAGE = "msg"

    LEVEL_NO = "levelno"
    CREATED = "created"

    def __init__(self, name, level=logging.DEBUG, parent=None):
        """
        Constructor.

        @param name: Name of the logger that has to been associated with this model.
        @type name: C{string}
        @param level: The initial logging level of the widget.
        @type level: C{object}
        @param parent: Parent L{QtCore.QObject} of the model.
        @type parent: C{QtCore.QObject}
        """

        QtCore.QAbstractTableModel.__init__(self, parent)
        logging.Handler.__init__(self, level)

        self.__methods = [self._LEVEL_NAME, self.CREATED, self._NAME, self._PATH_NAME,
                          self._FUNC_NAME, self._LINE_NO, self._MESSAGE]
        self.__headers = [self.tr("Level"), self.tr("Created"), self.tr("Logger"),
                          self.tr("Module"), self.tr("Function"), self.tr("Line"),
                          self.tr("Message")]
        self.__recordBuffer = []

        logging.getLogger(name).addHandler(self)

    def _getHeaders(self):
        """
        Return the headers of the this model.

        @return: List of headers.
        @rtype: C{list}
        """

        return self.__headers

    def _getBuffer(self):
        """
        Return the buffer of logging records.

        @return: List of logging records.
        @rtype: C{list}
        """

        return self.__recordBuffer

    @staticmethod
    def _parseModuleName(path):
        """
        Generates the module path relative to the current PYTHONPATH.

        @param path: Path the has to be converts to the module representation.
        @type path: C{unicode}
        """
        
        for pyPath in sys.path:
            if path.lower().startswith(pyPath.lower()):
                return path[len(pyPath) + 1:-3].replace(os.sep, ".")
        return path

    def rowCount(self, _=QtCore.QModelIndex()):
        """
        @see: QtCore.QAbstractTableModel#rowCount
        """

        return len(self.__recordBuffer)

    def columnCount(self, _=QtCore.QModelIndex()):
        """
        @see: QtCore.QAbstractTableModel#columnCount
        """

        return len(self.__methods)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """
        @see: QtCore.QAbstractTableModel#data
        """

        row = index.row()
        column = index.column()
        variant = QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            attribute = getattr(self.__recordBuffer[row], self.__methods[column])
            if self.__methods[column] == self.CREATED:
                attribute = time.strftime(_DATETIME_FORMAT, time.localtime(attribute))
            elif self.__methods[column] == self._PATH_NAME:
                attribute = self._parseModuleName(attribute)
            elif self.__methods[column] == self._MESSAGE:
                attribute = unicode(attribute).strip()
            variant = QtCore.QVariant(attribute)
        elif role == QtCore.Qt.ToolTipRole:
            attribute = getattr(self.__recordBuffer[row], self._MESSAGE)
            try:
                attribute.strip()
            except AttributeError:
                attribute = unicode(attribute)
            variant = QtCore.QVariant(attribute)
        elif role == QtCore.Qt.TextAlignmentRole:
            alignment = int(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
            if self.__methods[column] == self._LINE_NO:
                alignment = int(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
            variant = QtCore.QVariant(alignment)
        elif role == QtCore.Qt.ForegroundRole:
            color = QtGui.QColor(QtCore.Qt.black)
            if self.__recordBuffer[row].levelno in (logging.CRITICAL, logging.ERROR):
                color = QtGui.QColor(QtCore.Qt.red)
            variant = QtCore.QVariant(color)
        elif role == QtCore.Qt.BackgroundColorRole:
            color = QtGui.QColor(QtCore.Qt.white)
            variant = QtCore.QVariant(color)
        return variant

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """
        @see: QtCore.QAbstractTableModel#headerData
        """

        variant = QtCore.QVariant()
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                attribute = QtCore.QVariant(self.__headers[section])
                variant = QtCore.QVariant(attribute)
            elif role == QtCore.Qt.TextAlignmentRole:
                alignment = QtCore.QVariant(int(QtCore.Qt.AlignLeft))
                if self.__methods[section] == self._LINE_NO:
                    alignment = int(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
                variant = QtCore.QVariant(alignment)
        return variant

    def flush(self):
        """
        @see: logging.Handler#flush
        """

        try:
            self.beginRemoveRows(QtCore.QModelIndex(), 0, len(self.__recordBuffer))
            self.__recordBuffer = []
            self.endRemoveRows()
        except RuntimeError:
            return

    def emit(self, record):
        """
        @see: logging.Handler#emit
        """

        try:
            self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
            self.__recordBuffer.append(record)
            self.endInsertRows()
        except RuntimeError:
            return
    
    myBuffer = property(_getBuffer)
    del _getBuffer


class LoggingSortFilterModel(QtGui.QSortFilterProxyModel):
    """
    The LoggingSortFilterModel implements filter mechanism for logging messages.
    It also implements the ability for sorting logmessages.
    """

    def __init__(self, model, parent=None):
        """
        Constructor.

        @param model: Model that has to be sorted and filtered.
        @type model: C{QtCore.QAbstractItemModel}

        @param parent: Parent object.
        @type parent: C{QtCore.QObject}
        """

        QtGui.QSortFilterProxyModel.__init__(self, parent)

        self.__showCount = 0
        self.__filters = []

        self.setSourceModel(model)

    def __getattr__(self, name):
        """
        Returns the attribute under the given name.

        @param name: Name of the attribute that has to be returned.
        @type name: C{string}

        @return: The attribute for the given name.
        @rtype: C{object}
        """

        if hasattr(self.sourceModel(), name):
            return getattr(self.sourceModel(), name)
        raise AttributeError("Unknown attribute '%s'" % name)

    def addFilter(self, level):
        """
        Adds a given level to the filter list.

        @param level: The level that has to be filtered.
        @type level: C{int}
        """

        if not (level in self.__filters):
            self.__filters.append(level)
            self.invalidate()

    def removeFilter(self, level):
        """
        Removes the given level from the filter list.

        @param level: The level that to be removed from the filter list.
        @type level: C{int}
        """

        if level in self.__filters:
            self.__filters.remove(level)
            self.invalidate()

    def isFiltered(self, level):
        """
        Returns if the given level is contained in the filter list.

        @return: True if the level is contained else False.
        @rtype: C{boolean}
        """

        return level in self.__filters

    def filterAcceptsRow(self, row, _):
        """
        @see: QtGui.QSortFilterProxyModel#filterAcceptsRow
        """

        return not(self.sourceModel().myBuffer[row].levelno in self.__filters)

    def lessThan(self, left, right):
        """
        @see: QtGui.QSortFilterProxyModel#lessThan
        """

        leftData = left.data().toString()
        rightData = right.data().toString()
        if leftData == rightData:
            leftCreated = getattr(self.sourceModel().myBuffer[left.row()], LoggingModel.CREATED)
            rightCreated = getattr(self.sourceModel().myBuffer[right.row()], LoggingModel.CREATED)
            return leftCreated < rightCreated
        return leftData < rightData

    def columnCount(self, _=QtCore.QModelIndex()):
        """
        @see: QtCore.QAbstractItemModel#columnCount
        """
        
        return self.sourceModel().columnCount(None)
