# pylint: disable-msg=W0142
# Violating W0142 is necessary to be flexible enough handling the arguments of functions.
#
# Created: 27.01.2010 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: progress_dialog.py 4512 2010-03-04 15:44:43Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements a progress dialog.
"""


from PyQt4 import QtCore, QtGui

from datafinder.gui.user.common.util import startNewQtThread


__version__ = "$LastChangedRevision: 4512 $"


class ProgressDialog(QtCore.QObject):
    """ Implements a customizable progress dialog. """

    def __init__(self, windowTitle="Test Operation", labelText="Operation in progress...", 
                 minimum=0, maximum=100, interval=10, updateTriggerInterval=15000, parent=None):
        """
        Constructor.
        
        @param windowTitle: Title of the progress dialog window.
        @type windowTitle: C{unicode}
        @param labelText: Text of the progress dialog label.
        @type labelText: C{unicode}
        @param minimum: The minimum step.
        @type minimum: C{int}
        @param maximum: The maximum step.
        @type maximum: C{int}
        @param interval: The number of steps added when an update of progress is triggered.
        @type interval: C{int}
        @param updateTriggerInterval: Time interval (in milliseconds) when a prgress update is triggered.
        @type updateTriggerInterval: C{int} 
        @param parent: The parent widget.
        @type parent: L{QWidget<PyQt4.QtGui.QWidget>}
        """
        
        self._updateTriggerInterval = updateTriggerInterval
        self._interval = interval
        self._maximum = maximum
        self._minimum = minimum
        self._progressDialog = QtGui.QProgressDialog(parent)
        self._progressDialog.setLabelText(labelText)
        self._progressDialog.setCancelButtonText("Cancel")
        self._progressDialog.setMinimum(minimum)
        self._progressDialog.setMaximum(maximum)
        self._progressDialog.setWindowTitle(windowTitle)
        self._progressDialog.setModal(True)
        self._worker = None
        self._steps = 0
        self._timer = QtCore.QTimer()
        self._cb = lambda: None
        
        self.connect(self._timer, QtCore.SIGNAL("timeout()"), self._handleProgressUpdate)
        
    def start(self, function, *args, **kwargs): # W0142
        """
        Starts the execution of the given function and shows the progress dialog when necessary.
        """
        
        if self._worker is None:
            self._steps = self._interval
            self._progressDialog.setValue(self._interval)
            self._timer.start(self._updateTriggerInterval)
            self._worker = startNewQtThread(function, self._handleCallback, *args, **kwargs)
            
    def _handleProgressUpdate(self):
        """ Calculates the progress value and updates the dialog accordingly. """
        
        self._progressDialog.setValue(self._steps)
        if (self._steps + self._interval) < self._maximum:
            self._steps += self._interval
        
    def _handleCallback(self):
        """ Shows occurred errors and performs required clean up. """
        
        self._timer.stop()
        if not self._worker.error is None:
            caption = "Error During Operation"
            message = "The following error occurred while performing the user operation:\n" + self._worker.error.message
            QtGui.QMessageBox.critical(self._progressDialog, caption, message)

        if not self._cb is None:
            self._cb()
        self._worker = None
        self._progressDialog.setValue(self._maximum)
        self._progressDialog.cancel()

    def __del__(self):
        """ Cleans up the progress dialog. """

        self._timer.deleteLater()
