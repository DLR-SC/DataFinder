# pylint: disable-msg=R0901
# R0901: Tells you that you have to much ancestors in your class hierarchy.
#        But this is required here to build a error hierarchy.
#
# Created: 04.02.2010 Patrick Schaefer <patrick.schaefer@dlr.de>
# Changed: $Id: error.py 4578 2010-03-30 13:26:18Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


"""
Module that contains the exceptions on the script API level.
"""


__version__ = "$LastChangedRevision: 4578 $"


class ScriptApiError(Exception):
    """
    Base error class for the script API.
    """
    
    pass


class ConfigurationSupportError(ScriptApiError):
    """
    Indicates errors of the configuration support package.
    """
    pass

        
class PropertiesSupportError(ScriptApiError):
    """
    Indicates errors of the properties support package.
    """

    pass    

        
class ItemSupportError(ScriptApiError):
    """
    Indicates errors of the item support package.
    """

    pass
