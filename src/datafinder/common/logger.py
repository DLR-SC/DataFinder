# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
# All rights reserved.
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#met:
#
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


"""" 
Module provides access to a configured logger instance.
"""


import logging
import os

from datafinder.core.configuration.constants import USER_HOME


__version__ = "$Revision-Id:$" 


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
