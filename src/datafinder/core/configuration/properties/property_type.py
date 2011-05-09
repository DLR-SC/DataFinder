# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#
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
Provides the supported property types. A property type allows 
validation of property values against defined restrictions and
performs transformation of values for the persistence layer.
"""


from datetime import datetime
from decimal import Decimal
import logging

from datafinder.core.configuration.properties import constants
from datafinder.core.configuration.properties import domain
from datafinder.core.configuration.properties.validators import base_validators
from datafinder.core.configuration.properties.validators import type_validators
from datafinder.core.error import ConfigurationError


__version__ = "$Revision-Id:$" 


_log = logging.getLogger()


class BasePropertyType(object):
    """ Base class for all property types. """
    
    name = ""
    
    def __init__(self, notNull):
        """
        @param notNull: Indicates if a values may be C{None} or not.
        @type notNull: C{bool}
        """
        
        self.restrictions = dict()
        self.notNull = notNull

    def validate(self, value):
        """ Performs validation of the value against 
        the defined restrictions. Calls C{_validate}
        to perform concrete validation. 
        
        @raise ValueError: indicates validation errors.
        """
         
        if not value is None:
            self._validate(value)
        else:
            if self.notNull:
                raise ValueError("Value must not be None.")
        
    def _validate(self, value):
        """ Template method for concrete validation within
        a sub class. """
        
        pass
    
    def fromPersistenceFormat(self, persistedValue):
        """ Restores the value from the persistence layer format.
         
        @raise ValueError: Indicates problems during value transformation.
        """
        
        self = self # silent pylint
        return persistedValue
    
    def toPersistenceFormat(self, value):
        """ Transforms the value to the persistence layer format. 
        
        @raise ValueError: Indicates problems during value transformation.
        """
        
        self = self # silent pylint
        return value


class StringType(BasePropertyType):
    """ Represents string values. """

    name = constants.STRING_TYPE

    def __init__(self, minimum=None, maximum=None, pattern=None, 
                 options=None, optionsMandatory=None, notNull=False):
        """
        @see L{StringValidator.__init__<datafinder.core.configuration.
            properties.validators.type_validators.StringValidator.__init__>}
            for details on restriction parameters.
        """
        
        BasePropertyType.__init__(self, notNull)
        self.restrictions[constants.MINIMUM_LENGTH] = minimum
        self.restrictions[constants.MAXIMUM_LENGTH] = maximum
        self.restrictions[constants.PATTERN] = pattern
        self.restrictions[constants.OPTIONS] = options
        self.restrictions[constants.OPTIONS_MANDATORY] = optionsMandatory
        self._validate = type_validators.StringValidator(minimum, maximum, pattern, options, optionsMandatory)


class BooleanType(BasePropertyType):
    """ Represents a boolean values. """

    name = constants.BOOLEAN_TYPE

    def __init__(self, notNull=False):
        BasePropertyType.__init__(self, notNull)
        self._validate = type_validators.BooleanValidator()


class NumberType(BasePropertyType):
    """ Represents numeric values. """
    
    name = constants.NUMBER_TYPE

    def __init__(self, minimum=None, maximum=None, minDecimalPlaces=None, 
                 maxDecimalPlaces=None, options=None, optionsMandatory=None,
                 notNull=False):
        """
        @see L{NumberType.__init__<datafinder.core.configuration.
            properties.validators.type_validators.NumberType.__init__>}
            for details on restriction parameters.
        """
        
        BasePropertyType.__init__(self, notNull)
        self.restrictions[constants.MINIMUM_VALUE] = minimum
        self.restrictions[constants.MAXIMUM_VALUE] = maximum
        self.restrictions[constants.MINIMUM_NUMBER_OF_DECIMAL_PLACES] = minDecimalPlaces
        self.restrictions[constants.MAXIMUM_NUMBER_OF_DECIMAL_PLACES] = maxDecimalPlaces
        self.restrictions[constants.OPTIONS] = options
        self.restrictions[constants.OPTIONS_MANDATORY] = optionsMandatory
        self._validate = type_validators.NumberValidator(minimum, maximum, minDecimalPlaces, 
                                                         maxDecimalPlaces, options, optionsMandatory)


class DatetimeType(BasePropertyType):
    """ Represents date and time values. """
    
    name = constants.DATETIME_TYPE

    def __init__(self, minimum=None, maximum=None, options=None, 
                 optionsMandatory=None, notNull=False):
        """
        @see L{DatetimeType.__init__<datafinder.core.configuration.
            properties.validators.type_validators.DatetimeType.__init__>}
            for details on restriction parameters.
        """
        
        BasePropertyType.__init__(self, notNull)
        self.restrictions[constants.MINIMUM_VALUE] = minimum
        self.restrictions[constants.MAXIMUM_VALUE] = maximum
        self.restrictions[constants.OPTIONS] = options
        self.restrictions[constants.OPTIONS_MANDATORY] = optionsMandatory
        self._validate = type_validators.DatetimeValidator(minimum, maximum, options, optionsMandatory)


class ListType(BasePropertyType):
    """ Represents list of primitive values. """
    
    name = constants.LIST_TYPE

    def __init__(self, allowedSubtypes=None, minimum=None, 
                 maximum=None, notNull=False):
        """
        @see L{ListType.__init__<datafinder.core.configuration.
            properties.validators.type_validators.ListType.__init__>}
            for details on restriction parameters.
        """
        
        BasePropertyType.__init__(self, notNull)
        
        self.restrictions[constants.MINIMUM_VALUE] = minimum
        self.restrictions[constants.MAXIMUM_VALUE] = maximum
        self.restrictions[constants.ALLOWED_SUB_TYPES] = list()
        
        if allowedSubtypes is None:
            self._allowedSubtypes = list()
            self._allowedSubtypes.append(StringType())
            self._allowedSubtypes.append(NumberType())
            self._allowedSubtypes.append(BooleanType())
            self._allowedSubtypes.append(DatetimeType())
            self._allowedSubtypes.append(DomainObjectType())
        else:
            self._allowedSubtypes = allowedSubtypes
        
        subValidators = list()
        for subtype in self._allowedSubtypes:
            subValidators.append(subtype.validate)
            self.restrictions[constants.ALLOWED_SUB_TYPES].append(subtype.name)
        self._validate = type_validators.ListValidator(minimum, maximum, subValidators)

    def toPersistenceFormat(self, value):
        """ Ensures that the transformation for every
        list item is performed. """
        
        if not value is None:
            result = list()
            for item in value:
                transformationSucceeded = False
                for subType in self._allowedSubtypes:
                    try:
                        subType.validate(item)
                        result.append(subType.toPersistenceFormat(item))
                        transformationSucceeded = True
                        break
                    except ValueError:
                        continue
                if not transformationSucceeded:
                    raise ValueError("Cannot transform value '%s' to persistence format."
                                     % repr(item))
            return result
    
    def fromPersistenceFormat(self, persistedValue):
        """ Ensures that the transformation for every
         list item is performed. """
         
        if not persistedValue is None:
            result = list()
            for item in persistedValue:
                transformationSucceeded = False
                for subType in self._allowedSubtypes:
                    try:
                        value = subType.fromPersistenceFormat(item)
                        subType.validate(value)
                        result.append(value)
                        transformationSucceeded = True
                        break
                    except ValueError:
                        continue
                if not transformationSucceeded:
                    raise ValueError("Cannot restore value '%s' from persistence format."
                                     % repr(item))
            return result
        

class AnyType(BasePropertyType):
    """ Represents an unspecific property type. """
    
    name = constants.ANY_TYPE
    
    def __init__(self, allowedTypes=None, notNull=False):
        """ Constructor. """
        
        BasePropertyType.__init__(self, notNull)
        if allowedTypes is None:
            self._allowedTypes = list()
            self._allowedTypes.append(BooleanType())
            self._allowedTypes.append(NumberType())
            self._allowedTypes.append(DatetimeType())
            self._allowedTypes.append(StringType())
            self._allowedTypes.append(DomainObjectType())
            self._allowedTypes.append(ListType())
        else:
            self._allowedTypes = allowedTypes
        
        self.restrictions[constants.ALLOWED_SUB_TYPES] = list()
        subValidators = list()
        for subtype in self._allowedTypes:
            subValidators.append(subtype.validate)
            self.restrictions[constants.ALLOWED_SUB_TYPES].append(subtype.name)
        
        self.validate = base_validators.OrValidator(subValidators)
        
    def toPersistenceFormat(self, value):
        """ Ensures that the transformation for every
        supported type is tried. """
        
        if not value is None:
            result = None
            transformationSucceeded = False
            for subType in self._allowedTypes:
                try:
                    subType.validate(value)
                    result = subType.toPersistenceFormat(value)
                    transformationSucceeded = True
                    break
                except ValueError:
                    continue
            if not transformationSucceeded:
                raise ValueError("Cannot transform value '%s' to persistence format."
                                 % repr(value))
            return result
    
    def fromPersistenceFormat(self, persistedValue):
        """ Ensures that the transformation for every
         supported type is tried. """
         
        if not persistedValue is None:
            result = None
            transformationSucceeded = False
            for subType in self._allowedTypes:
                try:
                    value = subType.fromPersistenceFormat(persistedValue)
                    subType.validate(value)
                    result = value
                    transformationSucceeded = True
                    break
                except ValueError:
                    continue
            if not transformationSucceeded:
                raise ValueError("Cannot restore value '%s' from persistence format."
                                 % repr(persistedValue))
            return result
        

class UnknownDomainObject(domain.DomainObject):
    """ Used to represent values of domain object types whose
    class could not be loaded. """
    
    # Used to have a nice representation of the dictionary
    representation = domain.DomainProperty(StringType())
    
    def __init__(self, theDict):
        domain.DomainObject.__init__(self)
        self.theDict = theDict # Used to allow access to the properties
        self.representation = str(theDict)
        
        
class DomainObjectType(BasePropertyType):
    """ Represents a object values. """

    name = "" # Here you find the concrete class identifier after initialization

    def __init__(self, cls=None, notNull=False):
        """
        Constructor.
        
        @param cls: Full dotted class name (consists of package, module, and class name)
           or a class object.
        @type cls: C{unicode} or class object
        """
        
        BasePropertyType.__init__(self, notNull)
        
        if cls is None:
            cls = UnknownDomainObject       
      
        if isinstance(cls, basestring):
            self.name = cls   
            self._cls = self._importClass(cls)
        else:
            self.name = "%s.%s" % (cls.__module__, cls.__name__) 
            self._cls = cls
    
    @property
    def _isValid(self):
        """ Indicates whether the domain class has been correctly loaded or not. """
        
        return self._cls != UnknownDomainObject
            
    def _importClass(self, fullDottedClassName):
        """ Tries to import the associated class and raises a configuration 
        error if something goes wrong. """
        
        fullDottedModuleName = fullDottedClassName[:fullDottedClassName.rfind(".")]
        className = fullDottedClassName[fullDottedClassName.rfind(".") + 1:]
        try:
            moduleInstance = __import__(fullDottedModuleName, globals(), dict(), [""])
            cls = getattr(moduleInstance, className)
        except (ImportError, AttributeError, ValueError), error:
            return self._handleImportError(str(error.args))
        if cls.__name__ != className:
            cls = self._handleImportError("Failed to import class '%s'! Got '%s' instead!" \
                                          % (fullDottedClassName, cls.__name__))
        return cls
    
    def _handleImportError(self, reason):
        """ Common procedure to handle failed domain object imports. """
        
        errorMessage = "Cannot import '%s'. Reason: '%s'" % (self.name, reason)
        _log.error(errorMessage)
        self.name = "%s.%s" % (UnknownDomainObject.__module__, UnknownDomainObject.__name__)
        return UnknownDomainObject

    def _validate(self, value):

        """ Delegates the validation to the actual instance. """

        if self._cls != value.__class__:
            raise ValueError("The value '%s' has not the required type '%s'." \
                             % (str(value), str(self._cls)))
        try:
            value.validate()
        except AttributeError, error:
            raise ValueError("Cannot validate property value. Reason '%s'" % str(error.args))
        except ValueError, error:
            raise ValueError("Invalid property value found: '%s'" % str(error.args))
        
    def toPersistenceFormat(self, value):
        """ Transform the domain object into a dictionary. """
        
        if not self._isValid:
            raise ValueError("The domain class could not be found. Please " \
                             + "correct the configuration.")
        if not value is None:
            if self._cls != value.__class__:
                raise ValueError("The value '%s' has not the required type '%s'." \
                                 % (str(value), str(self._cls)))
            result = dict()
            try:
                for _, name, descriptor, subValue in value.walk():
                    result[name] = descriptor.type.toPersistenceFormat(subValue)
            except AttributeError:
                raise ValueError("The value '%s' is no valid domain object." % str(value))
            return result
        
    def fromPersistenceFormat(self, persistedValue):
        """ Restores the domain object from the given dictionary. """
        
        if not persistedValue is None:
            if not isinstance(persistedValue, dict):
                raise ValueError("The persisted value '%s' is no dictionary." 
                                 % str(persistedValue))
            if not self._isValid:
                return UnknownDomainObject(persistedValue)
            try:
                instance = self._cls()
            except TypeError:
                raise ValueError("Cannot create domain object '%s' using empty constructor."
                    % self.name)
            else:
                for instance, name, descriptor, value in instance.walk():
                    try:
                        value = descriptor.type.fromPersistenceFormat(persistedValue[name])
                    except KeyError:
                        raise ValueError(
                            "Persisted domain object '%s' does not fit defined domain class '%s'."
                            % (self.name, str(persistedValue)))
                    else:
                        setattr(instance, name, value)
            return instance


_propertyNameClassMap = {StringType.name: StringType,
    BooleanType.name: BooleanType,
    NumberType.name: NumberType,
    DatetimeType.name: DatetimeType,
    ListType.name: ListType,
    AnyType.name: AnyType}
PROPERTY_TYPE_NAMES = _propertyNameClassMap.keys()[:]


def createPropertyType(propertyTypeName, restrictions=dict()):
    """ 
    Factory method for property type creation.
    
    @param propertyTypeName: Name of the property type.
    @type propertyTypeName: C{unicode}
    @param restrictions: Map of restriction parameters and corresponding values.
    @type restrictions: C{dict} keys: C{unicode}, C{object}
    
    W0142: Here the */** magic is useful to simplify the property type 
    creation. Other approaches would "blow up" the code here.
    """ # pylint: disable=W0142
    
    if propertyTypeName in _propertyNameClassMap:
        try:
            return _propertyNameClassMap[propertyTypeName](**restrictions)
        except TypeError:
            raise ConfigurationError("Restrictions for property type '%s' are invalid." % propertyTypeName)
    else:
        return DomainObjectType(propertyTypeName)


_typeConstantsPythonTypeMap = {constants.BOOLEAN_TYPE: [bool],
    constants.DATETIME_TYPE: [datetime],
    constants.LIST_TYPE: [list],
    constants.NUMBER_TYPE: [int, float, Decimal],
    constants.STRING_TYPE: [str, unicode]}


def determinePropertyTypeConstant(value):
    """ 
    Helper function to determine the property type constant of the given value.
    If the no constant matches the full dotted class name is returned.
    @see: L{constants<datafinder.core.configuration.properties.constants>} 
    for property type constants.
    
    @param value: Python object.
    @type value: C{object}
    
    @return: Property type constant.
    @rtype: C{string}    
    """
    
    typeDisplayName = None
    valueType = type(value)
    for typeName, availableTypes in _typeConstantsPythonTypeMap.iteritems():
        if valueType in availableTypes:
            typeDisplayName = typeName
            break
    
    if typeDisplayName is None:
        typeDisplayName = \
            "%s.%s" % (value.__class__.__module__, value.__class__.__name__)
    return typeDisplayName
