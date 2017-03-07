"""
../wps.py?request=execute
&service=wps
&version=1.0.0
&identifier=esmvaltool-time-series-plot
&status=true
&storeExecuteResponse=true


"""
import datetime

import shutil

import netCDF4
import urlparse

from pywps.Process import WPSProcess
import os
import logging
from jinja2 import FileSystemLoader, Environment,select_autoescape
import glob


class Process(WPSProcess):
    def __init__(self):
        # init process
        WPSProcess.__init__(self,
                            identifier="esmvaltool-time-series-plot",  # the same as the file name
                            version="1.0",
                            title="Create a time series plot for the given data files",
                            storeSupported="True",
                            statusSupported="True",
                            abstract="Calls ESMValTool to create a time series plot",
                            grassLocation=False)

        self.input1 = self.addLiteralInput(identifier="netcdf1",
                                               title="Model file",
                                               type="String",
                                               abstract="application/netcdf",
                                               # default="http://opendap.knmi.nl/knmi/thredds/dodsC/CLIPC/cerfacs/vDTR/MPI-M-MPI-ESM-LR_rcp85_r1i1p1_SMHI-RCA4_v1/vDTR_MON_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_SMHI-RCA4_v1_EUR-11_2006-2100.nc",
                                               minOccurs=0,
                                               maxOccurs=1)

        self.input2 = self.addLiteralInput(identifier="netcdf2",
                                               title="Model file",
                                               type="String",
                                               abstract="application/netcdf",
                                               # default="http://opendap.knmi.nl/knmi/thredds/dodsC/CLIPC/cerfacs/vDTR/MPI-M-MPI-ESM-LR_rcp85_r1i1p1_SMHI-RCA4_v1/vDTR_MON_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_SMHI-RCA4_v1_EUR-11_2006-2100.nc",
                                               minOccurs=0,
                                               maxOccurs=1)

        self.input3 = self.addLiteralInput(identifier="netcdf3",
                                               title="Model file",
                                               type="String",
                                               abstract="application/netcdf",
                                               # default="http://opendap.knmi.nl/knmi/thredds/dodsC/CLIPC/cerfacs/vDTR/MPI-M-MPI-ESM-LR_rcp85_r1i1p1_SMHI-RCA4_v1/vDTR_MON_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_SMHI-RCA4_v1_EUR-11_2006-2100.nc",
                                               minOccurs=0,
                                               maxOccurs=1)

        self.input4 = self.addLiteralInput(identifier="netcdf4",
                                               title="Model file",
                                               type="String",
                                               abstract="application/netcdf",
                                               # default="http://opendap.knmi.nl/knmi/thredds/dodsC/CLIPC/cerfacs/vDTR/MPI-M-MPI-ESM-LR_rcp85_r1i1p1_SMHI-RCA4_v1/vDTR_MON_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_SMHI-RCA4_v1_EUR-11_2006-2100.nc",
                                               minOccurs=0,
                                               maxOccurs=1)


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
                                                type="String", )

        self.plot = self.addLiteralOutput(identifier="plot",
                    title="Raster out",
                    type="String",
                    asReference=False
                   )

    def copyNetCDF(self, source, destination, description, skipVariable=None):
        nc_fid = netCDF4.Dataset(source, 'r')
        w_nc_fid = netCDF4.Dataset(destination, 'w', format='NETCDF4')

        w_nc_fid.description = description

        for var_name, dimension in nc_fid.dimensions.iteritems():
            w_nc_fid.createDimension(var_name, len(dimension) if not dimension.isunlimited() else None)

        for var_name, ncvar in nc_fid.variables.iteritems():
            if ((skipVariable != None and skipVariable != var_name) or skipVariable == None):
                outVar = w_nc_fid.createVariable(var_name, ncvar.datatype, ncvar.dimensions)

                ad = dict((k, ncvar.getncattr(k)) for k in ncvar.ncattrs())

                outVar.setncatts(ad)
                try:
                    outVar[:] = ncvar[:]
                except:
                    outVar = ncvar
                    pass

        global_vars = dict((k, nc_fid.getncattr(k)) for k in nc_fid.ncattrs())

        for k in sorted(global_vars.keys()):
            w_nc_fid.setncattr(k, global_vars[k])

        nc_fid.close()
        w_nc_fid.close()

    def execute(self):
        self.status.set("starting", 0)


        #print some debugging info

        inputs = [self.input1.getValue(), self.input2.getValue(), self.input3.getValue(), self.input4.getValue()]
        start_year = self.startYear.getValue()
        end_year = self.endYear.getValue()

        logging.debug("inputs %s" % inputs)
        logging.debug("Start year is %s" % self.startYear.getValue())
        logging.debug("End year is %s" % self.endYear.getValue())

        # Very important: This allows the NetCDF library to find the users credentials (X509 cert)
        # Set current working directory to user HOME dir
        os.chdir(os.environ['HOME'])

        # Create output folder name
        output_folder_name = "WPS_" + self.identifier + "_" + datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")

        logging.debug(os.environ['POF_OUTPUT_PATH'])

        #OpenDAP Url prefix (hosted by portal)
        output_folder_url = os.environ['POF_OUTPUT_URL'] + output_folder_name

        #Filesystem output path
        output_folder_path = os.path.join(os.environ['POF_OUTPUT_PATH'], output_folder_name)

        logging.debug("output folder path is %s" % output_folder_path)

        #Create output directory
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)


        #copy input files to scratch (in correct folders for esmvaltool)

        inputs = [self.input1.getValue(), self.input2.getValue(), self.input3.getValue(), self.input4.getValue()]

        #next, copy input netcdf to a location esmvaltool expects

        # example cmpi5 esgf link
        # http://esgf-data1.ceda.ac.uk/thredds/dodsC/esg_dataroot/cmip5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r1i1p1/v1/tas/tas_Amon_ACCESS1-0_historical_r1i1p1_185001-200512.nc

        # esmvaltool data folder example
        # ETHZ_CMIP5/historical/Amon/ta/bcc-csm1-1/r1i1p1/ta_Amon_bcc-csm1-1_historical_r1i1p1_200001-200212.nc


        model_descriptions = []
        variable = None

        self.status.set("downloading input from esgf", 0)
        for input_url in inputs:

            if input_url: # if input_url is not an empty string or None
                parsed_url = urlparse.urlparse(input_url)
                filename = os.path.basename(parsed_url.path)


                logging.debug("url %s has path %s and filename %s" % (input_url, parsed_url.path, filename))


                parts = filename.split('_')

                elements = dict(variable=parts[0], period=parts[1], model=parts[2], experiment = parts[3], ensemble_member=parts[4])

                self.status.set("downloading input for %s from esgf" % elements['model'], 10 + self.status.percentCompleted)

                logging.debug("elements %s" % elements)

                input_file_dir = "/data/in/modeldata/ETHZ_CMIP5/%s/%s/%s/%s/%s" % ( elements['experiment'], elements['period'], elements['variable'], elements['model'], elements['ensemble_member'])
                input_file_path =input_file_dir + "/" + filename

                if not os.path.exists(input_file_dir):
                    os.makedirs(input_file_dir)

                logging.debug("input_file_path %s" % input_file_path)

                if os.path.exists(input_file_path):
                    logging.debug("deleting input file %s" % input_file_path)
                    os.remove(input_file_path)

                self.copyNetCDF(input_url,input_file_path, "copied")

                #description = <model> SOME DESCRIPTION FIELDS HERE </model>
                model_descriptions.append('CMIP5_ETHZ %s %s %s %s %s %s @{MODELPATH}/ETHZ_CMIP5/' % (elements['model'], elements['period'], elements['experiment'], elements['ensemble_member'], start_year, end_year))

                if variable is None:
                    variable = elements['variable']
                elif variable !=  elements['variable']:
                    raise Exception("All files need to be of the same variable")

        self.status.set("setting up namelist for esmvaltool", 50)


        logging.debug("model descriptions now %s" % model_descriptions)
        logging.debug("variable %s" % variable)

        #create esmvaltool config (using template)
        environment = Environment(loader=FileSystemLoader('/namelists'))
                                  #autoescape=select_autoescape(['html', 'xml']))

        template = environment.get_template('namelist_reformat.xml')

        generated_namelist = template.render(models=model_descriptions, variable=variable, work_dir=output_folder_path)

        logging.debug("template output = %s" % generated_namelist)

        #write generated namelist to file

        namelist_path = output_folder_path + "/" + 'namelist_reformat.xml'

        namelist_fd = open(namelist_path, 'w')
        namelist_fd.write(generated_namelist)
        namelist_fd.close()

        #run esmvaltool command

        self.status.set("running esmvaltool", 60)

        os.chdir('/src/ESMValTool-master')

        self.cmd(['python', 'main.py', namelist_path])

        #grep output from output folder

        self.status.set("processing output", 90)

        output_image = glob.glob(output_folder_path + "/tsline/*.png").pop()

        logging.debug("output image path is %s" % output_image)

        rel_output_image = os.path.relpath(output_image, output_folder_path)

        plot_url = output_folder_url + "/" + rel_output_image

        self.plot.setValue(plot_url)

        #KNMI WPS Specific Set output

        output_nc = glob.glob(output_folder_path + "/tsline/*.nc").pop()

        rel_output_nc = os.path.relpath(output_nc, output_folder_path)

        url = output_folder_url + "/" + rel_output_nc

        self.opendapURL.setValue(url);
        self.status.set("ready", 100);
