# pylint: disable-msg=R0201
# R0201 is disabled in order to correctly implement the interface.
#
# Created: Tobias Schlauch (mail to Tobias.Schlauch@dlr.de)
#
# Version: $Id: adapter.py 4628 2010-04-21 07:29:27Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder
#


"""
The class TSMConnectorDataStore represents a datastore where the data is 
stored in a Tivoli Storage Manager archive.              
"""


import logging
import socket
import tempfile

from paramiko import SSHException, SFTPClient

from datafinder.persistence.adapters.tsm.constants import CONNECTION_TIMEOUT, MAXIMUM_RECEIVED_BYTES
from datafinder.persistence.data.datastorer import NullDataStorer 
from datafinder.persistence.error import PersistenceError


__version__ = "$LastChangedRevision: 4628 $"


_BLOCK_SIZE = 30000

_TIMEOUT_ERROR_MESSAGE = "A timeout occurred during the execution of command '%s'!"
_COMMAND_STDERR_MESSAGE_START = "Problems executing command"

_ARCHIVE_COMMANDLINE_TOOL = u"dsmc"
_ARCHIVE_RESOURCE_COMMAND = _ARCHIVE_COMMANDLINE_TOOL + " archive %s -v2archive -deletefiles -se=%s"
_QUERY_RESOURE_COMMAND = _ARCHIVE_COMMANDLINE_TOOL + " query archive %s -se=%s"
_RETRIEVE_RESOURCE_COMMAND = _ARCHIVE_COMMANDLINE_TOOL + " retrieve %s -replace=yes -se=%s"
_DELETE_ARCHIVE_COMMAND = _ARCHIVE_COMMANDLINE_TOOL + " delete archive %s -noprompt -se=%s"

_UNKNOWN_TSM_NODE_ERROR_CODE = "ANS1217E"
_INVALID_OPTION_ERROR_CODE = "ANS1107E"
_NON_MATCHING_FILESEARCH_ERROR_CODE = "ANS1092W"


_log = logging.getLogger()


class DataTsmAdapter(NullDataStorer):
    """ Stores data in a TSM archive. """

    def __init__(self, identifier, persistenceIdentifier, serverNodeName, connectionPool):
        """
        @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}
        """
        
        NullDataStorer.__init__(self, identifier)
        
        self._persistenceIdentifier = persistenceIdentifier
        self._serverNodeName = serverNodeName
        self._connectionPool = connectionPool
        
    @property
    def isLeaf(self):
        """
        @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}
        """
        
        return True

    def createCollection(self, recursively):
        """
        @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}
        """
        
        raise PersistenceError("Not implemented.")

    def createLink(self, destination):
        """
        @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}
        """
        
        raise PersistenceError("Not implemented.")

    def getChildren(self):
        """
        @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}
        """
        
        raise PersistenceError("Not implemented.")

    def exists(self):
        """
        @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}
        """
        
        connection = self._connectionPool.acquire()
        try:
            exists = True
            command = _QUERY_RESOURE_COMMAND % (self._persistenceIdentifier, self._serverNodeName)
            try:
                self._sendCommand(command, connection)
            except PersistenceError, error:
                if _NON_MATCHING_FILESEARCH_ERROR_CODE in error.message:
                    if self.identifier != "/":
                        exists = False
                else:
                    raise error
            return exists
        finally:
            self._connectionPool.release(connection)
        
    def delete(self):
        """
        @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}
        """
        
        if not self.exists():
            errorMessage = u"The requested archive '%s' does not exist on the TSM server!" % self._persistenceIdentifier
            raise PersistenceError(errorMessage)
        connection = self._connectionPool.acquire()
        try:
            command = _DELETE_ARCHIVE_COMMAND % (self._persistenceIdentifier, self._serverNodeName)
            self._sendCommand(command, connection)
        finally:
            self._connectionPool.release(connection)

    def copy(self, destination):
        """
        @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}
        """
        
        fileObject = self.readData()
        destination.writeData(fileObject)

    @staticmethod
    def move(destination):
        """
        @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}
        """
        
        raise PersistenceError("Not implemented.")

    def readData(self):
        """
        @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}
        """
        
        if not self.exists():
            errorMessage = u"The requested archive '%s' does not exist on the TSM server!" % self._persistenceIdentifier
            raise PersistenceError(errorMessage)
        connection = self._connectionPool.acquire()
        try:
            command = _RETRIEVE_RESOURCE_COMMAND % (self._persistenceIdentifier, self._serverNodeName)
            self._sendCommand(command, connection)
            return self._getFile(connection)
        finally:
            self._connectionPool.release(connection)

    def _getFile(self, connection):
        """ Transfers the given file from the TSM host to the local file system. """

        try:
            temporaryFileObject = tempfile.TemporaryFile()
            sftp = SFTPClient.from_transport(connection)
            try:
                temporaryFileObject.seek(0)
                remoteFileObject = sftp.open(self._persistenceIdentifier)
                block = remoteFileObject.read(_BLOCK_SIZE)
                while len(block) > 0:
                    temporaryFileObject.write(block)
                    block = remoteFileObject.read(_BLOCK_SIZE)
                sftp.remove(self._persistenceIdentifier)
                temporaryFileObject.seek(0)
                return temporaryFileObject
            except (IOError, SSHException), error:
                errorMessage = "Cannot retrieve file from TSM host!\nReason: '%s'" % str(error)
                raise PersistenceError(errorMessage)
        finally:
            sftp.close()

    def writeData(self, data):
        """
        @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}
        """
        
        if self.exists():
            errorMessage = u"There does already exist an archive with the identifier '%s'!" % self._persistenceIdentifier
            raise PersistenceError(errorMessage)
        connection = self._connectionPool.acquire()
        try:
            self._putFile(data, connection)
            archiveCommand = _ARCHIVE_RESOURCE_COMMAND % (self._persistenceIdentifier, self._serverNodeName)
            self._sendCommand(archiveCommand, connection)
        finally:
            self._connectionPool.release(connection)
    
    def _putFile(self, data, connection):
        """ Puts the given file on the TSM host. """
        
        sftp = SFTPClient.from_transport(connection)
        try:
            try:
                remoteFileObject = sftp.open(self._persistenceIdentifier, "w")
                block = data.read(_BLOCK_SIZE)
                while len(block) > 0:
                    remoteFileObject.write(block)
                    block = data.read(_BLOCK_SIZE)
            except (IOError, SSHException), sshException:
                errorMessage = "Cannot transfer data to TSM host!\nReason: '%s'" % str(sshException)
                raise PersistenceError(errorMessage)
        finally:
            data.close()
            sftp.close()
            
    def _sendCommand(self, command, connection):
        """ 
        Helper method executing the given command on the connected host. 

        @raise PersistenceError: Indicating problem executing the specific command.
        """
        
        channel = connection.open_session()
        channel.settimeout(CONNECTION_TIMEOUT)
        try:
            channel.exec_command(command)
        except SSHException, sshException:
            errorMessage = "Cannot send command '%s' to TSM host.\nReason: '%s'" % (command, str(sshException)) 
            raise PersistenceError(errorMessage)
        else:
            standardOutput = self._getCommandOutput(channel.recv, command)
            _log.debug("standard out of command '%s' >>" % command)
            _log.debug(standardOutput)
            if _UNKNOWN_TSM_NODE_ERROR_CODE in standardOutput or _INVALID_OPTION_ERROR_CODE in standardOutput:
                raise PersistenceError(_COMMAND_STDERR_MESSAGE_START + "'%s'. Error message was:\n '%s'" % (command, standardOutput))
            standardError = self._getCommandOutput(channel.recv_stderr, command)
            _log.debug("standard error of command '%s' >>" % command)
            _log.debug(standardError)
            if len(standardError) > 0:
                raise PersistenceError(_COMMAND_STDERR_MESSAGE_START + "'%s'. Error message was:\n '%s'" % (command, standardError))

    @staticmethod
    def _getCommandOutput(outputFunction, command):
        """
        Returns required output of the executed command (standard out or standard error).
        
        @raise PersistenceError: Indicating problem time outs.
        """
        
        output = ""
        try:
            outputContentPart = outputFunction(MAXIMUM_RECEIVED_BYTES)
            while len(outputContentPart) > 0:
                output = output + outputContentPart
                outputContentPart = outputFunction(MAXIMUM_RECEIVED_BYTES)
        except socket.timeout:
            raise PersistenceError(_TIMEOUT_ERROR_MESSAGE % command)
        else:
            return output
