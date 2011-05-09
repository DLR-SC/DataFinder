# $Filename$$
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
Testing domain property base classes.
"""


import unittest

from datafinder.core.configuration.properties import domain 
from datafinder.core.configuration.properties import property_type

__version__ = "$Revision-Id:$" 


class _City(domain.DomainObject):    
    name = domain.DomainProperty(property_type.StringType(), "", "City Name", "Name of the city.")
    zip = domain.DomainProperty(property_type.StringType(), "", "ZIP", "The postal code of the city.")


class _Address(domain.DomainObject):
    street = domain.DomainProperty(property_type.StringType(), "", "Street", "This is the street name.")
    streetNumber = domain.DomainProperty(property_type.NumberType(), None, "Street Number", "This is the street number.")
    city = domain.DomainProperty(property_type.DomainObjectType(_City), _City(), "City", "This is the city.")

    
class _Author(domain.DomainObject):
    name = domain.DomainProperty(property_type.StringType(), None, "Name", "This is the author name")
    mainAddress = domain.DomainProperty(property_type.DomainObjectType(_Address), _Address(), "Addresses", "The main address.")
    addresses = domain.DomainProperty(property_type.ListType([property_type.DomainObjectType(_Address)]), 
                                      None, "Addresses", "These are additional addresses.")

    def __init__(self, name="", mainAddress=None, addresses=None):
        domain.DomainObject.__init__(self)
        self.name = name
        if not mainAddress is None:
            self.mainAddress = mainAddress
        if not addresses is None:
            self.addresses = addresses
            
    @name.setValidate
    def _validateName(self):
        if self.name is None or len(self.name) == 0:
            raise ValueError("Name should not be empty.")


class DomainObjectTestCase(unittest.TestCase):
    """ Tests behavior of domain objects and properties. """

    def testDomainPropertyRepresentation(self):
        domainProperty = domain.DomainProperty(property_type.StringType())
        self.assertEquals(repr(domainProperty), ": String\n")
        
    def testDomainObjectRepresentation(self):
        self.assertEquals(repr(_City()), "name: '' zip: ''")
        self.assertEquals(repr(domain.DomainObject()), "")
    
    def testValueAccess(self):
        """ Tests how to set and get values from the domain property. """
        
        anAuthor = _Author("Marc")
        anAuthor.mainAddress.street = "New Street"
        
        anotherAuthor = _Author("Pierre")
        anotherAuthor.mainAddress.city.name = "Paris"

        self.assertEquals(anAuthor.name, "Marc")
        self.assertEquals(anAuthor.mainAddress.street, "New Street")
        self.assertEquals(anotherAuthor.name, "Pierre")
        self.assertEquals(anotherAuthor.mainAddress.city.name, "Paris")
        
    def testWalk(self):
        """ Tests retrieval of descriptive information of a property. """
        
        anAuthor = _Author("Pierre")
        for counter, propertyInfo in enumerate(anAuthor.walk()):
            instance, name, descriptor, value = propertyInfo
            if counter == 0:
                self.assertEquals(instance, anAuthor)
                self.assertEquals(name, "addresses")
                self.assertEquals(descriptor, _Author.addresses)
                self.assertEquals(value, anAuthor.addresses)
            elif counter == 1:
                self.assertEquals(instance, anAuthor)
                self.assertEquals(name, "mainAddress")
                self.assertEquals(descriptor, _Author.mainAddress)
                self.assertEquals(value, anAuthor.mainAddress)
            else:
                self.assertEquals(instance, anAuthor)
                self.assertEquals(name, "name")
                self.assertEquals(descriptor, _Author.name)
                self.assertEquals(value, anAuthor.name)
                
    def testWalkRecursively(self):
        anAuthor = _Author("Arthur")
        fullPropertyInfo = [propertyInfo for propertyInfo in anAuthor.walk(True)]
        self.assertEquals(len(fullPropertyInfo), 8)

    def testValidate(self):
        anAuthor = _Author("Arthur")
        anAuthor.validate()
        
        anAuthor.name = ""
        self.assertRaises(ValueError, anAuthor.validate)

    def testComparison(self):
        author = _Author("me")
        other = _Author("you")
        self.assertNotEquals(author, other)
        self.assertNotEquals(hash(author), hash(other))
        
        other.name = "me" # make them equal
        self.assertEquals(author, other)
        self.assertEquals(hash(author), hash(other))
        
        # Empty domain objects
        self.assertEquals(domain.DomainObject(), domain.DomainObject())
        self.assertEquals(hash(domain.DomainObject()), hash(domain.DomainObject()))
            
        # Compare two different domain objects
        self.assertNotEquals(author, author.mainAddress)
        self.assertNotEquals(hash(author), hash(author.mainAddress))
