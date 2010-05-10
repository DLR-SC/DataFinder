#
# Created: 25.01.2010 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: base_state_handler.py 4525 2010-03-06 12:13:44Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Provides abstract base class implementing state handler.
"""


__version__ = "$LastChangedRevision: 4525 $"



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
