# pylint: disable-msg=E1103,R0901
#
# Created: Heiko Schoenert (mail to Heiko.Schoenert@dlr.de)
#
# Version: $Id: canvas_view.py 3906 2009-04-03 17:17:43Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder
#


"""
The class ContextMenu is the main popup menu for the IconView.
The class CanvasView shows and andministrates icons.
"""


from qt import QPopupMenu, QAction, QKeySequence, QIconSet, SIGNAL, QPixmap
from qtcanvas import QCanvasView, QCanvas
from math import sin, cos, pi

from datafinder.gui.admin import data_type_dialog
from datafinder.gui.admin import relation_type_dialog
from datafinder.gui.admin.datamodel_iconview.datatype_icon import DataTypeIcon
from datafinder.gui.admin.datamodel_iconview.relation_icon import RelationIcon


__version__ = "$LastChangedRevision: 3906 $"


class ContextMenu(QPopupMenu):

    def __init__(self, theFrame, parent, context, widgetName = 0):
        QPopupMenu.__init__(self, parent, widgetName)
        self.myFrame = theFrame
        self.initContextMenu(context)

    def initContextMenu(self, context):
        """
        Initiates the popup menu depending on the context and
        adds appropriate menu items.
        """

        #ACTION TO ARRANGE THE ICONS IN A LINE
        arrangeIcons01Action = QAction("Lines", QKeySequence(), self, "arrangeIcons01Actions")
        arrangeIcons01Action.setIconSet(QIconSet())
        self.connect(arrangeIcons01Action, SIGNAL("activated()"), self.parent().arrangeIconsInLines)

        #ACTION TO ARRANGE THE ICONS IN A CIRCLE
        arrangeIcons02Action = QAction("Circle", QKeySequence(), self, "arrangeIcons02Actions")
        arrangeIcons02Action.setIconSet(QIconSet())
        self.connect(arrangeIcons02Action, SIGNAL("activated()"), self.parent().arrangeIconsInCircle)

        #SUBMENU TO CHOOSE THE WAY OF ARRANGEMENT
        #----------------------------------------
        subMenu01 = QPopupMenu(self, "Arrange Icons")
        arrangeIcons01Action.addTo(subMenu01)
        arrangeIcons02Action.addTo(subMenu01)

        #ACTION TO UPDATE THE SCREEN
        updateCanvasViewAction = QAction("Update Screen", QKeySequence(), self, "updateCanvasViewAction")
        updateCanvasViewAction.setIconSet(QIconSet())
        self.connect(updateCanvasViewAction, SIGNAL("activated()"), self.parent().updateCanvasView)

        #ACTION TO ADD A NEW DATATYPE
        newDataTypeAction = QAction("New Data Type...", QKeySequence(), self, "newDataTypeAction")
        newDataTypeAction.setIconSet(QIconSet(QPixmap.fromMimeSource("newDataType16.png")))
        self.connect(newDataTypeAction, SIGNAL("activated()"), self.myFrame.addDataTypeSlot)

        #ACTION TO ADD A NEW RELATIONTYPE
        newRelationTypeAction = QAction("New Relation Type...", QKeySequence(), self, "newRelationTypeAction")
        newRelationTypeAction.setIconSet(QIconSet(QPixmap.fromMimeSource("newRelationType16.png")))
        self.connect(newRelationTypeAction, SIGNAL("activated()"), self.myFrame.addRelationTypeSlot)

        #ACTION TO EDIT THE MARKED DATATYPE
        editDataTypeAction = QAction("Edit Data Type...", QKeySequence(), self, "editDataTypeAction")
        editDataTypeAction.setIconSet(QIconSet(QPixmap.fromMimeSource("edit16.png")))

        #ACTION TO EDIT THE MARKED RELATIONTYPE
        editRelationTypeAction = QAction("Edit Relation Type...", QKeySequence(), self, "editRelationTypeAction")
        editRelationTypeAction.setIconSet(QIconSet(QPixmap.fromMimeSource("edit16.png")))

        #ACTION TO REMOVE THE MARKED ICON FROM SCREEN
        removeIconAction = QAction("Remove Icon", QKeySequence(), self, "removeIconAction")
        removeIconAction.setIconSet(QIconSet(QPixmap.fromMimeSource("delete16.png")))
        self.connect(removeIconAction, SIGNAL("activated()"), self.parent().removeIcon)

        #ACTION TO DELETE THE MARKED DATATYPEICON
        deleteDataTypeAction = QAction("Delete Data Type", QKeySequence(), self, "deleteDataTypeAction")
        deleteDataTypeAction.setIconSet(QIconSet(QPixmap.fromMimeSource("delete16.png")))
        self.connect(deleteDataTypeAction, SIGNAL("activated()"), self.myFrame.deleteSelectedDataType)

        #ACTION TO DELETE THE MARKED RELATIONTYPE
        deleteRelationTypeAction = QAction("Delete Relation Type", QKeySequence(), self, "deleteRelationTypeAction")
        deleteRelationTypeAction.setIconSet(QIconSet(QPixmap.fromMimeSource("delete16.png")))
        self.connect(deleteRelationTypeAction, SIGNAL("activated()"), self.myFrame.deleteSelectedRelationType)

        #CONTEXT-MENU IF NOTHING IS MARKED
        if context == 0:
            newDataTypeAction.addTo(self)
            newRelationTypeAction.addTo(self)

            self.insertSeparator()

            self.insertItem("Arrange Icons...", subMenu01)
            updateCanvasViewAction.addTo(self)

        else:
        #CONTEXT-MENU IF A DATATYPE IS MARKED
            if context.iconType == 1:
                dataTypeController = data_type_dialog.DataTypeController(self.myFrame, context.iconLabel, 
                                                                         self.myFrame.repositoryConfiguration)
                self.connect(editDataTypeAction, SIGNAL("activated()"), dataTypeController.show)

                editDataTypeAction.addTo(self)
                deleteDataTypeAction.addTo(self)

                self.insertSeparator()

                newDataTypeAction.addTo(self)
                newRelationTypeAction.addTo(self)

                self.insertSeparator()

                removeIconAction.addTo(self)
                self.insertItem("Arrange Icons...", subMenu01)
                updateCanvasViewAction.addTo(self)

        #CONTEXT-MENU IF A RELATIONTYPE IS MARKED
            if context.iconType == 2:
                relationTypeController = relation_type_dialog.RelationTypeController(self.myFrame, context.iconLabel, 
                                                                                     self.myFrame.repositoryConfiguration)
                self.connect(editRelationTypeAction, SIGNAL("activated()"), relationTypeController.show)

                editRelationTypeAction.addTo(self)
                deleteRelationTypeAction.addTo(self)

                self.insertSeparator()

                newDataTypeAction.addTo(self)
                newRelationTypeAction.addTo(self)

                self.insertSeparator()

                removeIconAction.addTo(self)
                self.insertItem("Arrange Icons...", subMenu01)
                updateCanvasViewAction.addTo(self)


class CanvasView(QCanvasView):

    def __init__(self, parent, theFrame, name, f):
        """
        Constructor.
        Initiates the IconView that provides a canvas.
        """

        QCanvasView.__init__(self, None, parent, name, f)
        self.__markedStart = None
        canvas = QCanvas(parent, "canvas")
        canvas.resize(1600, 1200)
        canvas.setAdvancePeriod(30)
        self.setCanvas(canvas)
        self.theFrame = theFrame

        self.__marked = 0
        self.__movingStart = 0

    def contentsMousePressEvent(self, e): # QMouseEvent e
        """
        If mouse is clicked this function determines the choosen icon
        and marks it.
        """

        for eachItem in self.canvas().allItems():
            eachItem.unmark()
        if e != None:
            point = self.inverseWorldMatrix().map(e.pos())
            ilist = self.canvas().collisions(point) #QCanvasItemList ilist
            for eachItem in ilist:
                if eachItem.getIconType() <= 2:
                    if not eachItem.hit(point):
                        continue
                    eachItem.mark()

                    if eachItem.iconType == 1:
                        self.theFrame.dataNavigator.setCurrentPage(0)
                        item  = self.theFrame.dataTypeBrowser.findItem(eachItem.iconLabel, 0)
                        self.theFrame.dataTypeBrowser.setSelected(item, True)

                    if eachItem.iconType == 2:
                        self.theFrame.dataNavigator.setCurrentPage(1)
                        #item = self.theFrame.relationTypeBrowser.findItem(eachItem..tabTitle, 0)
                        item = self.theFrame.relationTypeBrowser.findItem(eachItem.iconLabel, 0)
                        self.theFrame.relationTypeBrowser.setSelected(item, True)

                    self.__marked = eachItem
                    self.__markedStart = point
                    self.canvas().setAllChanged()
                    self.canvas().update()
                    return

        self.__marked = 0
        self.canvas().setAllChanged()
        self.canvas().update()

    def contentsMouseMoveEvent(self, e):
        """
        If mouse is moved the marked icon is dragged relatively to
        mouse movement.
        """

        if  self.__marked :
            point = self.inverseWorldMatrix().map(e.pos())
            self.__marked.moveBy(point.x() - self.__markedStart.x(), point.y() - self.__markedStart.y())
            self.__markedStart = point

    def contextMenuEvent(self, e):
        """ If mouse is right clicked this function creates a context menu. """

        self.contentsMousePressEvent(e)
        contextMenu = ContextMenu(self.theFrame, self, self.__marked, "contextMenu")
        contextMenu.popup(e.globalPos())

    def countAllIcons(self):
        """ To count all visible icons on the canvas. """

        iconNumber = 0
        iconNumber += self.countIconTypes(1)
        iconNumber += self.countIconTypes(2)

        return iconNumber

    def countIconTypes(self, iconType):
        """ To count visible icons with type iconType. """

        iconTypeNumber = 0
        for eachItem in self.canvas().allItems():
            if eachItem.iconType == iconType:
                iconTypeNumber += 1

        return iconTypeNumber

    def getMarkedIcon(self):
        """
        Returns the marked icon.
        If no icon is marked this function returns 0.
        """

        return self.__marked

    def getIcon(self, iconLabel):
        """ Returns the icon with name iconLabel. """

        for eachItem in self.canvas().allItems():
            if eachItem.iconLabel == iconLabel:
                return eachItem

    def getAllIcons(self):
        """ Returns a list of all icons on the canvas. """

        allIcons = []
        for eachItem in self.canvas().allItems():
            if eachItem.iconType != 3:
                allIcons.append(eachItem)

        return allIcons

    def clear(self):
        """ Removes all items from the canvas. """

        ilist = self.canvas().allItems()
        for eachItem in ilist:
            if eachItem:
                eachItem.setCanvas(None)
                del eachItem
        self.canvas().update()

    def updateCanvasView(self):
        """ Updates the canvas and reinitializes all relations. """

        for eachItem in self.canvas().allItems():
            if eachItem.iconType == 2:
                eachItem.reinitialize()

        self.canvas().setAllChanged()
        self.canvas().update()

    def markDataTypeIcon(self, iconLabel):
        """ Marks a DataTypeIcon. """

        self.markIcon(iconLabel, 1)

    def markRelationIcon(self, iconLabel):
        """ Marks a RelationIcon. """

        self.markIcon(iconLabel, 2)

    def markIcon(self, iconLabel, iconType = 1):
        """ Marks an icon with type iconType. """

        self.__marked  = 0
        for eachItem in self.canvas().allItems():
            if eachItem.iconType == iconType and eachItem.iconLabel == iconLabel:
                self.__marked = eachItem
            eachItem.unmark()

        if self.__marked != 0:
            self.__marked.mark()

        self.canvas().setAllChanged()
        self.canvas().update()

    def addDataTypeIcon(self, iconLabel, iconSet):
        """ Adds a DataTypeIcon to the canvas. """

        icon = iconSet.pixmap(QIconSet.Automatic, QIconSet.Active)
        i = DataTypeIcon(icon, iconLabel, self.canvas())
        i.setZ(255)
        i.show()
        self.updateCanvasView()

    def addRelationIcon(self, relationType, iconLabel, iconSet):
        """ Adds a RelationTypeIcon to the canvas. """

        icon = iconSet.pixmap(QIconSet.Automatic, QIconSet.Active)
        i = RelationIcon(relationType, icon, iconLabel, self.canvas())
        i.setZ(255)
        i.show()

    def removeIcon(self):
        """ Removes the marked icon from the canvas. """

        if self.getMarkedIcon() != 0:
            self.getMarkedIcon().destroyIcon()
            self.contentsMousePressEvent(None)

        self.canvas().update()

    def arrangeIconsInLines(self):
        """
        Arranges all visible icons in lines.
        First the DataTypeIcons are arranged, then the RelationIcons.
        """

        xPosition = 40
        yPosition = 40
        for iconType in range(1, 3):
            for eachItem in self.canvas().allItems():
                if eachItem.iconType == iconType:
                    eachItem.move(xPosition, yPosition)
                    eachItem.updatePartialRelations()
                    xPosition = xPosition + eachItem.width() + 20
                    if xPosition > 950:
                        xPosition = 40
                        yPosition = yPosition + eachItem.height() + 40
            xPosition = 40
            yPosition = yPosition + 80

        self.canvas().update()

    def arrangeIconsInCircle(self):
        """ Arranges all visible icons in a circle. """

        xPosition = 0
        yPosition = 0
        iconTypeNumber     = []
        iconTypeRadius     = [0, 0]
        iconTypeFactor     = [20, 25]
        iconTypePosition   = 0
        iconTypeNumber.append(self.countIconTypes(1))
        iconTypeNumber.append(self.countIconTypes(2))

        for iconType in range(1, 3):
            if iconTypeNumber[iconType - 1] != 0:
                iconTypeAngle      = 360.0 / iconTypeNumber[iconType - 1]
                iconTypeTotalAngle = 180.0

                iconTypeRadius[iconType - 1] = iconTypeNumber[iconType - 1] * 400 / iconTypeFactor[iconType - 1]

                iconTypePosition = iconTypeRadius[0] + 50

                for eachItem in self.canvas().allItems():
                    if eachItem.iconType == iconType:
                        xPosition = int(iconTypePosition + iconTypeRadius[iconType - 1] * sin(iconTypeTotalAngle * 2 * pi / 360))
                        yPosition = int(iconTypePosition + iconTypeRadius[iconType - 1] * cos(iconTypeTotalAngle * 2 * pi / 360))
                        eachItem.move(xPosition, yPosition)
                        eachItem.updatePartialRelations()
                        iconTypeTotalAngle += iconTypeAngle

            self.canvas().update()
