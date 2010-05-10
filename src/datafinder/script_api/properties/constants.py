#
# Created: 06.01.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: constants.py 4441 2010-02-09 08:58:13Z scha_pt $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Constants definitions of the meta data support. 
"""


from datafinder.core.configuration.properties import constants


__version__ = "$LastChangedRevision: 4441 $"



TYPES = "types"
MINIMUM_VALUE = "minimumValue"
MAXIMUM_VALUE = "maixmumValue"
MINIMUM_LENGTH = "minimumLength"
MAXIMUM_LENGTH = "maximumLength"
MINIMUM_NUMBER_OF_DECIMAL_PLACES = "minimumNumberOfDecimalPlaces"
MAXIMUM_NUMBER_OF_DECIMAL_PLACES = "maximumNumberOfDecimalPlaces"
OPTIONS = "options"
OPTIONS_MANDATORY = "optionsMandatory"
PATTERN = "pattern"

# definition of property categories
MANAGED_SYSTEM_PROPERTY_CATEGORY = constants.MANAGED_SYSTEM_PROPERTY_CATEGORY
UNMANAGED_SYSTEM_PROPERTY_CATEGORY = constants.UNMANAGED_SYSTEM_PROPERTY_CATEGORY
DATAMODEL_PROPERTY_CATEGORY = constants.DATAMODEL_PROPERTY_CATEGORY
USER_PROPERTY_CATEGORY = constants.USER_PROPERTY_CATEGORY
