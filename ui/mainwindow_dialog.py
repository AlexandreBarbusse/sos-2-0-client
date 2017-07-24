# -*- coding: utf-8 -*-

# =============================================================================
# Copyright (c) ARMINES / MINES ParisTech 
# Created by Alexandre Barbusse <alexandre.barbusse@gmail.com>
#
# this file is available under the BSD 3-clause License
# (https://opensource.org/licenses/BSD-3-Clause)
# =============================================================================


import traceback
import os
from PyQt4 import QtGui, QtCore, uic
import requests

import datetime

from qgis.core import *
import qgis.utils

from ..owslib.sos import SensorObservationService
from gui import CalendarWindow
from ..sos import WGS84conversion, getCapabilitiesSOS200, getSeriesSOS200
from ..sos import GetOfferingsList
from ..features import plotSeries, arraySeries, exportSeries

# Logs 
import logging
# Create log for OWSLib package
owslib_log = logging.getLogger('owslib')
# Add formatting and handlers as needed
owslib_log.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)
# Create log for requests package
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True



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
    
    

MainWindowForm, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'mainwindow.ui'))


class MainWindowDialog(QtGui.QMainWindow, MainWindowForm):
    """
    Create main window - called by the "run" method in the plugin main class -
    with its features.
    
    """
    
    def __init__(self, parent=None):
        """Constructor."""
        super(MainWindowDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        self.initUI()
        # Time series attributes.
        self.dates = []
        self.values = []
        
        # SOS related attributes.
        self.sos_service_url = ''
        self.getcap_response = ''       # GetCapabilities response.
        
        self.WGS84bbox_set = set()      # Set which will contain the 
                                        # bounding box of each station and thus 
                                        # the identifier of each station as the 
                                        # spatial information is used to select
                                        # the station here.
        self.WGS84bbox_list = []
        self.selected_station_index = 0
        self.offering = ''
        self.observedproperty = ''
        self.unit = ''
        self.getobs_response = ''       # GetObservation response.
        
        
        # QGIS related attributes.
        #
        # Initialize station layer.
        self.stations_layer = QgsVectorLayer("Point?crs=epsg:4326", 
                                             "Features of interest", "memory")
        # Define "myint" attribute to store the id of the stations.
        self.stations_layer.dataProvider().addAttributes(
                                    [QgsField('myint', QtCore.QVariant.Int)]
                                    )
        self.stations_layer.updateFields()
        # Set the symbol used to visualize stations.
        self.station_symbol_layer = QgsSvgMarkerSymbolLayerV2(size=10)
        self.filepath = resolve('ic_place_black_48px.svg')
        self.station_symbol_layer.setPath(self.filepath)
        self.stations_layer.rendererV2().symbols()[0].changeSymbolLayer(
                                                0, self.station_symbol_layer)
                                                
        # Fill OfferingComboBox with all offerings of the newly selected
        # station from "Features of interest" vector layer - spatially 
        # selected in QGIS - each time the layer selection changes.
        self.stations_layer.selectionChanged.connect(self.fillOfferingComboBox)
        
        
        # Initialize calendars used to select time series starting- 
        # and ending time.
        self.start_calendar = CalendarWindow()
        self.start_calendar.setWindowTitle("Starting Time Selection")
        self.ending_calendar = CalendarWindow()
        self.ending_calendar.setWindowTitle("Ending Time Selection")
        
        # Initialize boolean to indicate if a time series has already been 
        # successfully retrieved, so that no additional GetObservation request
        # is sent when, for instance, exporting time series after having 
        # plotted it.
        self.getseries_boolean = False
        
        
    def resetGetSeriesBoolean(self):
        self.getseries_boolean = False
        
        
    def initUI(self):
        self.setWindowTitle('SOS Client')
        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Initialize first block of main window (SOS 2.0 server selection and 
        # general server information retrieval) related attributes and signals 
        # and slots connection management. 
        self.select_sos_server_pushButton.clicked.connect(
                                            self.showServerSelectionDialog)
        self.get_server_informaton_pushButton.clicked.connect(
                                            self.getServerInformation)
        
        # Initialize second block of main window (GetObservation request 
        # parameters selection) related attributes and signals and slots 
        # connection management. 
        self.select_offering_comboBox.currentIndexChanged.connect(
                                            self.fillObservedPropertiesComboBox)
        self.select_offering_comboBox.currentIndexChanged.connect(
                                            self.resetGetSeriesBoolean)
        self.starting_time_pushButton.clicked.connect(self.showStartCalendar)
        self.ending_time_pushButton.clicked.connect(self.showEndingCalendar)
        
        # Initialize third block of main window (plugin functionnalities, 
        # plot time series, visualize it in tabular format, export it) 
        # related attributes and signals and slots connection management. 
        self.plot_pushButton.clicked.connect(self.plotTimeSeries)
        self.table_view_pushButton.clicked.connect(self.arrayTimeSeries)
        self.export_as_csv_pushButton.clicked.connect(self.exportTimeSeries)
        

    ##########################################################################
    ####### First block of main window related functions. 
    ####### SOS 2.0 server selection and general server information retrieval
    ########################################################################## 
     
    def showServerSelectionDialog(self):
        text, ok = QtGui.QInputDialog.getText(self, 'SOS server selection', 
                                              'Enter sos service url:')
   
        if ok :
            # Reset attributes.
            #
            # Reset UI attributes.
            self.statusBar.clearMessage()
            
            # Second block of main window attributes.
            self.select_offering_comboBox.clear()
            self.select_prop_comboBox.clear()
            self.starting_time_pushButton.setText("")
            self.ending_time_pushButton.setText("")
            self.time_series_starting_time_value.setText("")
            self.time_series_ending_time_value.setText("")
    
            # QGIS related attributes.
            # Remove station features and get an empty station layer.
            listOfIds = [feat.id() for feat in self.stations_layer.getFeatures()]
            self.stations_layer.dataProvider().deleteFeatures(listOfIds)
            # Other attributes.
            self.getobs_response = ''
            self.getseries_boolean = False
            
            
            # Set attributes using retrieved SOS server information.
            #
            self.sos_service_url = str(text)
            self.getcap_response = requests.get(
                self.sos_service_url + '?REQUEST=GetCapabilities'
                '&SERVICE=SOS&ACCEPTVERSIONS=2.0.0', stream=True)
            self.sos = SensorObservationService(
                None,xml=self.getcap_response.content, version="2.0.0")
            self.WGS84bbox_set=set(WGS84conversion(off) for off in self.sos.offerings)
            self.WGS84bbox_list=list(self.WGS84bbox_set)
            # Set UI attributes
            self.selected_sos_server_lineEdit.setText(self.sos_service_url)
            
            
            if self.WGS84bbox_list == []:
                # Display error message using QMessageBox.
                empty_bbox_msg = QtGui.QMessageBox()
                empty_bbox_msg.setWindowTitle("Error")
                empty_bbox_msg.setTextFormat(QtCore.Qt.RichText)
                msg_text = (
                        'Each offering bounding box is empty when using '
                        'OWSLib with this SOS 2.0 server'
                    )
                empty_bbox_msg.setText(msg_text)
                i_text = (
                        'This plugin uses the Open Source '
                        '<a href=\"https://geopython.github.io/OWSLib/\">OWSlib library</a> '
                        'to retrieve SOS 2.0 data. When collecting offerings '
                        'and their corresponding featureOfInterest bounding '
                        'boxes, only empty lists were retrieved.'
                    )
                empty_bbox_msg.setInformativeText(i_text)
                d_text = (
                        'In order to solve the problem, you may want to have '
                        'a look at OWSlib documentation '
                        '(https://geopython.github.io/OWSLib/) and at the '
                        'Python source file '
                        '(https://github.com/geopython/OWSLib/blob/master/owslib/swe/observation/sos200.py/) '
                        'containing the offering class, including the '
                        'bounding box attribute.'
                    )
                empty_bbox_msg.setDetailedText(d_text)
                empty_bbox_msg.setIcon(QtGui.QMessageBox.Critical)
                empty_bbox_msg.exec_()
                
                # Reload station layer as selected SOS server has changed.
                self.stations_layer.triggerRepaint()
                
                
            elif self.WGS84bbox_list == [None]:
                # Display warning message using QMessageBox.
                none_bbox_msg = QtGui.QMessageBox()
                none_bbox_msg.setWindowTitle("Warning")
                none_bbox_msg.setTextFormat(QtCore.Qt.RichText)
                msg_text = (
                        "Each offering has 'None' bounding box when using "
                        "OWSLib with this SOS 2.0 server. This plugin uses "
                        "the Open Source "
                        "<a href=\"https://geopython.github.io/OWSLib/\">OWSlib library</a>"
                        " to retrieve SOS 2.0 data. When collecting the "
                        "featureOfInterest bounding box for each offering, "
                        "only None objects were retrieved. Consequently, "
                        "no feature of interest could be added to the "
                        "'Features of interest' layer generated by the plugin."
                    )
                none_bbox_msg.setText(msg_text)
                i_text = (
                        'Please select directly an offering in the "Offering" '
                        'combobox to unlock the "ObservedPropery" combobox. '
                        'You will then be able to select all GetObservation '
                        'request parameters and to retrieve desired '
                        'time series.'
                    )
                none_bbox_msg.setInformativeText(i_text)
                d_text = (
                        'In order to solve the problem, you may want to have '
                        'a look at OWSlib documentation '
                        '(https://geopython.github.io/OWSLib/) and at the '
                        'Python source file '
                        '(https://github.com/geopython/OWSLib/blob/master/owslib/swe/observation/sos200.py/) '
                        'containing the offering class, including the '
                        'bounding box attribute.'
                    )
                none_bbox_msg.setDetailedText(d_text)
                none_bbox_msg.setIcon(QtGui.QMessageBox.Warning)
                none_bbox_msg.exec_()
                
                # Reload station layer as selected SOS server has changed.
                self.stations_layer.triggerRepaint()
                
                # Fill OfferingComboBox with all offerings from stations  
                # which have None bbox.
                self.selected_station_index = 0
                station = self.WGS84bbox_list[self.selected_station_index]
                for o in GetOfferingsList(self.sos, station).offering_list:
                    self.select_offering_comboBox.addItem(o.id)
                    
                    
            else:
                # Stations bbox content is valid.
                # 
                # For each station...
                for i, s in enumerate(self.WGS84bbox_list):
                    # Define pairs of coordinates of two points which 
                    # generate the bounding box of this stations.
                    if s is not None:
                        
                        xmin = min(s[1], s[3])
                        xmax = max(s[1], s[3])
                        ymin = min(s[0], s[2])
                        ymax = max(s[0], s[2])
                        
                        # Create new point which represents the station. 
                        # Here, we choose to set station location using the point
                        # which has min lat and min long, as several SOS 2.0
                        # we have tested lead to two points coinciding. 
                        # Therefore, we make the assumption xmin==xmax and 
                        # ymin==ymax. 
                        # When it is not the case, station location is likely 
                        # to be incorrect.
                        # Further development is required to solve this issue.
                        new_feature = QgsFeature()
                        new_feature.setGeometry(QgsGeometry.fromPoint(
                                                    QgsPoint(xmin, ymin)))
                        new_feature.setAttributes([i])
                        self.stations_layer.dataProvider().addFeatures(
                                                    [new_feature])
                
                # Update layer and refresh QGIS canvas extent.
                self.stations_layer.updateExtents()
                QgsMapLayerRegistry.instance().addMapLayer(self.stations_layer)
                self.stations_layer.triggerRepaint()
                canvas = qgis.utils.iface.mapCanvas()
                canvas.setExtent(self.stations_layer.extent())
                
                # Inform user he/she has to spatially select a station from 
                # newly added 'Features of interest' layer. 
                foi_layer_msg = QtGui.QMessageBox()
                foi_layer_msg.setWindowTitle("Information")
                msg_text = (
                    'A "Features of interest" layer has been added to the map!')
                foi_layer_msg.setText(msg_text)
                i_text = (
                        'Please select a station of the "Features of interest" '
                        'layer using the select features tool of the QGIS '
                        'toolbar to unlock the "Offering" combobox and the '
                        '"ObservedPropery" combobox. You will then be able to '
                        'select all GetObservation request parameters and to '
                        'retrieve desired time series.'
                    )
                foi_layer_msg.setInformativeText(i_text)
                foi_layer_msg.setIcon(QtGui.QMessageBox.Information)
                foi_layer_msg.exec_()
        
        
        
    def getServerInformation(self):
        
        if self.sos_service_url != '' and self.sos_service_url is not None:
            getCapabilitiesSOS200(self.getcap_response)
        else:
            QtGui.QMessageBox.critical(
                    self, "Critical error", 
                    'SOS server has not been selected. Please select one '
                    'using the "Select SOS 2.0 server" button above.'
                )
                
                
    ##########################################################################
    ####### Second block of main window related functions. 
    ####### GetObservation request parameters selection.
    ##########################################################################     


    def fillOfferingComboBox(self):
        
        # Reset attributes.
        #
        # Reset UI attributes.
        self.statusBar.clearMessage()
        self.select_offering_comboBox.clear()
        self.select_prop_comboBox.clear()
        self.time_series_starting_time_value.setText("")
        self.time_series_ending_time_value.setText("")
        self.starting_time_pushButton.setText("")
        self.ending_time_pushButton.setText("")
        
        # Get selected station.
        features_list = self.stations_layer.selectedFeatures()
        
        try:
            feat = features_list[0]
            self.selected_station_index = feat['myint'] # selected station 
                                                        # is identified by an
                                                        # index which is stored
                                                        # as "myint" attribute
                                                        # value of selected 
                                                        # feature of 'Features 
                                                        # of interest' layer
            station = self.WGS84bbox_list[self.selected_station_index]
            for o in GetOfferingsList(self.sos, station).offering_list:
                self.select_offering_comboBox.addItem(o.id)
                
        except IndexError:
            pass
        
        
    def fillObservedPropertiesComboBox(self):
        
        # Reset attributes.
        #
        # Reset UI attributes.
        self.statusBar.clearMessage()
        self.select_prop_comboBox.clear()
        
        # Fill observed properties combo box.
        station = self.WGS84bbox_list[self.selected_station_index]
        off = (
                GetOfferingsList(self.sos, station)
                .offering_list[self.select_offering_comboBox.currentIndex()]
            )
        for p in off.observed_properties:
            self.select_prop_comboBox.addItem(p)
            
        # Set UI attributes related to selected offering, as it has changed.
        #
        # Set a minimum and a maximum date so that the calendar used to select 
        # time series starting time prevents user from selecting a date earlier
        # than the begin position of the selected offering or later than its
        # end position.
        self.start_calendar.cal.setMinimumDate(
                QtCore.QDateTime(off.begin_position).date()
            )
        self.start_calendar.cal.setMaximumDate(
                QtCore.QDateTime(off.end_position).date()
            )
        # Set a maximum date so that the calendar used to select time series 
        # ending time preventts user from selecting a date later than the 
        # end position of the selected offering. 
        # 
        # Later, a minimum date will be set according to the starting date 
        # selected by the user. 
        self.ending_calendar.cal.setMaximumDate(
                QtCore.QDateTime(off.end_position).date()
            )
        # Default time period is set to 2 days to prevent user from waiting
        # a very long time for the GetObservation response retrieval.
        self.start_calendar.cal.setSelectedDate(
                QtCore.QDateTime(off.end_position - datetime.timedelta(days=2))
                .date()
            )
        # Default ending time is set according to end position of selected 
        # offering.
        self.ending_calendar.cal.setSelectedDate(
                QtCore.QDateTime(off.end_position).date()
            )
        #  Update UI attributes text to inform user of every change.
        self.starting_time_pushButton.setText(
                self.start_calendar.cal.selectedDate().toString()
            )
        self.ending_time_pushButton.setText(
                self.ending_calendar.cal.selectedDate().toString()
            )
        self.time_series_starting_time_value.setText(
                QtCore.QDateTime(off.begin_position).date().toString()
            )
        self.time_series_ending_time_value.setText(
                QtCore.QDateTime(off.end_position).date().toString()
            )
        
    # Create several functions to get a dynamic time management in both 
    # starting time and ending time selection calendars.
    def showStartCalendar(self):
        
        self.start_calendar.show()
        self.start_calendar.cal.clicked.connect(self.changeStartingTimeButtonText)
        self.start_calendar.cal.clicked.connect(self.closeStartCalendar)
        self.start_calendar.cal.clicked.connect(self.changeEndingCalendarMinimumDate)
    
    def changeStartingTimeButtonText(self, date):
        self.starting_time_pushButton.setText(date.toString())
        self.getseries_boolean = False 
        
    def closeStartCalendar(self):
        self.start_calendar.hide()
        
    def changeEndingCalendarMinimumDate(self, date):
        self.ending_calendar.cal.setMinimumDate(date.addDays(1))
        
    def showEndingCalendar(self):
        
        self.ending_calendar.show()
        self.ending_calendar.cal.clicked.connect(self.changeEndingTimeButtonText)
        self.ending_calendar.cal.clicked.connect(self.closeEndingCalendar)
    
    def changeEndingTimeButtonText(self, date):
        self.ending_time_pushButton.setText(date.toString())
        self.getseries_boolean = False
        
    def closeEndingCalendar(self):
        self.ending_calendar.hide()
        
        
    ##########################################################################
    ####### Third block of main window related functions. 
    ####### Plugin functionnalities:
    ####### Display time series in tabular, plot time series, 
    ####### export time series.
    ########################################################################## 
        
        
    def getObservation(self, *args):
        
        starting_time = QtCore.QDateTime(
            self.start_calendar.cal.selectedDate()).toPyDateTime()
        ending_time = QtCore.QDateTime(
            self.ending_calendar.cal.selectedDate()).toPyDateTime()
        
        try:
            self.statusBar.showMessage('Request in progress')
            
            if len(args)==1:        # Check if user has asked for a timeout.
                (self.dates, 
                 self.values, 
                 self.offering, 
                 self.observedproperty, 
                 self.unit, 
                 self.getobs_response) = getSeriesSOS200(
                                 self.sos,
                                 self.selected_station_index,
                                 self.select_offering_comboBox.currentIndex(),
                                 self.select_prop_comboBox.currentIndex(),
                                 starting_time,
                                 ending_time, 
                                 timeout=args[0])
            else:
                (self.dates, 
                 self.values, 
                 self.offering, 
                 self.observedproperty, 
                 self.unit, 
                 self.getobs_response) = getSeriesSOS200(
                                 self.sos,
                                 self.selected_station_index,
                                 self.select_offering_comboBox.currentIndex(),
                                 self.select_prop_comboBox.currentIndex(),
                                 starting_time,
                                 ending_time)
                                 
            self.getseries_boolean = True   # From now on a time series has 
                                            # already been successfully 
                                            # retrieved.
            
        except requests.exceptions.Timeout: 
            # Inform user timeout has elapsed.
            self.getobs_response = ''
            QtGui.QMessageBox.critical(
                    self, "Timeout error", 
                    "The timeout has expired. Please change it and try again."
                )
            self.statusBar.showMessage(
                    'Failed to retrieve time series as timeout has expired') 
            
        except:
            # Inform user that an error occured and print traceback.
            error_traceback = traceback.format_exc()
            
            getobs_error_msg = QtGui.QMessageBox()
            getobs_error_msg.setWindowTitle("Error")
            getobs_error_msg.setTextFormat(QtCore.Qt.RichText)
            getobs_error_msg.setText(
                    'Unexpected GetObservation request error. Something went '
                    'wrong when we asked this SOS 2.0 server for the '
                    'GetObservation response. Please make sure this '
                    'GetObservation request leads to a working response from '
                    'a browser.'
                )
            getobs_error_msg.setInformativeText(
                    'This plugin uses the Open Source '
                    '<a href=\"https://geopython.github.io/OWSLib/\">'
                    'OWSlib library</a> to retrieve SOS 2.0 data. In order '
                    'to fix this error, you might want to take a look at the '
                    'Python Error traceback below.'
                )
            getobs_error_msg.setDetailedText(error_traceback)
            getobs_error_msg.setIcon(QtGui.QMessageBox.Critical)
            getobs_error_msg.exec_()
            
            self.statusBar.showMessage(
                    'Failed to retrieve time series for unexpected error')  
        
        
    def getTimeSeries(self):
        
        # Prepare for GetObservation response retrieval step.
        self.statusBar.clearMessage()
        # Reset attributes.
        self.dates = []
        self.values = []
        self.offering = ''
        self.observedproperty = ''  
        self.getobs_response = ''
        ending_time = QtCore.QDateTime(
                    self.ending_calendar.cal.selectedDate()).toPyDateTime()
        starting_time = QtCore.QDateTime(
                    self.start_calendar.cal.selectedDate()).toPyDateTime()
        
        
        # GetObservation response retrieval step.
        #
        # Ask user if he/she wants to set a timeout value, as getting a 
        # response to a GetObservation request can take a long time.
        timeout_value = None
        timeout_option = QtGui.QMessageBox.question(
                self, "Timeout option", 
                "Parsing the response from a SOS GetObservation request can "
                "be very long. Would you like to set a request timeout?", 
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes
            )
        
        if timeout_option == QtGui.QMessageBox.Yes:
            # If user says "Yes", create a dialog window and retrieve input 
            # timeout value.
            timeout_value, ok = QtGui.QInputDialog.getInt(
                    self, "Timeout value selection", 
                    "Please enter a timeout value in seconds (integer):", 
                    value=60, min=0, max=7200
                )
            timeout_value = abs(timeout_value)
            
            if ok:
                # Launch GetObservation request with timeout_value as 
                # additional argument.
                self.getObservation(timeout_value)
        
        elif (ending_time - starting_time > datetime.timedelta(days=3)):
            # If time period is longer than 3 days, inform user time series 
            # retrieval may take some time.
            QtGui.QMessageBox.information(
                    self, "Information", 
                    "Time series retrieval may take some time"
                )
            # Launch GetObservation request with no additional arguments.
            self.getObservation()
                
        else:
            self.getObservation()
        
        
        # GetObservation response retrieval step is over.
        # Inform user about it, and about recognized errors if needed.
        #
        # Recognized errors.
        if self.dates == []:
            
            # Inform user that date and time column of retrieved time series
            # is empty.
            empty_dates_msgbox = QtGui.QMessageBox()
            empty_dates_msgbox.setWindowTitle("Empty dates list warning")
            empty_dates_msgbox.setText(
                    "WARNING: retrieval of time series time data failed! "
                    "Please make sure this GetObservation request leads to a "
                    "working response from a browser, and retry."
                )
            empty_dates_msgbox.setInformativeText(
                    "You might want to take a look at the request XML "
                    "reponse below!"
                )
            if not self.getobs_response:
                empty_dates_msgbox.setDetailedText(
                    "Empty GetObservation response")
            else:
                empty_dates_msgbox.setDetailedText(self.getobs_response)
            empty_dates_msgbox.setIcon(QtGui.QMessageBox.Warning)
            empty_dates_msgbox.exec_()
            
        elif self.values == []:
            
            empty_values_msgbox = QtGui.QMessageBox()
            empty_values_msgbox.setWindowTitle(
                    "Empty observations results values list warning")
            empty_values_msgbox.setText(
                    "WARNING: retrieval of time series y-axis data failed. "
                    "Please make sure this GetObservation request leads to a "
                    "working response from a browser, and retry."
                )
            empty_values_msgbox.setInformativeText(
                    "You might want to take a look at the request XML "
                    "reponse below!"
                )
            if not self.getobs_response:
                empty_dates_msgbox.setDetailedText(
                    "Empty GetObservation response")
            else:
                empty_dates_msgbox.setDetailedText(self.getobs_response)
            empty_values_msgbox.setIcon(QtGui.QMessageBox.Warning)
            empty_values_msgbox.exec_()
        
        else:                                           # No error occured.
            QtGui.QMessageBox.information(
                    self, "Information", 
                    "Time series retrieval is finished"
                )
                
        self.statusBar.clearMessage()
        self.statusBar.showMessage('Time series retrieval process is over')
        
        
    def arrayTimeSeries(self):
        
        if not self.getseries_boolean:
            # Time series has not been retrieved yet.
            # Reset GetObservation response attribute.
            self.getobs_response = ''
            self.getTimeSeries()
        arraySeries(self.dates, self.values, self.observedproperty, self.unit)
        
        
    def plotTimeSeries(self):
        
        if not self.getseries_boolean:
            # Time series has not been retrieved yet.
            # Reset GetObservation response attribute.
            self.getobs_response = ''
            self.getTimeSeries()
        plotSeries(self.dates, self.values, self.observedproperty, self.unit)
        
        
    def exportTimeSeries(self):
        
        if not self.getseries_boolean:
            # Time series has not been retrieved yet.
            # Reset GetObservation response attribute.
            self.getobs_response = ''
            self.getTimeSeries()
        
        # Get path for export from QFileDialog.
        path = QtGui.QFileDialog.getSaveFileName(
                self, 'Export Time Series', self.offering + ".csv", '*.csv')
        exportSeries(
                self.dates, self.values, self.observedproperty, self.unit, path)
        
 