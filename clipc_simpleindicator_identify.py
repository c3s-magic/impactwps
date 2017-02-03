

from pywps.Process.Process import WPSProcess   

from os.path import expanduser
from mkdir_p import *
from datetime import datetime
home = expanduser("~")

class Process(WPSProcess):
    def __init__(self):
        # init process
        WPSProcess.__init__(self,
                            identifier="clipc_simpleindicator_identify", #the same as the file name
                            title="CLIPC ICCLIM simple indicator calculator Identify",
                            version = "1.0",
                            storeSupported = "true",
                            statusSupported = "true",
                            abstract="Identify function for ICCLIM simple indicator calculator",
                            grassLocation =False)
     
        self.result = self.addLiteralOutput(identifier = "result",title = "answer");
        self.inputorder = self.addLiteralOutput(identifier = "inputorder",title = "inputorder");

    
    def execute(self):
        
        self.result.setValue("{}");
        self.inputorder.setValue("wpsnetcdfinput_files,wpsvariable_varName~wpsnetcdfinput_files,sliceMode,wpstimerange_timeRange~wpsnetcdfinput_files,wpsnlevel_NLevel~wpsnetcdfinput_files,indiceName,threshold,wpsnetcdfoutput_outputFileName");
        self.status.set("Finished....", 100)      
