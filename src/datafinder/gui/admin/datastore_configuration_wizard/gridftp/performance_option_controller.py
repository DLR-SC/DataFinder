# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
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
Implements the functionality of the GridFTP perfromacne option page. 
"""


from qt import SIGNAL

from datafinder.core.configuration.datastores import GRIDFTP_TRANSFER_MODE_ENUM
from datafinder.gui.admin.datastore_configuration_wizard.abstract_option_controller import AbstractOptionController


__version__ = "$Revision-Id:$" 


class PerformanceOptionController(AbstractOptionController):
    """ Handles the performance options of the GridFTP DataStore. """
    
    def __init__(self, wizardView, wizardController, pageType):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.__init__>}
        """
       
        AbstractOptionController.__init__(self, wizardView, wizardController, pageType)
        self.wizardView.connect(self.wizardView.gridFtpDatatransferModeButtonGroup, 
                                SIGNAL("clicked(int)"), 
                                self._dataTransferModeChangedSlot)
        self.wizardView.connect(self.wizardView.gridFtpParallelConnectionSpinBox, 
                                SIGNAL("valueChanged(int)"), 
                                self._gridFtpParallelConnectionSpinBoxValueChangedSlot)
        self.wizardView.connect(self.wizardView.gridFtpTcpBufferSizeLineEdit, SIGNAL("textChanged(const QString&)"), 
                                self._gridFtpTcpBufferSizeTextChanged)
        
    def showModelPart(self):
        """
        @see L{AbstractOptionController <datafinder.gui.
        DFDataStoreConfigurationWizard.AbstractOptionController.showModelPart>}
        """
       
        self.wizardView.performanceOptionsWidgetStack.raiseWidget(0)
        dataTransferMode = self.wizardController.datastore.dataTransferMode
        self._setDatatransferMode(dataTransferMode)
        self.wizardView.gridFtpTcpBufferSizeLineEdit.setText(str(self.wizardController.datastore.tcpBufferSize))
        self.wizardView.gridFtpParallelConnectionSpinBox.setValue(int(self.wizardController.datastore.parallelConnections))
        
    def _gridFtpParallelConnectionSpinBoxValueChangedSlot(self, parallelConnections):
        """ Set and validate number of parallel connections. """
        self.setDatastoreProperty("parallelConnections", parallelConnections, 
                                  self.wizardView.gridFtpParallelConnectionSpinBox)

    def _gridFtpTcpBufferSizeTextChanged(self, tcpBufferSize):
        """ Set and validate TCP buffer size. """
       
        self.setDatastoreProperty("tcpBufferSize", unicode(tcpBufferSize), self.wizardView.gridFtpTcpBufferSizeLineEdit)

    def _dataTransferModeChangedSlot(self, pressedButton):
        """ Slot that handles the change of the transfer mode. """
        
        if pressedButton == 0:
            mode = GRIDFTP_TRANSFER_MODE_ENUM.STREAM_MODE
        else:
            mode = GRIDFTP_TRANSFER_MODE_ENUM.EXTENDED_MODE
        self.setDatastoreProperty("dataTransferMode", mode)
        self._setDatatransferMode(mode)
    
    def _setDatatransferMode(self, dataTransferMode):
        """ Sets the the GUI elements according to the transfer mode. """
        
        if dataTransferMode == GRIDFTP_TRANSFER_MODE_ENUM.STREAM_MODE:
            self.wizardView.gridFtpStreamModeRadioButton.setChecked(True)
            self.wizardView.gridFtpParallelConnectionSpinBox.setEnabled(False)
        else:
            self.wizardView.gridFtpExtendedModeRadioButton.setChecked(True)
            self.wizardView.gridFtpParallelConnectionSpinBox.setEnabled(True)
