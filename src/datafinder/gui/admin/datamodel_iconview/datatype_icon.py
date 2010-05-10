#
# Description: The class draws a datatype icon
#
# Created: Heiko Schoenert (mail to Heiko.Schoenert@dlr.de)
#
# Version: $Id: datatype_icon.py 3675 2009-01-08 10:38:26Z mohr_se $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder
#


"""
The class draws a datatype icon
"""


from datafinder.gui.admin.datamodel_iconview.prototype_icon import PrototypeIcon


__version__ = "$LastChangedRevision: 3675 $"


class DataTypeIcon(PrototypeIcon):
    """
    collection-icon to be shown on QCanvasView

    @param ico: the new datatype-icons image as pixmap
    @type ico: L{qt.QPixmap}

    @param ico_text: the new datatype-icons name
    @type ico_text: string

    @param canvas: the new datatype-icons canvas
    @type canvas: qt.QCanvas
    """
    def __init__(self, icnPxmp, icnLbl, icnCnvs):
        PrototypeIcon.__init__(self, icnPxmp, icnLbl, icnCnvs)

        self.iconType = 1

    def setParent(self, thisRel):
        """
        adds a relation to isParent list

        @param thisRel: the relation
        @type thisRel: qt.QCanvasPolygonalItem
        """
        self.parentOf.append(thisRel)

    def setChild(self, thisRel):
        """
        adds a relation to isChild list

        @param thisRel: the relation
        @type thisRel: qt.QCanvasPolygonalItem
        """
        self.childOf.append(thisRel)
