#
# Created: 01.09.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: type_validators.py 3884 2009-03-26 17:07:42Z schlauch $ 
# 
# Copyright (C) 2003-2008 DLR/SISTEC, Germany
# 
# All rights reserved
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements aggregated type-specific validation functionalities.
"""


from datetime import datetime
from decimal import Decimal

from datafinder.core.configuration.properties.validators import base_validators


__version__ = "$LastChangedRevision: 3884 $"


class StringValidator(base_validators.AndValidator):
    """ Aggregates useful checks for checking string values. """
    
    def __init__(self, minimum=None, maximum=None, pattern=None, options=None, optionsMandatory=True):
        """
        Constructor.
        
        @param minimum: Minimum length of the string.
        @type minimum: C{int}
        @param maximum: Maximum length of the string.
        @type maximum: C{int}
        @param pattern: Regular expression pattern.
        @type pattern: C{str}
        @param options: List of options the value has to be taken from.
        @type options: C{list} of C{unicode}
        """
        
        base_validators.AndValidator.__init__(self, list())
        self.validators.append(base_validators.AreTypesMatched([str, unicode]))
        self.validators.append(base_validators.IsBinaryStringDecodable())
        self.validators.append(base_validators.IsLengthInRange(minimum, maximum))
        if not pattern is None:
            self.validators.append(base_validators.IsPatternMatched(pattern))
        if not options is None:
            self.validators.append(base_validators.AreOptionsMatched(options, optionsMandatory))


class NumberValidator(base_validators.AndValidator):
    """ Aggregates useful checks for checking numeric values. """
    
    def __init__(self, minimum=None, maximum=None, minDecimalPlaces=None, 
                 maxDecimalPlaces=None, options=None, optionsMandatory=True):
        """
        Constructor.
        
        @param minimum: Minimum value. 
        @type minimum: C{decimal.Decimal}
        @param maximum: Maximum value.
        @type maximum: C{decimal.Decimal}
        @param options: List of options the value has to be taken from.
        @type options: C{list} of C{decimal.Decimal}
        """
        
        base_validators.AndValidator.__init__(self, list())
        self.validators.append(base_validators.AreTypesMatched([int, float, Decimal]))
        self.validators.append(base_validators.IsInRange(minimum, maximum))
        self.validators.append(base_validators.IsNumberOfDecimalPlacesInRange(minDecimalPlaces, maxDecimalPlaces))
        if not options is None:
            self.validators.append(base_validators.AreOptionsMatched(options, optionsMandatory))


class BooleanValidator(base_validators.AndValidator):
    """ Aggregates useful checks for boolean values. """
    
    def __init__(self):
        """ Constructor. """
    
        base_validators.AndValidator.__init__(self, list())
        self.validators.append(base_validators.AreTypesMatched([bool]))
        
        
class DatetimeValidator(base_validators.AndValidator):
    """ The class aggregates all checks that are useful for validation of date times. """
    
    def __init__(self, minimum=None, maximum=None, options=None, optionsMandatory=True):
        """
        Constructor.
        
        @param minimum: Minimum length of the list.
        @type minimum: C{int}
        @param maximum: Maximum length of the list.
        @type maximum: C{int}
        @param options: List of options the value has to be taken from.
        @type options: C{list} of C{datetime}
        """
        
        base_validators.AndValidator.__init__(self, list())
        self.validators.append(base_validators.AreTypesMatched([datetime]))
        self.validators.append(base_validators.IsInRange(minimum, maximum))
        if not options is None:
            self.validators.append(base_validators.AreOptionsMatched(options, optionsMandatory))


class ListValidator(base_validators.AndValidator):
    """ The class aggregates all checks that are useful for validation of lists. """
    
    def __init__(self, minimum=None, maximum=None, itemValidators=None):
        """
        Constructor.
        
        @param minimum: Minimum length of the list.
        @type minimum: C{int}
        @param maximum: Maximum length of the list.
        @type maximum: C{int}
        @param itemValidators: List of checks for single items.
                               All checks are tried until at least one succeeds.
        @type itemValidators: C{list}
        """
        
        base_validators.AndValidator.__init__(self, list())
        self.validators.append(base_validators.AreTypesMatched([list]))
        self.validators.append(base_validators.IsInRange(minimum, maximum))
        if not itemValidators is None:
            self.validators.append(base_validators.ForEach(base_validators.OrValidator(itemValidators)))


class ArbitaryValidator(base_validators.OrValidator):
    """ 
    Represents a property that can hold a list of values. 
    
    @note: The list is a typed list which means the members of the list
    can own one of the basically supported types. At the moment nested
    lists are unsupported.
    """
    
    def __init__(self):
        """ Constructor. """

        base_validators.OrValidator.__init__(self, list())
        self.validators.append(BooleanValidator())
        self.validators.append(DatetimeValidator())
        self.validators.append(NumberValidator())
        listValidators = [BooleanValidator(), DatetimeValidator(), NumberValidator(), StringValidator()]
        self.validators.append(ListValidator(itemValidators=listValidators))
        self.validators.append(StringValidator())
