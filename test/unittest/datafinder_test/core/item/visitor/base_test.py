#pylint: disable=R0201,W0612
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
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
Test case for the ItemVisitorBase and ItemTreeWalkerBase classes.
"""


import unittest

from datafinder.core.item.base import ItemBase
from datafinder.core.item.collection import ItemRoot, ItemCollection
from datafinder.core.item.leaf import ItemLeaf
from datafinder.core.item.link import ItemLink
from datafinder.core.item.visitor.base import ItemTreeWalkerBase, VisitSlot
from datafinder_test.mocks import SimpleMock

__version__ = "$Revision-Id:$" 

class _TestItem(object):
    """
    Simple class definition to test failure of visitor class.
    """
    
    def __init__(self):
        """ Constructor. """
        pass

class _TestItemVisitor(object):
    """
    Mock visitor to test L{ItemVisitorBase<datafinder.core.item.visitor.base.ItemVisitorBase>}.
    
    Two visit slots are defined: C{test1} and C{test2} both of which only have a valid implementation
    for L{SimpleMock<datafinder_test.mocks.SimpleMock>}.
    """
    
    def test1ReturnsNodeValue(self, node):
        """
        Visitor slot implementation for C{SimpleMock}.
        
        @param node: The visited node.
        @type node: C{SimpleMock}
        
        @return: The value of the node (C{node.value}).
        """
        return node.value
    test1ReturnsNodeValue.accept = SimpleMock,
    
    def test1ReturnsFalse(self, _):
        """
        Visitor slot implementation for C{_FailTestItem}.
        
        @param node: The visited node.
        @type node: C{SimpleMock}
        
        @return: C{False}
        """
        return False
    test1ReturnsFalse.accept = _TestItem,

    test1 = VisitSlot(test1ReturnsNodeValue, test1ReturnsFalse)
    
    def test2ChecksNodeValueForPara(self, node, para):
        """
        Visitor slot implementation for C{SimpleMock} with extra parameter which is compared to
        the mocks value.
        
        @param node: The visited node.
        @type node: C{SimpleMock}
        @param para: A parameter to be passed.
        @type para: Boolean
        
        @return: Returns whether the node value (C{node.value}) equals the given
                 parameter.
        @rtype: Boolean
        """
        return node.value == para
    test2ChecksNodeValueForPara.accept = SimpleMock,
    
    test2 = VisitSlot(test2ChecksNodeValueForPara)

class _DerivedTestItemVisitor(_TestItemVisitor, object):
    def test1Overridden(self, _):
        return False
    test1Overridden.accept = SimpleMock,
    
    test1 = VisitSlot(test1Overridden, inherits="test1")
    
    def test2Hidden(self, node, para):
        return node.value == para
    test2Hidden.accept = _TestItem,
    
    test2 = VisitSlot(test2Hidden)

class ItemVisitorBaseTestCase(unittest.TestCase):
    """
    Test case for L{ItemVisitorBase<datafinder.core.item.visitor.base.ItemVisitorBase>}.
    """
    
    def setUp(self):
        """
        Unittest setup. Initializes an C{SimpleMock}, an C{_FailTestItem} and a
        C{_TestItemVisitor} for later use in the tests.
        """
        self.mockItem = SimpleMock(True)
        self.testItem = _TestItem()
        self.visitor = _TestItemVisitor()
        self.visitor2 = _DerivedTestItemVisitor()

    def testAllFine(self):
        """
        These test simply check whether calling a visitor slot works with and without parameters.
        """
        self.assertTrue(self.visitor.test1(self.mockItem))
        self.assertTrue(self.visitor.test2(self.mockItem, True))
        self.assertFalse(self.visitor.test2(self.mockItem, False))
    
    def testDispatch(self):
        """
        This method checks whether the slots really only respond to the data they
        are registered for.
        """
        self.assertTrue(self.visitor.test1(self.mockItem))
        self.assertFalse(self.visitor.test1(self.testItem))
        self.assertRaises(TypeError, self.visitor.test2, self.mockItem) # too less parameters
        self.assertTrue(self.visitor.test2(self.mockItem, True))
        self.assertRaises(AttributeError, self.visitor.test2, self.testItem) # no valid slot
        self.assertFalse(self.visitor2.test1(self.mockItem))
        self.assertFalse(self.visitor2.test1(self.testItem))
        self.assertRaises(AttributeError, self.visitor2.test2, self.mockItem)

class _TestItemTreeWalker(ItemTreeWalkerBase):
    """
    Mock tree walker class to test
    L{ItemTreeWalkerBase<datafinder.core.item.visitor.base.ItemTreeWalkerBase>}.
    """
    
    def __init__(self, mode=-1):
        """
        Constructor.
        """
        ItemTreeWalkerBase.__init__(self, mode=mode)
        self.sequence = list()
    
    def reset(self):
        """
        Reset the list of walked items.
        """
        self.sequence = list()
    
    def handleData(self, node):
        """
        Visitor slot C{handle} for all nodes expect links.
        """
        self.sequence.append(node.name)
    handleData.accept = ItemBase, ItemRoot, ItemCollection, ItemLeaf
    
    def handleLink(self, node):
        """
        Visitor slot C{handle} for link nodes.
        
        @return: False
        """
        self.sequence.append("*" + node.name)
    handleLink.accept = ItemLink,
    
    handle = VisitSlot(handleData, handleLink)
    
class _EmptyItemTreeWalker(ItemTreeWalkerBase):
    """
    Another mock up tree walker where the C{handle} slot has been disabled.
    """
    def __init__(self, mode=-1):
        """ Constructor. """
        ItemTreeWalkerBase.__init__(self, mode=mode)
    
class ItemTreeWalkerTestCase(unittest.TestCase):
    """
    Test case for L{ItemTreeWalkerBase<datafinder.item.visitor.base.ItemTreeWalkerBase>}.
    """
    PREORDER_RESULT = ("root", "collection", "leaf", "base", "*link")
    POSTORDER_RESULT = ("leaf", "base", "*link", "collection", "root")
    NODEONLY_RESULT = PREORDER_RESULT[1:]

    def setUp(self):
        # A tree walker that operates Pre-order (mode=-1)
        self.preorderWalker = _TestItemTreeWalker()
        self.preorderWalker.reset()
        # A tree walker that applies Post-order scheme (mode=1)
        self.postorderWalker = _TestItemTreeWalker(mode=1)
        self.postorderWalker.reset()
        # A root for testing
        self.testRoot = ItemRoot("root")
        self.testRoot._fileStorer = SimpleMock(list())
        self.testRoot.itemFactory = SimpleMock(SimpleMock(list()))
        self.testRoot.path = ""
        # A collection for testing
        self.testNode = ItemCollection("collection")
        self.testNode._fileStorer = SimpleMock(list())
        self.testNode.itemFactory = SimpleMock(SimpleMock(list()))
        self.testNode.parent = self.testRoot
        # A leaf for testing
        self.testLeaf = ItemLeaf("leaf")
        self.testLeaf._fileStorer = SimpleMock(list())
        self.testLeaf.itemFactory = SimpleMock(SimpleMock(list()))
        self.testLeaf.parent = self.testNode
        # A base item for testing
        self.testBase = ItemBase("base")
        self.testBase._fileStorer = SimpleMock(list())
        self.testBase.itemFactory = SimpleMock(SimpleMock(list()))
        self.testBase.parent = self.testNode
        # A link for testing
        self.testLink = ItemLink("link")
        self.testLink._fileStorer = SimpleMock(list())
        self.testLink.itemFactory = SimpleMock(SimpleMock(list()))
        self.testLink.parent = self.testNode
    
    def _assertSequencesEqual(self, results, expected):
        """
        Assert two sequences equal itemwise.
        
        @param results: The sequence to be tested.
        @type results: Any class implementing iterator protocol.
        @param expected: The expected results.
        @type expected: Any class implementing iterator protocol.
        """
        for result, expect in zip(results, expected):
            self.assertEqual(result, expect)
    
    def testAllFine(self):
        """
        Simply compares if the produced sequence is produced as expected.
        """
        self.preorderWalker.walk(self.testRoot)
        self._assertSequencesEqual(self.preorderWalker.sequence,
                                   ItemTreeWalkerTestCase.PREORDER_RESULT)
        self.postorderWalker.walk(self.testRoot)
        self._assertSequencesEqual(self.postorderWalker.sequence,
                                   ItemTreeWalkerTestCase.POSTORDER_RESULT)
    
    def testExceptions(self):
        """
        Check whether exceptions are raised just as expected.
        """
        self.assertRaises(ValueError, _EmptyItemTreeWalker, mode=0)
        walker = _EmptyItemTreeWalker()
        self.assertRaises(AttributeError, walker.walk, self.testRoot) # No handler slot
        _EmptyItemTreeWalker.handle = VisitSlot(inherits="handle")
        self.assertRaises(AttributeError, walker.walk, self.testRoot) # No slot for type

    def testNodes(self):
        """
        Check the performance of the tree walker when started on a collection.
        """
        self.preorderWalker.walk(self.testNode)
        self._assertSequencesEqual(self.preorderWalker.sequence,
                                   ItemTreeWalkerTestCase.NODEONLY_RESULT)
    
    def testLeafs(self):
        """
        Check the performance of the tree walker when started on a leaf or link.
        """
        self.preorderWalker.walk(self.testLeaf)
        self.assertEqual(self.preorderWalker.sequence[0], "leaf")
        self.preorderWalker.reset()
        self.preorderWalker.walk(self.testLink)
        self.assertEqual(self.preorderWalker.sequence[0], "*link")
            