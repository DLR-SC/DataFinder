#
# Created: 10.11.2008 schlauch <email>
# Changed: $Id: view.py 3906 2009-04-03 17:17:43Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder/
#


"""
The view component of the data store configuration wizard.
"""


from qt import QPalette
from qt import QColorGroup
from qt import Qt

from datafinder.gui.gen.DataStoreConfigurationWizard import DataStoreConfigurationWizard
from datafinder.gui.admin.datastore_configuration_wizard import constants
from datafinder.gui.admin.common.utils import getPixmapForImageName


__version__ = "$LastChangedRevision: 3906 $"


# constant tuple that holds the "error color red" (RGB)
_errorRgbColorCode = (255, 0, 0)


class DataStoreConfigurationWizardView(DataStoreConfigurationWizard):
    """ This class visualizes the Data Store configuration options. """

    def __init__(self, parentFrame):
        """
        Contructor.
        """

        DataStoreConfigurationWizard.__init__(self, parentFrame)
        self.helpButton().hide()
        # init dictionary to access page by the page constants
        self.pageDictionary = {}
        for pageIndex in range(self.pageCount()):
            page = self.page(pageIndex)
            title = unicode(self.title(page))
            self.pageDictionary[title] = page
        # init dictionary to access the error displaying elements by the page constants
        self.errorLabelDictionary = {
        constants.standardOptionsPage: (self.errorMessageLabel0, self.errorMessagePixmapLabel0),
        constants.storageOptionsPage: (self.errorMessageLabel1, self.errorMessagePixmapLabel1),
        constants.securityOptionsPage: (self.errorMessageLabel2, self.errorMessagePixmapLabel2),
        constants.authenticationOptionsPage: (self.errorMessageLabel3, self.errorMessagePixmapLabel3),
        constants.performanceOptionsPage: (self.errorMessageLabel4, self.errorMessagePixmapLabel4)
        }
        # save standard colors to be able to reset them
        self.backGroundColor = self.palette().color(QPalette.Active, QColorGroup.Base)

    def showCurrentErrorLabels(self, showIt, pageType, errorMessage=""):
        """ Shows the given error message. """
        errorMessageLabel = self.errorLabelDictionary[pageType][0]
        errorMessagePixmapLabel = self.errorLabelDictionary[pageType][1]
        if showIt:
            errorMessagePixmapLabel.show()
        else:
            errorMessagePixmapLabel.hide()
        errorMessageLabel.setText(errorMessage)
        # resize wizard if the whole error message cannot be shown
        errorMessageLabel.adjustSize()
        if errorMessageLabel.width() > errorMessageLabel.minimumWidth():
            self.adjustSize()

    def showErrorSource(self, source, showIt):
        """ Indicates the given error source with an "error color" border or removes this border. """

        if source:
            if showIt:
                source.palette().setColor(QPalette.Active, QColorGroup.Base, Qt.red)
            else:
                source.palette().setColor(QPalette.Active, QColorGroup.Base, self.backGroundColor)

    def setPageSequence(self, pageSequenceList):
        """
        Adapts the sequence of the wizard pages.

        @param pageSequenceList: list of page titles
        """

        for index in range(self.pageCount() - 1, -1, -1):
            page = self.page(index)
            if page:
                self.removePage(page)

        count = 0
        for pageTitle in pageSequenceList:
            self.insertPage(self.pageDictionary[pageTitle],
                            pageTitle,
                            count)
            count = count + 1
        self.showPage(self.page(0))

    def checkFinishButtonEnabledState(self):
        """
        Checks the enabled state of the "Finish" button.
        """

        currentPageIndex = self.indexOf(self.currentPage())
        if self.pageCount() - 1 == currentPageIndex:
            self.setFinishEnabled(self.currentPage(), True)
        else:
            self.setFinishEnabled(self.currentPage(), False)

    def setDatastoreIcon(self, iconName):
        """
        Shows the specified DataStore icon.

        @param iconName: Absolute name of the icon.
        @type iconName: C{unicode}
        """

        pixmap = getPixmapForImageName(iconName, False)
        self.selectedIconLabel.setPixmap(pixmap)

    def transitionEnabled(self, enabled):
        """ Enables or disables the transition to the next wizard page. """

        currentPageIndex = self.indexOf(self.currentPage())
        if self.pageCount() - 1 == currentPageIndex:
            self.setFinishEnabled(self.currentPage(), enabled)
        else:
            self.setNextEnabled(self.currentPage(), enabled)
        if not currentPageIndex == 0:
            self.setBackEnabled(self.currentPage(), enabled)
