# QGIS SOS 2.0 Client plugin
This QGIS Plugin is a client for OGC Sensor Observation Service 2.0 (SOS 2.0). 
It retrieves observations data from OGC SOS (Sensor Observation Service) 2.0 servers, and then allows you to visualise and download these data.  


## Table of contents    
 * [QGIS SOS 2.0 Client plugin](#qgis-sos-20-client-plugin)
  * [Table of contents](#table-of-contents)
  * [Installation](#installation)
  * [Usage example](#usage-example)
  * [Release History](#release-history)
  * [Meta](#meta)
  * [Contributing](#contributing)

## Installation    
1. Click on the "Clone or download" button of this GitHub project. 

   ![press_clone_or_download_red](https://user-images.githubusercontent.com/20395133/28575415-25421f3c-7151-11e7-97b4-aaf707255e0e.png)      


2. Download the .zip file containing the QGIS sos-2-0-client plugin.      

   ![press_download_zip_red](https://user-images.githubusercontent.com/20395133/28575446-3bc776e4-7151-11e7-8f17-d7d298d7f1a8.png)              

3. Move or copy-paste the .zip file to your QGIS plugins directory:
   ```
   ~/.qgis2/python/plugins/
   ```
    ![move_to_plugin_repository_red_2](https://user-images.githubusercontent.com/20395133/28575484-5273580e-7151-11e7-9512-3cb04730a730.png)      

4. Unzip the .zip file in your QGIS plugins directory to get the plugin folder.

5. Open QGIS.

6. Click on Plugins ‣ Manage and Install Plugins.... to open the Plugin Manager dialog.

7. Type "sos" into the search field to find the "SOS 2.0 Client" plugin.      

   ![tape_in_sos_red](https://user-images.githubusercontent.com/20395133/28575533-7b359a2c-7151-11e7-81bd-93d93fcbb807.png)              
   
8. Check on the checkbox next to "SOS 2.0 Client" Plugin. This will enable the plugin and you will be able to use it.          

   ![load_sos_2_0_red](https://user-images.githubusercontent.com/20395133/28575657-dd3f54ec-7151-11e7-95ab-a84fd6f78d33.png)    
   


## Usage example

In this section, we'll take a look at how you can use every feature of the plugin.

1. Click on the black and white "SOS" icon in the QGIS toolbar.                 

   ![press_sos_2_0_client_button](https://user-images.githubusercontent.com/20395133/28576345-0817b2f2-7154-11e7-859b-ac8031bead32.png)        
   
2. The client main dialog window opens. Click on the "Select SOS 2.0 server" button at the top.     

   ![press_select_sos_server](https://user-images.githubusercontent.com/20395133/28576984-b1c9dec8-7155-11e7-861d-2503abcfb8ed.png) 
   
3. The SOS server selection dialog window opens. Enter a valid SOS 2.0 server service URL in the line edit and press ok. In this example, we will use [this SOS server service URL](http://insitu.webservice-energy.org/52n-sos-webapp/sos), which you can also find in the [sample data text file](/test/sample_data.txt) in the test folder of the plugin .  

   ![enter_sos_url](https://user-images.githubusercontent.com/20395133/28578028-c29d9c5a-7158-11e7-87c9-01381ceb944f.png) 
   
4. A "Features of interest" layer as now been added to your current QGIS session. This layer indicates the locations of all the measurement stations whose measurement data are stored on the selected SOS server. Put this layer at the top of the list of layers, and then zoom to the layer to visualise all the stations.

5. Click on the "Get server information" button if you wish to... get general information on the selected SOS server.     

   ![press_get_server_info](https://user-images.githubusercontent.com/20395133/28581852-c23636e0-7163-11e7-8bb1-1e9b8e6d7ad7.png)
   
6. Now we would like to select a station of the "Features of interest" layer to retrieve its measurement data. So first we need to click on the selection icon in QGIS menu toolbar.    

   ![qgis_toolbar_selection](https://user-images.githubusercontent.com/20395133/28582596-4913e084-7166-11e7-9a37-6f83ad753167.png)    
   
7. And then we select a station.     

   ![select_station](https://user-images.githubusercontent.com/20395133/28582930-8c80f626-7167-11e7-8e4e-fd07752a71e9.png)
   
8. Default GetObservation request parameters are now set. Select an offering.     

   ![offering_selection](https://user-images.githubusercontent.com/20395133/28583494-a81ceec4-7169-11e7-820b-479c8c8c7052.png)
   
9. Select an observed property.     

   ![observed_property_selection](https://user-images.githubusercontent.com/20395133/28583677-4e8c0c68-716a-11e7-97aa-ae669b6aab2c.png)

10. Select time series starting and ending times.

    ![select_time_period](https://user-images.githubusercontent.com/20395133/28584078-b35d493a-716b-11e7-9836-e83c96c8a76d.png)
    
11. Now we are ready for measurement time series retrieval. Click on one of the three main features buttons ("Plot", "Table view", "Export as CSV file") at the bottom of the client dialog window. A pop-up dialog window opens which asks you if you wish to set a timeout for GetObservation request:

    ![timeout_option](https://user-images.githubusercontent.com/20395133/28584450-1a755bd4-716d-11e7-8969-619cf2f0c56b.png)
    
12. If you press yes, a new pop-up window allows you to set the timeout.

    ![timeout_value](https://user-images.githubusercontent.com/20395133/28584890-a2a6f1e2-716e-11e7-83cf-fab3086110b8.png)  
    
13. Then we have to wait for the SOS server to send us the GetObservation response. Once time series retrieval process is over, a pop-up window will open.

    ![time_series_retrieval_info](https://user-images.githubusercontent.com/20395133/28585100-79998624-716f-11e7-87ca-eac5a5154541.png)
    
14. Now we get, according to which main feature button we have clicked:
    
    *   A tabular containing the retrieved time series:

        ![table_result](https://user-images.githubusercontent.com/20395133/28585728-6e1206da-7171-11e7-9867-1eb27eb535ac.png) 
	
    *   A time series plot:

        ![plot_result](https://user-images.githubusercontent.com/20395133/28585838-f0b8e6d0-7171-11e7-90e7-97f0f2a0616e.png)    
     
    *   A window for export:

        ![export_result](https://user-images.githubusercontent.com/20395133/28585970-6fefef48-7172-11e7-9970-8f1d749976e7.png)  

## Release History

* 1.0.0-beta
    * First release for beta testing
    
## Meta

Alexandre Barbusse, MINES ParisTech / ARMINES – alexandre.barbusse@gmail.com

The development of this plugin is an initiative carried out by the [center Observation, Impacts, Energy (O.I.E.)](http://www.mines-paristech.eu/Research-valorization/Fields-of-Research/Energy-and-processes/O.I.E.-Centre-Observation-Impacts-Energy/) of MINES ParisTech / ARMINES (contact: lionel.menard@mines-paristech.fr)

The minimum version of QGIS required to use this plugin is 2.0.

This QGIS plugin is distributed under the [BSD licence](/LICENSE) (GPL compatible). 


## Contributing

1. Fork it (<https://github.com/AlexandreBarbusse/sos-2-0-client/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request




 
	


