#
# Created: 10.11.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: performance_option_controller.py 3906 2009-04-03 17:17:43Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the functionality of the GridFTP perfromacne option page. 
"""


from qt import SIGNAL

from datafinder.core.configuration.datastores import GRIDFTP_TRANSFER_MODE_ENUM
from datafinder.gui.admin.datastore_configuration_wizard.abstract_option_controller import AbstractOptionController


__version__ = "$LastChangedRevision: 3906 $"


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
