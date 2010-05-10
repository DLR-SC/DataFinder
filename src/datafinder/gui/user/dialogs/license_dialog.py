#
# Created: 26.05.2009 Heinrich Wendel <Heinrich.Wendel@dlr.de>
# Changed: $Id: license_dialog.py 4002 2009-05-06 16:31:59Z wend_he $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder/
#


"""
A simple "Licence"-dialog.
"""

from PyQt4 import QtGui

from datafinder.gui.gen.user.license_dialog_ui import Ui_licenseDialog



__version__ = "$LastChangedRevision: 4002 $"


class LicenseDialogView(QtGui.QDialog, Ui_licenseDialog):
    """
    A simple "License"-dialog.
    """
    def __init__(self, parent):
        """
        Constructor.
        """

        QtGui.QDialog.__init__(self, parent)
        Ui_licenseDialog.__init__(self)
        
        self.setupUi(self)

