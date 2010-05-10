# pylint: disable-msg=R0902
#
# Description: This is a basic icon to be shown on a canvas
#
# Created: Heiko Schoenert (mail to Heiko.Schoenert@dlr.de)
#
# Version: $Id: prototype_icon.py 3675 2009-01-08 10:38:26Z mohr_se $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder
#


"""
This is a basic icon to be shown on a canvas.
"""

 
from qt import QPixmap, QPoint, QPen, QColor
from qtcanvas import QCanvasRectangle, QCanvasText


__version__ = "$LastChangedRevision: 3675 $"


class PrototypeIcon(QCanvasRectangle):
    """
    Prototype-icon from wich other icons inherit.
    
    @param icnPxmp: a QPixmap representing the certain DataFinder-Type
    @type icnPxmp: L{QWidget<qt.Pixmap>}    
    @param icnLbl: the label of this icon
    @type icnLbl: C{unicode}
    @param icnCnvs: the canvas on wich this icon is shown
    @type icnCnvs: L{QWidget<qt.QCanvas>} 
    """
    
    def __init__(self, icnPxmp, icnLbl, icnCnvs):
        """ Constructor."""
        
        QCanvasRectangle.__init__(self, icnCnvs)
        
        self.isMarked = 0
        
        self.partialRelations = []
        self.iconType = 0
        
        self.iconLabel = icnLbl
        self.iconLabelWidth = 0
        self.iconLabelHeight = 0
        self.iconPainterWidth = 0
        self.iconPixmap = icnPxmp
        self.iconImage  = None

        self.scaleMaskUnmarked = QPixmap.convertToImage(QPixmap.fromMimeSource("layer01.png"))
        self.scaleMaskMarked = QPixmap.convertToImage(QPixmap.fromMimeSource("layer02.png"))
        self.scaleMaskHighlight = QPixmap.convertToImage(QPixmap.fromMimeSource("layer03.png"))
        self.scaledMaskUnmarked = self.scaleMaskUnmarked
        self.scaledMaskMarked = self.scaleMaskMarked
        self.scaledMaskHighlight = self.scaleMaskHighlight

        self.setIconPixmap(icnPxmp)
        self.setIconLabel(self.iconLabel)
    
    def mark(self, passIt = True):
        """
        Sets this icon as marked. If passIt is True, the icon will also mark all
        partial relations connected with this icon.
        """
        
        self.isMarked = 2

        if passIt:
            self.setZ(400)
            self.isMarked = 1
            for eachItem in self.partialRelations:
                eachItem.mark()
                
    def unmark(self, passIt = True):
        """
        Sets this icon as unmarked. If passIt is True, the icon will also unmark
        all partial relations connected with this icon.
        """
        
        self.isMarked = 0
        self.setZ(255)
        if passIt:
            for eachItem in self.partialRelations:
                eachItem.unmark()

    def getAnchorPoint(self):
        """
        Actually just returns the QPoint at the mid of this icon.
        """
        
        anchorPoint = QPoint(self.x() + self.iconPainterWidth / 2, self.y() + self.iconImage.height() / 2)
        return anchorPoint

    def getIconType(self):
        """
        Returns the type of this icon.
        Type 0 is a PrototypeIcon
        Type 1 is a DataTypeIcon
        Type 2 is a RelationIcon
        Type 3 is a PartialRelationIcon
        """
        
        return self.iconType

    def hit(self, p):
        """
        Proofs if this icon is clicked.
        
        @return: boolean indicating whether icon is clicked (True) or not (False)
        @rtype: C{boolean}
        """
        
        ix = p.x() - self.x() - (self.iconPainterWidth - self.iconImage.width()) / 2
        iy = p.y() - self.y()
        if not self.iconImage.valid( ix , iy ):
            return False
        return True
    
    def setIconPixmap(self, newIcnPxmp):
        """ Sets or changes the icons pixmap. """
        
        self.iconPixmap = newIcnPxmp
        self.iconImage  = self.iconPixmap.convertToImage()
        self.setIconLabel(self.iconLabel)        
    
    def setIconLabel(self, newIcnLbl):
        """
        Sets a new icon label and aligns it at the center.
        
        @param newIcoTxt: the icons new name
        @type newIcoTxt: C{unicode}
        """
        
        self.iconLabel       = newIcnLbl
        iconLabelBuffer      = QCanvasText(newIcnLbl, self.canvas())
        self.iconLabelWidth  = iconLabelBuffer.boundingRect().width()
        self.iconLabelHeight = iconLabelBuffer.boundingRect().height()
        iconLabelBuffer.setCanvas(None)
        del iconLabelBuffer

        self.setSize(self.iconImage.width() + 8, self.iconImage.height()+self.iconLabelHeight + 10)
        self.iconPainterWidth = self.iconImage.width()
        if self.iconLabelWidth > self.iconPainterWidth:
            self.setSize(self.iconLabelWidth + 8, self.iconPixmap.height()+self.iconLabelHeight + 10)
            self.iconPainterWidth = self.iconLabelWidth + 8

        self.scaledMaskUnmarked  = self.scaleMaskUnmarked.smoothScale(self.width(), self.height())
        self.scaledMaskMarked    = self.scaleMaskMarked.smoothScale(self.width(), self.height())
        self.scaledMaskHighlight = self.scaleMaskHighlight.smoothScale(self.width(), self.height())

    def updatePartialRelations(self):
        """
        To update the coordinates of the connected partial relations call
        this function.
        """
        
        for eachItem in self.partialRelations:
            eachItem.setCoords()
            
    def removePartialRelation(self, partialRelation):
        """ Removes the partialRelation from the icons partialRelations list. """
        
        self.partialRelations.remove(partialRelation)
            
    def moveBy(self, dx, dy):
        """ 
        To move this icon relative to its current position. At the same time
        all partial relations of this icon are updated.
        """
        
        QCanvasRectangle.moveBy(self, dx, dy)
        self.updatePartialRelations()
    
    def drawShape(self, p):
        """ Draws the icon. """

        p.setPen(QPen(QColor(100, 100, 100), 0))

        markPixmap = QPixmap(self.scaledMaskUnmarked)

        if self.isMarked == 1:
            markPixmap = QPixmap(self.scaledMaskMarked)
            p.setPen(QPen(QColor(0, 0, 0), 0))
        if self.isMarked == 2:
            markPixmap = QPixmap(self.scaledMaskHighlight)
            p.setPen(QPen(QColor(0, 0, 0), 0))

        p.drawPixmap(self.x(), self.y(), markPixmap)            
        p.drawPixmap(self.x() + (self.iconPainterWidth - self.iconPixmap.width()) / 2, self.y() + 4, self.iconPixmap)
        p.drawText(self.x() + (self.iconPainterWidth - self.iconLabelWidth) / 2, self.y() + self.iconPixmap.height() 
                   + self.iconLabelHeight + 4, self.iconLabel)

    def destroyIcon(self):
        """
        When deleting the icon, this function also removes all connected partial
        relations from the canvas and deletes them.
        """

        for eachItem in self.partialRelations:
            eachItem.setCanvas(None)
            del eachItem

        self.setCanvas(None)
        del self
