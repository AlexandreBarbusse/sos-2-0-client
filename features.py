# -*- coding: utf-8 -*-

# =============================================================================
# Copyright (c) ARMINES / MINES ParisTech 
# Created by Alexandre Barbusse <alexandre.barbusse@gmail.com>
#
# this file is available under the BSD 3-clause License
# (https://opensource.org/licenses/BSD-3-Clause)
# =============================================================================


from PyQt4 import QtGui
import csv

from qgis.core import *

from ui.gui import PlotSeriesWindow




def plotSeries(dates, values, observedproperty, unit):
    """
    Plot time series.
    
    arguments: 
        >>> dates:
            list of 'datetime.datetime' objects containing entries of 
            time series date and time column.
        >>> values: 
            list of float objects containing entries of time series value 
            column.
        >>> observedproperty:
            (string).
        >>> unit: 
            unit of measured observed property (string).     
    
    """
    
    if dates == [] or values == []:
        pass
    
    else:
        global  plot_window
        # Use PlotSeriesWindow() imported from gui module 
        # located in "ui" subdirectory. 
        plot_window = PlotSeriesWindow()
        
        ax = plot_window.figure.add_subplot(1,1,1)
        ax.plot(dates, values)
        ax.grid()
        ax.set_ylabel(observedproperty + "(" + unit +")")
        
        plot_window.show()
    


def arraySeries(dates, values, observedproperty, unit):
    """
    Display time series in tabular format.
    
    arguments: 
        >>> dates:
            list of 'datetime.datetime' objects containing entries of 
            time series date and time column.
        >>> values: 
            list of float objects containing entries of time series value 
            column.
        >>> observedproperty:
            (string).
        >>> unit: 
            unit of measured observed property (string).     
    
    """
    
    if dates == [] or values == []:
        pass
    
    else:
        global view
        view = QtGui.QTableView()
    
        model = QtGui.QStandardItemModel(len(values), 2)
        model.setHorizontalHeaderItem(0, QtGui.QStandardItem("Date"))
        model.setHorizontalHeaderItem(
            1, QtGui.QStandardItem(observedproperty + "(" + unit +")"))
        
        for i in range(len(values)):
            model.setItem(i, 0, QtGui.QStandardItem(str(dates[i])))
            model.setItem(i, 1, QtGui.QStandardItem(str(values[i])))
            
        view.setModel(model)
        view.setWindowTitle('Time series table view')
        view.show()
    


def exportSeries(dates, values, observedproperty, unit, path):
    """
    Export time series as CSV file.
    
    arguments: 
        >>> dates:
            list of 'datetime.datetime' objects containing entries of 
            time series date and time column.
        >>> values: 
            list of float objects containing entries of time series value 
            column.
        >>> observedproperty:
            (string).
        >>> unit: 
            unit of measured observed property (string).  
        >>> path: 
            complete path (folder + file name) where the CSV file will be
            saved (unicode).  
    
    """
    if dates == [] or values == []:
        pass

    else:
        rows = zip(dates, values)
        try:
            with open(path, 'wb') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", observedproperty + "(" + unit +")"])
                for row in rows:
                    writer.writerow(row)

        except IOError:
            pass
    


        
 