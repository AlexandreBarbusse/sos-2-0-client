# -*- coding: utf-8 -*-

# =============================================================================
# Copyright (c) ARMINES / MINES ParisTech 
# Created by Alexandre Barbusse <alexandre.barbusse@gmail.com>
#
# this file is available under the BSD 3-clause License
# (https://opensource.org/licenses/BSD-3-Clause)
# =============================================================================



import os
from PyQt4 import QtGui, uic
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
try:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
except ImportError:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from qgis.core import *




class PlotSeriesWindow(QtGui.QDialog):
    """ Create the window which will display the time series plot."""
    
    def __init__(self, parent=None):
        super(PlotSeriesWindow, self).__init__(parent)

        # a figure instance to plot on
        self.figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)
        self.setLayout(layout)
        self.setWindowTitle('Time series plot')
        
        



# import form from UI file
GetCapabilityForm, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'getcapibilities.ui'))
    

class GetCapabilityWindow(QtGui.QWidget, GetCapabilityForm):
    """ 
    Create the window which will display general server information
    from SOS GetCapabilities request.
    
    """
    
    def __init__(self, parent=None):
        """Constructor."""
        super(GetCapabilityWindow, self).__init__(parent)
        self.setupUi(self)





# import form from UI file    
CalendarForm, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'calendar.ui'))

   
class CalendarWindow(QtGui.QWidget, CalendarForm):
    """
    Create the window that will show a calendar used for time period 
    selection before GetObservation request.    
    
    """
    def __init__(self, parent=None):
        """Constructor."""
        super(CalendarWindow, self).__init__(parent)
        self.setupUi(self)


        
 