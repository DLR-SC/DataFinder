#
# $Filename$$
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
Implements the privilege dialog.
"""


from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QDialog, QDialogButtonBox

from datafinder.gui.user.dialogs.privilege_dialog.principal_search import PrincipalSearchController, \
                                                                          PrincipalSearchModel
from datafinder.gui.user.dialogs.privilege_dialog.inherited_privileges import InheritedPrivilegeModel, InheritedPrivilegeController
from datafinder.gui.user.dialogs.privilege_dialog.privileges import PrivilegeController, PrivilegeModel
from datafinder.gui.gen.user.privilege_dialog_ui import Ui_PrivilegeDialog


__version__ = "$Revision-Id$" 


class PrivilegeDialog(QDialog, Ui_PrivilegeDialog):
    """ Main controller of the privilege dialog. """
    
    _WINDOW_TITLE_TEMPLATE = "Editing Privileges of %s"
    
    def __init__(self, repositoryModel, parent=None):
        """ Constructor. 
        
        @param repositoryModel: The repository model.
        @type repositoryModel: L{<RepositoryModel>datafinder.gui.user.models.repository.repository.RepositoryModel} 
        @param parent: The parent object of the property dialog.
        @type parent: L{QWidget<PyQt4.QtGui.QWidget>}
        """
        
        QDialog.__init__(self, parent)
        Ui_PrivilegeDialog.__init__(self)
        self.setupUi(self)
        
        self._item = None
        self._repositoryModel = repositoryModel
        
        self._principalSearchModel = PrincipalSearchModel(self._repositoryModel)
        self._principalSearchController = PrincipalSearchController(self, self._principalSearchModel)
        self._privilegeModel = PrivilegeModel(self._repositoryModel)
        self._privilegeController = PrivilegeController(self, self._privilegeModel)
        self._inheritedPrivilegesModel = InheritedPrivilegeModel()
        self._inheritedPrivilegesController = InheritedPrivilegeController(self, self._repositoryModel, 
                                                                           self._inheritedPrivilegesModel)

        self.connect(self._principalSearchController, 
                     SIGNAL(self._principalSearchController.ADD_PRINCIPAL_SIGNAL),
                     self._privilegeController.addPrincipals)
        self.connect(self.buttonBox.button(QDialogButtonBox.Ok),
                     SIGNAL("clicked()"), self._privilegeController.applySlot)

    def _setItem(self, item):
        """ Setter for displayed item. """
        
        self._item = item
        self.setWindowTitle(self._WINDOW_TITLE_TEMPLATE % item.path)
        
        self._privilegeController.item = item
        self._inheritedPrivilegesController.item = item
        
        self.tabWidget.setCurrentIndex(0) # Selects the privilege editor tab
    
    def _getItem(self):
        """ Returns the current displayed item. """
        
        return self._item
    item = property(_getItem, _setItem)
