# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Label2AttrDialog
                                 A QGIS plugin
 Assign a label to an other layer's attribute
                             -------------------
        begin                : 2018-07-04
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Zoltan Siki
        email                : siki1958@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from qgis.core import QGis
from PyQt4 import QtGui, uic
import myutils

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'label2attr_dialog_base.ui'))


class Label2AttrDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(Label2AttrDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        # connect target layer change to fill column names
        self.TargetLayerCombo.currentIndexChanged.connect(self.fillCols)

    def showEvent(self, event):
        """ prepare combos """
        self.LabelLayerCombo.clear()
        self.LabelLayerCombo.addItems(myutils.getLayerNames([QGis.Point]))
        self.TargetLayerCombo.clear()
        self.TargetLayerCombo.addItems(myutils.getLayerNames([QGis.Line]))

    def fillCols(self):
        self.TargetColumnCombo.clear()
        lname = self.TargetLayerCombo.currentText()
        if len(lname):
            vlayer = myutils.getMapLayerByName(lname)
            self.TargetColumnCombo.addItems(myutils.getFieldNames(vlayer))
