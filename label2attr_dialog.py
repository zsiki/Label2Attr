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
from qgis.core import QGis, QgsProject
from PyQt4 import QtGui, uic
import myutils

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'label2attr_dialog_base.ui'))

class Label2AttrDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, plugin, parent=None):
        """Constructor."""
        super(Label2AttrDialog, self).__init__(parent)
        self.plugin = plugin
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        # connect target layer change to fill column names
        self.LabelLayerCombo.currentIndexChanged.connect(self.fillCols0)
        self.TargetLayerCombo.currentIndexChanged.connect(self.fillCols)

    def showEvent(self, event):
        """ prepare combos """
        proj = QgsProject.instance()
        self.LabelLayerCombo.clear()
        self.LabelLayerCombo.addItems(myutils.getVisibleLayerNames(
            [QGis.Point], self.plugin.canvas))
        self.plugin.labelLayer = proj.readEntry("Label2Attr", "labelLayer", None)[0]
        index = self.LabelLayerCombo.findText(self.plugin.labelLayer)
        if index > -1:
            self.LabelLayerCombo.setCurrentIndex(index)
        self.plugin.labelColumn = proj.readEntry("Label2Attr", "labelColumn", None)[0]
        index = self.LabelColumnCombo.findText(self.plugin.labelColumn)
        if index > -1:
            self.LabelColumnCombo.setCurrentIndex(index)
        self.TargetLayerCombo.clear()
        self.TargetLayerCombo.addItems(myutils.getVisibleLayerNames(
           [QGis.Line, QGis.Point, QGis.Polygon], self.plugin.canvas))
        self.plugin.targetLayer = proj.readEntry("Label2Attr", "targetLayer", None)[0]
        index = self.TargetLayerCombo.findText(self.plugin.targetLayer)
        if index > -1:
            self.TargetLayerCombo.setCurrentIndex(index)
        self.plugin.targetColumn = proj.readEntry("Label2Attr", "targetColumn", None)[0]
        index = self.TargetColumnCombo.findText(self.plugin.targetColumn)
        if index > -1:
            self.TargetColumnCombo.setCurrentIndex(index)
        self.plugin.tolerance = proj.readNumEntry("Label2Attr", "tolerance", 1)[0]
        self.ToleranceEdit.setText(str(self.plugin.tolerance))

    def fillCols0(self):
        self.LabelColumnCombo.clear()
        lname = self.LabelLayerCombo.currentText()
        if len(lname):
            vlayer = myutils.getMapLayerByName(lname)
            self.LabelColumnCombo.addItems(myutils.getFieldNames(vlayer))

    def fillCols(self):
        self.TargetColumnCombo.clear()
        lname = self.TargetLayerCombo.currentText()
        if len(lname):
            vlayer = myutils.getMapLayerByName(lname)
            self.TargetColumnCombo.addItems(myutils.getFieldNames(vlayer))
