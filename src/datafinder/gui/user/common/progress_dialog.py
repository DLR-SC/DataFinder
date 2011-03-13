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
Implements a progress dialog.
"""


from PyQt4 import QtCore, QtGui

from datafinder.gui.user.common.util import startNewQtThread


__version__ = "$Revision-Id:$" 


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
        
        QtCore.QObject.__init__(self)
         
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
