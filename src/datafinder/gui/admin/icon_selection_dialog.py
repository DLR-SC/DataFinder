#
# Description: Dialog to select icons for datatypes, relations and datastores
#
# Created: Matthias Wagner (mail to Matthias.Wagner@dlr.de)
#
# Version: $Id: icon_selection_dialog.py 3906 2009-04-03 17:17:43Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder
#


"""
Dialog to select icons for datatypes, relations and datastores.
"""


from qt import PYSIGNAL, SLOT, Qt, QPixmap, QListBox

from datafinder.gui.gen import SelectIconDialog


__version__ = "$LastChangedRevision: 3906 $"


class SelectUserIconDialog(SelectIconDialog.SelectIconDialog):
    """
    Dialog to select icons for datatypes, relations and datastores.
    """

    def __init__(self, parent=None, name=None, modal=0, flags=0, multiSelection=False):
        SelectIconDialog.SelectIconDialog.__init__(self, parent, name, modal, flags)
        self.connect(self, PYSIGNAL("quit"), SLOT("reject()"))
        self.buttonHelp.hide()
        if not name is None:
            self.setName("SelectUserIconForm")
        if multiSelection:
            self.iconListBox.setSelectionMode(QListBox.Multi)
        else:
            self.iconListBox.setSelectionMode(QListBox.Single)
        self.button = "cancel"


    def getIconName(self, iconList, preselected=None):
        """
        Show and handle dialog, and return name of selected icon.

        @param iconList: List of icons.
        @type iconList: List of strings.
        @param preselected: name of icon selected when opening dialog (opt.)
        @type preselected: C{String}

        @return: The selected items.
        @rtype: C{list} of C{unicode}.
        """

        self.iconListBox.clear()
        iconList.sort()
        for icon in iconList:
            pixmap = QPixmap.fromMimeSource(icon.largeName)
            self.iconListBox.insertItem(pixmap, icon.baseName, -1)

        if preselected:
            preselectedItem = self.iconListBox.findItem(preselected, Qt.ExactMatch | Qt.CaseSensitive)
            if preselectedItem != 0:
                self.iconListBox.setSelected(preselectedItem, True)

        self.exec_loop()

        result = list()
        if self.button == "ok":
            for index in range(0, self.iconListBox.numRows()):
                item = self.iconListBox.item(index)
                if item.isSelected():
                    result.append(unicode(item.text()))
        return result

    def cancelButtonSlot(self):
        """
        Slot for cancel-button; emits PYSIGNAL "quit".
        """
        self.button = "cancel"
        self.emit(PYSIGNAL("quit"), ())

    def okButtonSlot(self):
        """
        Slot for ok-button; emits PYSIGNAL "quit".
        """
        self.button = "ok"
        self.emit(PYSIGNAL("quit"), ())
