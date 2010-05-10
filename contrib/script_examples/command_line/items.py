#
# Created: 21.03.2010 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: items.py 4554 2010-03-21 11:58:03Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Demonstrates different items API functions.
"""


from StringIO import StringIO
import sys

from datafinder.script_api.repository import connectRepository, \
                                             getWorkingRepository, setWorkingRepository
from datafinder.script_api.item import item_support


__version__ = "$LastChangedRevision: 4554 $"


def unmanagedRepository(basePath):
    """ Demonstrates the script API using the local file system as unmanaged repository. """
    
    print "Connecting repository file:///..."
    repository = connectRepository("file:///")
    setWorkingRepository(repository)
    assert repository == getWorkingRepository()
    
    print "\nChecking base path and creating children..."
    print item_support.itemDescription(basePath)
    item_support.refresh(basePath)
    print item_support.getChildren(basePath)
    
    collectionPath = basePath + "/collection"
    item_support.createCollection(collectionPath)
    print item_support.itemDescription(collectionPath)
    
    leafPath = basePath + "/leaf"
    item_support.createLeaf(leafPath)
    item_support.storeData(leafPath, StringIO("some data..."))
    print item_support.itemDescription(leafPath)
    print "Put in the following data:"
    fileObject = item_support.retrieveData(leafPath)
    print fileObject.read()
    fileObject.close()
    
    linkPath = basePath + "/link.lnk"
    item_support.createLink(linkPath, collectionPath)
    print item_support.itemDescription(linkPath)
    
    print item_support.getChildren(basePath)
    
    print "\nCopy and move some things..."
    copyLeafPath = collectionPath + "/leaf_copy"
    item_support.copy(leafPath, copyLeafPath)
    print item_support.getChildren(collectionPath)
    item_support.move(copyLeafPath, collectionPath + "/leaf")
    print item_support.getChildren(collectionPath)
    
    print "\nArchiving everything..."
    item_support.createArchive(basePath, collectionPath)
    
    print "\nWalking the base path..."
    print item_support.walk(basePath)
    
    print "\nCleaning up..."
    for path in [collectionPath, leafPath, linkPath]:
        item_support.delete(path)
    print item_support.walk(basePath)
    
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Call: items.py basePath"
    else:
        basePath_ = unicode(sys.argv[1])
        unmanagedRepository(basePath_)
