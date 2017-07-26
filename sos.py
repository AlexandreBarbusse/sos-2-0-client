# -*- coding: utf-8 -*-

# =============================================================================
# Copyright (c) ARMINES / MINES ParisTech 
# Created by Alexandre Barbusse <alexandre.barbusse@gmail.com>
#
# this file is available under the BSD 3-clause License
# (https://opensource.org/licenses/BSD-3-Clause)
# =============================================================================




from qgis.core import *

from owslib.etree import etree
from owslib.sos import SensorObservationService
from owslib.swe.observation import sos200
from owslib.swe.observation import sos100
from ui.gui import GetCapabilityWindow
        



def WGS84conversion(off):
    """
    Make sure that offering spatial information is based on WGS84 
    coordinate reference system.
    
    argument: 
        >>> off: 
            owslib.swe.observation.sos200 offering object as defined by OWSLib 
            library.
    
    return values:
        >>> (wgs84_bottom, wgs84_left, wgs84_top, wgs84_right):
            tuple containing 2 lat/long pairs of coordinates from two points 
            creating a bounding box as defined by SOS standard and retrieved 
            by OWSLib library.
    """
    
    try:
        former_srs = QgsCoordinateReferenceSystem(off.bbox_srs.getcode())
        wgs84 = QgsCoordinateReferenceSystem('EPSG:4326')
        transformer = QgsCoordinateTransform(former_srs, wgs84) 
        
        former_left = off.bbox[0]
        former_bottom = off.bbox[1]
        wgs84_left, wgs84_bottom = transformer.transform(former_left, 
                                                         former_bottom)
        former_right = off.bbox[2]
        former_top = off.bbox[3]                                                 
        wgs84_right, wgs84_top = transformer.transform(former_right,
                                                       former_top)
    
        return (wgs84_bottom, wgs84_left, wgs84_top, wgs84_right)
        
    except:
        
        if off.bbox is not None:
            left = off.bbox[0]
            bottom = off.bbox[1]
            right = off.bbox[2]
            top = off.bbox[3]  
            return (bottom, left, top, right)
            
        else:
            return off.bbox



class GetOfferingsList:
    """
    Create a list of offering when given a station of a given SOS 2.0 
    server, using its WGS84 spatial information to identify 
    this station. 
    
    """
    
    def __init__(self, sos, WGS84bbox):
        self.offering_list = []
        for off in sos.offerings:
            if WGS84conversion(off) == WGS84bbox:
                self.offering_list.append(off)
                
 
               
def getCapabilitiesSOS200(getcap_response):
    """
    Retrieve information from GetCapabilities response,
    and then show the window displaying it.
    
    argument: 
        >>> getcap_response: 
            class 'requests.models.Response' object containing GetCapabilities 
            request response retrieved from HTTP "Get" response.

    """
    
    global cap_window
    # Use GetCapabilityWindow() imported from gui module 
    # located in "ui" subdirectory. 
    cap_window = GetCapabilityWindow()
    
    sos = SensorObservationService(None,xml=getcap_response.content)
    sos_id = sos.identification
    cap_window.title_value.setPlainText(sos_id.title)
    cap_window.abstract_value.setPlainText(sos_id.abstract)
    
    p = sos.provider
    cap_window.provider_name_value.setPlainText(p.name)
    cap_window.provider_website_value.setPlainText(p.url)
    
    sc = p.contact
    cap_window.contact_phone_value.setText(sc.phone)
    cap_window.contact_email_value.setText(sc.email)
    cap_window.contact_address_value.setText(sc.address)
    cap_window.contact_city_value.setText(sc.city)
    cap_window.contact_region_value.setText(sc.region)
    cap_window.contact_postcode_value.setText(sc.postcode)
    cap_window.contact_country_value.setText(sc.country)
    
    cap_window.show()



def getSeriesSOS200(sos, station_number, offering_number, property_number, 
                    user_starting_time, user_ending_time, **kwargs):
    """
    Launch GetObservation request using OWSLib library,
    and retrieve useful data from the response.
    
    arguments: 
        >>> sos: 
            class 'owslib.swe.observation.sos200.SensorObservationService_2_0_0'
            object.
        >>> station_number: 
            index (int) number of the station in WGS84bbox_list.
        >>> offering_number: 
            -- index number of the offering among in offerings_list 
            of selected station.
        >>> property_number: 
            index number of the observed property in observed_properties list 
            of selected offering.
        >>> user_starting_time: 
            datetime object indicating desired starting time of time series 
            for GetObservation request.
        >>> user_ending_time:
            datetime object indicating desired ending time of time series 
            for GetObservation request.
        >>> **kwargs: 
            additional arguments. For this plugin, only a timeout argument 
            will be added.
    
    return values:
        >>> dates:
            list of 'datetime.datetime' objects containing entries of 
            time series date and time column.
        >>> values: 
            list of float objects containing entries of time series value 
            column.
        >>> selected_offering:
            (string).
        >>> prop: 
            selected observed property (string).
        >>> unit: 
            unit of measured observed property (string).
        >>> response1:
            GetObservation response (string).      
    
    """
    
    dates = []
    values = []
    unit = ''
    
    #
    # Defining request parameters.                   
    #
    
    WGS84bbox_set=set(WGS84conversion(off) for off in sos.offerings)
    WGS84bbox_list=list(WGS84bbox_set)
                    
    # Selecting station.
    station = WGS84bbox_list[station_number]
    
    # Selecting offerings.
    off = GetOfferingsList(sos, station).offering_list[offering_number]
    offerings = [off.id]
    selected_offering = off.id
    
    # Selecting observed property.
    prop = off.observed_properties[property_number]
    observedProperties = [prop]
    
    # Selecting format.
    omFormat = 'http://www.opengis.net/om/2.0'
        
    # Adding namespace.
    namespace = 'xmlns(om,http://www.opengis.net/om/2.0)'
         
    # Selecting time period.
    iso_period_starting_time = user_starting_time.isoformat()
    iso_period_ending_time = user_ending_time.isoformat()
    event_time = "om:phenomenonTime," + str(iso_period_starting_time) + "/" + str(iso_period_ending_time)
    
    
    #
    # Launch GetObservation request 
    #
    
    try:
        response1 = sos.get_observation(responseFormat=omFormat, 
                                        offerings=offerings, 
                                        observedProperties=observedProperties, 
                                        eventTime=event_time, 
                                        namespaces=namespace, 
                                        **kwargs)
        xml_tree = etree.fromstring(response1)
        parsed_response = sos200.SOSGetObservationResponse(xml_tree)
        try:
            unit = parsed_response.observations[0].get_result().uom
        except:
            pass
            
        for i, obs in enumerate(parsed_response.observations):
            if obs.resultTime is not None and obs.get_result().value is not None:
                dates.append(obs.resultTime)
                values.append(obs.get_result().value)
            else:
                pass
    
        return dates, values, selected_offering, prop, unit, response1
        
           
    except:
        raise
        
    






 