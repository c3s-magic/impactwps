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
                            identifier = 'clipc_simpleindicator_execute', # only mandatary attribute = same file name
                            title = 'CLIPC ICCLIM simple indicator calculator Execute',
                            abstract = 'Using ICCLIM, single input indices of temperature TG, TX, TN, TXx, TXn, TNx, TNn, SU, TR, CSU, GD4, FD, CFD, ID, HD17; of rainfall: CDD, CWD, RR, RR1, SDII, R10mm, R20mm, RX1day, RX5day; and of snowfall: SD, SD1, SD5, SD50 can be computed.',
                            version = "1.0",
                            storeSupported = True,
                            statusSupported = True,
                            grassLocation =False)


        self.indiceNameIn = self.addLiteralInput(identifier = 'indiceName',
                                               title = 'Indicator name',
                                               abstract = 'The indicator to calculate' ,
                                               type="String",
                                               default = 'SU')        

        self.indiceNameIn.values = ["TG","TX","TN","TXx","TXn","TNx","TNn","SU","TR","CSU","GD4","FD","CFD","ID","HD17","CDD","CWD","PRCPTOT","RR1","SDII","R10mm","R20mm","RX1day","RX5day","SD","SD1","SD5cm","SD50cm"]


        self.sliceModeIn = self.addLiteralInput(identifier = 'sliceMode',
                                              title = 'Time slice mode',
                                              abstract = 'Selects temporal grouping to apply for calculations',
                                              type="String",
                                              default = 'year')
        self.sliceModeIn.values = ["year","month","ONDJFM","AMJJAS","DJF","MAM","JJA","SON"]


        self.thresholdIn = self.addLiteralInput(identifier = 'threshold', 
                                               title = 'Indicator threshold',
                                               abstract = 'Threshold(s) for certain indices (SU, CSU and TR). Input can be a single numer or a number range, e.g. for SU this can be "20" or "20,21,22"  degrees Celsius',
                                               type=type("S"),
                                               minOccurs=0,
                                               maxOccurs=1024,
                                               default = 'None')

       
        self.filesIn = self.addLiteralInput(identifier = 'wpsnetcdfinput_files',
                                               title = 'Input filelist',
                                               abstract="The input filelist to calculate the indicator on. The inputs need to be accessible by opendap URL's.",
                                               type=type("S"),
                                               minOccurs=0,
                                               maxOccurs=1024,
                                               default = 'http://opendap.knmi.nl/knmi/thredds/dodsC/IS-ENES/TESTSETS/tasmax_day_EC-EARTH_rcp26_r8i1p1_20060101-20251231.nc')
        
                                                
        self.varNameIn = self.addLiteralInput(identifier = 'wpsvariable_varName~wpsnetcdfinput_files',
                                               title = 'Input variable name',
                                               abstract = 'Variable name to process as specified in your input files.',
                                               type="String",
                                               default = 'tasmax')
        

        self.timeRangeIn = self.addLiteralInput(identifier = 'wpstimerange_timeRange~wpsnetcdfinput_files', 
                                               title =  'Time range',
                                               abstract = 'Time range, e.g. 2010-01-01/2012-12-31. None means all dates in the file.',
                                               type="String",
                                                default = 'None')
        
        self.outputFileNameIn = self.addLiteralInput(identifier = 'wpsnetcdfoutput_outputFileName', 
                                               title = 'Name of output netCDF file',
                                               type="String",
                                               default = 'out_icclim.nc')
        
        
        self.NLevelIn = self.addLiteralInput(identifier = 'wpsnlevel_NLevel~wpsnetcdfinput_files', 
                                               title = 'Model level number',
                                               abstract = 'The model level from your input data, in case you have 4D variables in your input data',
                                               type="String",
                                               default = 'None')

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
        self.status.set("ready",100);
        
        
