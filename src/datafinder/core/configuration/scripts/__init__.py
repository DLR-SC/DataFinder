#
# Created: 07.04.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: __init__.py 3913 2009-04-07 14:02:45Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements handling of script extensions.
"""


__version__ = "$LastChangedRevision: 3913 $"


from .registry import ScriptRegistry
from .handler import ScriptHandler
