# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Label2Attr
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QObject, SIGNAL
from PyQt4.QtGui import QAction, QIcon, QMessageBox
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from label2attr_dialog import Label2AttrDialog
import os.path
from qgis.gui import QgsMapToolEmitPoint

class Label2Attr:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Label2Attr_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Label to Attribute')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Label2Attr')
        self.toolbar.setObjectName(u'Label2Attr')
        # config vaiables
        self.labelLayer = None
        self.labelColumn = None
        self.targetLayer = None
        self.targetColumn = None
        self.clickTool = QgsMapToolEmitPoint(self.canvas)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Label2Attr', message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        self.dlg = Label2AttrDialog()
        icon = QIcon(':/plugins/Label2Attr/icon.png')
        self.action = QAction(icon, self.tr(u'Label to Attribute Settings'), 
            self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.action.setEnabled(True)
        self.toolbar.addAction(self.action)
        self.iface.addPluginToMenu(self.menu, self.action)
        icon1 = QIcon(':/plugins/Label2Attr/icon1.png')
        self.action1 = QAction(icon1, self.tr(u'Label to Attribute'), 
            self.iface.mainWindow())
        self.action1.setCheckable(True)
        self.action1.triggered.connect(self.assign)
        self.action1.setEnabled(True)
        self.toolbar.addAction(self.action1)
        result = QObject.connect(self.clickTool,
            SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"),
            self.handleMouseDown)

    def handleMouseDown(self, point, button):
        if button == 1:
            QMessageBox.information(self.iface.mainWindow(),"Info", "X,Y = %s,%s B=%s" % (str(point.x()),str(point.y()), str(button)))


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Label to Attribute'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # store parameters
            pass

    def assign(self):
        """ assign label to attribute """
        self.canvas.setMapTool(self.clickTool)
