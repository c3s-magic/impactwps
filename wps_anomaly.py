from pywps.Process import WPSProcess

import icclim
import icclim.util.callback as callback

import dateutil.parser
from datetime import datetime
import os
from os.path import expanduser
from mkdir_p import *

transfer_limit_Mb = 100

    
class ProcessSimpleIndice(WPSProcess):


    def __init__(self):
        WPSProcess.__init__(self,
                            identifier = 'wps_anomaly', # only mandatary attribute = same file name
                            title = 'AnomalyCalculation',
                            abstract = 'Calculates an anomaly of a variable: average of a long period compared to a base reference period (e.g. 2071-2100 compared to 1971-2000 for example).',
                            version = "1.0",
                            storeSupported = True,
                            statusSupported = True,
                            grassLocation =False)


        self.filesIn = self.addLiteralInput(identifier = 'files',
                                               title = 'Input netCDF files list',
                                               abstract="application/netcdf",
                                               type=type("S"),
                                               minOccurs=0,
                                               maxOccurs=1024,
                                               default = 'http://opendap.knmi.nl/knmi/thredds/dodsC/IS-ENES/TESTSETS/tasmax_day_EC-EARTH_rcp26_r8i1p1_20060101-20251231.nc,'+
                                                          'http://opendap.knmi.nl/knmi/thredds/dodsC/IS-ENES/TESTSETS/tasmax_day_EC-EARTH_rcp26_r8i1p1_20760101-21001231.nc')
                                                
        self.varNameIn = self.addLiteralInput(identifier = 'varName',
                                               title = 'Variable name to process',
                                               type="String",
                                               default = 'tasmax')
        

        self.timeRangeIn = self.addLiteralInput(identifier = 'timeRange', 
                                               title = 'Time range, e.g. 2010-01-01/2012-12-31',
                                               type="String",
                                               default = None)
        
        self.timeRangeRef = self.addLiteralInput(identifier = 'timeRangeRef', 
                                               title = 'Time range Reference Period, e.g. 2010-01-01/2012-12-31',
                                               type="String",
                                               default = None)
        
        self.outputFileNameIn = self.addLiteralInput(identifier = 'outputFileName', 
                                               title = 'Name of output netCDF file',
                                               type="String",
                                               default = 'out_icclim.nc')
        
        
        self.NLevelIn = self.addLiteralInput(identifier = 'NLevel', 
                                               title = 'Number of level (if 4D variable)',
                                               type="String",
                                               default = None)

        self.opendapURL = self.addLiteralOutput(identifier = "opendapURL",title = "opendapURL");   
        
    def callback(self,message,percentage):
        self.status.set("%s" % str(message),str(percentage));

    
    def execute(self):
        # Very important: This allows the NetCDF library to find the users credentials (X509 cert)
        homedir = os.environ['HOME']
        os.chdir(homedir)
        
        def callback(b):
          self.callback("Processing",b)
         
        files = [];
        files.extend(self.filesIn.getValue())
        var = self.varNameIn.getValue()
        time_range = self.timeRangeIn.getValue()
        time_range_ref = self.timeRangeRef.getValue()
        out_file_name = self.outputFileNameIn.getValue()
        level = self.NLevelIn.getValue()
        
        if(level == "None"):
            level = None
          
        if(time_range == "None"):
            time_range = None
        else:
            startdate = dateutil.parser.parse(time_range.split("/")[0])
            stopdate  = dateutil.parser.parse(time_range.split("/")[1])
            time_range = [startdate,stopdate]

        startdate_ref = dateutil.parser.parse(time_range_ref.split("/")[0])
        stopdate_ref = dateutil.parser.parse(time_range_ref.split("/")[1])
        time_range_ref = [startdate_ref,stopdate_ref]

                      
        self.status.set("Preparing....", 0)
        
        pathToAppendToOutputDirectory = "/WPS_"+self.identifier+"_" + datetime.now().strftime("%Y%m%dT%H%M%SZ")
        
        """ URL output path """
        fileOutURL  = os.environ['POF_OUTPUT_URL']  + pathToAppendToOutputDirectory+"/"
        
        """ Internal output path"""
        fileOutPath = os.environ['POF_OUTPUT_PATH']  + pathToAppendToOutputDirectory +"/"

        """ Create output directory """
        mkdir_p(fileOutPath)
        

        self.status.set("Processing input list: "+str(files),0)
        
        my_indice_params = {'indice_name': 'ANOM',
                            'calc_operation': 'anomaly',
                           }

        icclim.indice(user_indice=my_indice_params, 
                        in_files=files,
                        var_name=var,
                        time_range=time_range,
                        out_file=fileOutPath+out_file_name,
                        threshold=None,
                        N_lev=level,
                        transfer_limit_Mbytes=transfer_limit_Mb,
                        callback=callback,
                        callback_percentage_start_value=0,
                        callback_percentage_total=100,
                        base_period_time_range=time_range_ref,
                        window_width=5,
                        only_leap_years=False,
                        ignore_Feb29th=True,
                        interpolation='hyndman_fan',
                        netcdf_version='NETCDF4_CLASSIC',
                        out_unit='days')

        
        """ Set output """
        url = fileOutURL+"/"+out_file_name;
        self.opendapURL.setValue(url);
        self.status.set("ready",100);
        
        
