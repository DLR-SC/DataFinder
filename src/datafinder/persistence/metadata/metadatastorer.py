# pylint: disable-msg=W0613, R0201
# W0613 is disabled because the arguments are not required for provision of
# a default implementation but are required for documentation.
# R0201 is disabled for similar reasons.
#
# Created: 17.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: metadatastorer.py 3803 2009-02-20 16:26:50Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Defines interface and default implementation for meta-data-related actions.
"""


__version__ = "$LastChangedRevision: 3803 $"


class NullMetadataStorer(object):
    """ 
    Null pattern / default implementation of the meta-data-related interface.
    
    @note: Real implementations of this interface are raising errors of
           type L{PersistenceError<datafinder.persistence.error.PersistenceError>}
           to indicate problems.
    """
    
    def __init__(self, identifier):
        """ 
        Constructor. 
        
        @param identifier: The logical identifier of the associated item. 
                           This is usually the path relative to a root.
        @type identifier: C{unicode}
        """
        
        self.identifier = identifier
    
    def retrieve(self, propertyIds=None):
        """ 
        Retrieves all meta data associated with the item.
        C{propertyIds} allows explicit selection of meta data.
        
        @return: Meta data of the associated item.
        @rtype: C{dict} of C{unicode}, L{MetadataValue<datafinder.common.metadata.
        value_mapping.MetaddataValue>}
        """
        
        return dict()

    def update(self, properties):
        """ 
        Update the associated meta data. 
        Adds new properties or updates existing property values. 
        
        @param properties: New / updated meta data.
        @type properties: C{dict} of C{unicode}, C{object}
        """
        
        pass
    
    def delete(self, propertyIds):
        """
        Deletes the selected meta data.
        
        @param propertyIds: Specifies the meta data that has to be deleted.
        @type propertyIds: C{list} of C{unicode} 
        """
        
        pass
    
    def search(self, restrictions):
        """ 
        Allows searching for items based on meta data restrictions.
        
        @param restrictions: Boolean conjunction of meta data restrictions.
                             For defined search operators see L{datafinder.persistence.constants}.
        @type restrictions: C{list}
        
        @return: List of matched item identifiers.
        @rtype: C{list} of C{unicode}
        """
        
        return list()
