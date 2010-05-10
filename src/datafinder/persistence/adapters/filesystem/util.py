#
# Created: 19.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: util.py 4626 2010-04-20 20:57:02Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
This module provides some utility classes / function for platform-independent
file system access.
"""


_WIN32_PLATFORM = "win32"


import logging
import os
import sys
if sys.platform == _WIN32_PLATFORM:
    import pythoncom
    import pywintypes
    import win32api
    from win32com.shell import shell
    import win32netcon
    import win32wnet
    
from datafinder.persistence.error import PersistenceError

    
__version__ = "$LastChangedRevision: 4626 $"


_log = logging.getLogger(None)


class ShortCut(object):
    """ Implements platform-independent shortcut / symbolic link implementation. """
    
    _WINDOWS_LINK_EXTENSION = ".lnk"
    
    def __init__(self, destination):
        """ Constructor. """
        
        self._destination = destination
        
    def create(self, source):
        """ Creates the shortcut / symbolic link. """
        
        if sys.platform == _WIN32_PLATFORM:
            try:
                sh = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, \
                                                pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
                persist = sh.QueryInterface(pythoncom.IID_IPersistFile)
                sh.SetPath(source)
                persist.Save(self._destination, 1)
            except pywintypes.com_error, error:
                errorMessage = "Cannot create symbolic link '%s'. Reason: '%s'." % (self._destination, error[0])
                raise PersistenceError(errorMessage)
        else:
            try:
                os.symlink(source, self._destination)
            except OSError, error:
                reason = os.strerror(error.errno)
                errorMessage = "Cannot create symbolic link '%s'. Reason: '%s'" % (self._destination, reason)
                raise PersistenceError(errorMessage)
            
    def resolve(self):
        """ Resolves the link. """
        
        if sys.platform == _WIN32_PLATFORM:
            try:
                sh = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, \
                                                pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
                persist = sh.QueryInterface(pythoncom.IID_IPersistFile)
                persist.Load(self._destination)
                return sh.GetPath(shell.SLGP_UNCPRIORITY)[0]
            except pywintypes.com_error, error:
                errorMessage = "Cannot resolve symbolic link '%s'. Reason: '%s'." % (self._destination, error[0])
                raise PersistenceError(errorMessage)
        else:
            try:
                return os.readlink(self._destination)
            except OSError, error:
                reason = os.strerror(error.errno)
                errorMessage = "Cannot resolve symbolic link '%s'. Reason: '%s'" % (self._destination, reason)
                raise PersistenceError(errorMessage)
            
    def isLink(self):
        """ Figures out if the associated path is a symbolic link. """
        
        if sys.platform == _WIN32_PLATFORM:
            result = False
            if self._destination.endswith(self._WINDOWS_LINK_EXTENSION):
                try:
                    sh = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, \
                                                    pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
                    persist = sh.QueryInterface(pythoncom.IID_IPersistFile)
                    persist.Load(self._destination)
                    result = True
                except pywintypes.com_error:
                    result = False
            return result
        else:
            return os.path.islink(self._destination)


def createShortcut(path):
    """ Creates a platform-specific shortcut representation. """
    
    return ShortCut(path)


def isWindowsRootPath(path):
    """ Checks whether the given path corresponds to the virtual root directory on WIndows. """
    
    isWindowsRootPath_ = False
    if path == "/" and sys.platform == _WIN32_PLATFORM:
        isWindowsRootPath_ = True
    return isWindowsRootPath_


def listDirectory(directoryPath):
    """ Lists the given directory. """
    
    if directoryPath == "/" and sys.platform == _WIN32_PLATFORM:
        result = [driveLetter for driveLetter in win32api.GetLogicalDriveStrings().split("\000") if driveLetter]
    else:
        result = list()
        for path in os.listdir(directoryPath):
            path = os.path.join(directoryPath, path)
            decodedPath = _binaryToUnicodeFilePathDecoding(path)
            if not decodedPath is None:
                result.append(decodedPath)
            else:
                _log.debug("Unable to decode path string. Ignoring it.")
    return result


def _binaryToUnicodeFilePathDecoding(binaryString):
    """
    Decodes the given binary string into an unicode string.
    The primarily use is for decoding file system paths.
    In order to perform the decoding the default file system encoding
    is used. If it fails on non-Windows operating systems, it will be tried
    to use the Windows encoding "cp437". This encoding is used when a
    a file name is written via a Samba share from a Windows client.
    If the given string is already an unicode string this string is returned and
    no conversion is tried.
    
    @param binaryString: String to decode.
    @type binaryString: C{string}
    
    @retrun: Unicode representation of the binary string.
    @rtype: C{unicode}
    """
    
    fileSystemEncoding = sys.getfilesystemencoding()
    if fileSystemEncoding is None:
        fileSystemEncoding = "utf-8"
    if not isinstance(binaryString, unicode):
        try:
            unicodeString = binaryString.decode(fileSystemEncoding)
        except UnicodeDecodeError:
            if sys.platform != "win32":
                try:
                    unicodeString = binaryString.decode("cp437")
                except UnicodeDecodeError:
                    return None
    else:
        unicodeString = binaryString
    return unicodeString


def connectWindowsShare(share, username, password):
    """
    Connects a windows-share.

    @param share: Windows share in UNC path representation.
    @type share: C{unicode}

    @raise PersistenecError: raised if connection to a SMB-share failed
    """
    
    if sys.platform == _WIN32_PLATFORM:
        components = os.path.normpath(share).split("\\")
        if len(components) < 3:
            raise PersistenceError("Wrong file share configuration information!")
        else:
            if not os.path.exists(share):
                try:
                    win32wnet.WNetAddConnection2(win32netcon.RESOURCETYPE_DISK, 
                                                 None, #unused_drive,
                                                 share,
                                                 None,
                                                 username,
                                                 password,
                                                 0)
                except pywintypes.error, error:
                    raise PersistenceError("Could not connect to '%s'.\nReason: %s" % (share, error[2]))


class ItemIdentifierMapper(object):
    """ Maps identifiers. """
    
    def __init__(self, basePath):
        """ 
        Constructor. 
        
        @param basePath: Root path of the file system.
        @type basePath: C{unicode}
        """
        
        self.__basePath = basePath

    def mapIdentifier(self, identifier):
        """ 
        Maps the identifier to persistence representation.
        """
        
        mappedId = os.path.join(self.__basePath, identifier[1:])
        if mappedId.startswith("/"): # Ensures correct format on WIN32 when addressing a drive letter
            driveLetter, _ = os.path.splitdrive(mappedId[1:])
            if len(driveLetter) > 0:
                mappedId = mappedId[1:]
                if mappedId == driveLetter:
                    mappedId += "/"
        return mappedId
    
    def mapPersistenceIdentifier(self, persisentenceId):
        """ 
        Maps the persistence identifier to the path used to address the items logically.
        """
        
        mappedId = persisentenceId
        if persisentenceId.startswith(self.__basePath):
            mappedId = persisentenceId[len(self.__basePath):]
        if not mappedId.startswith("/"):
            mappedId = "/" + mappedId
        mappedId = mappedId.replace("\\", "/")
        if mappedId.endswith("/"):
            mappedId = mappedId[:-1]
        return mappedId
