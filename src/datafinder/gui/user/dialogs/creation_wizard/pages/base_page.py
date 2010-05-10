#
# Created: 22.01.2010 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: base_page.py 4413 2010-01-27 13:24:27Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Abstract base class for wizard pages.
"""


from PyQt4.QtGui import QWizardPage


__version__ = "$LastChangedRevision: 4413 $"


class BaseWizardPage(QWizardPage):
    """ Abstract base class for wizard pages. """

    def __init__(self):
        """ Constructor. """
        
        QWizardPage.__init__(self)
        self.errorHandler = None
        
    def configure(self):
        """ Configures the specific wizard page. """
        
        pass
    
    def isComplete(self):
        """ @see: L{isComplete<PyQt4.QtGui.QWizardPage.isComplete>} """
        
        isComplete = False
        if not self.errorHandler is None:
            isComplete = not self.errorHandler.hasErrors
        return isComplete

    def __getattr__(self, name):
        """ Redirects to the wizard instance resolving specific GUI widgets. """
        
        return getattr(self.wizard(), name)
