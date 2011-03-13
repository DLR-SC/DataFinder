# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
#Redistribution and use in source and binary forms, with or without
#
#modification, are permitted provided that the following conditions are
#
#met:
#
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
Dialog to select a script.
"""


from qt import PYSIGNAL, SLOT, QListViewItem

from datafinder.common.logger import getDefaultLogger
from datafinder.core.configuration.scripts.script import Script
from datafinder.gui.gen.SelectScriptDialog import SelectScriptDialogForm


__version__ = "$Revision-Id:$" 


class SelectScriptDialog(SelectScriptDialogForm):
    """
    Dialog to select a "script".
    (see L{datafinder.application.ScriptingHandler.ScriptingHandler})
    """

    __logger = getDefaultLogger()

    def __init__(self, *args):
        """
        Constructor.
        """

        SelectScriptDialogForm.__init__(self, *args)
        self.connect(self, PYSIGNAL("quit"), SLOT("reject()"))
        self.okay = 0

    def setScripts(self, scripts):
        """
        Set items of script-listview.
        Invoke this method before using getScript().

        @param scripts: list of scripts
        @type scripts: C{list} of C{dictionaries}
                           (keys: name, description, file, version, datatypes, icon)
        """

        self.scriptListView.clear()
        for script in scripts:
            if isinstance(script, Script):
                item = QListViewItem(self.scriptListView, script.title or "", script.description or "",
                                     script.version or "", ",".join(script.datatypes), script.iconName or "")
            else:
                item = QListViewItem(self.scriptListView, script.title or "", "", "", "", "")
            item.script = script
        self.scriptListView.clearSelection()
        self.adjustSize()

    def getScriptToRemove(self):
        """
        Show and handle dialog, returns name of selected script.

        @return: name of selected script (OK) or None (Cancel)
        @rtype: C{unicode} (or C{None})
        """
        
        self.setCaption(self.tr("Select Script"))
        self.taskTextLabel.setText(self.tr("Select Script to Remove:"))
        self.okButton.setText(self.tr("Remove"))
        self.cancelButton.setDefault(True)

        self.exec_loop()

        result = list()
        if self.okay:
            item = self.scriptListView.firstChild()
            while not item is None:
                if item.isSelected():
                    result.append(item.script)
                item = item.nextSibling()
        return result

    def cancelPushButtonSlot(self):
        """
        Slot for Cancel-button.
        """
        
        self.okay = 0 # false
        self.emit(PYSIGNAL("quit"), ())

    def okPushButtonSlot(self):
        """
        Slot for OK-button.
        """
        
        self.okay = 1 # true
        self.emit(PYSIGNAL("quit"), ())
