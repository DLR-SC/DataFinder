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
Provides abstract base class implementing state handler.
"""


__version__ = "$Revision-Id:$" 



class BaseStateHandler(object):
    """ Provides abstract base class implementing state handler. """

    WINDOW_TITLE = ""
    _PAGEID_TITLE_SUBTITLE_MAP = dict()
    
    def __init__(self, wizard):
        """
        Constructor.
        """
        
        self._wizard = wizard
        self.lockIndex = None
        
    def prepareFinishSlot(self):
        """ Hook called by the wizard controller before the finsi slot is called. """
        
        pass
        
    def finishSlotCallback(self):
        """ The default finish slot callback. """
        
        pass
    
    def checkPreConditions(self):
        """ Checks the preconditions which have to be full-filled to start the dailog. """
        
        pass
        
    def nextId(self):
        """ Returns the identifier of the next page. """
        
        pass
    
    def initializePage(self, identifier):
        """ Performs initialization actions for the wizard page with the given identifier. """
        
        pass
    
    def cleanupPage(self, identifier):
        """ Performs clean up actions for the wizard page with the given identifier. """
        
        pass
    
    def finishSlot(self):
        """ Performs specific actions when the user commits his parameters. """
        
        pass

    @property
    def currentTitle(self):
        """ Returns the currently used title. """
        
        try:
            return self._PAGEID_TITLE_SUBTITLE_MAP[self._wizard.currentId()][0]
        except KeyError:
            return ""
        
    @property
    def currentSubTitle(self):
        """ Returns the currently used title. """
        
        try:
            return self._PAGEID_TITLE_SUBTITLE_MAP[self._wizard.currentId()][1]
        except KeyError:
            return ""
