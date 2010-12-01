# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#
#Redistribution and use in source and binary forms, with or without
#
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
A simple "About" dialog.
"""


from datafinder.core.configuration import constants
from datafinder.gui.gen.AboutDialog import AboutDialogForm
from datafinder.gui.gen.license_dialog import LicenseDialog


__version__ = "$Revision-Id:$" 


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
