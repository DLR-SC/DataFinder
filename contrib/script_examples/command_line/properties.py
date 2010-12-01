# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#met:
#
# * Redistributions of source code must retain the above copyright 
#   notice, this list of conditions and the following disclaimer. 
#
# * Redistributions in binary form must reproduce the above copyright 
#   notice, this list of conditions and the following disclaimer in the 
#   documentation and/or other materials provided with the 
#   distribution. 
#
# * Neither the name of the German Aerospace Center nor the names of
#   its contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
#LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 
#A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
#OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
#SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
#LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
#DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
#THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  


""" 
Demonstrates the property access.
"""


import sys
import datetime

from datafinder.script_api.repository import connectRepository
from datafinder.script_api.properties.property_support import retrieveProperties, storeProperties, deleteProperties, \
                                                              validate, availableProperties, propertyDescription


__version__ = "$Revision-Id:$" 


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
