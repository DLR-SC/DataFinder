#
# Created: 22.01.2010 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: constants.py 4477 2010-02-26 17:30:12Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Holds constant definition of the creation wizard.
"""


__version__ = "$LastChangedRevision: 4477 $"


# definition of page identifiers
SOURCE_PAGE_ID = 0
TARGET_PAGE_ID = 1
DATASTORE_PAGE_ID = 2
PROPERTY_PAGE_ID = 3
    
# definition of error types
INVALID_NAME_ERROR_TYPE = 0
MISSING_TARGET_DATA_TYPES_ERROR_TYPE = 1
CHILDREN_NOT_ADDABLE_ERROR_TYPE = 2
INCOMPLETE_PROPERTY_DEFINITION = 3
MISSING_SELECTION = 4
INCOMPATIBLE_DATA_TYPES = 5

# data store selection constants
ALL_DATASTORE_MODE = 0
ARCHIVE_DATASTORE_MODE = 1
ONLINE_DATASTORE_MODE = 2
OFFLINE_DATASTORE_MODE = 3
