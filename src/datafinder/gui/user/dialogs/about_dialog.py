#
# Created: 26.05.2009 Heinrich Wendel <Heinrich.Wendel@dlr.de>
# Changed: $Id: about_dialog.py 4616 2010-04-18 10:41:05Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder/
#


"""
A simple "About" dialog.
"""

from PyQt4 import QtGui

from datafinder.core.configuration import constants
from datafinder.gui.gen.user.about_dialog_ui import Ui_aboutDialog
from datafinder.gui.user.dialogs.license_dialog import LicenseDialogView



__version__ = "$LastChangedRevision: 4616 $"


class AboutDialogView(QtGui.QDialog, Ui_aboutDialog):
    """
    A simple "About"-dialog.
    """
    def __init__(self, parent):
        """
        Constructor.
        """

        QtGui.QDialog.__init__(self, parent)
        Ui_aboutDialog.__init__(self)
        
        self.setupUi(self)
        
        self.revisionTextLabel.setText("Version: %s" % constants.VERSION)

    def copyrightSlot(self):
        """ Display the copyright dialog. """

        licenseDialog = LicenseDialogView(self)
        licenseDialog.exec_()
