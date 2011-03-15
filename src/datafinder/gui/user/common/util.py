# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#
#met:
#
#
# * Redistributions of source code must retain the above copyright 
#   notice, this list of conditions and the following disclaimer. 
#
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
This module contains utility classes for the datafinder.
"""


from datetime import datetime
from decimal import Decimal
import functools
import logging
import sys
import types

from PyQt4 import QtCore

from datafinder.core.configuration.properties.constants import SIZE_ID, CONTENT_SIZE_ID


__version__ = "$Revision-Id:$" 


class _PyQtThread(QtCore.QThread):
    """
    Helper class for creating a L{QtCore.QThread} object that acts like a python thread.
    """
    
    def __init__(self, function, callbacks, *args, **kwargs):
        """
        Constructor.
        
        @param function: Function that has to be called in a separate thread.
        @type function: C{function}
        @param callbacks: The functions that have to be called after the thread termination.
        @type callbacks: C{list} of C{function}
        @param *args: Additional parameters for the function.
        @type *args: C{list}
        @param **kwargs: Additional parameters for the function.
        @type **kwargs: C{dict}
        """
        
        QtCore.QThread.__init__(self, None)
        
        self.result = None
        self.error = None
        
        self.__function = function
        
        self.__args = args[:]
        self.__kwargs = kwargs.copy()
        
        for callback in callbacks:
            if not callback is None:
                self.connect(self, QtCore.SIGNAL("finished()"), callback)
        
    def run(self):
        """
        @see: L{run<PyQt4.QtCore.QThread.run>}
        """
        # pylint: disable=E1101, W0703
        # E1101: "pythoncom" has a "CoInitialize" member but Pylint cannot detect it.
        # W0703: Here it is fine to catch Exception as this is a generic thread implementation
        # and the error is later available to the client code.

        if sys.platform == "win32":
            import pythoncom
            pythoncom.CoInitialize()
        try:
            try:
                self.result = self.__function(*self.__args, **self.__kwargs)
            except Exception, error:
                self.error = error
        finally:
            if sys.platform == "win32":
                pythoncom.CoInitialize()
        
    def __del__(self):
        """ Cleans up the thread. """

        self.deleteLater()
            

def startNewQtThread(function, callback, *args, **kwargs):
    """
    Starts a new qt thread instance with the given function.
    After the thread is finished the callback will be called.
    Result/error can be retrieved from the thread instance using
    the attributes C{result} / C{error}.
    
    @param function: The function that has to be executed in a separated thread.
    @type function: C{function}
    @param callback: The function that has to be called after thread has finished.
    @type callback: C{function}
    @param *args: Additional parameters for the function.
    @type *args: C{list}
    @param **kwargs: Additional parameters for the function.
    @type **kwargs: C{dict}
    
    @return: Returns the L{QtCore.QThread} instance that is working.
    @rtype: C{QtCore.QThread}
    """
    
    if not hasattr(callback, "__iter__"):
        callback = [callback]
    qtThread = _PyQtThread(function, callback, *args, **kwargs)
    qtThread.start()
    return qtThread


class StartInQtThread(object):
    """
    Decorator class to ease threading.
    """
    
    _workers = list()
    
    def __init__(self, callback=None):
        """
        @param callback: callback function to call after the decorated function is finished
        """
        
        self.callback = callback
    
    def __call__(self, function):
        """
        Calls function in a new Qt thread.
        """
        
        def startInNewQtThread(*args, **kwargs):
            StartInQtThread._workers.append(startNewQtThread(function, self._callback, *args, **kwargs))
        return startInNewQtThread
      
    def _callback(self):
        """ Default callback. """
        
        if not self.callback is None:
            self.callback()
        self._cleanup()
        
    @staticmethod
    def _cleanup():
        """
        Cleans up the internal static worker list and removes all finished threads.
        This internal list is needed to prevent threads from being garbage-collected.
        """
        
        activeWorker = list()
        for worker in StartInQtThread._workers:
            if not worker.isFinished():
                activeWorker.append(worker)
            else:
                del worker
        StartInQtThread._workers = activeWorker


class BisectColumnHelper(object):
    """
    Helper class that allow to insert items with the bisect module.
    """
    
    def __init__(self, list_, column=0):
        """
        Constructor.
        
        @param list_: The list that has to be wrapped by this helper class.
        @type list_: C{list} of C{list} objects.
        
        @param column: The index of the L{list} objects in the given list_, 
                       that has to be returned by the __getitem__ method.
        @type column: C{int}
        """
        
        self.__list = list_
        self.column = column
        
    def __getitem__(self, index):
        """
        Returns the item of the internal 2 dimensional array at the postion index, column.
        A unicode object will transformed to lower characters.
        
        @param index: The index of the item that has to be returned.
        @type index: C{int}
        """
        
        item = self.__list[index][self.column]
        if isinstance(item, unicode):
            item = item.lower()
        return item
    
    def __len__(self):
        """
        Returns the length of the internal list object.
        
        @return: The length of the internal list.
        @rtype: C{int}
        """
        
        return len(self.__list)


_immediateConnectionType = "immediate"
_deferredConnectionType = "deferred"


def immediateConnectionDecorator(sender, signalSignature):
    """
    Tags the function/method with specific connection information. 
    The connection is directly established on scanning time.
    The sender references are determined as attributes of given
    sender containers. For that reason the attribute hierarchy of a 
    sender is relative to a potential sender container.

    @param sender: Relative attribute hierarchy of the sender/senders.
                   E.g. "myModel.myParent" / ["myModel.myParent", "myModel.myParent"].
    @type sender: C{string} or C{list}
    @param signalSignature: The Qt signal signature.
    @type signalSignature: C{string}
    
    @return: The decorator function.
    @rtype: callable.
    """
    
    def wrapper(function):
        if not isinstance(function, types.FunctionType): #required for non-Python methods/functions
            function = functools.partial(function)
        function.sender = sender
        function.signalSignature = signalSignature
        function.connectionType = _immediateConnectionType
        return function
    return wrapper


def deferredConnectionDecorator(sender, signalSignature):
    """
    Tags the function/method with specific connection information. 
    The connection is not directly established on scanning time. This type
    of connection is established when calling C{QtConnectionDelegate.establishDeferredConnections}
    and the connections are removed when calling C{QtConnectionDelegate.removeDeferredConnections}.
    The sender references are determined as attributes of given
    sender containers. For that reason the attribute hierarchy of a 
    sender is relative to a potential sender container.

    @param sender: Relative attribute hierarchy of the sender/senders.
                   E.g. "myModel.myParent" / ["myModel.myParent", "myModel.myParent"].
    @type sender: C{string} or C{list}
    @param signalSignature: The Qt signal signature.
    @type signalSignature: C{string}
    
    @return: The decorator function.
    @rtype: callable.
    """
    
    def wrapper(function):
        if not isinstance(function, types.FunctionType): #required for non-Python methods/functions
            function = functools.partial(function)
        function.sender = sender
        function.signalSignature = signalSignature
        function.connectionType = _deferredConnectionType
        return function
    return wrapper


class QtConnectionDelegate(object):
    """
    This class can automatically connects a Qt sender objects (subclasses of C{QObect})
    with a given Qt signal signature and a function/method which handles the signal (slot).
    In order to determine the connections which have to be established use the C{scan} method.
    This method checks all methods of the given object for tagged slot methods. For tagging
    slot methods the decorator function C{immediateConnectionDecorator} and C{deferredConnectionDecorator}
    are currently provided.
    """
    
    def __init__(self, logger=None, deferredConnectionHook=None):
        """ 
        Constructor. 
        
        @param logger: An optional logger reference which is used for debug output.
        @type logger: C{logging.Logger}
        @param deferredConnectionHook: Function object which performs certain action on 
                                       the specific sender object. Function gets the sender
                                       reference and a flag whether the sender is currently
                                       connected or not.
        @type deferredConnectionHook: Callable.
        """

        self.__senderContainers = list()
        self.__immediateConnections = list()
        self.__deferredConnections = list()
        self.__unresolvedConnections = list()
        self.__logger = logger
        if self.__logger is None:
            self.__logger = logging.getLogger()
        self.__deferredConnectionHook = deferredConnectionHook
    
    def scan(self, obj, senderContainers):
        """
        Scans the given object for tagged slot methods. The senders are searched 
        in the attribute hierarchy of the given sender containers.
        
        @param obj: Object which is scanned for tagged slot methods.
        @type obj: C{object}
        @param senderContainers: List of containers which contain potential sender objects.
        @type senderContainers: C{list} of C{object} 
        """

        self.__senderContainers = senderContainers
        self.__clearConnections()
        for methodName in dir(obj):
            try:
                method = getattr(obj, methodName)
            except AttributeError:
                continue
            try:
                connectionType = method.connectionType
                qtSignal = QtCore.SIGNAL(method.signalSignature)
                senderNames = method.sender
                if isinstance(senderNames, types.StringType):
                    senderNames = [senderNames]
                for senderName in senderNames:
                    sender = self.__determineSender(connectionType, senderName, qtSignal, method)
                    if sender is None:
                        self.__logger.debug("Sender '%s' was not found." % method.sender)
                    else:
                        if connectionType == _immediateConnectionType:
                            self.__establishConnection(sender, qtSignal, method)
                            self.__immediateConnections.append((sender, qtSignal, method))
                        else:
                            self.__deferredConnections.append((sender, qtSignal, method))
                            self.__logger.debug("Successfully parsed connection '%s %s %s %s %s'." \
                                                % (connectionType, method.sender, method.signalSignature, methodName, sender))
            except AttributeError:
                continue

    def __clearConnections(self):
        """ Disconnects all established connections and resets the internal state. """

        for sender, qtSignal, slotMethod in self.__immediateConnections + self.__deferredConnections:
            self.__removeConnection(sender, qtSignal, slotMethod)
        self.__immediateConnections = list()
        self.__deferredConnections = list()
        self.__unresolvedConnections = list()

    def __determineSender(self, connectionType, senderName, qtSignal, slotMethod):
        """ 
        Determines the sender reference. If a reference cannot be determined the
        the connection information will be added to C{self.__missingConnections}.
        """
        
        sender = None
        attributeNames = senderName.split(".")
        senderContainers = self.__senderContainers
        
        for attributeName in attributeNames:
            found = False
            for senderContainer in senderContainers:
                if hasattr(senderContainer, attributeName):
                    sender = getattr(senderContainer, attributeName)
                    if sender is None:
                        if not (connectionType, senderName, qtSignal, slotMethod) in self.__unresolvedConnections:
                            self.__unresolvedConnections.append((connectionType, senderName, qtSignal, slotMethod))
                            self.__logger.debug("Adding '%s %s %s %s' to unresolved connections." \
                                                % (connectionType, senderName, qtSignal, slotMethod))
                    found = True
                    break
            if found:
                senderContainers = [sender]
            else:
                break
        return sender

    @staticmethod
    def __establishConnection(sender, qtSignal, slotMethod):
        """ Establishes a connection with the given parameters. """
        
        try:
            success = QtCore.QObject.connect(sender, qtSignal, slotMethod)
        except TypeError:
            success = False
        return success
    
    @staticmethod
    def __removeConnection(sender, qtSignal, slotMethod):
        """ Removes a connection with the given parameters. """
        
        try:
            success = QtCore.QObject.disconnect(sender, qtSignal, slotMethod)
        except TypeError:
            success = False
        return success

    def establishUnresolvedConnections(self):
        """
        Connections whose sender reference was not found on scanning time 
        are tried to be determined again. If the sender is found at this
        time the connection is established in accordance to its connection type. 
        """
        
        self.__logger.debug("Try to connect unresolved connections.")
        establishedMissingConnections = list()
        for connectionType, senderName, qtSignal, slotMethod in self.__unresolvedConnections:
            sender = self.__determineSender(connectionType, senderName, qtSignal, slotMethod)
            if not sender is None:
                establishedMissingConnections.append((connectionType, senderName, qtSignal, slotMethod))
                self.__logger.debug("Resolved sender '%s'." % senderName)
                if connectionType == _immediateConnectionType:
                    self.__establishConnection(sender, qtSignal, slotMethod)
                    self.__immediateConnections.append([sender, qtSignal, slotMethod])
                else:
                    self.__deferredConnections.append([sender, qtSignal, slotMethod])
            else:
                self.__logger.debug("Unable to resolve '%s'." % senderName)
        
        for establishedMissingConnection in establishedMissingConnections:
            self.__unresolvedConnections.remove(establishedMissingConnection)

    def establishDeferredConnections(self):
        """ Establishes all deferred connections. """
        
        for sender, qtSignal, slotMethod in self.__deferredConnections:
            success = self.__establishConnection(sender, qtSignal, slotMethod)
            if not self.__deferredConnectionHook is None:
                self.__deferredConnectionHook(sender, success)
    
    def removeDeferredConnections(self):
        """ Removes/Disconnects all deferred connections. """
        
        for sender, qtSignal, slotMethod in self.__deferredConnections:
            success = self.__removeConnection(sender, qtSignal, slotMethod)
            if not self.__deferredConnectionHook is None:
                self.__deferredConnectionHook(sender, not success)
                

def extractPyObject(qVariant):
    """
    Extracts the included python object from a QVariant
    @param qVariant: object to extract python object from
    @type qVariant: L{PyQt4.QtCore.QVariant}
    @return: the included python object
    """

    try:
        objectType = qVariant.type()
    except AttributeError:
        return convertToPlainPythonObject(qVariant)
    
    if objectType == QtCore.QVariant.Double:
        casted = Decimal(str(qVariant.toDouble()[0])) # toDouble return a tuple (double,boolean)
    elif objectType == QtCore.QVariant.String:
        casted = qVariant.toString()
        casted = unicode(casted)
    elif objectType == QtCore.QVariant.Bool:
        casted = qVariant.toBool()
    elif objectType == QtCore.QVariant.DateTime:
        casted = qVariant.toDateTime()
        dt = casted.toPyDateTime()
        casted = datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)
    elif objectType == QtCore.QVariant.List:
        casted = qVariant.toList()
        casted = [extractPyObject(x) for x in casted]
    elif objectType == QtCore.QVariant.LongLong:
        casted = Decimal(str(qVariant.toLongLong()[0])) # same as toDouble
    elif objectType == QtCore.QVariant.UserType:
        casted = qVariant.toPyObject()
    elif objectType == QtCore.QVariant.Int:
        casted = Decimal(str(qVariant.toInt()[0]))
    elif objectType == QtCore.QVariant.Date:
        casted = qVariant.toDate()
    elif qVariant.isNull():
        casted = None
    else:
        raise TypeError("Unknown type. Unable to convert type: %s" % qVariant.typeName())
    
    return convertToPlainPythonObject(casted)

_mappingDict = {
                QtCore.QString: lambda x: unicode(x),
                QtCore.QDateTime: lambda x: x.toPyDateTime(),
                QtCore.QDate: lambda x: x.toPyDate()
               }

def convertToPlainPythonObject(qDataType):
    """
    Converts a Qt object to a python object
    """
    
    try:
        returnValue = _mappingDict[type(qDataType)](qDataType)
    except KeyError:
        returnValue = qDataType
     
    return returnValue


def determineDisplayRepresentation(value, propertyIdentifier=None):
    """ 
    Returns the display representation for the given Python value. 
    
    @param value: Value that should be displayed.
    @type value: C{object}
    @param propertyIdentifier: Optional property identifier. Default: C{None}
    @type propertyIdentifier: C{unicode}
    
    @return: Representation of the value as human readable string.
    @rtype: C{unicode}
    """

    if isinstance(value, bool):
        displayRepresentation = "False"
        if value:
            displayRepresentation = "True"
    elif isinstance(value, datetime):
        displayRepresentation = value.strftime("%d.%m.%Y %H:%M:%S")
    elif isinstance(value, Decimal):
        decimalAsTuple = value.as_tuple()
        if propertyIdentifier in (SIZE_ID, CONTENT_SIZE_ID):
            displayRepresentation = str(long(value / 1024)) + " KB"
        elif decimalAsTuple[2] >= 0:
            displayRepresentation = str(long(value))
        else:
            displayRepresentation = str(float(value))
    elif isinstance(value, list):
        displayRepresentation = u"["
        for item in value:
            displayRepresentation += determineDisplayRepresentation(item) + ", "
        if len(displayRepresentation) >= 2:
            displayRepresentation = displayRepresentation[:-2] + "]"
        else:
            displayRepresentation = displayRepresentation + "]"
    elif value is None:
        displayRepresentation = u""
    else:
        displayRepresentation = unicode(value)
    return displayRepresentation


def determinePropertyDefinitionToolTip(propertyDefinition):
    """ 
    Determines a tool tip text for the given property definition. 
    
    @param propertyDefinition: Definition instance holding specific property parameter.
    @type propertyDefinition: L{PropertyDefinition<datafinder.core.configuration.properties.property_definition.PropertyDefinition>}
    
    @return: Tool tip text describing the property.
    @rtype: C{unicode}
    """
    
    description = propertyDefinition.description
    toolTip = propertyDefinition.displayName
    type_ = propertyDefinition.type
    if not type_ is None:
        toolTip += ": " + type_
    if not description is None:
        toolTip += "\n" + description
    return toolTip
