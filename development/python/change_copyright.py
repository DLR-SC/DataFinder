#
# Created: 19.11.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: change_copyright.py 3671 2009-01-07 09:19:10Z mohr_se $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
# http://www.dlr.de/datafinder/
#


"""
Changes copyright and version string of Python modules
in the specified directories.
"""


import os


__version__ = "$LastChangedRevision: 3671 $"


licence = ["# Copyright (c) 2008, German Aerospace Center (DLR)\r\n",
           "# All rights reserved.\r\n"]
version = "__version__"
newVersion = "__version__ = \"$LastChangedRevision: 3671 $\"\r\n"
dirs = list # Specifies the directories


def main():
    """ Main function. """

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
                    _changeContent(content, filePath)
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


def test():
    """ Simple self-test. """
    testData = """\
    #
    # Copyright (C) 2003-2007 DLR, Simulation and Software Technology
    #
    # All rights reserved
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


    __version__ = "$Revision: 3671 $"


    _templateErrorCaption = "Create Collection from Template Error"
    """

    testDataList = testData.split("\n")
    _changeContent(testDataList)
    for line in testDataList:
        print(line)

main()
