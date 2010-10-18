#
# Created: 21.03.2010 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: properties.py 4556 2010-03-21 14:48:01Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Demonstrates the property access.
"""


import sys
import datetime

from datafinder.script_api.repository import connectRepository
from datafinder.script_api.properties.property_support import retrieveProperties, storeProperties, deleteProperties, \
                                                              validate, availableProperties, propertyDescription


__version__ = "$LastChangedRevision: 4556 $"


def propertyAccess(baseUrl, username=None, password=None):
    """ Demonstrates the access to properties. """
    
    connectRepository(baseUrl, username=username, password=password)
    for propertyDescription_ in availableProperties().values():
        print propertyDescription_
    print propertyDescription("anotherProperty")
    
    print retrieveProperties("/")
    properties = {"anotherProperty": datetime.datetime.now()}
    validate(properties)
    storeProperties("/", properties)
    print retrieveProperties("/")
    deleteProperties("/", ["anotherProperty"])
    print retrieveProperties("/")
    

if __name__ == "__main__":

    if len(sys.argv) == 2:
        propertyAccess(unicode(sys.argv[1]))
    elif len(sys.argv) == 4:
        propertyAccess(unicode(sys.argv[1]), unicode(sys.argv[2]), unicode(sys.argv[3]))
    else:
        print "Call: properties.py URL [username] [password]"
