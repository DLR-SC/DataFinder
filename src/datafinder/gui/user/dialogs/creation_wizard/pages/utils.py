#
# Created: 25.01.2010 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: utils.py 4477 2010-02-26 17:30:12Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Provides some general functionalities commonly used by different pages.
"""


__version__ = "$LastChangedRevision: 4477 $"


def determineTargetDataTypes(baseRepositoryModel, index):
    """ Determines the target data types for the given index. """
    
    targetDataTypes = list()
    item = baseRepositoryModel.nodeFromIndex(index)
    repository = baseRepositoryModel.repository
    dataTypeName = None
    
    if not item.dataType is None:
        dataTypeName = item.dataType.name
    if not dataTypeName is None or item.isRoot:
        targetDataTypes = repository.configuration.getTargetDataTypes(dataTypeName)
    return targetDataTypes


def dataTypesCompatible(baseRepositoryModel, sourceIndex, targetIndex):
    """ Determines whether a connection from source index to the target index is defined in the data model. """
    
    source = baseRepositoryModel.nodeFromIndex(targetIndex)
    target = baseRepositoryModel.nodeFromIndex(sourceIndex)
    repository = baseRepositoryModel.repository
    sourceDataTypeName = None
    
    if not source.dataType is None:
        sourceDataTypeName = source.dataType.name
    targetDataTypeName = None
    if not target.dataType is None:
        targetDataTypeName = target.dataType.name
    try:
        result = repository.configuration.existsConnection(sourceDataTypeName, targetDataTypeName)
    except AttributeError:
        result = True
    return result
