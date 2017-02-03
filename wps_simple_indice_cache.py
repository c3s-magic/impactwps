from pywps.Process import WPSProcess

import icclim
import icclim.util.callback as callback

import dateutil.parser
from datetime import datetime
import os
from os.path import expanduser
from mkdir_p import *

#Added for supporting cache
import logging
import clipccache as _clipccache
#End

transfer_limit_Mb = 100

    
class ProcessSimpleIndice(WPSProcess):


    def __init__(self):
        WPSProcess.__init__(self,
                            identifier = 'wps_simple_indice_cache.py', # only mandatary attribute = same file name
                            title = 'SimpleIndices',
                            abstract = 'Computes single input indices of temperature TG, TX, TN, TXx, TXn, TNx, TNn, SU, TR, CSU, GD4, FD, CFD, ID, HD17; of rainfal: CDD, CWD, RR, RR1, SDII, R10mm, R20mm, RX1day, RX5day; and of snowfall: SD, SD1, SD5, SD50.',
                            version = "1.0",
                            storeSupported = True,
                            statusSupported = True,
                            grassLocation =False)


        self.indiceNameIn = self.addLiteralInput(identifier = 'indiceName',
                                               title = 'Indice name',
                                               type="String",
                                               default = 'SU')        

        self.indiceNameIn.values = ["TG","TX","TN","TXx","TXn","TNx","TNn","SU","TR","CSU","GD4","FD","CFD","ID","HD17","CDD","CWD","PRCPTOT","RR1","SDII","R10mm","R20mm","RX1day","RX5day","SD","SD1","SD5cm","SD50cm"]


        self.sliceModeIn = self.addLiteralInput(identifier = 'sliceMode',
                                              title = 'Slice mode (temporal grouping to apply for calculations)',
                                              type="String",
                                              default = 'year')
        self.sliceModeIn.values = ["year","month","ONDJFM","AMJJAS","DJF","MAM","JJA","SON"]


        self.thresholdIn = self.addLiteralInput(identifier = 'threshold', 
                                               title = 'Threshold(s) for certain indices (SU, CSU and TR). Can be a comma separated list, e.g. 20,21,22',
                                               type=type("S"),
                                               minOccurs=0,
                                               maxOccurs=1024,
                                               default = None)

       
        self.filesIn = self.addLiteralInput(identifier = 'files',
                                               title = 'Input netCDF files list',
                                               abstract="application/netcdf",
                                               type=type("S"),
                                               minOccurs=0,
                                               maxOccurs=1024,
                                               default = 'http://aims3.llnl.gov/thredds/dodsC/cmip5_css02_data/cmip5/output1/CMCC/CMCC-CM/rcp85/day/atmos/day/r1i1p1/tasmax/1/tasmax_day_CMCC-CM_rcp85_r1i1p1_20060101-20061231.nc')
        
                                                
        self.varNameIn = self.addLiteralInput(identifier = 'varName',
                                               title = 'Variable name to process',
                                               type="String",
                                               default = 'tasmax')
        

        self.timeRangeIn = self.addLiteralInput(identifier = 'timeRange', 
                                               title = 'Time range, e.g. 2010-01-01/2012-12-31',
                                               type="String",
                                                default = '2006-01-01/2006-12-31')
        
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

	#Added for supporting cache
	#Change the db connection parameter (if needed)
	cache = _clipccache.clipccache(username='root', password='abcd', server='127.0.0.1', port=5432, homedir=homedir)
        result = cache.cache_search(self, None)
        if result is not None:
                #return already computed results
                self.opendapURL.setValue(result);
                logging.debug("Found Result in cache " + self.opendapURL.value)
                self.status.set("ready",100);
                return
        #End

        def callback(b):
          self.callback("Processing",b)
         
        files = [];
        files.extend(self.filesIn.getValue())
        var = self.varNameIn.getValue()
        indice_name = self.indiceNameIn.getValue()
        slice_mode = self.sliceModeIn.getValue()
        time_range = self.timeRangeIn.getValue()
        out_file_name = self.outputFileNameIn.getValue()
        level = self.NLevelIn.getValue()
        thresholdlist = self.thresholdIn.getValue()
        thresh = None
        
        if(level == "None"):
            level = None
            
          
        if(time_range == "None"):
            time_range = None
        else:
            startdate = dateutil.parser.parse(time_range.split("/")[0])
            stopdate  = dateutil.parser.parse(time_range.split("/")[1])
            time_range = [startdate,stopdate]
            
          
        if(thresholdlist != "None"):
            if(thresholdlist[0]!="None"):
                thresh = []
                for threshold in thresholdlist:
                    thresh.append(float(threshold))
        
      
        self.status.set("Preparing....", 0)
        
        pathToAppendToOutputDirectory = "/WPS_"+self.identifier+"_" + datetime.now().strftime("%Y%m%dT%H%M%SZ")
        
        """ URL output path """
        fileOutURL  = os.environ['POF_OUTPUT_URL']  + pathToAppendToOutputDirectory+"/"
        
        """ Internal output path"""
        fileOutPath = os.environ['POF_OUTPUT_PATH']  + pathToAppendToOutputDirectory +"/"

        """ Create output directory """
        mkdir_p(fileOutPath)
        

        self.status.set("Processing input list: "+str(files),0)
        
        icclim.indice(indice_name=indice_name,
                        in_files=files,
                        var_name=var,
                        slice_mode=slice_mode,
                        time_range=time_range,
                        out_file=fileOutPath+out_file_name,
                        threshold=thresh,
                        N_lev=level,
                        transfer_limit_Mbytes=transfer_limit_Mb,
                        callback=callback,
                        callback_percentage_start_value=0,
                        callback_percentage_total=100,
                        base_period_time_range=None,
                        window_width=5,
                        only_leap_years=False,
                        ignore_Feb29th=True,
                        interpolation='hyndman_fan',
                        netcdf_version='NETCDF4_CLASSIC',
                        out_unit='days')
        
        """ Set output """
        url = fileOutURL+"/"+out_file_name;
        self.opendapURL.setValue(url);

	#Added for supporting cache
        resinsert = cache.insert_new(self, None)
        if resinsert is None:
                logging.error("Error updating the cache catalog")
	#End

        self.status.set("ready",100);
        
