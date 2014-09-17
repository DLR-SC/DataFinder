#
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
Implements the basic SFTP file system.
"""


import decimal
import logging
import socket

from paramiko import SSHException

from datafinder.persistence.error import PersistenceError

from datafinder.persistence.adapters.sftp import constants, utils
from datafinder.persistence.adapters.sftp.configuration import Configuration
from datafinder.persistence.adapters.sftp.connection_pool import SftpConnectionPool
from datafinder.persistence.adapters.sftp.data.adapter import SftpDataAdapter
from datafinder.persistence.common.base_factory import BaseFileSystem
from datafinder.persistence.common.connection.manager import ConnectionPoolManager


__version__ = "$Revision-Id:$" 


class FileSystem(BaseFileSystem):
    """ Implements factory of the SFTP file system. """
    
    _connectionManager = ConnectionPoolManager(constants.MAX_POOL_NUMBER)
    
    def __init__(self, baseConfiguration):
        """ 
        @param baseConfiguration: Configuration parameters.
        @type baseConfiguration: L{BaseConfiguration<datafinder.persistence.common.BaseConfiguration>}
        """
        
        BaseFileSystem.__init__(self)
        self._configuration = Configuration(baseConfiguration)
        self._connectionPool = self._getConnectionPool()
        self._idMapper = utils.ItemIdentifierMapper(self._configuration.basePath)
        
    def _getConnectionPool(self):
        connectionPool = self._connectionManager.get(self._configuration.baseUri)
        if connectionPool is None:
            connectionPool = SftpConnectionPool(self._configuration)
            self._connectionManager.add(self._configuration.baseUri, connectionPool)
        return connectionPool
    
    def createDataStorer(self, identifier):
        """ 
        Creates a SFTP specific data storer instance.
        
        @param identifier: Logical identifier of a file system item.
        @type identifier: C{unicode}
        
        @return: TSM specific data storer instance.
        @rtype: L{SftpDataAdapter<datafinder.persistence.adapters.sftp.adapter.SftpDataAdapter>}
        """
        
        persistenceId = self._idMapper.determinePeristenceId(identifier)
        return SftpDataAdapter(
            identifier, persistenceId, self._connectionPool, self, self._idMapper)
    
    def release(self):
        """ 
        @see: L{FileSystem.release<datafinder.persistence.factory.FileSystem.release>}
        Cleans up the connection pool
        """
        
        self._connectionManager.remove(self._configuration.baseUri)

    def updateCredentials(self, credentials):
        """ 
        @see: L{FileSystem.updateCredentials<datafinder.persistence.factory.FileSystem.updateCredentials>} 
        Change the credentials and initializes the the connection pool again.
        """
        
        self._configuration.username = credentials["username"]
        self._configuration.password = credentials["password"]
        self._connectionPool.reload()

    def determineFreeDiskSpace(self):
        """
        @see: L{FileSystem.determineFreeDiskSpace<datafinder.persistence.factory.FileSystem.determineFreeDiskSpace>}
        """
        
        connection = self._connectionPool.acquire()
        try:
            transport = connection.get_channel().get_transport()
            diskFreeCommand = "df %s" % self._configuration.basePath
            print diskFreeCommand
            commandRunner = _SshCommandRunner(diskFreeCommand, transport)
            diskFreeCommandOutput, _ = commandRunner.executeCommand()
            return _parseDiskFreeCommandOutForAvailableSpace(diskFreeCommandOutput)
        finally:
            self._connectionPool.release(connection)

            
def _parseDiskFreeCommandOutForAvailableSpace(diskFreeCommandOutput):
    """ This helper function parses the output of the df command to determine the available
    free space of the first device listed. This functions is a first attempt in this direction and is intended
    to work fine with the result of 'df <PATH>'. 
    Consider introducing a separate helper class when introducing different/alternative parsing strategy. """
    
    for line in diskFreeCommandOutput.split("\n"):
        line = line.strip()
        if line and not line.startswith("Filesystem"): # Ignoring header
            token = line.split()
            if len(token) > 3:
                try:
                    return decimal.Decimal(token[3])
                except decimal.InvalidOperation:
                    raise PersistenceError("Unable to parse df command output '%s' for avaialble disk space." % diskFreeCommandOutput)
    # Handle all non-conformant df command outputs
    raise PersistenceError("Unable to parse df command output '%s' for avaialble disk space." % diskFreeCommandOutput)


class _SshCommandRunner(object):
    """ Helper class which executes a specific SSH command on the basis of an 
    authenticated transport channel. It creates a new channel and properly closes it.
    This class might be reused in the TSM adapter.
    """
    
    _log = logging.getLogger()
    
    def __init__(self, command, transport, timeout=500.0, maxReceivedBytes=1024):
        """
        @param command: String representing the command that should be executed.
        @type command: C{str}
        @param transport: An authenticated paramiko transport channel.
        @type transport: C{paramiko.Transport}
        """
        
        self._command = command
        self._transport = transport
        self._timeout = timeout
        self._maxReceivedBytes = maxReceivedBytes
        
    def executeCommand(self):
        """ 
        Executes the given command on the connected host and returns corresponding
        standard output and standard error output.

        @raise PersistenceError: Indicating problem executing the specific command.
        """
        
        channel = self._transport.open_session()
        channel.settimeout(self._timeout)
        try:
            channel.exec_command(self._command)
        except SSHException, sshException:
            errorMessage = "Cannot send command '%s' to host.\nReason: '%s'" % (self._command, str(sshException)) 
            raise PersistenceError(errorMessage)
        else:
            standardOutput =  self._getCommandOutput(channel.recv)
            standardError = self._getCommandOutput(channel.recv_stderr)
            if standardError:
                self._log.debug(standardError)
            return standardOutput, standardError
        finally:
            channel.close()

    def _getCommandOutput(self, outputFunction):
        output = ""
        try:
            outputContentPart = outputFunction(self._maxReceivedBytes)
            while len(outputContentPart) > 0:
                output = output + outputContentPart
                outputContentPart = outputFunction(self._maxReceivedBytes)
        except socket.timeout:
            raise PersistenceError("Receiving out put from '%s' command timed out." % self._command)
        else:
            return output
