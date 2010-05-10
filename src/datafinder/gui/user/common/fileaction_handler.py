#
# Created: 04.02.2010 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: fileaction_handler.py 4532 2010-03-07 17:22:29Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Handles open and print actions of items. Currently it only works on Windows
"""


import os
import logging
   
_platformNotSupported = False
try:             
    import pywintypes
    from win32com.shell import shell, shellcon
    from win32event import WaitForSingleObject, INFINITE
except ImportError:
    _platformNotSupported = True
    
from datafinder.core.error import ItemError
from datafinder.gui.user.constants import LOGGER_ROOT
from datafinder.gui.user.common.util import startNewQtThread


__version__ = "$LastChangedRevision: 4532 $"


class FileActionHandler(object):
    """ 
    Handles open and print actions of items. 
    Currently it only works on WIndows systems.
    """

    _OPEN_COMMAND = "open"
    _PRINT_COMANND = "print"
    
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
        
        self._performFileAction(item, self._PRINT_COMANND)
    
    def _performFileAction(self, item, command):
        """ Performs the given command on the specific file. """

        if _platformNotSupported:
            raise ItemError("The '%s' action for files is currently only supported on Windows." % command)
        localContentPath, alreadyLocal = self._getContent(item)
        if not alreadyLocal and len(self._checkUntilClosedWorker) == self._MAX_WORKER_THREADS:
            errorMessage = "The maximum (%i) of parallel started and monitored applications " % self._MAX_WORKER_THREADS \
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
        if not item.isManaged and dataUri.startswith("file://"): # directly accessable
            localContentPath = dataUri[8:]
            temporaryFileObject = None
        else: # get temporary file
            localContentPath, temporaryFileObject = item.getTemporaryFileObject(False)
            temporaryFileObject.close()
        return localContentPath, temporaryFileObject is None
