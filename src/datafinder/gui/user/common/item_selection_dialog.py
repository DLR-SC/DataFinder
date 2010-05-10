#
# Created: 12.10.2009 schlauch <Tobias.SChlauch@dlr.de>
# Changed: $Id: item_selection_dialog.py 4577 2010-03-30 09:27:39Z schlauch $ 
# 
# Copyright (c) 2009, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the dialog allowing selection of the collection which is searched. 
"""


from PyQt4 import QtGui

from datafinder.gui.gen.user.item_selection_dialog_ui import Ui_ItemSelectionDialog


__version__ = "$LastChangedRevision: 4577 $"


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
