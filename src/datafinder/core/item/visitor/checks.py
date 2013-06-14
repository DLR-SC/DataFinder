# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
# All rights reserved.
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
This module implements some sanity checks based on the visitor/tree walker classes
defined in this package.
"""


import logging

from datafinder.core.item.base import ItemBase
from datafinder.core.item.collection import ItemRoot, ItemCollection
from datafinder.core.item.data_persister import constants
from datafinder.core.item.leaf import ItemLeaf
from datafinder.core.item.link import ItemLink
from datafinder.core.item.privileges.privilege import ALL_PRIVILEGE, WRITE_CONTENT, WRITE_PROPERTIES, READ_PRIVILEGE
from datafinder.core.item.visitor.base import ItemTreeWalkerBase, VisitSlot
from datafinder.persistence.error import PersistenceError


__version__ = "$Revision-Id:$" 


_logger = logging.getLogger()


class ActionCheckVisitor(object):
    """
    This class performs sanity checks on a given L{ItemBase<datafinder.core.item.base.ItemBase>}.
    
    It checks what capabilities this item has (e.g. can be read/write/deleted etc.).
    
    To ensure a special capability, you may use the convenience C{canDo} methods. But as those
    re-check the item each time they are called, it is better to access the C{capabilites} dictionary
    in conjunction with the L{check<datafinder.core.item.visitor.checks.ActionCheckTreeWalker.check>}
    method if you want to query different capabilities at once.
    
    @cvar CAPABILITY_ADD_CHILDREN: Other items can be added below this item.
    @cvar CAPABILITY_DELETE: The item can be deleted (or does not exist yet).
    @cvar CAPABILITY_COPY: The item can be copied.
    @cvar CAPABILITY_MOVE: The item can be moved.
    @cvar CAPABILITY_STORE: The associated data for the item can be stored.
    @cvar CAPABILITY_RERTRIEVE: The associated data for the item can be retrieved.
    @cvar CAPABILITY_ARCHIVE: The given item can be archived.
    @cvar CAPABILITY_SEARCH: Searches can be performed using the given item.
    @cvar CAPAPILITY_PRIVILEGES: The item can have added privileges
    @cvar CAPABILITY_RETRIEVE_PROPERTIES: Properties of the item can be retrieved.
    @cvar CAPABILITY_STORE_PROPERTIES: Properties of the given item can be written.
    """
    
    
    CAPABILITY_ADD_CHILDREN = "canAddChildren"
    CAPABILITY_DELETE = "delete"
    CAPABILITY_COPY = "copy"
    CAPABILITY_MOVE = "move"
    CAPABILITY_STORE = "storeData"
    CAPABILITY_RETRIEVE = "retrieveData"
    CAPABILITY_ARCHIVE = "archive"
    CAPABILITY_SEARCH = "search"
    CAPABILITY_PRIVILEGES = "privilege"
    CAPABILITY_RETRIEVE_PROPERTIES = "retrieveProperties"
    CAPABILITY_STORE_PROPERTIES = "storeProperties"

    
    def __init__(self, resolveLinks=False, hasCustomMetadataSupport=False, hasSearchSupport=False):
        self.resolveLinks = resolveLinks
        self._hasCustomMetadataSupport = hasCustomMetadataSupport
        self._hasSearchSupport = hasSearchSupport
        
        self.capabilities = dict()
        self._path = list()
    
    def check(self, item):
        """
        Run checks.
        
        This method cares for resetting the capabilities dictionary first. It then triggers the visitor
        to check the items capabilities.
        
        @param item: The item to be checked
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        self._initCapabilities()
        if not item.ignoreChecks:
            self.handle(item)
    
    def _initCapabilities(self):
        self.capabilities = {
            ActionCheckTreeWalker.CAPABILITY_ADD_CHILDREN: True,
            ActionCheckTreeWalker.CAPABILITY_DELETE: True,
            ActionCheckTreeWalker.CAPABILITY_COPY: True,
            ActionCheckTreeWalker.CAPABILITY_MOVE: True,
            ActionCheckTreeWalker.CAPABILITY_STORE: True,
            ActionCheckTreeWalker.CAPABILITY_RETRIEVE: True,
            ActionCheckTreeWalker.CAPABILITY_ARCHIVE: True,
            ActionCheckTreeWalker.CAPABILITY_SEARCH: self._hasSearchSupport,
            ActionCheckTreeWalker.CAPABILITY_PRIVILEGES: False,
            ActionCheckTreeWalker.CAPABILITY_RETRIEVE_PROPERTIES: self._hasCustomMetadataSupport,
            ActionCheckTreeWalker.CAPABILITY_STORE_PROPERTIES: self._hasCustomMetadataSupport
        }
    
    def handleDataNode(self, item):
        """
        Implementation of the C{handle} slot for any items except links.
        
        It enforces that only valid combinations of state, strategy and location are given
        and cares for setting the capabilities dictionary correctly. If one of the sanity checks
        fail, a C{ValueError} along with an expressive error message is raised. 
        
        @param item: The item which should be checked.
        @type item: L{ItemRoot<datafinder.core.item.collection.ItemRoot>},
                    L{ItemCollection<datafinder.core.item.collection.ItemCollection>} or
                    L{ItemLeaf<datafinder.core.item.leaf.ItemLeaf>}
        @raise ValueError: Any sanity check failed on the given item or any of its child.
        """
        
        if item.isRoot:
            self._disableAllCapabilities()
            try:
                self.capabilities[self.CAPABILITY_ADD_CHILDREN] = item.fileStorer.canAddChildren
            except PersistenceError, error:
                _logger.error(error)
                self.capabilities[self.CAPABILITY_ADD_CHILDREN] = False
            self.capabilities[self.CAPABILITY_SEARCH] = self._hasSearchSupport
        else:
            self._checkPrivileges(item)
            self._checkDataState(item)
        if not (item.isCollection and item.state == constants.ITEM_STATE_NULL):
            self._disable((ActionCheckVisitor.CAPABILITY_ARCHIVE,))
            
    def _disableAllCapabilities(self):
        self._disable(self.capabilities.keys())
        
    def _disable(self, caps):
        for capability in caps:
            self.capabilities[capability] = False
    
    def _checkPrivileges(self, item):
        if not item is None and not (ALL_PRIVILEGE in item.privileges or WRITE_CONTENT in item.privileges):
            self._disable((ActionCheckVisitor.CAPABILITY_ADD_CHILDREN,
                           ActionCheckVisitor.CAPABILITY_STORE,
                           ActionCheckVisitor.CAPABILITY_STORE_PROPERTIES,
                           ActionCheckVisitor.CAPABILITY_MOVE,
                           ActionCheckVisitor.CAPABILITY_DELETE))
        if not item is None and not (ALL_PRIVILEGE in item.privileges or WRITE_PROPERTIES in item.privileges):
            self._disable((ActionCheckVisitor.CAPABILITY_STORE_PROPERTIES,))
        if not item is None and not (ALL_PRIVILEGE in item.privileges or READ_PRIVILEGE in item.privileges):
            self._disable((ActionCheckVisitor.CAPABILITY_RETRIEVE, 
                           ActionCheckVisitor.CAPABILITY_RETRIEVE_PROPERTIES, 
                           ActionCheckVisitor.CAPABILITY_COPY, 
                           ActionCheckVisitor.CAPABILITY_ARCHIVE,
                           ActionCheckVisitor.CAPABILITY_SEARCH))
    
    def _checkDataState(self, item):
        state = item.state
        # Capability constraints for items in state INACCESSIBLE or NULL
        #  - must not store data
        #  - must not retrieve data
        #  - (i.e. may not access data)
        if state == constants.ITEM_STATE_INACCESSIBLE \
           or state == constants.ITEM_STATE_NULL:
            self._disable((ActionCheckVisitor.CAPABILITY_STORE,
                           ActionCheckVisitor.CAPABILITY_RETRIEVE))
        # Capability constraints for items in state MIGRATED
        #  - must not be accessed
        elif state == constants.ITEM_STATE_MIGRATED \
             or state == constants.ITEM_STATE_UNSUPPORTED_STORAGE_INTERFACE:
            self._disableAllCapabilities()
        # Capability constraints for items in state ARCHIVE
        #  - must not change properties
        elif state == constants.ITEM_STATE_ARCHIVED:
            self._disable((ActionCheckVisitor.CAPABILITY_STORE_PROPERTIES, ))
        # Capability constraints for items in state ARCHIVE MEMBER
        #  - must not delete data
        #  - must not store data
        #  - addition sub-items is optional
        #  - must not change properties
        #  - must not be copied or moved 
        elif state == constants.ITEM_STATE_ARCHIVED_MEMBER:
            self._disable((ActionCheckVisitor.CAPABILITY_COPY, 
                           ActionCheckVisitor.CAPABILITY_MOVE,
                           ActionCheckVisitor.CAPABILITY_DELETE,
                           ActionCheckVisitor.CAPABILITY_STORE,
                           ActionCheckVisitor.CAPABILITY_STORE_PROPERTIES))
        # Capability constraints for items in state READONLY ARCHIVE
        #  - must not delete data
        #  - must not store data
        #  - must not change properties
        elif state == constants.ITEM_STATE_ARCHIVED_READONLY:
            self._disable((ActionCheckVisitor.CAPABILITY_STORE,
                           ActionCheckVisitor.CAPABILITY_DELETE,
                           ActionCheckVisitor.CAPABILITY_STORE_PROPERTIES))

    def handleLink(self, item):
        """
        Implementation of the C{handle} slot for L{ItemLink<datafinder.core.item.link.ItemLink>}.
        """
        
        if self.resolveLinks and item.name not in self._path:
            item = item.linkTarget
            self.handle(item)
        else:
            self._checkPrivileges(item)
            self._checkDataState(item)
    
    def handleBase(self, item):
        """
        Implementation of the C{handle} slot for L{ItemBase<datafinder.core.item.base.ItemBase>}.
        """
        
        if item.isLink:
            self.handleLink(item)
        else:
            self.handleDataNode(item)
    
    handle = VisitSlot((handleDataNode, [ItemRoot, ItemCollection, ItemLeaf]), 
                       (handleLink, [ItemLink]), 
                       (handleBase, [ItemBase]))
    
    def canAddChildren(self, item):
        """
        Convenience method to check whether an item can be created below.
        
        @note: The sanity checks are run again when this method is called.
        
        @param item: The item to be checked.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        self.check(item)
        return self.capabilities[ActionCheckVisitor.CAPABILITY_ADD_CHILDREN]
    
    def canDelete(self, item):
        """
        Convenience method to check whether an item can be deleted.
        
        @note: The sanity checks are run again when this method is called.
        
        @param item: The item to be checked.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        self.check(item)
        return self.capabilities[ActionCheckVisitor.CAPABILITY_DELETE]
    
    def canCopy(self, item):
        """
        Convenience method to check whether an item can be copied.
        
        @note: The sanity checks are run again when this method is called.
        
        @param item: The item to be checked.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        self.check(item)
        return self.capabilities[ActionCheckVisitor.CAPABILITY_COPY]
    
    def canMove(self, item):
        """
        Convenience method to check whether an item can be moved.
        
        @note: The sanity checks are run again when this method is called.
        
        @param item: The item to be checked.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        self.check(item)
        return self.capabilities[ActionCheckVisitor.CAPABILITY_MOVE]
    
    def canStoreData(self, item):
        """
        Convenience method to check whether the associated data can be stored using this item.
        
        @note: The sanity checks are run again when this method is called.
        
        @param item: The item to be checked.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        self.check(item)
        return self.capabilities[ActionCheckVisitor.CAPABILITY_STORE]
    
    def canRetrieveData(self, item):
        """
        Convenience method to check whether the associated data can be retrieved using this item.
        
        @note: The sanity checks are run again when this method is called.
        
        @param item: The item to be checked.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        self.check(item)
        return self.capabilities[ActionCheckVisitor.CAPABILITY_RETRIEVE]
    
    def canArchive(self, item):
        """
        Convenience method to check whether an item can be archived.
        
        @note: The sanity checks are run again when this method is called.
        
        @param item: The item to be checked.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        self.check(item)
        return self.capabilities[ActionCheckVisitor.CAPABILITY_ARCHIVE]
    
    def canSearch(self, item):
        """
        Convenience method to check whether an item can be searched.
        @note: The sanity checks are run again when this method is called.
        
        @param item: The item to be checked.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        self.check(item)
        return self.capabilities[ActionCheckVisitor.CAPABILITY_SEARCH]
    
    def canPrivileges(self, item):
        """
        Convenience method to check whether an item can have rights added to it.
        @note: The sanity checks are run again when this method is called.
        
        @param item: The item to be checked.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        self.check(item)
        return self.capabilities[ActionCheckVisitor.CAPABILITY_PRIVILEGES]

    def canRetrieveProperties(self, item):
        """
        Convenience method to check whether an item`s properties can be retrieved.
        @note: The sanity checks are run again when this method is called.
        
        @param item: The item to be checked.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        self.check(item)
        return self.capabilities[ActionCheckVisitor.CAPABILITY_RETRIEVE_PROPERTIES]

    def canStoreProperties(self, item):
        """
        Convenience method to check whether an item`s properties can be written.
        @note: The sanity checks are run again when this method is called.
        
        @param item: The item to be checked.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        self.check(item)
        return self.capabilities[ActionCheckVisitor.CAPABILITY_STORE_PROPERTIES]

    
class ActionCheckTreeWalker(ItemTreeWalkerBase, ActionCheckVisitor):
    """
    This class does essentially the same as
    L{ActionCheckVisitor<datafinder.core.item.visitor.checks.ActionCheckVisitor>} but extends the checks
    to any children of the item due to its nature as tree walker.
    
    @ivar handle: Visitor slot that does the actual handling.
    @type handle: C{VisitSlot}
    """

    def __init__(self, resolveLinks=False, hasCustomMetadataSupport=False, hasSearchSupport=False):
        """
        Constructor.
        
        @param resolveLinks: Select whether links should be resolved or not.
        @type resolveLinks: boolean
        """
        
        ActionCheckVisitor.__init__(self, resolveLinks, hasCustomMetadataSupport, hasSearchSupport)
        ItemTreeWalkerBase.__init__(self, mode=-1) # enforce pre-order scheme
        self.affectedItems = list()
        self._path = list()
    
    def check(self, item):
        """
        Run checks.
        
        This method cares for resetting the capabilities dictionary first. It then starts walking
        the tree and updates the capabilities for each node it hits.
        
        @param item: The item to be checked
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        self._initCapabilities()
        if not item.ignoreChecks:
            self.affectedItems = list()
            self.walk(item)
            self.affectedItems.remove(item)

    def walk(self, node):
        """
        Re-implementation of the C{walk} slot for any item.
        
        Simply cares for appending current node to the list of affected items and calling
        the base implementation of this slot.
        """
        
        if node.state in [constants.ITEM_STATE_ARCHIVED, constants.ITEM_STATE_ARCHIVED_READONLY]: 
            currentCapabilities = self.capabilities.copy() #ignoring capabilities of archive members

        self.affectedItems.append(node)
        super(ActionCheckTreeWalker, self).walk(node)
        
        if node.state in [constants.ITEM_STATE_ARCHIVED, constants.ITEM_STATE_ARCHIVED_READONLY]:
            self.capabilities = currentCapabilities
            self.handle(node)
    
    def handleLink(self, item):
        """
        Implementation of the C{handle} slot for L{ItemLink<datafinder.core.item.link.ItemLink>}.
        """
        
        if self.resolveLinks and item.name not in self._path:
            self._path.append(item.name)
            item = item.linkTarget
            self.walk(item)
            self._path = self._path[:-1]
    
    handle = VisitSlot((handleLink, [ItemLink]), inherits="handle")
    

class ItemCapabilityChecker(object):
    """ 
    Convenience class providing the can* methods of C{ActionCheckVisitor}.
    The item is not passed to the method but to the constructor.
    """
    
    def __init__(self, item, hasCustomMetadataSupport=False, hasSearchSupport=False):
        """ Constructor. """
        
        self._item = item
        self._actionCheckVisitor = ActionCheckVisitor(False, hasCustomMetadataSupport, hasSearchSupport)
        
    def _decorateMethodWithItemInstance(self, method):
        """ Returns a method decorated with the item instance. """
        
        def _decoratedMethod():
            """ The decorated method implementation. """
            
            return method(self._item)
        return property(_decoratedMethod).fget()

    def __getattr__(self, name):
        """ The implementation does the decoration magic. """
        
        if hasattr(self._actionCheckVisitor, name):
            return self._decorateMethodWithItemInstance(getattr(self._actionCheckVisitor, name))
        else:
            raise AttributeError("AttributeError: '%s' object has no attribute '%s'" % (str(self), name))
