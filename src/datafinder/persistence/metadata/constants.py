#
# Created: 20.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: constants.py 3820 2009-02-27 12:34:40Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Defines meta data specific constants.
"""


__version__ = "$LastChangedRevision: 3820 $"


# search restrictions
EQUAL_OPERATOR = "="
LT_OPERATOR = "<"
GT_OPERATOR = ">"
LTE_OPERATOR = "<="
GTE_OPERATOR = ">="
LIKE_OPERATOR = "like"
EXISTS_OPERATOR = "exists"
CONTENT_CONTAINS_OPERATOR = "contains"
IS_COLLECTION_OPERATOR = "isCollection"
AND_OPERATOR = "AND"
OR_OPERATOR = "OR"
NOT_OPERATOR = "NOT"

# default properties
CREATION_DATETIME = "____creationdatetime____" # as datetime
MODIFICATION_DATETIME = "____modificationdatetime____" # as datetime
SIZE = "____size____" # size in bytes
OWNER = "____owner____"
MIME_TYPE = "____mimetype____"
