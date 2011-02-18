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
Implements mapping of logical identifiers to SVN-specific identifiers.
"""


import platform

if platform.platform().lower().find("java") == -1:
    from datafinder.persistence.adapters.svn.util.cpython import CPythonSubversionWrapper
    SubversionWrapper = CPythonSubversionWrapper
else:
    from datafinder.persistence.adapters.svn.util.jython import JythonSubversionWrapper
    SubversionWrapper = JythonSubversionWrapper


__version__ = "$Revision-Id$" 


def createSubversionConnection(repoPath, workingCopyPath, username, password):
    """ 
    Creates a SVN connection and determines which interpreter is used.
        
    @param repoPath: The path to the repository.
    @type repoPath: C{unicode}
    @param workingCopyPath: The path to the local working copy.
    @type workingCopyPath: C{unicode}
    @param username: The username.
    @type username: C{unicode}
    @param password: The password.
    @type password: C{unicode}
    
    @return: SVN connection.
    """
    
    return SubversionWrapper(repoPath, workingCopyPath, username, password)


def mapIdentifier(identifier):
    """ 
    Maps the logical identifier to the persistence representation.
        
    @param identifier: Path relative to the configured base URL.
                       Base URL is implicitly represented by '/'.
    @type identifier: C{unicode}
        
    @return: URL identifying the resource.
    @rtype: C{unicode}
    """
        
    if identifier.startswith("/"):
        persistenceId = identifier
    else:
        persistenceId = "/" + identifier
    return persistenceId


def determineParentPath(path):
    """ 
    Determines the parent path of the logical path. 
       
    @param path: The path.
    @type path: C{unicode}
      
    @return: The parent path of the identifier.
    @rtype: C{unicode}
    """
       
    parentPath = "/".join(path.rsplit("/")[:-1])
    if parentPath == "" and path.startswith("/") and path != "/":
        parentPath = "/"
    return parentPath


def import2(from_name, fromlist=None, globals={}, locals={}):
    """
    An easy wrapper around ``__import__``.

    >>> import sys
    >>> sys2 = import2("sys")
    >>> sys is sys2
    True

    >>> import os.path
    >>> ospath2 = import2("os.path")
    >>> os.path is ospath2
    True

    >>> from time import time
    >>> time2 = import2("time", "time")
    >>> time is time2
    True

    >>> from os.path import sep
    >>> sep2 = import2("os.path", "sep")
    >>> sep is sep2
    True

    >>> from os import sep, pathsep
    >>> sep2, pathsep2 = import2("os", ["sep", "pathsep"])
    >>> sep is sep2; pathsep is pathsep2
    True
    True

    >>> import2("existiertnicht")
    Traceback (most recent call last):
        ...
    ImportError: No module named existiertnicht

    >>> import2("os", "gibtsnicht")
    Traceback (most recent call last):
        ...
    ImportError: cannot import name gibtsnicht
    """

    oneonly = False
    if isinstance(fromlist, basestring):
        oneonly = True
        fromlist = [fromlist]

    obj = __import__(from_name, globals, locals, ["foo"])
    if fromlist is None:
        return obj

    result = []
    for object_name in fromlist:
        try:
            result.append(getattr(obj, object_name))
        except AttributeError:
            raise ImportError("cannot import name " + object_name)

    if oneonly:
        return result[0]
    return result
