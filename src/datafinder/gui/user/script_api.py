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


from datafinder.gui.user.common.progress_dialog import ProgressDialog


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
        

def lock(paths):
    """ 
    Locks the given paths. Instead of the child
    items a place holder item ("...") is displayed until
    the specific path gets unlocked.
    
    @param paths: Paths of the items which should be locked.
    @type paths: C{unicode}
    """
    
    rm = _context.determineRepositoryModel()
    indexes = _context.determinesIndexes(rm, paths)
    rm.lock(indexes)


def unlock(paths):
    """ 
    Unlocks the given paths.
    
    @param paths: Paths of the items which should be unlocked.
    @type paths: C{unicode}
    """
    
    rm = _context.determineRepositoryModel()
    indexes = _context.determinesIndexes(rm, paths)
    for index in indexes:
        rm.unlock(index)


def currentSelection():
    """ 
    Returns paths of the current selected items. 
    
    @return: Paths of the selected items.
    @rtype: C{list} of C{unicode}
    """
    
    rc = _context.determineRepositoryController()
    paths = list()
    for index in rc.collectionController.selectedIndexes:
        if index.isValid():
            paths.append(index.model().nodeFromIndex(index).path)
    return paths


def currentCollection():
    """ 
    Returns the current active collection. 
    
    @return: Path of the current active collection.
    @rtype: C{unicode}
    """
    
    rm = _context.determineRepositoryModel()
    return rm.nodeFromIndex(rm.activeIndex).path


def selectItem(path):
    """
    Selects the item identified by the given path.
    
    @param path: Path of the item to select.
    @type path: C{unicode}
    """

    rm = _context.determineRepositoryModel()
    rm.activePath = path
    
    
def performWithProgressDialog(function, callback=None):
    """
    Performs the given function and shows a nice progres dialog.
    Please make sure to perform no action changing GUI elements within this function.
    Moreover the locking and unlocking of items not be performed within this function.
    Cleaning up actions can be implemented in the given call back function.
    
    @param function: Function to perform.
    @type function: Callable without any arguments.
    @param callback: Function to perform clean up actions.
    @type callback: Callable without any arguments.
    """

    if _context.progressDialog is None:
        _context.progressDialog = ProgressDialog("Perform Script Action", "Performing a script action in background...")
    _context.progressDialog._cb = callback
    _context.progressDialog.start(function)
