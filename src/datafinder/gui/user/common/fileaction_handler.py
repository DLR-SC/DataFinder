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
Handles open and print actions of items. Currently it only works on Windows
"""


import os
import logging
import subprocess
   
try: 
# pylint: disable=E0611,F0401 
# E0611: "shell" exists in win32com but Pylint cannot detect it.
# F0401: "win32com.shell" exists but Pylint cannot import.          
    import pywintypes
    from win32com.shell import shell, shellcon
    from win32event import WaitForSingleObject, INFINITE
    _isWin32 = True
except ImportError:
    _isWin32 = False
    
from datafinder.core.error import ItemError
from datafinder.gui.user.constants import LOGGER_ROOT
from datafinder.gui.user.common.util import startNewQtThread


__version__ = "$Revision-Id:$" 


class FileActionHandler(object):
    """ 
    Handles open and print actions of items. 
    Currently it only works on WIndows systems.
    """

    _OPEN_COMMAND = "open"
    _PRINT_COMMAND = "print"
    
    _DF_DEFAULT_FILE_VIEWER_ENV = "DF_DEFAULT_FILE_VIEWER"
    _DF_DEFAULT_LINUX_VIEWER = "evince"
    
    _MAX_WORKER_THREADS = 30
    _logger = logging.getLogger(LOGGER_ROOT)
    
    
    def __init__(self):
        """ Constructor. """
        
        self._checkUntilClosedWorker = dict()

    def performOpen(self, item):
        """
        Opens the file content of the associated item in a suitable external application.
        
        @param item: Item which is opened.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        self._performFileAction(item, self._OPEN_COMMAND)

    def performPrint(self, item):
        """
        Prints the file content of the associated item.
        
        @param item: Item which is opened.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        self._performFileAction(item, self._PRINT_COMMAND)
    
    def _performFileAction(self, item, command):
        """ Performs the given command on the specific file. """
        print _isWin32
        if _isWin32:
            self._performFileActionWin32(item, command)
        else:
            if self._OPEN_COMMAND: # Run a default viewer
                defaultViewer = os.environ.get(self._DF_DEFAULT_FILE_VIEWER_ENV , self._DF_DEFAULT_LINUX_VIEWER)
                localContentPath, _ = self._getContent(item)
                try:
                    subprocess.Popen((defaultViewer, localContentPath))
                except OSError, error:
                    raise ItemError("Cannot open file. Reason: '%s'" % str(error))
            else:
                raise ItemError("Printing is not supported on this platform!")

    def _performFileActionWin32(self, item, command):
        """ Performs the given command on the specific file. """
        # pylint: disable=E1101
        # E1101: Pylint cannot resolve specific win32 modules.
        
        localContentPath, alreadyLocal = self._getContent(item)
        print localContentPath, alreadyLocal
        if not alreadyLocal and len(self._checkUntilClosedWorker) == self._MAX_WORKER_THREADS:
            errorMessage = "The maximum number (%i) of parallel opened editors " % self._MAX_WORKER_THREADS \
                           + "has been reached. Please close at least one external application."
            raise ItemError(errorMessage)
        
        fMask = 0
        if not alreadyLocal:
            fMask = shellcon.SEE_MASK_NOCLOSEPROCESS
        try:
            result = shell.ShellExecuteEx(fMask, 0, command, localContentPath, "", "", 1)
        except pywintypes.error:
            return
        else:
            if not alreadyLocal:
                workerId = str(result["hProcess"])
                worker = startNewQtThread(self._checkUntilClosed, self._createCheckUntilClosedCallback(workerId), 
                                          result["hProcess"], command == self._OPEN_COMMAND, item, localContentPath)
                self._checkUntilClosedWorker[workerId] = worker
                
    @staticmethod
    def _checkUntilClosed(processHandle, writeBack, item, localContentPath):
        """ Waits until the opened application is closed, writes data back, and removes the temporary file. """
                
        startModificationTime = os.path.getmtime(localContentPath)
        WaitForSingleObject(processHandle, INFINITE)
        finalModificationTime = os.path.getmtime(localContentPath)
        
        if writeBack and startModificationTime != finalModificationTime:
            if item.capabilities.canStoreData:
                fh = open(localContentPath, "rb")
                item.storeData(fh)
        os.remove(localContentPath)
            
    def _createCheckUntilClosedCallback(self, workerId):
        """ Creates a callback function performs the clean up actions. """
        
        def _callback():
            if workerId in self._checkUntilClosedWorker:
                try:
                    worker = self._checkUntilClosedWorker[workerId]
                    if not worker.error is None:
                        self._logger.error(worker.error.message)
                finally:
                    del self._checkUntilClosedWorker[workerId]
        return _callback
    
    @staticmethod
    def _getContent(item):
        """ Retrieves the file content of the associated item and returns its local path. """
        
        dataUri = item.dataUri
        print item.dataUri
        if not item.isManaged and dataUri.startswith("file://"): # directly accessible
            localContentPath = dataUri[8:]
            temporaryFileObject = None
        else: # get temporary file
            localContentPath, temporaryFileObject = item.getTemporaryFileObject(False)
            temporaryFileObject.close()
        return localContentPath, temporaryFileObject is None
