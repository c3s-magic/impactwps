

from pywps.Process.Process import WPSProcess   

from os.path import expanduser
from mkdir_p import *
from datetime import datetime
home = expanduser("~")

class Process(WPSProcess):
    def __init__(self):
        # init process
        WPSProcess.__init__(self,
                            identifier="clipc_combine_identify", #the same as the file name
                            title="CLIPC Combine Identify",
                            version = "1.0",
                            storeSupported = "true",
                            statusSupported = "true",
                          abstract="Lists possible operations for two resources",
                          grassLocation =False)
        
        self.inputa = self.addLiteralInput(identifier="inputa",
                                                title="Input 1",
                                                abstract="application/netcdf",
                                                default = "http://opendap.knmi.nl/knmi/thredds/dodsC/CLIPC/tier1_indicators/icclim_cerfacs/vDTR/MPI-M-MPI-ESM-LR_rcp45_r1i1p1_SMHI-RCA4_v1-SMHI-DBS43-MESAN-1989-2010/vDTR_OCT_MPI-M-MPI-ESM-LR_rcp45_r1i1p1_SMHI-RCA4_v1-SMHI-DBS43-MESAN-1989-2010_EUR-11_2006-2100.nc",
                                                type = type("String"))   
        self.inputb = self.addLiteralInput(identifier="inputb",
                                                title="Input 2",
                                                abstract="application/netcdf",
                                                default = "http://opendap.knmi.nl/knmi/thredds/dodsC/CLIPC/tier1_indicators/icclim_cerfacs/TNn/MPI-M-MPI-ESM-LR_rcp85_r1i1p1_SMHI-RCA4_v1/TNn_OCT_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_SMHI-RCA4_v1_EUR-11_2006-2100.nc",
                                                type = type("String"))   
       
        
        self.result = self.addLiteralOutput(identifier = "result",title = "answer");
        self.inputorder = self.addLiteralOutput(identifier = "inputorder",title = "inputorder");

    
    def execute(self):
        
        self.result.setValue("{\"operator\":[\"add\",\"substract\",\"divide\",\"multiply\"]}");
        self.inputorder.setValue("input1,input2,time1,time2,norm1,norm2,bbox,operator,width,height,outputfilename");
        self.status.set("Finished....", 100)      
