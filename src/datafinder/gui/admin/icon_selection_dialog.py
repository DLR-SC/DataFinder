# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
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
Dialog to select icons for datatypes, relations and datastores.
"""


from qt import PYSIGNAL, SLOT, Qt, QPixmap, QListBox

from datafinder.gui.gen import SelectIconDialog


__version__ = "$Revision-Id:$" 


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
