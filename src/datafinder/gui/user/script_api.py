#
# Created: 07.03.2010 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: script_api.py 4578 2010-03-30 13:26:18Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Provides access to certain states of the user GUI.
"""


from PyQt4.QtGui import QDialog

from datafinder.gui.user.common.item_selection_dialog import ItemSelectionDialog
from datafinder.gui.user.common.progress_dialog import ProgressDialog
from datafinder.gui.user.models.repository.filter.leaf_filter import LeafFilter
from datafinder.script_api.repository import RepositoryDescription


__version__ = "$LastChangedRevision: 4578 $"


_context = None


def unmanagedRepositoryDescription():
    """ 
    Returns the context of the unmanaged repository.
    
    @return: Unmanaged repository descriptor.
    @rtype: L{RepositoryDescription<datafinder.script_api.repository.RepositoryDescription>}
    """
    
    return _context.unmanagedRepositoryDescription


def managedRepositoryDescription():
    """ 
    Returns the context of the managed repository.
    
    @return: Managed repository descriptor.
    @rtype: L{RepositoryDescription<datafinder.script_api.repository.RepositoryDescription>}
    """
    
    return _context.managedRepositoryDescription
        

def lock(paths, repositoryDescription=None):
    """ 
    Locks the given paths. Instead of the child
    items a place holder item ("...") is displayed until
    the specific path gets unlocked.
    
    @param paths: Paths of the items which should be locked.
    @type paths: C{unicode}
    @param repositoryDescription: Identifies the target repository.
    @type repositoryDescription: L{RepositoryDescription<datafinder.script_api.repository.RepositoryDescription>}
    """
    
    rm = _context.determineRepositoryModel(repositoryDescription)
    indexes = _context.determinesIndexes(rm, paths)
    rm.lock(indexes)


def unlock(paths, repositoryDescription=None):
    """ 
    Unlocks the given paths.
    
    @param paths: Paths of the items which should be unlocked.
    @type paths: C{unicode}
    @param repositoryDescription: Identifies the target repository.
    @type repositoryDescription: L{RepositoryDescription<datafinder.script_api.repository.RepositoryDescription>}
    """
    
    rm = _context.determineRepositoryModel(repositoryDescription)
    indexes = _context.determinesIndexes(rm, paths)
    for index in indexes:
        rm.unlock(index)


def currentSelection(repositoryDescription=None):
    """ 
    Returns paths of the current selected items. 
    
    @return: Paths of the selected items.
    @rtype: C{list} of C{unicode}
    @param repositoryDescription: Identifies the target repository.
    @type repositoryDescription: L{RepositoryDescription<datafinder.script_api.repository.RepositoryDescription>}
    """
    
    rc = _context.determineRepositoryController(repositoryDescription)
    paths = list()
    for index in rc.collectionController.selectedIndexes:
        if index.isValid():
            paths.append(index.model().nodeFromIndex(index).path)
    return paths


def currentCollection(repositoryDescription=None):
    """ 
    Returns the current active collection. 
    
    @return: Path of the current active collection.
    @rtype: C{unicode}
    @param repositoryDescription: Identifies the target repository.
    @type repositoryDescription: L{RepositoryDescription<datafinder.script_api.repository.RepositoryDescription>}
    """
    
    rm = _context.determineRepositoryModel(repositoryDescription)
    return rm.nodeFromIndex(rm.activeIndex).path


def selectItem(path, repositoryDescription=None):
    """
    Selects the item identified by the given path.
    
    @param path: Path of the item to select.
    @type path: C{unicode}
    @param repositoryDescription: Identifies the target repository.
    @type repositoryDescription: L{RepositoryDescription<datafinder.script_api.repository.RepositoryDescription>}
    """

    rm = _context.determineRepositoryModel(repositoryDescription)
    rm.activePath = path
    
    
def performWithProgressDialog(function, callback=None, 
                              windowTitle="Perform Script Action", 
                              labelText="Performing a script action in background..."):
    """
    Performs the given function and shows a nice progress dialog.
    Please make sure to perform no action changing GUI elements within this function.
    Moreover the locking and unlocking of items not be performed within this function.
    Cleaning up actions can be implemented in the given call back function.
    
    @param function: Function to perform.
    @type function: Callable without any arguments.
    @param callback: Function to perform clean up actions. Default: C{None}
    @type callback: Callable without any arguments.
    @param windowTitle: Title of the progress dialog. Default: C{Perform Script Action}
    @type windowTitle: C{unicode}
    @param labelText: Message shown in the progress dialog. Default: C{Performing a script action in background...}
    @type labelText: C{unicode}
    """

    if _context.progressDialog is None:
        _context.progressDialog = ProgressDialog(windowTitle, labelText)
    _context.progressDialog._cb = callback
    _context.progressDialog.start(function)


def getExistingCollection(repositoryDescription=None, helpText=""):
    """ 
    Shows a dialog allowing the selection of a collection and returns its path.
    When the dialog has been canceled by the user C{None} is returned.
    
    @param repositoryDescription: Identifies the target repository.
    @type repositoryDescription: L{RepositoryDescription<datafinder.script_api.repository.RepositoryDescription>}
    @param helpText: An optional information displayed in the dialog. Default: C{}
    @type helpText: C{unicode}
    """
    
    existingCollectionPath = None
    rm = _context.determineRepositoryModel(repositoryDescription)
    filteredRm = LeafFilter(rm)
    itemSelectionDialog = ItemSelectionDialog(filteredRm)
    itemSelectionDialog.selectedIndex = filteredRm.activeIndex
    itemSelectionDialog.helpText = helpText
    exitCode = itemSelectionDialog.exec_()
    
    if exitCode == QDialog.Accepted:
        existingCollectionPath = rm.nodeFromIndex(itemSelectionDialog.selectedIndex).path
    return existingCollectionPath


def getScriptExecutionContext():
    """
    Returns the repository description instance and
    the set of items selected on script action execution.
    
    @return: Script execution context.
    @rtype: L{ScriptExecutionContext<datafinder.gui.user.script_api.ScriptExecutionContext>}
    """
    
    scriptExecutionContext = None
    if not _context.scriptController.boundScriptExecutionContext is None:
        repository, items = _context.scriptController.boundScriptExecutionContext
        itemPaths = [item.path for item in items]
        scriptExecutionContext = ScriptExecutionContext(RepositoryDescription(repository), itemPaths)
    return scriptExecutionContext


class ScriptExecutionContext(object):
    """ Simple context object which contains the script execution context. """
    
    def __init__(self, repositoryDescription, itemPaths):
        """
        Constructor. 
        
        @param repositoryDescription: The description of the repository.
        @type: L{RepositoryDescription<datafinder.script_api.repository.RepositoryDescription>}
        @param itemPaths: Selected item paths in which context the script is executed.
        @type itemPaths: C{list} of C{unicode} 
        """
        
        self.repositoryDescription = repositoryDescription
        self.itemPaths = itemPaths
