#
# Created: Malte Legenhausen (mail to malte.legenhausen@dlr.de)
#
# Version: $Id: leaf.py 4464 2010-02-18 21:04:07Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder
#


"""
Module that contains the leaf item type.
"""


from datafinder.core.configuration.properties.constants import DATA_FORMAT_ID, MIME_TYPE_ID
from datafinder.core.error import ItemError
from datafinder.core.item.base import ItemBase
from datafinder.persistence.error import PersistenceError


__version__ = "$LastChangedRevision: 4464 $"


class ItemLeaf(ItemBase):
    """
    Leaf type that can not contain any child elements.
    """
    
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
                self.fileStorer.createResource()
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
