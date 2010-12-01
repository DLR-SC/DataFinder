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
Changes copyright and version string of Python modules
in the specified directories.
"""


import os


__version__ = "$Revision-Id$"


licence = ["# Copyright (c) 2011, German Aerospace Center (DLR)\r\n",
           "# All rights reserved.\r\n"]
version = "__version__"
newVersion = "__version__ = \"$LastChangedRevision$\"\r\n"
dirs = list # Specifies the directories


licenselong =["# $Filename$ \r\n", 
              "# $Authors$\r\n", 
              "#\r\n", 
              "# Last Changed: $Date$ $Committer$ $Revision-Id$\r\n",
            "#\r\n",
            "# Copyright (c) 2003-2011, German Aerospace Center (DLR)\r\n",
            "# All rights reserved.\r\n",
            "#\r\n",
            "#Redistribution and use in source and binary forms, with or without\r\n",
            "#modification, are permitted provided that the following conditions are\r\n",
            "#met:\r\n",
            "#\r\n",
            "# * Redistributions of source code must retain the above copyright \r\n",
            "#   notice, this list of conditions and the following disclaimer. \r\n",
            "#\r\n",
            "# * Redistributions in binary form must reproduce the above copyright \r\n",
            "#   notice, this list of conditions and the following disclaimer in the \r\n",
            "#   documentation and/or other materials provided with the \r\n",
            "#   distribution. \r\n",
            "#\r\n",
            "# * Neither the name of the German Aerospace Center nor the names of\r\n",
            "#   its contributors may be used to endorse or promote products derived\r\n",
            "#   from this software without specific prior written permission.\r\n",
            "#\r\n",
            "#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS \r\n",
            "# \"AS IS\" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT \r\n",
            "#LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR \r\n",
            "#A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT \r\n",
            "#OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, \r\n",
            "#SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT \r\n",
            "#LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, \r\n",
            "#DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY \r\n",
            "#THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT \r\n",
            "#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE \r\n",
            "#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  \r\n" 
                          ]

def main():
    """ Main function. """

    print(list)
    
    for dir_ in dirs:
        for walkTuple in os.walk(dir_):
            fileNames = walkTuple[2]
            baseDir = walkTuple[0]
            for fileName in fileNames:
                if fileName.endswith(".py"):
                    filePath = os.path.join(baseDir, fileName)
                    fh = open(filePath, "rb")
                    content = fh.readlines()
                    fh.close()
                    _changeContent2LongLicense(content, filePath)
                    fh = open(filePath, "wb")
                    fh.writelines(content)
                    fh.close()


def _changeContent(content, filePath=""):
    """ Changes the copyright and version string in the given content. """

    allRightsIndex = -1
    copyrightIndex = -1
    versionIndex = -1
    for line in content:
        if "All rights reserved" in line:
            allRightsIndex = content.index(line)
        elif "Copyright " in line:
            copyrightIndex = content.index(line)
        elif version in line:
            versionIndex = content.index(line)
    if copyrightIndex != -1 and allRightsIndex != -1:
        content.remove(content[copyrightIndex])
        content.insert(copyrightIndex, licence[0])
        content.remove(content[allRightsIndex])
        content.insert(copyrightIndex + 1, licence[1])
    else:
        print("No copyright in '%s'." % filePath)
    if versionIndex != -1:
        content.remove(content[versionIndex])
        content.insert(versionIndex, newVersion)
    else:
        print("No version string in '%s'." % filePath)

def _changeContent2LongLicense(content, filepath = ""):
    headerreached = False
    counterlicense = 0
    removeindex= 0
    newpylintindex = 0
    headerendindex = 0
    
    for line in content: 
        if "pylint:" in line:
            newpylint = line.split("-msg")
            newpylintindex = content.index(line)
            if len(newpylint)>1 :
                content.remove(content[content.index(line)])
                content.insert(newpylintindex, newpylint[0]+newpylint[1])
            removeindex = newpylintindex
        elif line.startswith("#") and not headerreached : 
            if content.index(line) >= removeindex:
                removeindex = content.index(line)
            else:
                removeindex = removeindex + 1
            content.remove(content[removeindex])
            print removeindex
            
            if not counterlicense >= len(licenselong):
                content.insert(removeindex, licenselong[counterlicense])
                counterlicense = counterlicense + 1
        elif not line.startswith("#") and not headerreached :
            headerendindex = content.index(line)
            headerreached = True
            
                  
        elif "__version__" in line:
            versionindex = content.index(line)
            content.remove(content[content.index(line)])
            content.insert(versionindex, "__version__ = $Revision-Id$ \n")          
    
     
    while counterlicense < len(licenselong):
        content.insert(headerendindex,licenselong[counterlicense])
        counterlicense = counterlicense + 1  
        headerendindex=  headerendindex+ 1  

def test():
    """ Simple self-test. """
    testData = """\
    #
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
    #
    #
    # http://www.dlr.de/datafinder/
    #
    # @scrtitle: Create from Template
    # @scrdesc: Creates defined Template structures.


    \"\"\"
    Module provides functionality to read the templates for the Proof of Concept at EADS-MAS,
    to create the collection structure and to upload files to the correct collection in this
    structure.
    \"\"\"


    import os

    from qt import QMessageBox, qApp, SIGNAL, PYSIGNAL, QObject, QPushButton, QSize, QPixmap, QFileDialog
    from qttable import QTableItem, QCheckTableItem

    from webdav.WebdavClient import WebdavError, CollectionStorer
    from webdav import Utils
    from datafinder.application import ExternalFacade
    from datafinder.application import UIFacade
    from datafinder.application.Constants import DF_USER_HOME
    from datafinder.common import LoggerMain

    from eadsScriptExtension.gen_ui.SelectTemplateDialog import SelectTemplateDialog


__version__ = "$LastChangedRevision$"


    _templateErrorCaption = "Create Collection from Template Error"
    """

    testDataList = testData.split("\n")
    _changeContent(testDataList)
    for line in testDataList:
        print(line)

main()
