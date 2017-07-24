# -*- coding: utf-8 -*-

# =============================================================================
# Copyright (c) ARMINES / MINES ParisTech 
# Created by Alexandre Barbusse <alexandre.barbusse@gmail.com>
#
# this file is available under the BSD 3-clause License
# (https://opensource.org/licenses/BSD-3-Clause)
# =============================================================================


import os
from PyQt4 import QtGui, QtCore, uic

from ui.mainwindow_dialog import MainWindowDialog



def resolve(name, basepath=None):
    """
    Resolve path to a file relative to the plugin given its name. 
    
    argument: 
        >>> name: 
            File name (string) containing its type.
    """
    
    if not basepath:
      basepath = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(basepath, name)



class SOSpluginMain:
    """QGIS Plugin Implementation."""

    def __init__(self, iface): 
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface 
        # Create the dialog (after translation) and keep reference
        self.win = MainWindowDialog()
               
    def initGui(self): 
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # Create the icon which will open the plugin main dialog window once clicked
        filepath = resolve('icon.png')
        self.action = QtGui.QAction(QtGui.QIcon(filepath),
                                    u"&SOS 2.0 client" , self.iface.mainWindow())
        
        # Connect the icon with run method
        QtCore.QObject.connect(self.action, QtCore.SIGNAL("triggered()" ), self.run)
        
        # Add icon to QGIS toolBar and to the "Web Menu" located in the toolbar
        self.iface.addToolBarIcon(self.action)

        self.iface.addPluginToWebMenu(u"&SOS 2.0 client (alpha release)", 
                                      self.action)
        
    def unload(self): 
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.removePluginWebMenu (u"&SOS 2.0 client (alpha release)",
                                        self.action)
        # remove the toolbar
        self.iface.removeToolBarIcon(self.action)
        
    def run(self): 
        """Run method that performs all the real work"""
        
        
        self.win.show()
    
 
    
        
        
        