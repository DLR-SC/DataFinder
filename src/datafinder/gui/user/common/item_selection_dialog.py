# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#
#Redistribution and use in source and binary forms, with or without
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
Implements the dialog allowing selection of the collection which is searched. 
"""


from PyQt4 import QtGui

from datafinder.gui.gen.user.item_selection_dialog_ui import Ui_ItemSelectionDialog


__version__ = "$Revision-Id:$" 


class ItemSelectionDialog(QtGui.QDialog, Ui_ItemSelectionDialog):
    """
    Dialog allowing selection of collection that is searched.
    """

    def __init__(self, repositoryModel, parentWidget=None):
        """
        Constructor.
        
        @param repositoryModel: Reference on the repository model.
        @type repositoryModel: L{LeafFilter<datafinder.gui.user.models.leaf_filter.LeafFilter>}
        @param parentWidget: Reference to the parent widget.
        @type parentWidget: L{QWidget<PyQt4.QtGui.QWidget>}
        """

        QtGui.QDialog.__init__(self, parentWidget)
        Ui_ItemSelectionDialog.__init__(self)

        self.setupUi(self)
        
        self.selectItemWidget.hidePathEditor()
        self.setModal(True)
        self.selectItemWidget.repositoryModel = repositoryModel
        
    def _setSelectedIndex(self, index):
        """
        @see: L{<datafinder.gui.user.common.widget.select_item.SelectItemWidget.selectedIndex>}
        """
        
        self.selectItemWidget.selectedIndex = index
        
    def _getSelectedIndex(self):
        """
        @see: L{<datafinder.gui.user.common.widget.select_item.SelectItemWidget.selectedIndex>}
        """
        
        return self.selectItemWidget.selectedIndex

    selectedIndex = property(_getSelectedIndex, _setSelectedIndex)
    
    def _getHelpText(self):
        """ Returns the help text show in the specific label. """
        
        return unicode(self.helpTextLabel.text())

    def _setHelpText(self, text):
        """ Sets the help text show in the specific label. """
        
        return self.helpTextLabel.setText(text)

    helpText = property(_getHelpText, _setHelpText)
