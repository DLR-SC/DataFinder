#
# Created: 09.05.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: identifier_mapping.py 3865 2009-03-19 09:26:12Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
This module is intended to hold the mapping of the logical meta data identifiers used
in the DataFinder core package to storage technology specific (here: WebDAV) persistence identifiers.
In later DataFinder versions this is going to be moved to an external configuration file.
"""


from webdav import Constants

from datafinder.persistence.metadata import constants


__version__ = "$LastChangedRevision: 3865 $"


# the logical system-specific identifiers are mapped to WebDAV-specific counterparts consisting of name space, name pairs  
_davNamespace = Constants.NS_DAV
_datafinderNamespace = "http://dlr.de/"

_logicalToPersistenceIdMapping = dict()
_logicalToPersistenceIdMapping[constants.MODIFICATION_DATETIME] = (_davNamespace, Constants.PROP_LAST_MODIFIED)
_logicalToPersistenceIdMapping[constants.CREATION_DATETIME] = (_davNamespace, Constants.PROP_CREATION_DATE)
_logicalToPersistenceIdMapping[constants.OWNER] = (_davNamespace, Constants.PROP_OWNER)
_logicalToPersistenceIdMapping[constants.MIME_TYPE] = (_davNamespace, Constants.PROP_CONTENT_TYPE)
_logicalToPersistenceIdMapping[constants.SIZE] = (_davNamespace, Constants.PROP_CONTENT_LENGTH)
 
_persistenceToLogicalIdMapping = dict([[value, key] for key, value in _logicalToPersistenceIdMapping.iteritems()])
    

def mapMetadataId(logicalId):
    """ 
    Maps logical identifiers to persistence identifiers. 
    
    @param logicalId: Interface property identifier, i.e. just a name.
    @type logicalId: C{unicode}
    """
    
    try:
        persistenceId = _logicalToPersistenceIdMapping[logicalId]
    except KeyError:
        persistenceId = (_datafinderNamespace, logicalId)
    return persistenceId


def mapPersistenceMetadataId(persistenceId):
    """ 
    Maps persistence identifiers to logical identifiers. 
    
    @param persistenceId: WebDAV-Specific identifier of a property, i.e. a namespace, name pair.
    @type persistenceId: C{tuple} of C{unicode}, C{unicode}
    
    @return: Interface property identifier, i.e. just a name.
    @rtype: C{unicode}
    """
    
    logicalId = None
    try:
        logicalId = _persistenceToLogicalIdMapping[persistenceId]
    except KeyError:
        if persistenceId[0] == _datafinderNamespace:
            logicalId = persistenceId[1]
    return logicalId
