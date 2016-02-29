from pywps.Process.Process import WPSProcess   

from os.path import expanduser
from mkdir_p import *
from datetime import datetime
home = expanduser("~")

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
                            identifier="clipc_combine_execute", #the same as the file name
                            title="CLIPC Combine Execute",
                            version = "1.0",
                            storeSupported = "true",
                            statusSupported = "true",
                          abstract="Performs operation on two nc files and returns the answer as nc file",
                          grassLocation =False)
        
        self.inputa = self.addLiteralInput(identifier="inputa",
                                                title="Input A",
                                                abstract="application/netcdf",
                                                default = "http://opendap.knmi.nl/knmi/thredds/dodsC/CLIPC/tier1_indicators/icclim_cerfacs/vDTR/MPI-M-MPI-ESM-LR_rcp45_r1i1p1_SMHI-RCA4_v1-SMHI-DBS43-MESAN-1989-2010/vDTR_OCT_MPI-M-MPI-ESM-LR_rcp45_r1i1p1_SMHI-RCA4_v1-SMHI-DBS43-MESAN-1989-2010_EUR-11_2006-2100.nc",
                                                type = type("String"))  

        self.inputb = self.addLiteralInput(identifier="inputb",
                                                title="Input B",
                                                abstract="application/netcdf",
                                                default = "http://opendap.knmi.nl/knmi/thredds/dodsC/CLIPC/tier1_indicators/icclim_cerfacs/TNn/MPI-M-MPI-ESM-LR_rcp85_r1i1p1_SMHI-RCA4_v1/TNn_OCT_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_SMHI-RCA4_v1_EUR-11_2006-2100.nc",
                                                type = type("String"))  

        self.operator = self.addLiteralInput(identifier = 'operator',
                                              title = 'operator',
                                              type=type("String"),
                                              default = 'multiply')  

        self.norm1 = self.addLiteralInput(identifier = 'norm1',
                                              title = 'normalisation operator 1',
                                              type=type("String"),
                                              default = 'normnone')

        self.norm2 = self.addLiteralInput(identifier = 'norm2',
                                              title = 'normalisation operator 2',
                                              type=type("String"),
                                              default = 'normnone')


        self.bbox = self.addLiteralInput(identifier = "bbox",title = "Bounding box in defined coordinate system",type="String",minOccurs=4,maxOccurs=4,default="-40,20,60,85")
        
        self.timea = self.addLiteralInput(identifier = "timea",title = "Time A for netcdf input A",type="String",minOccurs=1,maxOccurs=1,default="2010-10-16T00:00:00Z")
        self.timeb = self.addLiteralInput(identifier = "timeb",title = "Time B for netcdf input B",type="String",minOccurs=1,maxOccurs=1,default="2010-10-16T00:00:00Z")
        
        self.operator.values = ["add","subtract","divide","multiply"] 
        self.norm1.values = ["normnone" , "normzero", "normminmax", "normstndrd"]
        self.norm2.values = ["normnone" , "normzero", "normminmax", "normstndrd"]

        self.width  = self.addLiteralInput(identifier = "width"  ,title = "width of wcs"  ,type="String",minOccurs=1,maxOccurs=1,default="400")
        self.height = self.addLiteralInput(identifier = "height" ,title = "height of wcs" ,type="String",minOccurs=1,maxOccurs=1,default="300")

        self.outputFileName = self.addLiteralInput(identifier="outputFileName",title = "Output file name",type="String",default="combine.nc")
        
        self.result = self.addLiteralOutput(identifier = "result",title = "result as OpenDAP URL");

    def callback(self,message,percentage):
        self.status.set("Processing: [%s]" % message,percentage);
        
    def execute(self):
        def callback(a,b):
          self.callback(a,b)
        tmpFolderPath=os.getcwd()
        os.chdir(home)
        
        import time
        from clipc_combine_process import clipc_combine_process 

        self.status.set("Preparing....", 0)
        
        pathToAppendToOutputDirectory = "/WPS_"+self.identifier+"_" + datetime.now().strftime("%Y%m%dT%H%M%SZ")
        
        """ URL output path """
        fileOutURL  = os.environ['POF_OUTPUT_URL']  + pathToAppendToOutputDirectory+"/"
        
        """ Internal output path"""
        fileOutPath = os.environ['POF_OUTPUT_PATH']  + pathToAppendToOutputDirectory +"/"

        """ Create output directory """
        mkdir_p(fileOutPath)
        self.status.set("Starting....", 1)
        """ Get output filename """
        outputfile = self.outputFileName.getValue()
      
        wcs_url1 =  'https://dev.climate4impact.eu/impactportal/adagucserver?source='+self.inputa.getValue()+"&"
        wcs_url2 =  'https://dev.climate4impact.eu/impactportal/adagucserver?source='+self.inputb.getValue()+"&"

        bbox =  self.bbox.getValue()[0]+","+self.bbox.getValue()[1]+","+self.bbox.getValue()[2]+","+self.bbox.getValue()[3];
        time1 = self.timea.getValue();
        time2 = self.timeb.getValue();
        
        op = "*"
        
        if(self.operator.getValue() == "multiply"):
          op= "*"
        if(self.operator.getValue() == "add"):
          op= "+"
        if(self.operator.getValue() == "subtract"):
          op= "-"
        if(self.operator.getValue() == "divide"):
          op= "/"
        
        certfile = home+'/certs/creds.pem'
        
        norm1 = self.norm1.getValue()
        norm2 = self.norm2.getValue()

        width = self.width.getValue()
        height = self.height.getValue()

        #nc1 , nc2 , nc_combo = clipc_combine_process.combine_two_indecies_wcs(wcs_url1, wcs_url2, op , bbox , time1 , time2 , tmpFolderPath+'/wcs_nc1.nc' , '/tmp/wcs_nc2.nc', fileOutPath+"/"+outputfile,callback=callback ,certfile=certfile)
        nc1 , nc2 , nc_combo = clipc_combine_process.combine_two_indecies_wcs(wcs_url1, wcs_url2, op , norm1 , norm2 , bbox , time1 , time2 , tmpFolderPath+'/wcs_nc1.nc' , tmpFolderPath+'/wcs_nc2.nc', fileOutPath+"/"+outputfile,width=width , height=height, callback=callback ,certfile=certfile)


        #The final answer    
        url = fileOutURL+"/"+outputfile;
        self.result.setValue(url);
        self.status.set("Finished....", 100)      
