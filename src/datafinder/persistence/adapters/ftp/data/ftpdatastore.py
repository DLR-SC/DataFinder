# pylint: disable-msg=R0903,W0511,C0103
# R0903 (not enough public methods) disabled because the class uses the 
# public default interface of the base class.
#
# Description: The class FTPDataStore represents a Data Store where the data is 
#              stored on a separated FTP server.              
#
# Created: Tobias Schlauch (mail to Tobias.Schlauch@dlr.de)
#
# Version: $Id: FTPDataStore.py 2746 2007-11-06 20:49:01Z eife_an $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder
#


"""
The class FTPDataStore represents a Data Store where the data is stored on a separated FTP server.
"""


import socket
from ftplib import error_perm, FTP
from urlparse import urlsplit
from tempfile import mkstemp
import os

from datafinder.common.utility import encodeUtf8, decodeUtf8, isAsciiString, encrypt, decrypt
from datafinder.persistence.datastore.datastore import ExternalOnlineDataStore, \
                                                       DataStoreAccessError, \
                                                       DataStoreLoginError, \
                                                       DataStoreConnectError, \
                                                       DataStoreIOError


__version__ = "$LastChangedRevision$"


ftpAnonymousLoginName = u"anonymous"

_ftpErrorCodePermissionDenied = "553"
_ftpErrorCodeNotFound = "550"

_resourceNameEncoding = "UTF-8"


class FTPDataStore(ExternalOnlineDataStore):
    """
    The class FTPDataStore represents a Data Store where the data is 
    stored on a separated FTP server.
    """

    def __init__(self):
        """
        @see L{DataStore <datafinder.application.datastore.DataStore.
        DataStore.__init__>}
        """
        
        ExternalOnlineDataStore.__init__(self)
        self.dataLocation = "ftp://"
        self.username = ftpAnonymousLoginName
        self.__password = u""
        self.configDataDict["username"] = ("username", encodeUtf8, decodeUtf8)
        self.configDataDict["password"] = ("password", encrypt, decrypt)
        self.ftpConnection = None
                
    def setAnonymousAuthentication(self):
        """ Sets the authentication to anonymous. """
        
        self.username = ftpAnonymousLoginName
        self.__password = u""
        
    def isAnonymousAuthentication(self):
        """ Returns True if anonymous authentication is set. """
        
        if self.username == ftpAnonymousLoginName:
            return True
        else:
            return False
        
    def _getPassword(self):
        """ Getter of the property password. """
        
        return self.__password
           
    def _setPassword(self, password):
        """ Setter of the property password. """
        
        if isAsciiString(password):
            self.__password = password
        else:
            raise ValueError("The password contains Non-ASCII characters!")
                
    password = property(_getPassword, _setPassword)
        
    def _prepareDataStoreOperation(self):
        """
        @see L{ExternalOnlineDataStore <datafinder.application.datastore.DataStore.
        ExternalOnlineDataStore._prepareDataStoreOperation>}
        In this case a new FTP connection is created.
        """
        
        self.ftpConnection = self._getConnection()
    
    def _cleanupDataStoreOperation(self):
        """
        @see L{ExternalOnlineDataStore <datafinder.application.datastore.DataStore.
        ExternalOnlineDataStore._cleanupDataStoreOperation>}
        In this case the existing FTP connection is closed.
        """
        
        try:
            self.ftpConnection.quit()
        except (socket.error, error_perm):
            errorMessage = u"Cannot close FTP connection. Connection is already closed!"
            self.__logger.debug(errorMessage)

    def _upload(self, resourceName, fileName):
        """
        @see L{ExternalOnlineDataStore <datafinder.application.datastore.DataStore.
        ExternalOnlineDataStore.upload>}
        
        @raise DataStoreIOError: unable to open file that should be uploaded
        @raise DataStoreAccessError: unable to upload file on FTP Data Store
        """
        
        try:
            fileToUpload = open(fileName, "rb")
        except IOError, ioerr:
            raise DataStoreIOError(ioerr.errno, ioerr.strerror, ioerr.filename)
       
        resourceName = resourceName[1:]
        tmpResourceName = resourceName.encode(_resourceNameEncoding)
        destinationDirectoryPath = os.path.dirname(tmpResourceName)
        self._prepareFtpStructure(destinationDirectoryPath)
        
        # In this case the method os.path.join should not be applied, 
        # because the path is built for FTP, where the seperator is always "/".
        try:
            self.ftpConnection.storbinary("STOR " + tmpResourceName, fileToUpload)
        except error_perm, excText:
            if str(excText).find(_ftpErrorCodePermissionDenied) == 0:
                fileToUpload.close()
                self.ftpConnection.quit()
                raise DataStoreAccessError, "Permission denied - cannot store file '%s' in '%s'." \
                                            % (fileName, destinationDirectoryPath)
        fileToUpload.close()
        
    def _download(self, resourceName, destinationFileName):
        """
        @see L{ExternalOnlineDataStore <datafinder.application.datastore.DataStore.
        ExternalOnlineDataStore.download>}
        
        @raise DataStoreAccessError: unable to download resource from FTP Data Store
        @raise DataStoreIOError: unable to write file to local file system
        """
        
        resourceName = resourceName[1:]
        tmpResourceName = resourceName.encode(_resourceNameEncoding)
         
        try:
            self.ftpConnection.retrbinary("RETR " + tmpResourceName,
                                          open(destinationFileName, "wb").write)
        except error_perm, excText:
            # file doesn't exists?
            if (str(excText).find(_ftpErrorCodeNotFound) == 0):
                raise DataStoreAccessError, "File '%s' not found on Data Store '%s'." % \
                                            (unicode(tmpResourceName, _resourceNameEncoding), self.name)
            else:
                raise
        except IOError, ioerr:
            self.ftpConnection.quit()
            raise DataStoreIOError(ioerr.errno, ioerr.strerror, ioerr.filename)    
                     
    def _deleteEmptyCollection(self, directoryName):
        """
        Deletes the given collection. The collection has to be empty.

        @raise DataStoreAccessError: unable to delete directory from FTP Data Store
        """
        
        directoryName = directoryName[1:]
        if isinstance(directoryName, unicode): 
            tmpDirectoryName = directoryName.encode(_resourceNameEncoding)
        else:
            tmpDirectoryName = directoryName
        try:
            self.ftpConnection.rmd(tmpDirectoryName)
        except error_perm, excText:
            if str(excText).find(_ftpErrorCodePermissionDenied) == 0:
                self.ftpConnection.quit()
                raise DataStoreAccessError, "Permission denied - cannot delete '%s'." \
                                             % (directoryName)
            elif str(excText).find(_ftpErrorCodeNotFound) == 0:
                self.__logger.warning(u"Directory '%s' does not exist or is not " % directoryName + \
                                      u"empty on Data Store '%s'." % self.name)
            else:
                self.ftpConnection.quit()
                raise DataStoreAccessError(str(excText))
            
    def _delete(self, resourceName):
        """
        @see L{ExternalOnlineDataStore <datafinder.application.datastore.DataStore.
        ExternalOnlineDataStore._delete>}
        
        @raise DataStoreAccessError: unable to delete directory from FTP Data Store
        """
        
        resourceName = resourceName[1:]
        fileName = resourceName.encode(_resourceNameEncoding)
        try:
            self.ftpConnection.delete(fileName)
        except error_perm, excText:
            self.ftpConnection.quit()
            if str(excText).find(_ftpErrorCodePermissionDenied) == 0:
                raise DataStoreAccessError, "Permission denied - cannot delete '%s'." \
                                             % (resourceName,)
            else:
                raise DataStoreAccessError, "FTP Error '%s' while deleting '%s'." \
                                             % (str(excText), resourceName)
        self._removeExistingFtpStructure("/" + fileName)
                     
    def _move(self, sourceName, destinationName):
        """
        @see L{ExternalOnlineDataStore <datafinder.application.datastore.DataStore.
        ExternalOnlineDataStore._move>}
        
        @raise DataStoreAccessError: unable to rename resource on FTP Data Store
        """
        
        sourceName = sourceName[1:]
        fromPath = sourceName.encode(_resourceNameEncoding)
        destinationName = destinationName[1:]
        toPath = destinationName.encode(_resourceNameEncoding)
        testFromPath = os.path.dirname(fromPath)
        testToPath = os.path.dirname(toPath)
        
        self._prepareFtpStructure(testFromPath)
        self._prepareFtpStructure(testToPath)
        try:
            self.ftpConnection.rename(fromPath, toPath)
        except error_perm, excText:
            self.ftpConnection.quit()
            if str(excText).find(_ftpErrorCodePermissionDenied) == 0:
                raise DataStoreAccessError, "Permission denied - cannot rename '%s' to '%s'." \
                                             % (sourceName, destinationName)
            else:
                raise DataStoreAccessError, "FTP Error '%s' while renaming '%s'." \
                                             % (str(excText), sourceName)
        self._removeExistingFtpStructure("/" + fromPath)
        
        
    def _copy(self, resourceName, destinationName):
        """
        @see L{ExternalOnlineDataStore <datafinder.application.datastore.DataStore.
        ExternalOnlineDataStore._copy>}
        """
        
        fileDescriptor, fileName = mkstemp()
        try:
            os.close(fileDescriptor)
        except OSError:
            errorMessage = u"Unable to create temporary file!"
            raise DataStoreAccessError(errorMessage)
        try:
            self._download(resourceName, fileName)
            self._upload(destinationName, fileName)
        finally:
            try:
                os.remove(fileName)
            except OSError:
                self.__logger.warning(u"Unable to delete temporary file %s!" % (fileName))
                
#    def copyResource(self, collectionNameList, resourceNameList, destinationName):
#        """
#        @see L{ExternalOnlineDataStore <datafinder.application.datastore.DataStore.
#        ExternalOnlineDataStore.copyResource>}
#        
#        @raise DataStoreAccessError: unable to copy resource on FTP Data Store 
#        """    
        #TODO: check ftpcp function - limitation of PORT command
#===============================================================================
#        ftpSourceConnection = self._getConnection()
#        ftpTargetConnection = self._getConnection()
#        fromPath = sourceName
#        toPath = destinationName
#        testPath = dirname(toPath)
#        basePath = urlsplit(self.getDataLocation())[2]
#        self._prepareFtpStructure(testPath)
#        
#        try:
#            ftpcp(ftpSourceConnection, basePath + fromPath, ftpTargetConnection, basePath + toPath)
#        except error_perm, excText:
#            ftpSourceConnection.quit()
#            ftpTargetConnection.quit()
#            if str(excText).find(FTP_ERROR_CODE_PERMISSON_DENIED) == 0:
#                raise DataStoreAccessError, "Permission denied - cannot rename '%s' to '%s'." \
#                                             % (fromPath, toPath)
#            else:
#                raise DataStoreAccessError, "FTP Error '%s' while renaming '%s'." \
#                                             % (str(excText), fromPath)
#        ftpSourceConnection.quit()
#        ftpTargetConnection.quit()
#===============================================================================
            
    def _getConnection(self):
        """
        Creates the connection to the FTP server.
        
        @return: connection to the FTP server
        @rtype: C{ftplib.FTP}
        
        @raise DataStoreLoginError: unable to perform FTP server login
        @raise DataStoreConnectError: unable to connect to FTP server
        """
        
        self._checkUsernamePassword()
        username, password = self.getUsernamePassword()
        # split URL of Data Store and use domain -> ...[1]:
        try:
            ftpConnection = FTP(urlsplit(self.getDataLocation())[1])
            ftpConnection.login(username, password)
            ftpConnection.cwd(urlsplit(self.getDataLocation())[2][1:])
        except error_perm:
            raise DataStoreLoginError(self.name, "FTP server login failed!") 
        except socket.error, socerr:
            raise DataStoreConnectError, "socket.error: " + str(socerr)
        
        return ftpConnection
    
    def _removeExistingFtpStructure(self, resourceName):
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
            pathToDelete =  resourceName
            for path in pathComponents:
                startIndex = pathToDelete.rfind(path)
                pathToDelete = pathToDelete[:(startIndex - 1)]
                try:
                    directoryContent = self.ftpConnection.nlst(pathToDelete[1:])
                except error_perm, ftpError:
                    errorMessage = u"Cannot list content of FTP directory '%s'! Reason: %s" \
                                   % (resourceName, str(ftpError))
                    raise DataStoreAccessError(errorMessage)
                if len(directoryContent) == 0:
                    self._deleteEmptyCollection(pathToDelete)
                else:
                    return
    
    def _prepareFtpStructure(self, path):
        """
        Recursive directory creation function for FTP-servers (similar to
        C{os.makedirs()}).
        Remark: ftpConnection.cwd() is not being changed.

        @param path: the path (relative to ftpConnection.cwd())
        @type path: C{unicode}
        """
        
        pathComponents = path.split("/")
        pathComponents = [pathcomp for pathcomp in pathComponents if pathcomp != ""]

        # store path:
        rpath = self.ftpConnection.pwd()

        for subdir in pathComponents:
            try:
                # try to change working directory:
                self.ftpConnection.cwd(subdir)
            except error_perm, ftpError:
                # directory doesn't exist, so we try to create it
                # (assume that error message starts with FTP-error-num.):
                if (str(ftpError).find(_ftpErrorCodeNotFound) == 0):
                    try:
                        self.ftpConnection.mkd(subdir)
                    except error_perm, ftpError:
                        errorMessage = u"Cannot create sub directory %s! Reason: %s" \
                                         % (unicode(subdir, _resourceNameEncoding),
                                            unicode(ftpError))
                        raise DataStoreAccessError(errorMessage)
                    try:
                        self.ftpConnection.cwd(subdir)
                    except error_perm, ftpError:
                        errorMessage = u"Cannot change to created sub " + \
                                         "directory %s! Reason: %s" \
                                         % (unicode(subdir, _resourceNameEncoding),
                                            unicode(ftpError))
                        raise DataStoreAccessError(errorMessage)
                else:
                    errorMessage = u"Cannot change to sub directory %s! Reason: %s" \
                                    % (unicode(subdir, _resourceNameEncoding),
                                       unicode(ftpError))
                    raise DataStoreAccessError(errorMessage)
        # reset path:
        self.ftpConnection.cwd(rpath)
