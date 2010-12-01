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
Handles the scripts.
"""


import logging
import operator

from PyQt4 import QtCore, QtGui

from datafinder.core.error import ConfigurationError
from datafinder.core.configuration.scripts.constants import LOCAL_SCRIPT_LOCATION
from datafinder.core.configuration.scripts.script import createScript
from datafinder.gui.user.common.item_selection_dialog import ItemSelectionDialog
from datafinder.gui.user.models.repository.filter.property_filter import PropertyFilter
from datafinder.gui.user.common.widget.widget import ActionTooltipMenu


__version__ = "$Revision-Id:$" 


class ScriptController(object):
    """ Controls script management. """
    
    _logger = logging.getLogger()

    _REMOVE_TOOLTIP = "Removes script extension '%s'."
    _PREFERENCES_TOOLTIP = "Configures script extension '%s'."
    _USE_TOOLTIP = "Starts script extension '%s'.\n\nAvailability: %s\n\nDetails: %s"
                      
    _USE_TOOLTIP_TYPE = 0
    _REMOVE_TOOLTIP_TYPE = 1
    _PREFERENCES_TOOLTIP_TYPE = 2
    
    _SCRIPT_COLLECTION_ICON = None
    _PREFERENCES_ICON = None
    _SCRIPT_ICON = None
    

    def __init__(self, scriptRegistry, repositoryModel, mainWindow):
        """ Constructor. """
        
        self._scriptRegistry = scriptRegistry
        self._repositoryModel = repositoryModel
        self._mainWindow = mainWindow
        self._addScriptAction = mainWindow.addScriptAction
        self._removeScriptMenu = mainWindow.removeScriptMenu
        self._useLocalScriptMenu = mainWindow.useLocalScriptMenu
        self._useSharedScriptMenu = mainWindow.useSharedScriptMenu
        self._scriptPreferencesMenu = mainWindow.scriptPreferencesMenu
        self._useScriptMenu = mainWindow.useScriptAction

        self._boundScriptActions = set()
        self._dataFormatScriptActionMap = dict()
        self._dataTypeScriptActionMap = dict()
        self._sharedScriptRemovalSlots = list()
        self._currentActions = list()
        self._boundScriptExecutionContext = None
        filterModel = PropertyFilter(self._repositoryModel, allowedItemNameSuffixes=[".py", ".tar"])
        self._itemSelectionDialog = ItemSelectionDialog(filterModel, self._mainWindow)
        self._itemSelectionDialog.helpText = "Select a single Python script or Tar Archive."
        self._itemSelectionDialog.setWindowTitle("Add Script")
        
        QtCore.QObject.connect(self._addScriptAction, QtCore.SIGNAL("triggered()"), self._addScriptSlot)
        
        self.__class__._SCRIPT_COLLECTION_ICON = QtGui.QIcon(QtGui.QPixmap(":/icons/icons/package24.png"))
        self.__class__._PREFERENCES_ICON = QtGui.QIcon(QtGui.QPixmap(":/icons/icons/preferences24.png"))
        self.__class__._SCRIPT_ICON = QtGui.QIcon(QtGui.QPixmap(":/icons/icons/lightning_bolt24.png"))
    
    def load(self):
        """ Initializes the scripts menu. """
        
        scripts = self._scriptRegistry.getScripts(LOCAL_SCRIPT_LOCATION)
        scripts.sort(cmp=lambda x,y: cmp(x.lower(),y.lower()), 
                     key=operator.attrgetter("title"))
        for script in scripts:
            self._addScript(script)

    def _addScript(self, script, isLocal=True):
        """ Adds the corresponding actions for the given script. """
         
        useScriptMenu = self._useLocalScriptMenu
        if not isLocal:
            useScriptMenu = self._useSharedScriptMenu
        if hasattr(script, "scripts"):
            scriptCollectionMenu = ActionTooltipMenu(useScriptMenu)
            scriptCollectionMenu.setIcon(self._SCRIPT_COLLECTION_ICON)
            scriptCollectionMenu.setTitle(script.title)
            useScriptMenu.addMenu(scriptCollectionMenu)
            scripts = list()
            for script_ in script.scripts:
                action = self._createAction(scriptCollectionMenu, script_.name, 
                                            self._createUseScriptSlot(script_), self._determineScriptTooltip(script_))
                scripts.append((script_, action))
            self._registerScripts(scripts)
            useScriptAction = scriptCollectionMenu.menuAction()
        else:
            useScriptAction = self._createAction(useScriptMenu, script.title, 
                                                 self._createUseScriptSlot(script), self._determineScriptTooltip(script))
            self._registerScripts([(script, useScriptAction)])
            
        preferencesAction = None
        if hasattr(script, "hasPreferences"):
            if script.hasPreferences:
                preferencesAction = self._createAction(self._scriptPreferencesMenu, "Configure " + script.title + "...",
                                                       self._createPreferencesSlot(script),
                                                       self._determineScriptTooltip(script, self._PREFERENCES_TOOLTIP_TYPE),
                                                       self._PREFERENCES_ICON)

        if isLocal:
            removeActionIcon = self._SCRIPT_ICON
            if hasattr(script, "scripts"):
                removeActionIcon = self._SCRIPT_COLLECTION_ICON
            removeScriptAction = self._createAction(self._removeScriptMenu, script.title, None,
                                                    self._determineScriptTooltip(script, self._REMOVE_TOOLTIP_TYPE), removeActionIcon)
            self._connectAction(removeScriptAction, self._createRemoveScriptSlot(script, useScriptMenu, useScriptAction, 
                                                                                 removeScriptAction, preferencesAction))
        else:
            removeScriptSlot = self._createRemoveScriptSlot(script, useScriptMenu, useScriptAction, None, preferencesAction)
            self._sharedScriptRemovalSlots.append(removeScriptSlot)
            
    def _createAction(self, parentMenu, name, slot=None, toolTip=None, icon=None):
        """ Creates the requested action. """
        
        action = QtGui.QAction(name, parentMenu)
        parentMenu.addAction(action)
        if not slot is None:
            self._connectAction(action, slot)
        if not toolTip is None:
            action.setToolTip(toolTip)
        if icon is None:
            icon = self._SCRIPT_ICON
        action.setIcon(icon)
        return action
    
    @staticmethod
    def _connectAction(action, slot):
        """ Connects the given action. """
        
        QtCore.QObject.connect(action, QtCore.SIGNAL("triggered()"), slot)

    def _determineScriptTooltip(self, script, whichTooltip=_USE_TOOLTIP_TYPE):
        """ Determines the tool tip text for the given type. """
        
        if whichTooltip == self._USE_TOOLTIP_TYPE:
            availability = ""
            if len(script.dataformats) > 0:
                availability += "\nData Formats: "
                for dataFormatName in script.dataformats:
                    availability += dataFormatName 
                    if dataFormatName != script.dataformats[-1]:
                        availability += ","
            if len(script.datatypes) > 0:
                availability += "\nData Types: "
                for dataTypeName in script.datatypes:
                    availability += dataTypeName
                    if dataTypeName != script.datatypes[-1]:
                        availability += ","
            if len(script.dataformats) == 0 and len(script.datatypes) == 0:
                availability = "Common Script Extension"
            description = script.description or "No details available."
            tooltip = self._USE_TOOLTIP % (script.title, availability, description)
        elif whichTooltip == self._REMOVE_TOOLTIP_TYPE:
            tooltip = self._REMOVE_TOOLTIP % (script.title)
        else:
            tooltip = self._PREFERENCES_TOOLTIP % (script.title)
        return tooltip
    
    def _registerScripts(self, scripts):
        """ Registers the given scripts and script actions so that they can be easily queried later. """
        
        for script, scriptAction in scripts:
            for dataFormatName in script.dataformats:
                self._dataFormatScriptActionMap.setdefault(dataFormatName, list()).append(scriptAction)
        
            for dataTypeName in script.datatypes:
                self._dataTypeScriptActionMap.setdefault(dataTypeName, list()).append(scriptAction)
        
            if script.isBound:
                self._boundScriptActions.add(scriptAction)
                scriptAction.setEnabled(False)
        
    def _createUseScriptSlot(self, script):
        """ Creates a handler allowing usage of the given script. """
        
        def _useScriptCallback():
            """ Executes the script and handles errors. """

            if not script.isBound: # general scripts do not gave specific execution context
                boundScriptExecutionContext = self._boundScriptExecutionContext
                self._boundScriptExecutionContext = None
            try:
                script.execute()
            except ConfigurationError, error:
                QtGui.QMessageBox.critical(self._mainWindow,
                                           "Problems on usage of script '%s'..." % script.title,
                                           "The following problem occurred:\n'%s'" % error.message)
            if not script.isBound: # reset the context
                self._boundScriptExecutionContext = boundScriptExecutionContext
        return _useScriptCallback
    
    def _createRemoveScriptSlot(self, script, useScriptMenu, useAction, removeAction, preferencesAction):
        """ Creates a handler allowing removal of the given script. """
        
        def _removeScriptCallback():
            """ Removes the script from registry and the corresponding action from the menus. """
            
            self._scriptRegistry.unregister(script.location, script)
            
            useScriptMenu.removeAction(useAction)
            for actionContainer in [[self._boundScriptActions], 
                                    self._dataFormatScriptActionMap.values(), 
                                    self._dataTypeScriptActionMap.values()]:
                for actions in actionContainer:
                    if useAction in actions:
                        actions.remove(useAction)
            if not removeAction is None:
                self._removeScriptMenu.removeAction(removeAction)
            if not preferencesAction is None:
                self._scriptPreferencesMenu.removeAction(preferencesAction)
        return _removeScriptCallback
    
    def _createPreferencesSlot(self, script):
        """ Creates a handler allowing display of the script preferences. """
        
        def _preferencesCallback():
            """ Shows the preference page and handles errors. """
            
            try:
                script.executePreferences()
            except ConfigurationError, error:
                QtGui.QMessageBox.critical(self._mainWindow,
                                           "Problems on showing preferences of script '%s'..." % script.title,
                                           "The following problem occurred:\n'%s'" % error.message)
        return _preferencesCallback
            
    def _addScriptSlot(self):
        """ Handles the local script import. """
        
        self._itemSelectionDialog.selectedIndex = self._repositoryModel.activeIndex
        self._itemSelectionDialog.exec_()
        item = self._repositoryModel.nodeFromIndex(self._itemSelectionDialog.selectedIndex)
        if item.isLeaf:
            try:
                script = createScript(item.fileStorer)
            except ConfigurationError, error:
                errorMessage = "Cannot add script '%s'.\nReason:%s" % (item.uri, error.message)
                self._logger.error(errorMessage)
            else:
                self._scriptRegistry.register(LOCAL_SCRIPT_LOCATION, [script])
                self._addScript(script)

    def scriptsAvailable(self, dataFormatNames, dataTypeNames, context):
        """
        Enables bound (to data type or data format) scripts extensions and
        returns whether those script extension are available at all.
        
        @param dataFormatNames: List of data format names to look for scripts.
        @type: dataFormatNames: C{list} of C{unicode}
        @param dataTypeNames: List of data format names to look for scripts.
        @type: dataTypeNames: C{list} of C{unicode}
        @context: Returns the current set of items used on script execution. 
        @context: C{tuple} of L{Repository<datafinder.core.repository.Repository>}, 
                              C{list} of L{ItemBase<datafinder.core.item.base.ItemBase>}
    
        @return: Flag indicating availability of those actions.
        @rtype: C{bool}
        """
        
        scriptsAvailable = False
        if len(dataFormatNames) > 0 or len(dataTypeNames) > 0:
            self._boundScriptExecutionContext = context
            actions = self._boundScriptActions
            for dataFormatName in dataFormatNames:
                actions = actions & set(self._dataFormatScriptActionMap.get(dataFormatName, list()))
            for dataTypeName in dataTypeNames:
                actions = actions & set(self._dataTypeScriptActionMap.get(dataTypeName, list()))
            self._setCurrentActions(list(actions))
            scriptsAvailable = len(actions) > 0
        return scriptsAvailable
    
    def _setCurrentActions(self, useScriptActions):
        """ Sets currently used script actions and disables the remaining ones. """
        
        self._currentActions = useScriptActions
        self._currentActions.sort(cmp=lambda x,y: cmp(x.toLower(),y.toLower()), 
                                  key=operator.methodcaller("text"))
        for action in self._boundScriptActions:
            action.setEnabled(action in self._currentActions)
        self._useScriptMenu.clear()
        self._useScriptMenu.addActions(self._currentActions)
    
    def clearUseScriptMenu(self):
        """ Clears the current usable actions. """

        self._setCurrentActions(list())

    def loadSharedScripts(self, scripts):
        """
        Adds the given shared scripts to the script menus.
        
        @param scripts: Scripts that should be added.
        @type scripts: C{list} of L{Script<datafinder.core.configuration.scripts.script.Script>}/
                                  L{ScriptCollection<datafinder.core.configuration.scripts.script.ScriptCollection>}
        """
        
        self._useSharedScriptMenu.setEnabled(True)
        scripts.sort(cmp=lambda x,y: cmp(x.lower(),y.lower()), 
                     key=operator.attrgetter("title"))
        for script in scripts:
            self._addScript(script, False)
            
    def clearSharedScripts(self):
        """ Removes the registered shared scripts. """
        
        for removeScriptSlot in self._sharedScriptRemovalSlots:
            removeScriptSlot()
        self._sharedScriptRemovalSlots = list()
        self._useSharedScriptMenu.setEnabled(False)
        
    @property
    def useScriptMenu(self):
        """ The use script menu containing the current active actions """
        
        return self._useScriptMenu

    @property
    def boundScriptExecutionContext(self):
        """  
        @return: Returns the current set of items used on script execution. 
        @rtype: C{tuple} of L{Repository<datafinder.core.repository.Repository>}, 
                            C{list} of L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        return self._boundScriptExecutionContext
