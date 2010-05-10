#
# Created: 11.04.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: __init__.py 4100 2009-05-24 18:12:19Z schlauch $ 
# 
# Copyright (C) 2003-2008 DLR/SISTEC, Germany
# 
# All rights reserved
# 
# http://www.dlr.de/datafinder/
#


""" 
This package provides for accessing meta data.
"""


from .property_definition import PropertyDefinition, PropertyDefinitionFactory
from .registry import PropertyDefinitionRegistry


__version__ = "$LastChangedRevision: 4100 $"
