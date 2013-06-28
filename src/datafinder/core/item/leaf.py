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
Module that contains the leaf item type.
"""


from datafinder.core.configuration.properties.constants import DATA_FORMAT_ID, MIME_TYPE_ID
from datafinder.core.error import ItemError
from datafinder.core.item.base import ItemBase
from datafinder.persistence.error import PersistenceError


__version__ = "$Revision-Id:$" 


class ItemLeaf(ItemBase):
    """
    Leaf type that can not contain any child elements.
    """
    # Root cause is ItemBase: pylint: disable=R0904
    
    def __init__(self, name=None, fileStorer=None):
        """ @see: L{ItemBase.__init__<datafinder.core.item.base.ItemBase.__init__>} """
        
        ItemBase.__init__(self, name, fileStorer)
        self._isLeaf = True
        self._created = False
        self._dataFormat = None
        
    def create(self, properties):
        """ @see: L{ItemBase.create<datafinder.core.item.base.ItemBase.create>} """

        ItemBase.create(self, properties)
        try:
            if not self.fileStorer.exists():
                canStoreProperties = self.capabilities.canStoreProperties
                self.fileStorer.createResource()
                if canStoreProperties:
                    self.updateProperties(properties)
                self.dataPersister.create()
                self._refreshProperties()
        except PersistenceError, error:
            raise ItemError("Unable to create leaf item.\nReason:'%s'" % error.message)
        else:
            self._created = True
            
    def refresh(self, itemStateOnly=False):
        """ 
        L{ItemBase.refresh<datafinder.core.item.base.ItemBase.refresh>} 
        Extends the refresh behavior so the data format can be refreshed as well. 
        """
        
        self._dataFormat = None
        ItemBase.refresh(self, itemStateOnly)
        
    @property
    def dataFormat(self):
        """ Getter for the data format attribute. """

        if self._dataFormat is None:
            dataFormatName = None
            mimeType = None
            
            if DATA_FORMAT_ID in self.properties:
                dataFormatName = self.properties[DATA_FORMAT_ID].value
            if MIME_TYPE_ID in self.properties:
                mimeType = self.properties[MIME_TYPE_ID].value
            self._dataFormat = self.itemFactory.getDataFormat(dataFormatName, mimeType, self.name)
        return self._dataFormat
