#pylint: disable=W0612
# W0612: The accept attribute of methods _walkAny, _walkCollection, _walkBase
# is used later to find out the acceptable visitors. So they are not really unused as 
# warned by pylint.
#
# $Filename$ 
# $Authors$
#
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
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
This module provides an item repository walker.
"""


from datafinder.core.item.collection import ItemCollection, ItemRoot
from datafinder.core.item.link import ItemLink
from datafinder.core.item.leaf import ItemLeaf
from datafinder.core.item.visitor.base import ItemTreeWalkerBase, VisitSlot


__version__ = "$Revision-Id:$" 


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
