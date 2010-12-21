# pylint: disable=E1101,E0611,F0401
# E1101: Pylint cannot resolve specific win32 modules.
# E0611: "shell" exists in win32com but Pylint cannot detect it.
# F0401: "win32com.shell" exists but Pylint cannot import.
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

    
__version__ = "$Revision-Id:$" 


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
