# pylint: disable-msg=W0212,W0613,W0621,C0302
#
# Created: 04.02.2010 Patrick Schaefer <patrick.schaefer@dlr.de>
# Changed: $Id: item_support.py 4557 2010-03-22 09:22:42Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


"""
Module that supports simple item operations.
"""


from datafinder.core.error import CoreError, PropertyError, ItemError
from datafinder.core.repository_manager import repositoryManagerInstance
from datafinder.script_api.error import ItemSupportError
from datafinder.script_api.item.item_description import ItemDescription


__version__ = "$LastChangedRevision: 4557 $"

    
def refresh(path, stateOnly=False):
    """ 
    Resets the state of the item so that 
    its information is reloaded when accessed.
    
    @param path: The item to refresh.
    @type path: C{unicode}     
    @param itemStateOnly: If set it indicates that only the item 
                         state is refreshed but no structural information. Default is C{False}
    @type stateOnly: C{bool}
    """
    
    try:
        item = repositoryManagerInstance.workingRepository.getItem(path)
        item.refresh(stateOnly)
    except ItemError:
        raise ItemSupportError("Problem during refreshing.")


def createCollection(path, properties=None):
    """ 
    Creates a collection. 
        
    @param path: Path of the collection which should be created.
    @type path: C{unicode} 
    @param properties: Creation properties of the collection.
    @type properties: C{dict} of C{unicode}, C{object}
    
    @raise ItemSupportError: Raised when the collection could not be created.
    """
    
    try:
        childName, parentItemPath = __getChildParentPath(path)
        cwr = repositoryManagerInstance.workingRepository
        parentItem = cwr.getItem(parentItemPath)
        item = cwr.createCollection(childName, parentItem)
    except ItemError, error:
        raise ItemSupportError("Collection cannot be created.\nReason: '%s'" % error.message)
    else:
        __createItem(item, properties)

    
def createLeaf(path, properties=None):
    """
    Creates a leaf.
    
    @param path: Path of the leaf which should be created.
    @type path: C{unicode} 
    @param properties: Creation properties of the leaf.
    @type properties: C{dict} of C{unicode}, C{object}
    
    @raise ItemSupportError: Raised when the leaf could not be created.
    """
    
    try:
        childName, parentItemPath = __getChildParentPath(path)
        cwr = repositoryManagerInstance.workingRepository
        parentItem = cwr.getItem(parentItemPath)
        item = cwr.createLeaf(childName, parentItem)
    except ItemError, error:
        raise ItemSupportError("Leaf cannot be created.\nReason: '%s'" % error.message)
    else:
        __createItem(item, properties)


def createLink(path, linkTargetPath):
    """
    Creates a link.
    
    @param path: Path of the link which should be created.
    @type path: C{unicode} 
    @param linkTargetPath: Path of the item which is referenced by the link.
    @type linkTargetPath: C{unicode} 
       
    @raise ItemSupportError: Raised when the link could not be created.
    """
    
    try:
        childItemPath, parentItemPath = __getChildParentPath(path)
        cwr = repositoryManagerInstance.workingRepository
        parentItem = cwr.getItem(parentItemPath)
        targetItem = cwr.getItem(linkTargetPath)
        item = cwr.createLink(childItemPath, targetItem, parentItem)
    except ItemError, error:
        raise ItemSupportError("Link cannot be created.\nReason: '%s'" % error.message)
    else:
        __createItem(item)
    

def __createItem(item, properties=None):
    """
    Creates the given item object.

    @raise ItemSupportError: Raised when an error occurred.
    """
    
    try:
        mappedProperties = list()
        if not properties is None:
            for propertyIdentifier, value in properties.iteritems():
                mappedProperties.append(repositoryManagerInstance.workingRepository.createProperty(propertyIdentifier, value))
    except PropertyError, error:
        raise ItemSupportError("Invalid properties found.\nReason: %s" % error.message)
    else:
        try:
            item.create(mappedProperties)
        except ItemError, error:
            item.invalidate()
            raise ItemSupportError("Item cannot be created.\nReason: %s" % error.message)
    

def __getChildParentPath(path):
    """
    Returns the child name and parent path.
    
    @param path: The item path.
    @type path: C{unicode}
    
    @return: Child name and parent path
    @rtype: C{tuple}, C{unicode} C{unicode}  
    """
    
    if path.endswith("/"):
        path_ = path[:len(path)-1]
    else:
        path_ = path
    try:    
        if path_.rindex("/") == 0:
            parentItemPath = "/"
            childItemPath = path_[path_.rindex("/") + 1:]
        else:
            parentItemPath = path_[:path_.rindex("/")]
            childItemPath = path_[path_.rindex("/") + 1:]
    except ValueError:
        parentItemPath = "/"
        childItemPath = path_
    return childItemPath, parentItemPath


def delete(path):
    """
    Deletes the item. 
    
    @param path: Path to the item which has to be deleted.
    @type path: C{unicode}
    
    @raise ItemSupportError: Raised when the item could not be deleted.
    """
    
    try:
        item = repositoryManagerInstance.workingRepository.getItem(path)
    except ItemError:
        raise ItemSupportError("Item could not be found.")
    else:
        try:
            item.delete()
        except ItemError, error:
            raise ItemSupportError("Unable to delete item.\nReason: '%s'" % error.message)


def copy(sourcePath, targetPath):
    """
    Copies an item.
        
    @param sourcePath: Path of the source item.
    @type sourcePath: C{unicode} 
    @param targetPath: Path of the target item representing the copied item.
    @type targetPath: C{unicode}
    
    @raise ItemSupportError: Raised when an item cannot be copied. 
    """
        
    try:
        item, targetItem = __getItemHelper(sourcePath, targetPath) 
    except ItemError:
        raise ItemSupportError("One of the items cannot be found.")
    else:
        try:
            item.copy(targetItem)
        except ItemError, error:
            targetItem.invalidate()
            raise ItemSupportError("Item cannot be copied.\nReason: '%s'" % error.message)


def move(sourcePath, targetPath):
    """
    Moves an item.
        
    @param sourcePath: Path of the source item.
    @type sourcePath: C{unicode} 
    @param targetPath: Path of the target item representing the moved item.
    @type targetPath: C{unicode} 
    
    @raise ItemSupportError: Raised when an item cannot be moved.
    """
        
    try:
        item, targetItem = __getItemHelper(sourcePath, targetPath)
    except ItemError:
        raise ItemSupportError("One of the items cannot be found.")
    else:
        try:
            item.move(targetItem)
        except ItemError, error:
            targetItem.invalidate()
            raise ItemSupportError("Item cannot be moved.\nReason: '%s'" % error.message)


def __getItemHelper(sourcePath, targetPath):
    """
    Helper which fetches an item and an empty targetItem.
    
    @param sourcePath: The source item path.
    @type sourcePath: C{unicode} 
    @param targetPath: The target item path.
    @type targetPath: C{unicode}
    """
    
    cwr = repositoryManagerInstance.workingRepository
    item = cwr.getItem(sourcePath)
    childName, parentItemPath = __getChildParentPath(targetPath)
    parentItem = cwr.getItem(parentItemPath)
            
    if item.isCollection:
        targetItem = cwr.createCollection(childName, parentItem)
    elif item.isLeaf:
        targetItem = cwr.createLeaf(childName, parentItem)
    else: # isLink
        targetItem = cwr.createLink(childName, item.linkTarget, parentItem)
    return item, targetItem


def retrieveData(path):
    """
    Receives the data associated with this item.
    
    @param path: Path of the item form the data should be retrieved.
    @type path: C{unicode} 
        
    @return: Readable file-like object.
    
    @raise ItemSupportError: Raised when the data cannot be accessed.
    """
    
    try:
        item = repositoryManagerInstance.workingRepository.getItem(path)
    except ItemError:
        raise ItemSupportError("Item cannot be found.")
    else:
        try:
            return item.retrieveData()
        except ItemError, error:
            raise ItemSupportError("Cannot read item data.\nReason: '%s'" % error.message)


def storeData(path, fileObject):
    """
    Stores the data that has to be associated with this item.
    
    @param path: Path of the item where the data should be stored.
    @type path: C{unicode}  
    @param fileObj: File-like object that can be read from.
    
    @raise ItemSupportError: Raised when an error occurred.
    """
    
    try:
        item = repositoryManagerInstance.workingRepository.getItem(path)
    except ItemError:
        raise ItemSupportError("Item cannot be found.")
    else:
        try:
            item.storeData(fileObject)
        except ItemError, error:
            raise ItemSupportError("Cannot write data.\nReason: '%s'" % error.message)


def search(path, restrictions):
    """
    Search the given item path.

    @param path: Path of the item where the search should start.
    @type path: C{unicode}  
    @param restrictions: The search restrictions.
    @type restrictions: C{unicode}
    
    @return: List of items paths matching the given query.
    @rtype: C{list} of C{unicode}
    
    @raise ItemSupportError: Indicates problems while parsing the restrictions or executing the search. 
    """
    
    try:
        item = repositoryManagerInstance.workingRepository.getItem(path)
    except ItemError:
        raise ItemSupportError("Item cannot be found.")
    else:
        try:
            return [item.path for item in item.search(restrictions)]
        except CoreError, error:
            raise ItemSupportError("Problems during search occurred.\nReason:'%s'" % error.message)


def createArchive(path, targetPath, defaultProperties=None):
    """ Archives the given path. """
    
    cwr = repositoryManagerInstance.workingRepository
    try:
        item = cwr.getItem(path)
        targetItem = cwr.getItem(targetPath)
    except ItemError:
        raise ItemSupportError("One of the items has not been found.")
    else:
        try:
            mappedProperties = _mapProperties(defaultProperties, cwr)
            cwr.createArchive(item, targetItem, mappedProperties)
        except ItemError, error:
            errorMessage = "cannot archive item.\nReason:'%s'" % error.message
            raise ItemSupportError(errorMessage)


def performImport(sourcePath, targetParentPath, targetRepository, defaultProperties=None, copyData=True):
    """
    This method initiates the copy process and starts walking the source creating a
    new node in the destination tree for each item it passes.
        
    @param sourcePath: The item that should be imported.
    @type sourcePath: C{unicode}
    @param targetParentPath: The collection that should afterwards contain the copy.
    @type targetParentPath: C{unicode}
    @param targetRepository: The repository that should afterwards contain the copy.
    @type targetRepository: L{Repository<datafinder.script_api.repository.Repository>}
    @param defaultProperties: Optional properties which are set for every item. Default: C{None}
    @type defaultProperties: C{dict} of C{unicode},C{object}
    
    @raise ItemSupportError: Raised when errors during the import occur.
    """

    cwr = repositoryManagerInstance.workingRepository
    try:
        sourceItem = cwr.getItem(sourcePath)
        targetParentItem = targetRepository._repository.getItem(targetParentPath)
    except ItemError:
        raise ItemSupportError("One of the items cannot be found.")
    else:
        mappedProperties = _mapProperties(defaultProperties, cwr)
        try:
            targetItemName = targetRepository.determineUniqueItemName(sourceItem.name, targetParentPath)
            targetRepository._repository.performImport(sourceItem, targetParentItem, targetItemName, mappedProperties)  
        except ItemError, error:
            errorMessage = "Problems during import of the following item:\n"
            errorMessage += "\n" + sourceItem.path + "\nReason: " + error.message
            raise ItemSupportError(errorMessage)


def _mapProperties(properties, cwr):
    """ Converts the given properties. """
    
    mappedProperties = list()
    if not properties is None:
        for propertyIdentifier, value in properties.iteritems():
            try:
                mappedProperties.append(cwr.createProperty(propertyIdentifier, value))
            except PropertyError:
                continue
    return mappedProperties


def walk(path):
    """
    @param path: The item where the walk should start.
    @type path: C{unicode}
    
    @raise ItemSupportError: Raised when an error occurred.
    
    @see: L{walk<datafinder.core.item.visitor.base.ItemTreeWalkerBase.walk>} method to add further post-processing.
    """
    
    cwr = repositoryManagerInstance.workingRepository
    try:
        item = cwr.getItem(path)
    except ItemError:
        raise ItemSupportError("The requested item cannot be found.")
    else:
        return [item.path for item in cwr.walk(item)]


def itemDescription(path):
    """ 
    Returns the item description for the given item path.
        
    @param path: Path identifying the item.
    @type path: C{unicode}
        
    @return: Item description instance.
    @rtype: L{ItemDescription<datafinder.script_api.item.item_description.ItemDescription>}
    """
    
    try:
        item = repositoryManagerInstance.workingRepository.getItem(path)
    except ItemError:
        raise ItemSupportError("Problem during retrieval of the item.")
    else:
        return ItemDescription(item)


def getChildren(path):
    """ Determines the children of the given item. """
    
    try:
        item = repositoryManagerInstance.workingRepository.getItem(path)
    except ItemError:
        raise ItemSupportError("Problem during retrieval of the item.")
    else:
        try:
            children = item.getChildren()
        except ItemError, error:
            errorMessage = "Cannot determine children.\nReason: '%s'" % error.message
            raise ItemSupportError(errorMessage)
        else:
            return [item.path for item in children]
