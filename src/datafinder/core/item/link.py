# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#
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
Item that represents a symbolic link to an item.
"""


from datafinder.core.error import ItemError
from datafinder.core.item.base import ItemBase
from datafinder.persistence.error import PersistenceError


__version__ = "$Revision-Id:$" 


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
            except PersistenceError:
                self._linkTarget = None
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
            
        if not self._linkTarget is None:
            if self._linkTarget.parent is None: # checks for removed parent
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
