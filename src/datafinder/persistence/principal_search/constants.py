#
# Created: 20.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: constants.py 3824 2009-03-01 13:56:03Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Principal search specific constants.
"""


__version__ = "$LastChangedRevision: 3824 $"


# principal search constants
SEARCH_MODE_USER_ONLY = 0
SEARCH_MODE_GROUP_ONLY = 1
SEARCH_MODE_USER_AND_GROUP = 2

# special principals
ALL_PRINCIPAL = "____allprincipal____"
AUTHENTICATED_PRINCIPAL = "____authenticatedprincipal____"
UNAUTHENTICATED_PRINCIPAL = "____unauthenticatedprincipal____"
OWNER_PRINCIPAL = "____ownerprincipal____"

# principal types
USER_PRINCIPAL_TYPE = "user"
GROUP_PRINCIPAL_TYPE = "group"
