# pylint: disable=W0212
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
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
This module implements unit tests for the item-based checks of the core layer. For now, only
checks done by L{SanityCheckTreeWalker<datafinder.core.item.visitor.checks.SanityCheckTreeWalker>}
are tested.
"""


import unittest

from datafinder.core.item.collection import ItemRoot, ItemCollection
from datafinder.core.item.data_persister import constants
from datafinder.core.item.leaf import ItemLeaf
from datafinder.core.item.link import ItemLink
from datafinder.core.item.privileges.privilege import ALL_PRIVILEGE
from datafinder.core.item.visitor.checks import ActionCheckVisitor, ActionCheckTreeWalker
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


class ActionCheckTestCase(unittest.TestCase):
    """
    Abstract base test class for both checkers of L{datafinder.core.item.visitor.checks}.
    """
    
    __checker__ = object
    
    def __init__(self, name):
        """
        Constructor.
        """
        
        unittest.TestCase.__init__(self, name)

    def setUp(self):
        """
        Set up a minimal item tree which has a root->collection[->leaf, ->link] structure.
        
        It uses the configuration attribute "__checker__" as the checker in charge.
        """
        # A sanity checker (tree walker)
        self.checker = self.__checker__(False, True, True)
        
        # A root for testing
        self.testRoot = ItemRoot("root")
        self.testRoot._privileges = [ALL_PRIVILEGE]
        self.testRoot._fileStorer = SimpleMock(list(), canAddChildren=True)
        self.testRoot._dataPersister = SimpleMock(self.testRoot.fileStorer, state=constants.ITEM_STATE_ACCESSIBLE)
        self.testRoot.itemFactory = SimpleMock(self.testRoot.fileStorer)
        self.testRoot.path = "/"
        # A collection for testing
        self.testNode = ItemCollection("collection")
        self.testNode._privileges = [ALL_PRIVILEGE]
        self.testNode._fileStorer = SimpleMock(list(), state=constants.ITEM_STATE_ARCHIVED)
        self.testNode.itemFactory = SimpleMock(self.testNode.fileStorer)
        self.testNode.parent = self.testRoot
        # A leaf for testing
        self.testLeaf = ItemLeaf("leaf")
        self.testLeaf._privileges = [ALL_PRIVILEGE]
        self.testLeaf._fileStorer = SimpleMock(list(), state=constants.ITEM_STATE_ACCESSIBLE)
        self.testLeaf.itemFactory = SimpleMock(self.testLeaf.fileStorer)
        self.testLeaf.parent = self.testNode
        # A link for testing
        self.testLink = ItemLink("link")
        self.testLink._privileges = [ALL_PRIVILEGE]
        self.testLink._fileStorer = SimpleMock(list())
        self.testLink.itemFactory = SimpleMock(self.testLink.fileStorer)
        self.testLink.parent = self.testNode
        self.testLink._linkTarget = self.testRoot


class ActionCheckVisitorTestCase(ActionCheckTestCase):
    """
    Test case for L{ActionCheckVisitor<datafinder.core.item.visitor.checks.ActionCheckVisitor>}.
    """
    
    __checker__ = ActionCheckVisitor
    
    def testAllFine(self):
        """
        Simply compares if the resulting constraints match the expectations.
        """
        
        # Root
        self.checker.check(self.testRoot)
        self.assertTrue(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_ADD_CHILDREN])
        self.assertFalse(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_DELETE])
        self.assertFalse(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_COPY])
        self.assertFalse(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_MOVE])
        self.assertFalse(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_STORE])
        self.assertFalse(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_RETRIEVE])
        self.assertFalse(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_ARCHIVE])
        self.assertEquals(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_SEARCH], self.checker._hasSearchSupport)
        self.assertFalse(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_RETRIEVE_PROPERTIES])
        self.assertFalse(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_STORE_PROPERTIES])
        # Collection is archived
        self.checker.check(self.testNode)
        self.assertTrue(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_ADD_CHILDREN]) # it is an archive
        self.assertTrue(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_DELETE])
        self.assertTrue(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_COPY])
        self.assertTrue(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_MOVE])
        self.assertTrue(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_STORE])
        self.assertTrue(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_RETRIEVE])
        self.assertFalse(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_ARCHIVE])
        self.assertEquals(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_SEARCH], self.checker._hasSearchSupport)
        self.assertEquals(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_RETRIEVE_PROPERTIES], 
                          self.checker._hasCustomMetadataSupport)
        self.assertFalse(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_STORE_PROPERTIES])  # it is an archive
    
    def testCanCreate(self):
        """
        Tests the C{canAddChildren} check.
        """
        
        self.assertTrue(self.checker.canAddChildren(self.testRoot))
        self.assertTrue(self.checker.canAddChildren(self.testNode)) # it is an archive
        self.assertTrue(self.checker.canAddChildren(self.testLeaf))
    
    def testCanDelete(self):
        """ Tests the C{canDelete} check. """
        
        self.assertFalse(self.checker.canDelete(self.testRoot))
        self.assertTrue(self.checker.canDelete(self.testNode))
        self.assertTrue(self.checker.canDelete(self.testLeaf))
    
    def testCanCopy(self):
        """
        Tests the C{canCopy} check.
        """
        
        self.assertFalse(self.checker.canCopy(self.testRoot))
        self.assertTrue(self.checker.canCopy(self.testNode))
        self.assertTrue(self.checker.canCopy(self.testLeaf))
    
    def testCanMove(self):
        """
        Tests the C{canMove} check.
        """
        
        self.assertFalse(self.checker.canMove(self.testRoot))
        self.assertTrue(self.checker.canMove(self.testNode))
        self.assertTrue(self.checker.canMove(self.testLeaf))
    
    def testCanStoreData(self):
        """
        Tests the C{canStoreData} check.
        """
        
        self.assertFalse(self.checker.canStoreData(self.testRoot))
        self.assertTrue(self.checker.canStoreData(self.testNode))
        self.assertTrue(self.checker.canStoreData(self.testLeaf))
    
    def testCanRetrieveData(self):
        """
        Tests the C{canRetrieveData} check.
        """
        
        self.assertFalse(self.checker.canRetrieveData(self.testRoot))
        self.assertTrue(self.checker.canRetrieveData(self.testNode))
        self.assertTrue(self.checker.canRetrieveData(self.testLeaf))
    
    def testCanArchive(self):
        """
        Tests the C{canArchive} check.
        """
        
        self.assertFalse(self.checker.canArchive(self.testRoot))
        self.assertFalse(self.checker.canArchive(self.testNode))
        self.assertFalse(self.checker.canArchive(self.testLeaf))  # only collections can be archived
    
    def testCanSearch(self):
        """
        Tests the C{canSearch} check.
        """
        
        self.assertEquals(self.checker.canSearch(self.testRoot), self.checker._hasSearchSupport)
        self.assertEquals(self.checker.canSearch(self.testNode), self.checker._hasSearchSupport)
        self.assertEquals(self.checker.canSearch(self.testLeaf), self.checker._hasSearchSupport)
    
    def testCanRetrieveProperties(self):
        """
        Tests the C{canRetrieveProperties} check.
        """
        
        self.assertFalse(self.checker.canRetrieveProperties(self.testRoot))
        self.assertEquals(self.checker.canRetrieveProperties(self.testNode), self.checker._hasCustomMetadataSupport)
        self.assertEquals(self.checker.canRetrieveProperties(self.testLeaf), self.checker._hasCustomMetadataSupport)
    
    def testCanStoreProperties(self):
        """
        Tests the C{canStoreProperties} check.
        """
        
        self.assertFalse(self.checker.canStoreProperties(self.testRoot))
        self.assertEquals(self.checker.canStoreProperties(self.testNode), False) # it is an archive
        self.assertEquals(self.checker.canStoreProperties(self.testLeaf), self.checker._hasCustomMetadataSupport)
    
    
class ActionCheckTreeWalkerTestCase(ActionCheckTestCase):
    """
    Test case for L{ActionCheckTreeWalker<datafinder.core.item.visitor.checks.ActionCheckTreeWalker>}.
    """
    
    __checker__ = ActionCheckTreeWalker
    
    def testAllFine(self):
        """ Simply compares if the resulting constraints match the expectations. """
        
        # Only check root as it inherits attributes from children
        self.checker.check(self.testRoot)
        self.assertTrue(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_ADD_CHILDREN])
        self.assertFalse(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_DELETE])
        self.assertFalse(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_COPY])
        self.assertFalse(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_MOVE])
        self.assertFalse(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_STORE])
        self.assertFalse(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_RETRIEVE])
        self.assertFalse(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_ARCHIVE])
        self.assertEquals(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_SEARCH], self.checker._hasSearchSupport)
        self.assertFalse(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_RETRIEVE_PROPERTIES])
        self.assertFalse(self.checker.capabilities[ActionCheckTreeWalker.CAPABILITY_STORE_PROPERTIES])
    
    def testCanCreate(self):
        """ Tests the C{canAddChildren} check. """
        
        self.assertTrue(self.checker.canAddChildren(self.testRoot))
        self.assertTrue(self.checker.canAddChildren(self.testNode)) # it is an archive
        self.assertTrue(self.checker.canAddChildren(self.testLeaf))
    
    def testCanDelete(self):
        """ Tests the C{canDelete} check. """
        
        self.assertFalse(self.checker.canDelete(self.testRoot))
        self.assertTrue(self.checker.canDelete(self.testNode))
        self.assertTrue(self.checker.canDelete(self.testLeaf))
    
    def testCanCopy(self):
        """ Tests the C{canCopy} check. """
        
        self.assertFalse(self.checker.canCopy(self.testRoot))
        self.assertTrue(self.checker.canCopy(self.testNode))
        self.assertTrue(self.checker.canCopy(self.testLeaf))
    
    def testCanMove(self):
        """ Tests the C{canMove} check. """
        
        self.assertFalse(self.checker.canMove(self.testRoot))
        self.assertTrue(self.checker.canMove(self.testNode))
        self.assertTrue(self.checker.canMove(self.testLeaf))
    
    def testCanStoreData(self):
        """ Tests the C{canStoreData} check. """
        
        self.assertFalse(self.checker.canStoreData(self.testRoot))
        self.assertTrue(self.checker.canStoreData(self.testNode))
        self.assertTrue(self.checker.canStoreData(self.testLeaf))
    
    def testCanRetrieveData(self):
        """ Tests the C{canRetrieveData} check. """
        
        self.assertFalse(self.checker.canRetrieveData(self.testRoot))
        self.assertTrue(self.checker.canRetrieveData(self.testNode))
        self.assertTrue(self.checker.canRetrieveData(self.testLeaf))
    
    def testCanArchive(self):
        """ Tests the C{canArchive} check. """
        
        self.assertFalse(self.checker.canArchive(self.testRoot))
        self.assertFalse(self.checker.canArchive(self.testNode))
        self.assertFalse(self.checker.canArchive(self.testLeaf)) # only collections can be archived

    def testCanSearch(self):
        """
        Tests the C{canSearch} check.
        """
        
        self.assertEquals(self.checker.canSearch(self.testRoot), self.checker._hasSearchSupport)
        self.assertEquals(self.checker.canSearch(self.testNode), self.checker._hasSearchSupport)
        self.assertEquals(self.checker.canSearch(self.testLeaf), self.checker._hasSearchSupport)
    
    def testCanRetrieveProperties(self):
        """
        Tests the C{canRetrieveProperties} check.
        """
        
        self.assertFalse(self.checker.canRetrieveProperties(self.testRoot))
        self.assertEquals(self.checker.canRetrieveProperties(self.testNode), self.checker._hasCustomMetadataSupport)
        self.assertEquals(self.checker.canRetrieveProperties(self.testLeaf), self.checker._hasCustomMetadataSupport)
    
    def testCanStoreProperties(self):
        """
        Tests the C{canStoreProperties} check.
        """
        
        self.assertFalse(self.checker.canStoreProperties(self.testRoot))
        self.assertEquals(self.checker.canStoreProperties(self.testNode), self.checker._hasCustomMetadataSupport)
        self.assertEquals(self.checker.canStoreProperties(self.testLeaf), self.checker._hasCustomMetadataSupport)
    
    def testAffectedItems(self):
        """ Checks the the C{affectedItems} attribute. """
        
        self.checker.check(self.testRoot)
        self.assertEquals(len(self.checker.affectedItems), 3)
        self.checker.check(self.testNode)
        self.assertEquals(len(self.checker.affectedItems), 2)
        self.checker.check(self.testLeaf)
        self.assertEquals(len(self.checker.affectedItems), 0)
        self.checker.check(self.testLink)
        self.assertEquals(len(self.checker.affectedItems), 0)
