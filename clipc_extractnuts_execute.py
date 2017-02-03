from pywps.Process.Process import WPSProcess   

from os.path import expanduser
from mkdir_p import *
from datetime import datetime
import base64
import time
from clipc_combine_process import extractnuts

home = expanduser("~")

import logging;
logging.debug("Something has been debugged")

# python
# clipc combine process
# combine two netCDFs
# knmi team
# authors: maarten, andrej
# clipc@knmi.nl
#


class Process(WPSProcess):
    def __init__(self):
        # init process
        WPSProcess.__init__(self,
                            identifier="clipc_extractnuts_execute", #the same as the file name
                            title="CLIPC Create statistics per NUTS region Execute",
                            version = "1.0",
                            storeSupported = "true",
                            statusSupported = "true",
                            abstract="The NUTS extractor calculates statistics for any NetCDF file by extracting geographical areas defined in a GeoJSON file. The statistics per geographical area include minimum, maximum, mean and standard deviation. The statistics are presented in a CSV table and a NetCDF file.",
                            grassLocation =False)
        
        self.input1 = self.addLiteralInput(identifier="input1",
                                                title="File A",
                                                abstract="application/netcdf",
                                                default = "http://opendap.knmi.nl/knmi/thredds/dodsC/CLIPC/storyline_urbanheat/geojson/NUTS_2010_L0.geojson.nc",
                                                type = type("String"))  

        self.input2 = self.addLiteralInput(identifier="input2",
                                                title="File B",
                                                abstract="application/netcdf",
                                                default = "http://opendap.knmi.nl/knmi/thredds/dodsC/IS-ENES/TESTSETS/tas_day_EC-EARTH_rcp26_r8i1p1_20060101-20251231.nc",
                                                type = type("String"))  

        self.bbox = self.addLiteralInput(identifier = "bbox",title = "Bounding box",type="String",minOccurs=4,maxOccurs=4,default="-40,20,60,85")
        self.time2 = self.addLiteralInput(identifier = "time2",title = "Time B",type="String",minOccurs=1,maxOccurs=1,default="2016-08-29T12:00:00Z")
        self.width  = self.addLiteralInput(identifier = "width"  ,title = "Width"  ,type="String",minOccurs=1,maxOccurs=1,default="1500")
        self.height = self.addLiteralInput(identifier = "height" ,title = "Height" ,type="String",minOccurs=1,maxOccurs=1,default="1500")
        self.crs  = self.addLiteralInput(identifier = "crs"  ,title = "Coordinate reference system"  ,type="String",minOccurs=1,maxOccurs=1,default="EPSG:4326")
        self.tags = self.addLiteralInput(identifier = "tags",title = "Your tag for this process",type="String",default="provenance_research_knmi");
        self.netcdfnutsstatfilename = self.addLiteralInput(identifier="netcdfnutsstatfilename",title = "NetCDF outputfile with geographical statistics",type="String",default="nutstat.nc")
        self.csvnutsstatfilename = self.addLiteralInput(identifier="csvnutsstatfilename",title = "CSV outputfile with statistics in table form",type="String",default="nutstat.csv")
        
        self.netcdfnutsstatout = self.addLiteralOutput(identifier = "netcdfnutsstatout",title = "NetCDF outputfile with geographical statistics");
        self.csvnutsstatout = self.addLiteralOutput(identifier = "csvnutsstatout",title = "CSV outputfile with statistics in table form");
        self.csvnutsstatdata = self.addLiteralOutput(identifier = "csvnutsstatdata",title = "CSV with statistics in table form");


    def callback(self,message,percentage):
        self.status.set("Processing: [%s]" % message,percentage);
        
    def execute(self):
        def callback(message,percentage):
          self.callback(message,percentage)
        tmpFolderPath=os.getcwd()
        os.chdir(home)


        self.status.set("Preparing....", 0)
        
        pathToAppendToOutputDirectory = "/WPS_"+self.identifier+"_" + datetime.now().strftime("%Y%m%dT%H%M%SZ")
        
        """ URL output path """
        fileOutURL  = os.environ['POF_OUTPUT_URL']  + pathToAppendToOutputDirectory+"/"
        
        """ Internal output path"""
        fileOutPath = os.environ['POF_OUTPUT_PATH']  + pathToAppendToOutputDirectory +"/"

        """ Create output directory """
        mkdir_p(fileOutPath)
        self.status.set("Starting....", 1)
     
        bbox =  self.bbox.getValue()[0]+","+self.bbox.getValue()[1]+","+self.bbox.getValue()[2]+","+self.bbox.getValue()[3];
        time2 = self.time2.getValue();
        width = int(self.width.getValue())
        height = int(self.height.getValue())

        CSV = extractnuts.nutsCombine(self.input1.getValue(),
            self.input2.getValue(),
            bbox= bbox,
            time=time2,
            width=width,
            height=height,
            crs= self.crs.getValue(),
            outncfile=fileOutPath+self.netcdfnutsstatfilename.getValue(),
            outcsvfile=fileOutPath+self.csvnutsstatfilename.getValue(),
            callback=callback)        

        #The final answer    
        self.netcdfnutsstatout.setValue(fileOutURL+"/"+self.netcdfnutsstatfilename.getValue());
        self.csvnutsstatout.setValue(fileOutURL+"/"+self.csvnutsstatfilename.getValue());
        self.csvnutsstatdata.setValue("base64:"+base64.b64encode(CSV));
        self.status.set("Finished....", 100)      
