# $Filename$ 
# $Authors$
#
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
#Redistribution and use in source and binary forms, with or without
# All rights reserved.
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
Contains constants to be used by DataFinder classes.
"""


import os


__version__ = "$Revision-Id:$" 


DATAMODEL_FILENAME = "datamodel.xml"
DATASTORE_FILENAME = "datastores.xml"
ICON_DIRECTORYNAME = "icons"
SCRIPT_DIRECTORYNAME = "scripts"

# Homedir for the user
USER_HOME = os.path.join(os.path.expanduser("~"), ".datafinder")

# DataFinder install directory
INSTALLATION_HOME = os.environ.get("DF_HOME")

# Installed image files
if not INSTALLATION_HOME is None:
    LOCAL_INSTALLED_ICONS_DIRECTORY_PATH = os.path.abspath(os.path.join(INSTALLATION_HOME, "resources", "images"))
else:
    LOCAL_INSTALLED_ICONS_DIRECTORY_PATH = ""

# version number
VERSION = ""
