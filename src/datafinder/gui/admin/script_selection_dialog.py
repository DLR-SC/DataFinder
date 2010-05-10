# pylint: disable-msg=W0142,W0612
# W0142: *-magic
# W0612: unused variable (item - see setScripts())
#
# Created: 29.03.2004 Uwe Tapper <Uwe.Tapper@dlr.de>
# Changed: $Id: script_selection_dialog.py 3934 2009-04-14 12:26:49Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder/
#


"""
Dialog to select a script.
"""


from qt import PYSIGNAL, SLOT, QListViewItem

from datafinder.common.logger import getDefaultLogger
from datafinder.core.configuration.scripts.script import Script
from datafinder.gui.gen.SelectScriptDialog import SelectScriptDialogForm


__version__ = "$LastChangedRevision: 3934 $"


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
