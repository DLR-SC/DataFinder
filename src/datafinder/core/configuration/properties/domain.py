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
Defines two classes to support domain objects. Domain objects allow you to
model meta data in a more compact way.

Domain objects should always be inherited from C{DomainObject}. Then the required 
properties should be defined on class level using C{DomainProperty}. 

Here an example:
>>> class Author(DomainObject):
...    name = DomainProperty(StringType(), None, "Name", "This is the author name.")
...
...    @name.setValidate
...    def _validateName(self):
...        if self.name is None or len(self.name) == 0:
...            raise ValueError("Name should not be empty.")
...
... author = Author()
... author.name = "Pierre"
"""


import inspect

__version__ = "$Revision-Id:$" 

    
class DomainProperty(property):
    """ Describes a property of a domain object. 
    
    Properties defined in this way are persisted and can be further described by a 
    documentation string, display name, and a default value. You can also provide a 
    custom validation function using C{setValidate). The existing property types 
    L{property_type<datafinder.core.configuration.properties.property_type>} can 
    be used.
    """
    
    def __init__(self, type_, defaultValue=None, displayName="", docString=""):
        property.__init__(self, self._getter, self._setter)
        
        self.type = type_
        self.__doc__ = docString
        self.defaultValue = defaultValue
        self.displayName = displayName
        self._values = dict()
        self._validate = lambda _: None
        
    def validate(self, instance):
        """ Validates the given object.
        @raise ValueError: Indicates an invalid object.
        """
        
        self.type.validate(self._getter(instance))
        self._validate(instance)

    def setValidate(self, function):
        """ This method is intended to be used as method decorator.
        >>> @name.setValidate
        ... def _validateName(self):
        ...     pass
        
        The decorated method should just expect the domain
        property instance as argument. Invalid values should be
        indicated using C{ValueError}. The default validation method
        does nothing.
        """
        
        self._validate = function

    def _getter(self, instance):
        if id(instance) in self._values:
            return self._values[id(instance)]
        else:
            return self.defaultValue
    
    def _setter(self, instance, value):
        self._values[id(instance)] = value
        
    def __repr__(self):
        return "%s: %s\n%s" % (self.displayName, self.type.name, self.__doc__)
    

class DomainObject(object):
    """ Base class for all domain objects. 
    @note: Domain object should be created using an empty constructor.
    """
    
    def validate(self):
        """ Indicates validation errors using C{ValueError}. """
        
        for instance, _, propertyDescriptor, value in self.walk():
            propertyDescriptor.validate(instance)
            if isinstance(value, DomainObject):
                value.validate()
    
    def walk(self, recursively=False):
        """ Returns a generator which allows walking through 
        all defined domain properties.
        
        For every property the following information is returned:
        - The instance on which the property is defined.
        - The attribute name to which the property is bound.
        - The property descriptor.
        - The current value of the property.
        
        @param recursively: Indicates whether sub domain 
            objects are processed as well. Default: C{False}
        @type recursively: C{bool}
        """

        processLater = list()
        for name, propertyDescriptor in inspect.getmembers(self.__class__):
            if isinstance(propertyDescriptor, DomainProperty):
                value = getattr(self, name)
                yield self, name, propertyDescriptor, value
                if isinstance(value, DomainObject) and recursively:
                    processLater.append(value)
        for theProperty in processLater:
            for propertyInfo in theProperty.walk(recursively):
                yield propertyInfo

    def __cmp__(self, other):
        """ Two instances are equal if all domain properties are equal. """
        
        for _, name, __, value in self.walk():
            try:
                if cmp(getattr(other, name), value) != 0:
                    return 1
            except AttributeError:
                return 1
        return 0
    
    def __hash__(self):
        hashValue = list()
        for _, __, ___, value in self.walk():
            hashValue.append(value)
        return hash(tuple(hashValue))

    def __repr__(self):
        result = ""
        for _, name, __, value in self.walk():
            result += "%s: '%s' " % (name, str(value))
        return result.strip()
