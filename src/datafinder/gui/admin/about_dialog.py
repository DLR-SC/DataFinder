#
# Created: 27.07.2003 Uwe Tapper <Uwe.Tapper@dlr.de>
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


from datafinder.core.configuration import constants
from datafinder.gui.gen.AboutDialog import AboutDialogForm
from datafinder.gui.gen.license_dialog import LicenseDialog


__version__ = "$LastChangedRevision: 4616 $"


class AboutDialog(AboutDialogForm):
    """
    A simple "About"-dialog.
    """
    def __init__(self):
        """
        Constructor.
        """

        AboutDialogForm.__init__(self, modal=1)
        self.revisionTextLabel.setText(self.tr("Version: %s" % constants.VERSION))

    def setPixmap(self, pixmap):
        """
        Set an "about"-pixmap.

        @param pixmap: graphic shown in "About"-dialog
        @type pixmap: L{qt.QPixmap}
        """

        self.pixmapLabel.setPixmap(pixmap)
        self.repaint()

    def copyrightSlot(self):
        """ Display the copyright dialog. """

        licenceDialog = LicenseDialog(self)
        licenceDialog.exec_loop()
