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


import datetime
import logging
import sys

from datafinder.script_api.repository import connectRepository
from datafinder.script_api.properties import property_support as prop_supp
from datafinder.script_api.properties import \
    DomainObject, DomainObjectType, DomainProperty, StringType


__version__ = "$Revision-Id:$" 


_logger = logging.getLogger()
_logger.addHandler(logging.StreamHandler(sys.stdout))


class _Author(DomainObject):
    firstName = DomainProperty(StringType(2), None, "First Name", "This is the first name.")
    lastName = DomainProperty(StringType(2), None, "Last Name", "This is the last name.")

    def __init__(self, firstName="", lastName=""):
        DomainObject.__init__(self)
        self.firstName = firstName
        self.lastName = lastName
    
    @firstName.setValidate
    def _validateFirstName(self):
        self._validateName(self.firstName)
    
    @lastName.setValidate
    def _validateLastName(self):
        self._validateName(self.lastName)
    
    @staticmethod
    def _validateName(name):
        if name is None:
            raise ValueError("Name should not be empty.")


def propertyAccess(baseUrl, username=None, password=None):
    """ Demonstrates the access to properties. """
    
    connectRepository(baseUrl, username=username, password=password)
    prop_supp.registerPropertyDefinition("author", DomainObjectType(_Author))
    for propertyDescription_ in prop_supp.availableProperties().values():
        _logger.info(propertyDescription_)
    _logger.info(prop_supp.propertyDescription("anotherProperty"))
    
    _logger.info(prop_supp.retrieveProperties("/"))
    properties = {"anotherProperty": datetime.datetime.now(),
                  "author": _Author("Me", "You")}
    prop_supp.validate(properties)
    prop_supp.storeProperties("/", properties)
    _logger.info(prop_supp.retrieveProperties("/"))
    prop_supp.deleteProperties("/", ["anotherProperty", "author"])
    _logger.info(prop_supp.retrieveProperties("/"))
    

if __name__ == "__main__":
    if len(sys.argv) == 2:
        propertyAccess(unicode(sys.argv[1]))
    elif len(sys.argv) == 4:
        propertyAccess(unicode(sys.argv[1]), unicode(sys.argv[2]), unicode(sys.argv[3]))
    else:
        _logger.info("Call: properties.py URL [username] [password]")
