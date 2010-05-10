#
# Created: 24.01.2008 Tobias Schlauch
# Changed: $Id: logger.py 3978 2009-04-29 17:22:06Z schlauch $
# 
# Version: $Revision: 3978 $
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


"""" 
Module provides access to a configured logger instance.
"""


import logging
import os

from datafinder.core.configuration.constants import USER_HOME


__version__ = "$LastChangedRevision: 3978 $"


_fileLogFormat = "%(asctime)s: %(levelname)s: %(message)s"
_logFileName = "debug.log"
_webdavLogFileName = "webdav.log"
    

def getDefaultLogger():
    """ 
    Returns a configured logger object.
    
    @return: Logger instance.
    @rtype: C{logging.Logger}
    """
    
    myLogger = logging.getLogger(None)
    if len(myLogger.handlers) == 0:
        from webdav import logger 
        webdavLogger = logger.getDefaultLogger(_getFileHandler(_webdavLogFileName))
        webdavLogger.level = logging.INFO
        myLogger.level = logging.INFO
        myLogger.addHandler(_getFileHandler(_logFileName))
    return myLogger


def _getFileHandler(fileName):
    """ Initializes a file handler with the given file name. """
     
    formatter = logging.Formatter(_fileLogFormat)
    if not os.path.exists(USER_HOME):
        os.mkdir(USER_HOME)
    fileHandler = logging.FileHandler(os.path.join(USER_HOME, fileName), "wb")
    fileHandler.setFormatter(formatter)
    return fileHandler
