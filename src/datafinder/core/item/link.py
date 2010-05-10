#
# Created: Malte Legenhausen (mail to malte.legenhausen@dlr.de)
#
# Version: $Id: link.py 4554 2010-03-21 11:58:03Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder
#


"""
Item that represents a symbolic link to an item.
"""


from datafinder.core.error import ItemError
from datafinder.core.item.base import ItemBase
from datafinder.persistence.error import PersistenceError


__version__ = "$LastChangedRevision: 4554 $"


class ItemLink(ItemBase):
    """
    Item class that represents a symbolic link to another item.
    """
    
    def __init__(self, name=None, fileStorer=None, linkTargetItem=None):
        """
        @see: L{ItemBase.__init__<datafinder.core.item.base.ItemBase.__init__>} 
        
        @param linkTargetItem: The target item of the link.
        @type linkTargetItem: L{ItemBase<datafinder.core.item.base.ItemBase}
        """

        ItemBase.__init__(self, name, fileStorer)
        self._isLeaf = False
        self._isLink = True
        self._created = False
        self._linkTarget = None
        self._linkTargetPath = None
        self._refreshLinkTarget = True
        
        self.linkTarget = linkTargetItem
    
    def refresh(self, itemStateOnly=False):
        """ 
        L{ItemBase.refresh<datafinder.core.item.base.ItemBase.refresh>} 
        Extends the refresh behavior so the data format can be refreshed as well. 
        """
        
        self._refreshLinkTarget = True
        ItemBase.refresh(self, itemStateOnly)
        
    def create(self, properties):
        """ @see: L{ItemBase.create<datafinder.core.item.base.ItemBase.create>} """

        if self._linkTarget is None:
            raise ItemError("Cannot create link because the link target is missing.")
        else:
            ItemBase.create(self, properties)
            try:
                if not self.fileStorer.exists():
                    self.fileStorer.createLink(self._linkTarget.fileStorer)
                    self._refreshProperties()
            except PersistenceError, error:
                raise ItemError("Unable to create leaf item.\nReason:'%s'" % error.message)
            else:
                self._created = True
                
    def _getLinkTarget(self):
        """ Getter for the link target. """
        
        if self._refreshLinkTarget:
            try:
                targetFileStorer = self._fileStorer.linkTarget
                if not targetFileStorer is None:
                    self._linkTargetPath = targetFileStorer.identifier
            except PersistenceError:
                self._linkTargetPath = None
            else:
                if not targetFileStorer is None:
                    try:
                        self._linkTarget = self.itemFactory.create(targetFileStorer.identifier, 
                                                                   fileStorer=targetFileStorer)
                    except ItemError:
                        self._linkTarget = None
                else:
                    self._linkTarget = None
            self._refreshLinkTarget = False
            
        if not self._linkTarget is None: # checks for removed parent
            if self._linkTarget.parent is None:
                self._linkTarget = None
        return self._linkTarget 

    def _setLinkTarget(self, linkTarget):
        """ Sets the link target. """
        
        if not linkTarget is None:
            if linkTarget.isLink:
                self._linkTarget = linkTarget.linkTarget
            else:
                self._linkTarget = linkTarget
        else:
            self._linkTarget = linkTarget
    linkTarget = property(_getLinkTarget, _setLinkTarget)

    @property
    def linkTargetPath(self):
        """ Returns the link target path. """
        
        return self._linkTargetPath
