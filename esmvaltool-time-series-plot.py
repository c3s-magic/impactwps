"""
../wps.py?request=execute
&service=wps
&version=1.0.0
&identifier=esmvaltool-time-series-plot
&status=true
&storeExecuteResponse=true


"""
import datetime
from pywps.Process import WPSProcess
import os
import logging


class Process(WPSProcess):
    def __init__(self):
        # init process
        WPSProcess.__init__(self,
                            identifier="esmvaltool-time-series-plot",  # the same as the file name
                            version="1.0",
                            title="Create a time series plot for the given data files",
                            storeSupported="false",
                            statusSupported="True",
                            abstract="Calls ESMValTool to create a time series plot",
                            grassLocation=False)

        self.inputFiles = self.addLiteralInput(identifier="netcdf",
                                               title="Model file",
                                               type="String",
                                               # default="http://opendap.knmi.nl/knmi/thredds/dodsC/CLIPC/cerfacs/vDTR/MPI-M-MPI-ESM-LR_rcp85_r1i1p1_SMHI-RCA4_v1/vDTR_MON_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_SMHI-RCA4_v1_EUR-11_2006-2100.nc",
                                               minOccurs=1,
                                               maxOccurs=10)

        self.startYear = self.addLiteralInput(identifier="startYear",
                                              title="First year data used in plot",
                                              type="Integer",
                                              default=2002,
                                              minOccurs=1,
                                              maxOccurs=1)

        self.endYear = self.addLiteralInput(identifier="endYear",
                                            title="Last year data used in plot",
                                            type="Integer",
                                            default=2004,
                                            minOccurs=1,
                                            maxOccurs=1)

        self.opendapURL = self.addLiteralOutput(identifier="opendapURL",
                                                title="opendapURL",
                                                type="String", );

    def execute(self):
        self.status.set("starting", 0)

        logging.debug("Input files are %s" % self.inputFiles.getValue())
        logging.debug("Start year is %d" % self.startYear.getValue())
        logging.debug("End year is %d" % self.endYear.getValue())

        #KNMI WPS Specific


        # Very important: This allows the NetCDF library to find the users credentials (X509 cert)
        # Set current working directory to user HOME dir
        os.chdir(os.environ['HOME'])

        # Create output folder name
        output_folder_name = "/WPS_" + self.identifier + "_" + datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")

        #OpenDAP Url prefix (hosted by portal)
        output_folder_url = os.environ['POF_OUTPUT_URL'] + output_folder_name + "/"

        #Filesystem output path
        output_folder_path = os.environ['POF_OUTPUT_PATH'] + output_folder_name + "/"

        #Create output directory
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        output_file_name = 'test.nc'

        #KNMI WPS Specific Set output
        url = output_folder_url + "/" + output_file_name;
        self.opendapURL.setValue(url);
        self.status.set("ready", 100);
