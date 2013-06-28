# $Filename$ 
# $Authors$
#
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
#Redistribution and use in source and binary forms, with or without
# All rights reserved.
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
This module implements the visitor pattern in a reusable way by providing an abstract base class
upon which concrete implementations can be build.
"""


from datafinder.core.item.base import ItemBase
from datafinder.core.item.collection import ItemRoot, ItemCollection
from datafinder.core.item.leaf import ItemLeaf
from datafinder.core.item.link import ItemLink


__version__ = "$Revision-Id:$" 


class VisitSlot(object):
    """
    This class implements a dispatcher for implementing the visitor pattern.
    
    Its constructor takes an arbitrary number of handler methods (i.e. callables)
    each of which has an attribute C{accept} with a tuple with all the names of
    the class types that can be handled by the respective method. If you pass in
    a value for the keyword parameter C{inherits}, the dispatcher will try to call
    the inherited method if it cannot find any suitable handler in its own list.
    """
    
    def __init__(self, *handlers, **kw):
        """
        Constructor. Takes a list of handlers and optionally the name of a
        method of any base class to use as fallback.
        
        @param handlers: Describes the handlers: callable, list of accepted classes, 
        e.g. (_walkItem, [ItemBase], _walkCollection, [ItemCollection])
        @type handlers: Tuples of callables, list of classes.
        @param inherits: The handler to call on the base class if all own handlers fail.
        @type inherits: str.
        """
        
        self._inherits = kw.get("inherits", None)
        self._handlers = handlers
    
    def __get__(self, instance, owner):
        """ Descriptor implementation: __get__. """
        
        def _visitClosure(node, *args, **kw):
            clazz = node.__class__
            for method, classes in self._handlers:
                if clazz in classes:
                    return method(instance, node, *args, **kw)
            
            if self._inherits:
                for superclass in owner.__mro__[1:-1]: # ignore object class
                    method = superclass.__dict__.get(self._inherits, None)
                    if isinstance(method, VisitSlot):
                        try:
                            return method.__get__(instance, superclass)(node, *args, **kw)
                        except AttributeError:
                            continue
            raise AttributeError("No matching handler found for %s." % (clazz.__name__))
        return _visitClosure
    

class ItemTreeWalkerBase(object):
    """
    This class implements an abstract base for an ItemTreeWalker based on the
    L{ItemVisitorBase<datafinder.core.item.visitor.base.ItemVisitorBase>}.
    
    It provides the visit slot C{walk} to walk the tree. This method itself calls the second defined
    slot C{handle} for each node it passes. For the latter one, the implementations for the different
    handled types have to be made in the derived class.
    
    As the passed tree is usually not binary at all, only the pre- and post-order schemes
    for walking the tree are implemented.
    
    @ivar walk: The classical tree walker slot.
    """
    
    def __init__(self, mode=-1, stopTraversalStates=None, stopProcessStates=None):
        """
        Constructor.
                
        @param mode: The scheme to traverse the tree (pre- or post-order). Pass C{mode=-1} for
                     pre-order and C{mode=1} for post-order
        @type mode: C{int}
        @param stopTraversalStates: List of states that are used to prevent traversal of specific collections. Default: C{None}
        @type stopTraversalStates: C{list} of C{unicode}
        @param stopProcessStates: List of states that are used to prevent processing a specific items. Default: C{None}
        @type stopProcessStates: C{list} of C{unicode}
        """
        
        super(ItemTreeWalkerBase, self).__init__()
        self._mode = mode
        self._stopTraversalStates = stopTraversalStates
        self._stopProcessStates = stopProcessStates
        
        if self._mode == 0:
            raise ValueError("Mode should be -1 (pre-order) or 1 (post-order).")
        if self._stopTraversalStates is None:
            self._stopTraversalStates = list()
        if self._stopProcessStates is None:
            self._stopProcessStates = list()
            
    def _walkCollection(self, node, *args, **kw):
        """
        Implementation of the visit slot C{walk} for collections and roots.
        
        @param node: The node that should be traversed.
        @type node: L{ItemRoot<datafinder.core.item.collection.ItemRoot>} or
                    L{ItemCollection<datafinder.core.item.collection.ItemCollection>}
        """
        
        if self._mode < 0:
            if not node.state in self._stopTraversalStates:
                self.handle(node, *args, **kw) # PRE-Order

        if not node.state in self._stopTraversalStates:
            for child in node.getChildren():
                self.walk(child)

        if self._mode > 0:
            if not node.state in self._stopTraversalStates:
                self.handle(node, *args, **kw) # POST-Order
    
    def _walkAny(self, node, *args, **kw):
        """
        Implementation of the visit slot C{walk} for leafs and links.
        
        @param node: The leaf or link that should be traversed.
        @type node: L{ItemLeaf<datafinder.core.item.leaf.ItemLeaf>} or
                    L{ItemLink<datafinder.core.item.link.ItemLink>}
        """
        
        if not node.state in self._stopProcessStates:
            self.handle(node, *args, **kw)
    
    def _walkBase(self, node, *args, **kw):
        """
        Implementation of the visit slot C{walk} for instances of the base item class.
        
        @param node: The instance of the base item.
        @type node: The L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        if node.isLink or node.isLeaf:
            self._walkAny(node, *args, **kw)
        else:
            self._walkCollection(node, *args, **kw)
    
    walk = VisitSlot((_walkCollection, [ItemRoot, ItemCollection]), 
                     (_walkAny, [ItemLeaf, ItemLink]), 
                     (_walkBase, [ItemBase]))
    
    handle = VisitSlot()
