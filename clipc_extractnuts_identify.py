

from pywps.Process.Process import WPSProcess   

from os.path import expanduser
from mkdir_p import *
from datetime import datetime
home = expanduser("~")

class Process(WPSProcess):
    def __init__(self):
        # init process
        WPSProcess.__init__(self,
                            identifier="clipc_extractnuts_identify", #the same as the file name
                            title="CLIPC  Create statistics per NUTS region Identify",
                            version = "1.0",
                            storeSupported = "true",
                            statusSupported = "true",
                            abstract="Identify process for statistics per NUTS region calculations",
                            grassLocation =False)
     
        self.result = self.addLiteralOutput(identifier = "result",title = "answer");
        self.inputorder = self.addLiteralOutput(identifier = "inputorder",title = "inputorder");

    
    def execute(self):
        
        self.result.setValue("{}");
        self.inputorder.setValue("input1,input2,bbox,time2,width,height,crs,tags,netcdfnutsstatfilename,csvnutsstatfilename");
        self.status.set("Finished....", 100)      
