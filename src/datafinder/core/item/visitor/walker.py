# pylint: disable-msg=W0612
# W0612: The accept properties are recognized as not used 
#        but are required for correctly using the base visitor implementation. 
#
# Created: 01.03.2010 Patrick Schaefer <patrick.schaefer@dlr.de>
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


"""
This module provides an item repository walker.
"""


from datafinder.core.item.collection import ItemCollection, ItemRoot
from datafinder.core.item.link import ItemLink
from datafinder.core.item.leaf import ItemLeaf
from datafinder.core.item.visitor.base import ItemTreeWalkerBase, VisitSlot


__version__ = "$LastChangedRevision: 4589 $"


class ItemTreeWalker(ItemTreeWalkerBase, object):
    """
    This class uses the L{ItemTreeWalkerBase<datafinder.core.item.visitor.base.ItemTreeWalkerBase>}
    protocol to implement a recursive walk algorithm.
    """
    
    def __init__(self, stopTraversalStates=None, stopProcessStates=None, defaultProperties=None):
        """
        Constructor. Cares for switching to pre-order mode.
        
        @param stopTraversalStates: List of states that are used to prevent traversal of specific collections. Default: C{None}
        @type stopTraversalStates: C{list} of C{unicode}
        @param stopProcessStates: List of states that are used to prevent processing a specific items. Default: C{None}
        @type stopProcessStates: C{list} of C{unicode}
        @param defaultProperties: Optional list of properties which are set for every item. Default: C{None}
        @type defaultProperties: C{list} of L{Property<datafinder.core.item.property.Property>}
        """
        
        super(ItemTreeWalker, self).__init__(-1, stopTraversalStates, stopProcessStates)
        self._defaultProperties = defaultProperties
        
        self.__items = list()
 
    def walk(self, node):
        """
        @see: L{walk<datafinder.core.item.visitor.base.ItemTreeWalkerBase.walk>} method to add further post-processing.
        """
        
        super(ItemTreeWalker, self).walk(node)
        return self.__items

    def _handle(self, item):
        """
        Generic handle method.
        """
        
        if not self._defaultProperties is None:
            item.updateProperties(self._defaultProperties)
        self.__items.append(item)
    
    _handle.accept = ItemCollection, ItemLink, ItemRoot, ItemLeaf, # W0612
    
    handle = VisitSlot(_handle)
