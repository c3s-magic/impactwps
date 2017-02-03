import os
from pywps.Process.Process import WPSProcess   
from SimpleDRSChecker import SimpleDRSChecker
import base64
class Process(WPSProcess):
    def __init__(self):
        # init process
        WPSProcess.__init__(self,
                            identifier="clipc_drschecker", #the same as the file name
                            title="CLIPC DRS Checker",
                            version = "1.0",
                            storeSupported = "true",
                            statusSupported = "true",
                            abstract="Checks file for correct DRS",
                            grassLocation =False)
        
        self.resource = self.addLiteralInput(identifier="resource",
                                                title="Please select the input NetCDF file URL to check",
                                                abstract="application/netcdf",
                                                default = "select a file",
                                                minOccurs=1,
                                                maxOccurs=1,
                                                type = type("String"))   
 
        self.activity = self.addLiteralInput(identifier = 'activity',
                                               title = 'Project or activity',
                                               abstract = 'Project or activity' ,
                                               type="String",
                                               default = 'CLIPC')        
        self.tags = self.addLiteralInput(identifier = "tags",title = "Your tag for this process",type="String",default="provenance_research_knmi");

        self.activity.values = ["CLIPC","CORDEX"]
      
        self.goodorbad = self.addLiteralOutput(identifier = "goodorbad",title = "OK means good, ERROR means error",  type = type("String"));
        self.logmessages = self.addLiteralOutput(identifier = "logmessages",title = "logmessages" , type = type("String"));
        self.errors = self.addLiteralOutput(identifier = "errors",title = "errors" , type = type("String"));
        self.nroferrors = self.addLiteralOutput(identifier = "nroferrors",title = "nroferrors" , type = type("String"));
        self.DatasetDRS = self.addLiteralOutput(identifier = "DatasetDRS",title = "DatasetDRS" , type = type("String"));
        self.FilenameDRS = self.addLiteralOutput(identifier = "FilenameDRS",title = "FilenameDRS" , type = type("String"));

    def execute(self):
        # Very important: This allows the NetCDF library to find the users credentials (X509 cert)
        homedir = os.environ['HOME']
        os.chdir(homedir)
        self.status.set("Checking....", 0)      
        drsChecker = SimpleDRSChecker()
        drsChecker.checkFile(self.resource.getValue(),self.activity.getValue())
        #print drsChecker.stdOutString
        #print "DatasetDRS :"+drsChecker.DRSDatasetname
        #print "FilenameDRS:"+drsChecker.DRSFilename
        if drsChecker.nrOfErrors == 0:
            self.goodorbad.setValue("OK");
        else:
            self.goodorbad.setValue("ERROR");
        self.DatasetDRS.setValue("base64:"+base64.b64encode(drsChecker.DRSDatasetname));
        self.FilenameDRS.setValue("base64:"+base64.b64encode(drsChecker.DRSFilename));
        self.logmessages.setValue("base64:"+base64.b64encode(drsChecker.stdOutString));
        self.errors.setValue("base64:"+base64.b64encode(drsChecker.errorString));
        self.nroferrors.setValue(drsChecker.nrOfErrors);
        self.status.set("Finished....", 100)      
