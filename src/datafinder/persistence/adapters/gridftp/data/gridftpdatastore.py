# pylint: disable=W0613, W0704, R0902, W0621, W0612, R0903
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
The class GridFTPDataStore represents a datastore where the data is 
stored on a separated GridFTP server. This datastore can only be used 
in conjunction with an installed and configured Globus / pyGlobus.
"""


from os.path import dirname
from urllib import quote

from datafinder.persistence.datastore.datastore import ExternalOnlineDataStore, \
                                                       DataStoreAccessError, \
                                                       DataStoreLoginError, \
                                                       DataStoreConnectError, \
                                                       DataStoreIOError, \
                                                       DataStoreReleaseError
from datafinder.persistence.datastore.datastore import unsupportedDatastoreList, GRIDFTP_STORE


__version__ = "$Revision-Id:$" 


# GridFTP security modes
securityModeStandard = "Standard"
securityModeSafe = "Safe"
securityModePrivate = "Private"

# GridFTP transfer modes
transferModeStream = "Stream"
transferModeExtended = "Extended"

# importing pyGlobus
try:
    from pyGlobus.ftpClient import EasyFtpClient
    from pyGlobus.ftpClient import FtpClientException
    from pyGlobus.util import GlobusException
    from pyGlobus.security import grid_proxy_init, \
                                  grid_proxy_info, \
                                  grid_proxy_destroy, \
                                  GSIException
    from pyGlobus.ftpClientAttr import OperationAttr
    from pyGlobus import ftpControl
    
    def _releaseGridProxy():
        """ Destories the current certificate. Called at DataFinder exit. """
        try:
            grid_proxy_destroy()
        except GSIException:
            pass
        
    _transferModeDictionary = {transferModeStream: ftpControl.MODE_STREAM,
                               transferModeExtended: ftpControl.MODE_EXTENDED_BLOCK}
    _securityModeDictionary = {securityModeStandard: ftpControl.PROTECTION_CLEAR,
                               securityModeSafe: ftpControl.PROTECTION_SAFE,
                               securityModePrivate: ftpControl.PROTECTION_PRIVATE}

except ImportError:
    unsupportedDatastoreList.append(GRIDFTP_STORE)


_resourceNameEncoding = "UTF-8"


class GridFTPDataStore(ExternalOnlineDataStore):
    """
    The class GridFTPDataStore represents a datastore where the data is 
    stored on a separated GridFTP server.
    """

    def __init__(self):
        """
        @see L{DataStore <datafinder.application.datastore.DataStore.
        DataStore.__init__>}
        """
        
        ExternalOnlineDataStore.__init__(self)
        self.dataLocation = "gsiftp://"
        self.securityMode = securityModeStandard
        self.dataTransferMode = transferModeStream
        self.parallelConnections = 0
        self.passphrase = "undefined"
        self.__tcpBufferSize = 64
        self.errorMessage = None
        self.configDataDict["securityMode"] = ("securityMode", None, None)
        self.configDataDict["dataTransferMode"] = ("dataTransferMode", None, None)
        self.configDataDict["parallelConnections"] = ("parallelConnections", None, None)
        self.configDataDict["tcpBufferSize"] = ("tcpBufferSize", None, None)
        self.gridFtpConnection = None
        self.deleteProxyCertificate = False
  
    def _getTcpBufferSize(self):
        """ Getter of the property tcpBufferSize. """
        
        return self.__tcpBufferSize
    
    def _setTcpBufferSize(self, tcpBufferSize):
        """ Setter of the property tcpBufferSize. """
        
        if not isinstance(tcpBufferSize, int):
            try:
                self.__tcpBufferSize = int(tcpBufferSize)
            except ValueError:
                raise ValueError("The TCP Buffer Size has to be an integer!")
        else:
            self.__tcpBufferSize = tcpBufferSize
          
    tcpBufferSize = property(_getTcpBufferSize, _setTcpBufferSize)
          
    def _createGridFTPUrl(self, resourceName):
        """ Returns the GridFTP url according to the given resource """
        
        gridFTPUrl = self.getDataLocation() + resourceName
        gridFTPUrl = gridFTPUrl.encode(_resourceNameEncoding)
        gridFTPUrl = quote(gridFTPUrl, ":/")
        return gridFTPUrl
    
    def _prepareDataStoreOperation(self):
        """
        @see L{ExternalOnlineDataStore <datafinder.application.datastore.DataStore.
        ExternalOnlineDataStore._prepareDataStoreOperation>}
        """
        
        self.gridFtpConnection = self._getConnection()
    
    def _cleanupDataStoreOperation(self):
        """
        @see L{ExternalOnlineDataStore <datafinder.application.datastore.DataStore.
        ExternalOnlineDataStore._cleanupDataStoreOperation>}
        """
        
        self.gridFtpConnection = None
    
    def _upload(self, resourceName, fileName):
        """
        @see L{ExternalOnlineDataStore <datafinder.application.datastore.DataStore.
        ExternalOnlineDataStore._upload>}
        
        @raise DataStoreIOError: unable to open file that should be uploaded
        @raise DataStoreAccessError: unable to upload file on GridFTP datastore
        @raise DataStoreReleaseError: unable to release GridFTP handle
        """
        
        #get destination url
        destinationUrl = self._createGridFTPUrl(resourceName)
        
        #create structure if necessary
        destinationDirectoryPath = dirname(resourceName)
        self._prepareGridFtpStructure(destinationDirectoryPath)
        
        # put it on the server
        try:
            try:
                self.gridFtpConnection.put(fileName, destinationUrl, self._getTransferProperties())
                if self.errorMessage:
                    raise FtpClientException(self.errorMessage)
            finally:
                self.errorMessage = None
                self._destroyConnection()
        except IOError, ioerr:
            raise DataStoreIOError(ioerr.errno, ioerr.strerror, ioerr.filename)
        except FtpClientException, ftpClientError:
            errorMessage = u"Cannot put GridFTP resource:\n'%s'\n on GridFTP server! Reason: %s" \
                           % (unicode(destinationUrl, _resourceNameEncoding), 
                              ftpClientError)
            raise DataStoreAccessError(errorMessage)
        
    def _download(self, resourceName, destinationFileName):
        """
        @see L{ExternalOnlineDataStore <datafinder.application.datastore.DataStore.
        ExternalOnlineDataStore._download>}
        
        @raise DataStoreAccessError: unable to download resource from GridFTP datastore
        @raise DataStoreIOError: unable to write file to local file system
        @raise DataStoreReleaseError: unable to release GridFTP handle
        """
        
        sourceUrl = self._createGridFTPUrl(resourceName) 
        try:
            try:
                self.gridFtpConnection.get(destinationFileName, sourceUrl, self._getTransferProperties())
                if self.errorMessage:
                    raise FtpClientException(self.errorMessage)
            finally:
                self.errorMessage = None
                self._destroyConnection()
        except FtpClientException, ftpClienterror:
            errorMessage = u"Unable to download GridFTP resource \n'%s'\n from " \
                            % unicode(sourceUrl, _resourceNameEncoding) + \
                            "GridFTP server! Reason: %s!" % ftpClienterror
            raise DataStoreAccessError(errorMessage)
        except IOError, ioerr:
            raise DataStoreIOError(ioerr.errno, ioerr.strerror, ioerr.filename)    
                  
    def _deleteEmptyCollection(self, directoryName):
        """
        Deletes the given collection. The collection has to be empty.

        @raise DataStoreAccessError: unable to delete directory from GridFTP datastore
        @raise DataStoreReleaseError: unable to release GridFTP handle
        """
        
        sourceUrl = self._createGridFTPUrl(directoryName)
        
        if self._resourceExists(sourceUrl):
            try:
                self.gridFtpConnection.rmdir(sourceUrl, self._getTransferProperties())
                if self.errorMessage:
                    tmpErrorMessage = self.errorMessage
                    self.errorMessage = None
                    raise FtpClientException(tmpErrorMessage)
            except FtpClientException, ftpClientError:
                self._destroyConnection()
                errorMessage = u"Cannot delete empty directory: \n'%s'\n " \
                                % unicode(sourceUrl, _resourceNameEncoding) + \
                                "from GridFTP datastore! Reason: %s" \
                                % ftpClientError
                raise DataStoreAccessError(errorMessage)
    
    def _resourceExists(self, urlToCheck):
        """
        Checks if the given GridFTP URL does exist.
        
        @param urlToCheck: GridFTP URL to check for existence
        @type urlToCheck: C{unicode}
        
        @return: True if the URL exists; otherwise False
        @rtype: C{bool}
        
        @raise DataStoreReleaseError: unable to release GridFTP handle
        """
        
        sourceUrlExists = False
        try:
            sourceUrlExists = self.gridFtpConnection.exists(urlToCheck, self._getTransferProperties())
            if self.errorMessage:
                raise FtpClientException(self.errorMessage)
        except FtpClientException, ftpClientError:
            self._destroyConnection()
            errorMessage = u"Cannot check existence of GridFTP resource: \n'%s'\n" \
                           % unicode(urlToCheck, _resourceNameEncoding) + \
                           "Reason: %s" % ftpClientError
            raise DataStoreAccessError(errorMessage)
        return sourceUrlExists
    
    def _delete(self, resourceName):
        """
        @see L{ExternalOnlineDataStore <datafinder.application.datastore.DataStore.
        ExternalOnlineDataStore._delete>}
        
        @raise DataStoreAccessError: unable to delete directory from GridFTP datastore
        @raise DataStoreReleaseError: unable to release GridFTP handle
        """
        
        sourceUrl = self._createGridFTPUrl(resourceName)
        try:
            self.gridFtpConnection.delete(sourceUrl, self._getTransferProperties())
            if self.errorMessage:
                tmpErrorMessage = self.errorMessage
                self.errorMessage = None
                raise FtpClientException(tmpErrorMessage)
        except FtpClientException, ftpClientError:
            self._destroyConnection()
            errorMessage = u"Cannot delete GridFTP resource: \n'%s'\n from GridFTP datastore!" \
                            % unicode(sourceUrl, _resourceNameEncoding) + \
                            " Reason: %s" % ftpClientError
            raise DataStoreAccessError(errorMessage)
        self._removeExistingCollectionStructure(resourceName)         
    
    def _move(self, sourceName, destinationName):
        """
        @see L{ExternalOnlineDataStore <datafinder.application.datastore.DataStore.
        ExternalOnlineDataStore._move>}
        
        @raise DataStoreAccessError: unable to rename resource on GridFTP datastore
        @raise DataStoreReleaseError: unable to release GridFTP handle
        """
        
        fromPath = self._createGridFTPUrl(sourceName)
        toPath = self._createGridFTPUrl(destinationName)
        testFromPath = dirname(sourceName)
        testToPath = dirname(destinationName)
        
        self._prepareGridFtpStructure(testFromPath)
        self._prepareGridFtpStructure(testToPath)
        try:
            try:
                self.gridFtpConnection.move(fromPath, toPath, self._getTransferProperties())
                if self.errorMessage:
                    raise FtpClientException(self.errorMessage)
            finally:
                self.errorMessage = None
        except FtpClientException, ftpClientError:
            self._destroyConnection()
            errorMessage = u"Cannot move GridFTP resource \nfrom '%s' \nto '%s'!\nReason: %s" \
                            % (unicode(fromPath, _resourceNameEncoding), 
                               unicode(toPath, _resourceNameEncoding), 
                               ftpClientError)
            raise DataStoreAccessError(errorMessage)
        self._removeExistingCollectionStructure(sourceName)
        
    def _copy(self, sourceName, destinationName):
        """
        @see L{ExternalOnlineDataStore <datafinder.application.datastore.DataStore.
        ExternalOnlineDataStore._copy>}
        
        @raise DataStoreAccessError: unable to copy resource on GridFTP datastore
        @raise DataStoreReleaseError: unable to release GridFTP handle
        """
        
        fromPath = self._createGridFTPUrl(sourceName)
        toPath = self._createGridFTPUrl(destinationName)
        testFromPath = dirname(sourceName)
        testToPath = dirname(destinationName)
        
        self._prepareGridFtpStructure(testFromPath)
        self._prepareGridFtpStructure(testToPath)
        try:
            try:
                self.gridFtpConnection.third_party_transfer(fromPath, toPath) 
                # Copy seems always to comlain if transfer properties are given. , self._getTransferProperties())
                if self.errorMessage:
                    raise FtpClientException(self.errorMessage)
            finally:
                self.errorMessage = None
        except FtpClientException, ftpClientError:
            self._destroyConnection()
            errorMessage = u"Cannot copy GridFTP resource \nfrom '%s' \nto '%s'!\nReason: %s" \
                            % (unicode(fromPath, _resourceNameEncoding), 
                               unicode(toPath, _resourceNameEncoding), 
                               ftpClientError)
            raise DataStoreAccessError(errorMessage)
            
    def _getConnection(self):
        """
        Creates the connection to the GridFTP server.
        
        @return: connection to the GridFTP server
        @rtype: C{pyGlobus.ftpClient.EasyFtpClient}
        
        @raise DataStoreLoginError: unable to perform FTP server login
        @raise DataStoreConnectError: unable to connect to FTP server
        """
        
        performGridProxyInit = False
        try:
            certInfo = grid_proxy_info(verbose=0)
            if certInfo[0].find("0:00:00") >= 0:
                performGridProxyInit = True
            else: 
                removeCredentials = True
        except GSIException:
            performGridProxyInit = True
 
        if performGridProxyInit:
            try:
                grid_proxy_init(passphrase=str(self.passphrase), verbose=0)
                removeCredentials = True
            except GSIException, gsiError:
                raise DataStoreLoginError(self.name, unicode(gsiError))

        # register function that destroies the proxy certificate on exit
        if removeCredentials and not self.deleteProxyCertificate:
            from atexit import register
            register(_releaseGridProxy)
            self.deleteProxyCertificate = True

        try:
            myGridFtpConnection = EasyFtpClient()
            myGridFtpConnection.done_cb = self._doneCallback
        except GlobusException, globusErr:
            errorMessage = u"Cannot create GridFTP connection! Reason: %s"  \
                             % globusErr
            raise DataStoreConnectError(errorMessage)
        return myGridFtpConnection
    
    def _getTransferProperties(self):
        """ Returns the different properties of the file transfer. """
        
        properties = OperationAttr()
        properties.set_mode(_transferModeDictionary[self.dataTransferMode])
        properties.set_data_protection(_securityModeDictionary[self.securityMode])
        from pyGlobus.ftpControl import TcpBuffer
        aTcpBuffer = TcpBuffer()
        aTcpBuffer.set_automatic(self.tcpBufferSize, self.tcpBufferSize, self.tcpBufferSize)
        # The setting of this property does not work. properties.set_tcp_buffer(aTcpBuffer)
        if self.parallelConnections > 0 and self.dataTransferMode == transferModeExtended:
            parallelism = ftpControl.Parallelism()
            parallelism.set_mode(ftpControl.PARALLELISM_FIXED)
            parallelism.set_size(self.parallelConnections)
            properties.set_parallelism(parallelism)
        return properties
    
    def _doneCallback(self, condV, handle, error):
        """ Replacement for EasyFtpClient specific callback function. """
        
        if not error[0] == 0:
            self.errorMessage = error[1] 
        condV.acquire()
        condV.notify()
        condV.release()
        return 
 
    def _destroyConnection(self):
        """
        Destroies the given GridFTP connection
        
        @param gridFtpConnection: GridFTP connection
        @type gridFtpConnection: L{EasyFtpClient}
        
        @raise DataStoreReleaseError: unable to release GridFTP handle
        """
        
        try:
            del self.gridFtpConnection
        except FtpClientException:
            errorMessage = u"Cannot remove GridFTP handle!"
            raise DataStoreReleaseError(errorMessage)
    
    def _prepareGridFtpStructure(self, pathToPrepare):
        """
        Recursive directory creation function for GridFTP servers.
        
        @param pathToPrepare: path to prepare for operation
        @type pathToPrepare: C{unicode-string}
        
        @raise DataStoreAccessError: unable to create sub directory
        @raise DataStoreReleaseError: unable to release GridFTP handle
        """     
        
        urlToPrepare = self._createGridFTPUrl(pathToPrepare)        
        if not self._resourceExists(urlToPrepare):
            pathComponents = pathToPrepare.split("/")
            pathComponents = [pathcomp for pathcomp in pathComponents if pathcomp != ""]
            
            currentDirectory = ""
            for subDirectory in pathComponents:
                currentDirectory = currentDirectory + "/" + subDirectory
                try:
                    directoryExists = self._resourceExists(self._createGridFTPUrl(currentDirectory))
                    if not directoryExists:
                        self.gridFtpConnection.mkdir(self._createGridFTPUrl(currentDirectory))
                        if self.errorMessage:
                            tmpErrorMessage = self.errorMessage
                            self.errorMessage = None
                            raise FtpClientException(tmpErrorMessage)
                except FtpClientException, ftpClientError:
                    self._destroyConnection()
                    errorMessage = u"Cannot prepare structure for GridFTP resource: " + \
                                    "\n'%s'!\nReason: %s" % (unicode(urlToPrepare, \
                                     _resourceNameEncoding), ftpClientError)
                    raise DataStoreAccessError(errorMessage)

    def _removeExistingCollectionStructure(self, resourceName):
        """ 
        This function tries to remove the existing structure that was created
        to upload, copy or move a resource. This method is used during by the 
        methods _delete and _move.
        """
        
        pathComponents = resourceName.split("/")
        pathComponents = [pathcomp for pathcomp in pathComponents if pathcomp != ""]
        if len(pathComponents) > 1:
            pathComponents = pathComponents[1:]
            pathComponents.reverse()
            pathToDelete = resourceName
            for path in pathComponents:
                startIndex = pathToDelete.rfind(path)
                pathToDelete = pathToDelete[:(startIndex - 1)]
                if self._isCollectionEmpty(pathToDelete):
                    self._deleteEmptyCollection(pathToDelete)
                else:
                    return
                
    def _isCollectionEmpty(self, resourceName):
        """ Checks if the given collection resource is empty. """
        
        isCollectionEmpty = False
        gridFtpResourceToList = self._createGridFTPUrl(resourceName)
        try:
            listResult = self.gridFtpConnection.list(gridFtpResourceToList)
            if self.errorMessage:
                raise FtpClientException(self.errorMessage)
            isCollectionEmpty = len(listResult.replace(".", "").strip()) == 0
        except FtpClientException, ftpClientError:
            self._destroyConnection()
            errorMessage = u"Cannot list GridFTP resource: \n'%s'\n" \
                           % unicode(gridFtpResourceToList, _resourceNameEncoding) + \
                           "Reason: %s" % ftpClientError
            raise DataStoreAccessError(errorMessage)
        return isCollectionEmpty
