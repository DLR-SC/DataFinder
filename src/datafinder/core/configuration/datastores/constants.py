#
# Created: 08.04.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: constants.py 4540 2010-03-09 13:46:33Z ney_mi $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements common constants
"""


__version__ = "$LastChangedRevision: 4540 $"


DEFAULT_STORE_ICONNAME = "dataStore"

DEFAULT_STORE = "Default Store"
FILE_STORE = "File System Store" 
FTP_STORE = "FTP Store" 
GRIDFTP_STORE = "GridFTP Store"
OFFLINE_STORE = "Off-line Store" 
TSM_CONNECTOR_STORE = "TSM Store"
WEBDAV_STORE = "WebDAV Store"
S3_STORE = "S3 Store"


ARCHIVE_STORE_CATEGORY = (TSM_CONNECTOR_STORE)
ONLINE_STORE_CATEGORY = (DEFAULT_STORE, FILE_STORE, FTP_STORE, GRIDFTP_STORE, WEBDAV_STORE, S3_STORE)
OFFLINE_STORE_CATEGORY = (OFFLINE_STORE)


# enumeration definitions
class _StorageReailisationModeEnumeration(object):
    """ Defines modes for storage realization. """
    
    FLAT = "Flat"
    HIERARCHICAL = "Hierarchical"

class _SecurityModeEnumeration(object):
    """ Defines GridFTP-specific security modes. """
    
    STANDARD = "Standard"
    PRIVATE = "Private"
    SAFE = "Safe"
    
class _TransferModeEnumeration(object):
    """ Defines GridFTP-specific transfer modes. """
    
    STREAM_MODE = "Stream"
    EXTENDED_MODE = "Extended"

    
GRIDFTP_SECURITY_MODE_ENUM = _SecurityModeEnumeration
GRIDFTP_TRANSFER_MODE_ENUM = _TransferModeEnumeration
STORAGE_REALISATION_MODE_ENUM = _StorageReailisationModeEnumeration
