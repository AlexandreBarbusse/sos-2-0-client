# QGIS SOS 2.0 Client plugin
This QGIS Plugin is a client for OGC Sensor Observation Service 2.0 (SOS 2.0). 
It retrieves observations data from OGC SOS (Sensor Observation Service) 2.0 servers, and then allows you to visualise and download these data.     

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
   
4. A "Features of interest" layer as now been added to your current QGIS session. This layer indicates the locations of all the measurement stations whose measurement data are stored on the selected SOS server. Put this layer at the top of the list of layers, and then zoom to the layer to isualise all the stations.

5. Click on the "Get server information" button if you wish to... get general information on the selected SOS server.     

   ![press_get_server_info](https://user-images.githubusercontent.com/20395133/28581852-c23636e0-7163-11e7-8bb1-1e9b8e6d7ad7.png)    
 
	


