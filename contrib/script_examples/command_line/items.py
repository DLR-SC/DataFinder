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
Demonstrates different items API functions.
"""


from StringIO import StringIO
import sys

from datafinder.script_api.repository import connectRepository, \
                                             getWorkingRepository, setWorkingRepository
from datafinder.script_api.item import item_support


__version__ = "$Revision-Id:$" 


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
