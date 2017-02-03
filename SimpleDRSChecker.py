## @package SimpleDRSChecker
#  Very simple DRS checker made for the CLIPC project.
#  Follows document http://www.clipc.eu/media/clipc/org/documents/other/metadata_standards_for_climate_impact_indicators-v1.pdf.
#
# @author Maarten Plieger - maarten.plieger@knmi.nl
# @version 0.02


# DONE: When are we dealing with model DRS and when general DRS? Ruth: Check by sourceDataID attribute
# DONE: output_frequency needs to be validated: Not possible.
# DONE: reference_period needs to be validated
# DONE: Ask Ruth: Check why Activity and activity occurs
# DONE: Ask Ruth: Check why sourceDataID and sourceDataId occurs
# DONE: Ask Ruth: time_coverage_start should be mandatory attribute with format YYYYMMDD, as it is used as StartTime in the drsnames. Or startTime in drsname needs to be optional.
# DONE: Ask Ruth: tile-nnnnn should become tilennnnn or tilenr in the metadata document as it is a delimiter. E.g <StartTime-EndTime>

#<VariableName>_<package>_<institution>_<GCMName>_<ExperimentName>_<EnsembleMember>_<RCMName>_<RCMRealisation>_<domain>_<BcName>_<BcObsName>_<BcRefPeriod>_<frequency>_<StartTime-EndTime>_<Reference_period>_<tilennnnn>
#prcptot_icclim-4-1-0_KNMI_GFDL-ESM2M-none-GFDL-ESM2M_rcp45_r1i1p1_SMHI-RCA4_v1_rcp4.5 or v1?_EUR-44_SMHI-DBS43_EOBSv10_1981-2010_yr_20060101-20991231_2006-2099_none.nc
#prcptot_icclim-4-2-3_KNMI_GFDL-ESM2M_r1i1p1_SMHI-RCA4_v1_EUR-44_SMHI-DBS43_EOBS10-1981-2010_yr_20060101-20991231.nc

import datetime as dt  # Python standard library datetime  module
import numpy as np
import netCDF4
import fnmatch
import os
import datetime
import sys
import re

fixFiles=False
cfOnly=False
## The SimpleDRSChecker class
#
# Use checkFile method.
class SimpleDRSChecker:

    ## The constructor.
    def __init__(self):
        return

    nrOfErrors = 0
    errorString = ""
    stdOutString = ""
    DRSDatasetname=""
    DRSFilename=""
    
    DRS = {
        "CORDEX":{
            "requiredGlobalAttributes":{
                'institute_id':{},
                'contact':{},
                'rcm_version_id':{},
                'product':{},
                'CORDEX_domain':{},
                'creation_date':{'validator':['datetimeYYYY-MM-DDTHH_MM_SSZ']},
                'frequency':{},
                'model_id':{},
                'driving_model_id':{},
                'driving_experiment':{},
                "driving_model_ensemble_member":{},
                'experiment_id':{},
                'project_id':{}
                },
            "drsMappings": {
                'variable':'@var',
                'institute':'institute_id',
                'product':'product',
                'experiment':'experiment_id',
                'ensemble':'driving_model_ensemble_member',
                'model':'model_id',
                'driving_model':'driving_model_id',
                'frequency':'frequency',
                'project':'project_id',
                'domain':'CORDEX_domain',
                'model_version':'rcm_version_id'
                },
            "drsConstructors":{
                "filename":"@<VariableName>@_<domain>_<driving_model>_<experiment>_<ensemble>_<model>_<model_version>_<frequency>_@<version>@.nc",
                "dataset": "<project>.<product>.<domain>.<institute>.<driving_model>_<experiment>_<ensemble>_<model>_<model_version>_<frequency>_@<VariableName>@_@<version>@.nc"
                }
            },
            "CLIPCModelDRS":{
                "requiredGlobalAttributes":{
                    'Conventions':{},
                    'activity':{'validator':['activity_is_clipc']},
                    'title':{'validator':['checklengthisatleast3']},
                    'summary':{},
                    'variable_name':{},
                    'product':{},
                    'comment':{},
                    'references':{},
                    'package_name':{},
                    'package_references':{},
                    'institution_id':{},
                    'institution_url':{},
                    'contact':{},
                    'contributor_name':{},
                    'contributor_role':{},
                    'date_created':{'validator':['datetimeYYYYMMDD']},
                    'date_issued':{'validator':['datetimeYYYYMMDD']},
                    'date_modified':{'validator':['datetimeYYYYMMDD']},
                    'realisation_id':{},
                    'source_data_id':{},
                    'source_data_id_comment':{},
                    'invar_platform':{},
                    'invar_platform_id':{},
                    'invar_satellite_algorithm':{},
                    'invar_satellite_sensor':{},
                    'invar_rcm_model_id':{},
                    'invar_rcm_model_realization_id':{},
                    'invar_rcm_model_driver':{},
                    'invar_reanalysis_id':{},
                    'invar_gcm_model_id':{},
                    'invar_experiment_name':{},
                    'invar_ensemble_member':{},
                    'invar_bc_method_id':{},
                    'invar_bc_observation_id':{},
                    'invar_bc_period':{'validator':['datetimeYYYY-YYYY']},
                    'invar_variable_name':{},
                    'invar_tracking_id':{'validator':['validate_uuid']},
                    'reference_period':{'validator':['datetimeYYYY-YYYY']},
                    'time_coverage_start':{'validator':['datetimeYYYYMMDD','checklengthisatleast3']},
                    'time_coverage_end':{},
                    'output_frequency':{}, # TODO validate
                    'cdm_datatype':{},
                    'domain':{},
                    'geospatial_bounds':{},
                    'geospatial_lat_min':{'validator':['geospatial_lat_degrees_north']},
                    'geospatial_lat_max':{'validator':['geospatial_lat_degrees_north']},
                    'geospatial_lat_resolution':{'validator':['geospatial_resolution']},
                    'geospatial_lon_min':{'validator':['geospatial_lon_degrees_east']},
                    'geospatial_lon_max':{'validator':['geospatial_lon_degrees_east']},
                    'geospatial_lon_resolution':{'validator':['geospatial_resolution']},
                    'tile':{'validator':['tilennnnn']},
                    'tracking_id':{'validator':['checklengthisatleast3','validate_uuid']},
                    'keywords':{'validator':['clipckeywordvalidator']},
                    'history':{}
                    },
                "drsMappings": {
                    'activity':'activity',
                    'VariableName':'variable_name',
                    'product':'product',
                    'package':'package_name',
                    'domain':'domain',
                    'institution':'institution_id',
                    'sourceDataID':'source_data_id',
                    'sourceDataId':'source_data_id',
                    'frequency':'output_frequency',
                    'StartTime':'time_coverage_start',
                    'EndTime':'time_coverage_end',
                    'Reference_period':'reference_period',
                    'tilennnnn':'tile',#tile-nnnnn will not work, because in that case it looks like two attributes.
                    'GCMName':['invar_rcm_model_driver','invar_reanalysis_id','invar_gcm_model_id'],
                    'ExperimentName':'invar_experiment_name',
                    'EnsembleMember':'invar_ensemble_member',
                    'RCMName':'invar_rcm_model_id',
                    'RCMRealisation':'invar_rcm_model_realization_id',
                    'BcName':'invar_bc_method_id',
                    'BcObsName':'invar_bc_observation_id',
                    'BcRefPeriod':'invar_bc_period',
                    
                    },
                "drsConstructors":{
                    "filename":"<VariableName>_<package>_<institution>_<GCMName>_<ExperimentName>_<EnsembleMember>_[IndicatorRealisation_][<RCMName>_<RCMRealisation>_<domain>_][<BcName>_<BcObsName>_<BcRefPeriod>_] <frequency>_<StartTime-EndTime>_[<Reference_period>_][<tilennnnn>].nc",
                    "dataset": "<activity>.<product>.<package>.<institution>.<GCMName>.<ExperimentName>.<EnsembleMember>.[<RCMName>.<RCMRealisation>.<domain>.][<BcName>.<BcObsName>.<BcRefPeriod>.]<frequency>.[<Reference_period>.]<VariableName>"
                    }
                },
                "CLIPCGeneralDRS":{
                "requiredGlobalAttributes":{
                    'Conventions':{},
                    'activity':{'validator':['activity_is_clipc']},
                    'title':{'validator':['checklengthisatleast3']},
                    'summary':{},
                    'variable_name':{},
                    'product':{},
                    'comment':{},
                    'references':{},
                    'package_name':{},
                    'package_references':{},
                    'institution_id':{},
                    'institution_url':{},
                    'contact':{},
                    'contributor_name':{},
                    'contributor_role':{},
                    'date_created':{'validator':['datetimeYYYYMMDD']},
                    'date_issued':{'validator':['datetimeYYYYMMDD']},
                    'date_modified':{'validator':['datetimeYYYYMMDD']},
                    'realisation_id':{},
                    'source_data_id':{},
                    'source_data_id_comment':{},
                    'invar_platform':{},
                    'invar_platform_id':{},
                    'invar_satellite_algorithm':{},
                    'invar_satellite_sensor':{},
                    'invar_rcm_model_id':{},
                    'invar_rcm_model_realization_id':{},
                    'invar_rcm_model_driver':{},
                    'invar_reanalysis_id':{},
                    'invar_gcm_model_id':{},
                    'invar_experiment_name':{},
                    'invar_ensemble_member':{},
                    'invar_bc_method_id':{},
                    'invar_bc_observation_id':{},
                    'invar_bc_period':{},
                    'invar_variable_name':{},
                    'invar_tracking_id':{'validator':['validate_uuid']},
                    'reference_period':{'validator':['datetimeYYYY-YYYY']},
                    'time_coverage_start':{'validator':['datetimeYYYYMMDD','checklengthisatleast3']},
                    'time_coverage_end':{},
                    'output_frequency':{}, # TODO validate
                    'cdm_datatype':{},
                    'domain':{},
                    'geospatial_bounds':{},
                    'geospatial_lat_min':{'validator':['geospatial_lat_degrees_north']},
                    'geospatial_lat_max':{'validator':['geospatial_lat_degrees_north']},
                    'geospatial_lat_resolution':{'validator':['geospatial_resolution']},
                    'geospatial_lon_min':{'validator':['geospatial_lon_degrees_east']},
                    'geospatial_lon_max':{'validator':['geospatial_lon_degrees_east']},
                    'geospatial_lon_resolution':{'validator':['geospatial_resolution']},
                    'tile':{'validator':['tilennnnn']},
                    'tracking_id':{'validator':['checklengthisatleast3','validate_uuid']},
                    'keywords':{'validator':['clipckeywordvalidator']},
                    'history':{}
                    },
                "drsMappings": {
                    'activity':'activity',
                    'VariableName':'variable_name',
                    'product':'product',
                    'package':'package_name',
                    'domain':'domain',
                    'institution':'institution_id',
                    'sourceDataID':'source_data_id',
                    'sourceDataId':'source_data_id',
                    'frequency':'output_frequency',
                    'StartTime':'time_coverage_start',
                    'EndTime':'time_coverage_end',
                    'Reference_period':'reference_period',
                    'tilennnnn':'tile',#tile-nnnnn will not work, because in that case it looks like two attributes.
                    'version':'version'                   
                    },
                "drsConstructors":{
                    "filename":"<VariableName>_<package>_<institution>_<sourceDataID>_<frequency>_<StartTime-EndTime>_[<Reference_period>_][<tilennnnn>].nc",
                    "dataset": "<activity>.<product>.<package>.<domain>.<institution>.<sourceDataID>.<frequency>.[<Reference_period>].<VariableName>"
                    }
                }
            }
         
    def printmessage(self,message):
        self.stdOutString = self.stdOutString +message+"\n"
        return
    
    def printerror(self,message):
        self.printmessage("[ERROR]\t"+message)
        self.nrOfErrors = self.nrOfErrors +1
        self.errorString = self.errorString+("Error nr %d: "%(self.nrOfErrors))+str(message)+"\n"
        return
      
    ## Returns nonzero if there are errors, otherwise returns zero ##
    #  @return Returns non zero if errors occured
    def hasErrors(self):
        if self.nrOfErrors != 0:
            return 1
        return 0
    
    
    ## Validates DRS facet values for a given validator
    #  @param self The object pointer
    #  @param value The DRS value of the netcdf attribute
    #  @param validator The validator to use
    #  @param nc_attr The name of the netcdf attribute
    def __validate(self,value,validator,nc_attr):
        
        
        if validator == "validate_uuid":
            if(value == " " or value == ""):
                return True
            regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
            match = regex.match(value)
            if bool(match) == False:
                self.printerror('Unable to validate attribute [%s] with value [%s]: should be in form [00000000-0000-4000-0000-000000000000]' % (nc_attr,value))
                return False
            return True
        
        if validator == "geospatial_lat_degrees_north":
            if type(value)!=type("S"):
                return True
                
            if len(value)<2:
                self.printerror('Unable to validate attribute [%s] with value [%s]: should be in form [value<space>degrees_north]' % (nc_attr,value))
                return False
            newvalue = value.split(" ");
            if len(newvalue)<2:
                self.printerror('Unable to validate attribute [%s] with value [%s]: should be in form [value<space>degrees_north]' % (nc_attr,value))
                return False
            if(newvalue[1]!="degrees_north"):
                self.printerror('Unable to validate attribute [%s] with value [%s]: should be in form [value<space>degrees_north]' % (nc_attr,value))
                return False
            return True
        
        if validator == "geospatial_lon_degrees_east":
            if type(value)!=type("S"):
                return True
               
            if len(value)<2:
                self.printerror('Unable to validate attribute [%s] with value [%s]: should be in form [value<space>degrees_east]' % (nc_attr,value))
                return False
            newvalue = value.split(" ");
            if len(newvalue)<2:
                self.printerror('Unable to validate attribute [%s] with value [%s]: should be in form [value<space>degrees_east]' % (nc_attr,value))
                return False
            if(newvalue[1]!="degrees_east"):
                self.printerror('Unable to validate attribute [%s] with value [%s]: should be in form [value<space>degrees_east]' % (nc_attr,value))
                return False
            return True
        
        
        if validator == "geospatial_resolution":
            if type(value)!=type("S"):
                return True
               
            if len(value)<2:
                self.printerror('Unable to validate attribute [%s] with value [%s]: length should be at least 2 characters' % (nc_attr,value))
                return False
            newvalue = value.split(" ");
            if len(newvalue)<2:
                self.printerror('Unable to validate attribute [%s] with value [%s]: should be in form [value<space>unit]' % (nc_attr,value))
                return False
            return True
        
        if validator == "checklengthisatleast3":
            if len(value)<3:
                self.printerror('Unable to validate attribute [%s] with value [%s]: this attribute needs to be specified' % (nc_attr,value))
                return False
            else:
                return True
        
        if validator == "datetimeYYYY-MM-DDTHH_MM_SSZ":
            try:
                datetime.datetime.strptime(value,'%Y-%m-%dT%H:%M:%SZ')
                
            except:
                self.printerror('Unable to validate datetime attribute [%s] with value [%s] against [YYYY-MM-DDTHH:MM:SSZ]' % (nc_attr,value))
                return False
            return True
        
        if validator == "datetimeYYYYMMDD":
            # Date must be either "YYYYMMDD" or " " or ""
            if(value == " " or value == ""):
                return True
            try:
                datetime.datetime.strptime(value,'%Y%m%d')
                
            except:
                self.printerror('Unable to validate datetime attribute [%s] with value [%s] against [YYYYMMDD]' % (nc_attr,value))
                return False
            return True
        
        if validator == "datetimeYYYY-YYYY":
            # Date must be either "YYYY-YYYY" or " " or ""
            if(value == " " or value == ""):
                return True
            try:
                if len(value) != 4+1+4:
                    raise ValueError('Length is not 9')
                values = value.split("-")
                if len(values) != 2:
                    raise ValueError('Does not consist of two YYYY parts')
                datetime.datetime.strptime(values[0],'%Y')
                datetime.datetime.strptime(values[1],'%Y')
            except:
                self.printerror('Unable to validate datetime attribute [%s] with value [%s] against [YYYY-YYYY]' % (nc_attr,value))
                return False
            return True
        
        if validator == "activity_is_clipc":
            if value == "clipc":
                return True
            else:
                self.printerror('Unable to validate activity [%s]. This should be [clipc]' % value)
                return False
         
        if validator == "tilennnnn":
            if(value == " " or value == ""):
                return True
              
            if len(value) == 5:
                if value.isdigit():
                    return True
                else:
                    self.printerror('Unable to validate tilennnnn [%s]. Length is OK, but not all characters are nunbers.' % value)
                    return False
            else:
                self.printerror('Unable to validate tilennnnn [%s]. This should either be an empty string or have a length of 5 digits.' % value)
                return False
              
            
              
        if validator == "clipckeywordvalidator":
            if len(value.split(","))>=2:
                return True;
            else:
                self.printerror('Unable to validate clipc keywords [%s]. This should have at least two values comma separated]' % value)
        return False
    
    ## Expands DRS into an array with optional and mandatory attributes. Mode can be optional, mandatory or unknown.
    #  @param self The object pointer
    #  @param currentDRSStandard The name of the current DRS standard,e.g. CLIPC or CORDEX
    #  @return the array with the expanded DRS
    def __expandDRSMapping(self,drsMappingFilenameOrder):
        parsedFacetDRS = []
        facet = ""
        mode = ""
        mandatory_optional = 0 # means mandatory
        for i in range(0,len(drsMappingFilenameOrder)):
            c=drsMappingFilenameOrder[i]
            if c == "[":
                mandatory_optional=1
            if c == "]" or c == "@":
                mandatory_optional=0
            if c == "@":
                mandatory_optional=2
            if c == "<":
                facet=""
                mode="recordfacet"
            if c == ">":
                if mandatory_optional == 0:
                    parsedFacetDRS.append({facet:"M"});
                elif mandatory_optional == 1:
                    parsedFacetDRS.append({facet:"O"});
                elif mandatory_optional == 2:
                    parsedFacetDRS.append({facet:"U"});
                    
                mode=""
            if  mode=="recording":
                facet=facet+c
            if  mode=="recordfacet":                
                mode="recording"
        return parsedFacetDRS
    
    
    ## Generates the DRS name for a filename or a dataset
    #  @param self The object pointer
    #  @param nc_fid The NetCDF4 dataset pointer
    #  @param baseName The filename without the prefixed path
    #  @param currentDRSStandard The name of the current DRS standard,e.g. CLIPC or CORDEX
    def __generateDRSName(self,nc_fid,currentDRSStandard, filename_or_dataset = "filename",separator=None):
        
        
        if separator == None:
            if filename_or_dataset=="filename":
                separator="_"
            else:
                separator="."
        
        parsedFacetDRS = self.__expandDRSMapping(self.DRS[currentDRSStandard]["drsConstructors"][filename_or_dataset]);
        
        nc_attrs = self.__getGlobalAttributes(nc_fid)
        drsMappings =  self.DRS[currentDRSStandard]["drsMappings"]
        suggestedFileName = "";
        usedDRSFileNameMapping = "";
        for i in range(0,len(parsedFacetDRS)):
            facetName = parsedFacetDRS[i].keys()[0]
            mo = parsedFacetDRS[i].values()[0] # mandatory or optional
            
            # Get facetValue, e.g compose time_coverage_start-time_coverage_end from multiple attributes
            fs = facetName.split("-") 
            facetValue = ""
            for drsFacet in fs:
                netcdfAttrName=[]
                try:
                    netcdfAttrName=drsMappings[drsFacet]
                    if type(netcdfAttrName) == type("String"):
                        netcdfAttrName = [netcdfAttrName]
                except:
                    if mo != "U":
                        self.printerror("DRS facet '%s' is unknown" % drsFacet)
                    pass
                
                # Loop over the netcdf attributes names and compose the drsfacet.
                for f in netcdfAttrName:
                    #self.printmessage(str(f))

                    if f in nc_attrs:
                        v = "Unable to read nc attribute value"
                        try:
                            v = nc_fid.getncattr(f)
                        except:
                            self.printerror('Unable to read netcdf attribute %s as string. Have you provided a string type in your netcdf attribute?' % (f))
                            pass
                        if v == " ":
                            v=""
                        if len(v)>0:
                            #self.printmessage("[INFO]\tFound attribute ["+drsFacet+"]/["+f+"] = "+v)
                            if len(facetValue) > 0:
                                facetValue= facetValue+"-"
                            if drsFacet == "BcRefPeriod":
                                facetValue=facetValue+"bcref-"
                            facetValue=facetValue+v
                        else:
                            self.printmessage("[INFO]\tAttribute ["+drsFacet+"]/["+f+"] is not filled in")
                        
            fnFacetPart=""
            if len(facetValue)>0:
                    fnFacetPart=facetValue
            else:
                if mo == "M":
                    fnFacetPart="<%s>"%facetName
                if mo == "U":
                    fnFacetPart="*"
           
            if len(fnFacetPart)>0:
                if len(usedDRSFileNameMapping)>0 and usedDRSFileNameMapping[-1]!=separator:
                        usedDRSFileNameMapping = usedDRSFileNameMapping  +separator
                usedDRSFileNameMapping = usedDRSFileNameMapping+"<"+facetName+">"
                if len(suggestedFileName)>0 and suggestedFileName[-1]!=separator:
                        suggestedFileName = suggestedFileName  +separator
                suggestedFileName = suggestedFileName + fnFacetPart
        return suggestedFileName,usedDRSFileNameMapping        
    
    ## Validates the filename against the found DRS.
    #  @param self The object pointer
    #  @param nc_fid The NetCDF4 dataset pointer
    #  @param baseName The filename without the prefixed path
    #  @param currentDRSStandard The name of the current DRS standard,e.g. CLIPC or CORDEX
    def __validateFileName(self,nc_fid,baseName,currentDRSStandard):               
        suggestedFileName,usedDRSFileNameMapping = self.__generateDRSName(nc_fid,currentDRSStandard);
        suggestedFileName = suggestedFileName + ".nc"
        self.DRSFilename = suggestedFileName
        self.printmessage("[INFO]\tUsed DRS file mapping: "+usedDRSFileNameMapping)
        self.printmessage("[INFO]\tDRS Filename: "+suggestedFileName)
        
        # Now test if the composed filename from the drs metadata matches the given filename
        if fnmatch.fnmatch(baseName,suggestedFileName):
                self.printmessage("[OK]\tFilename matches %s" %(suggestedFileName))
                return True
        else:
                self.printerror("Derived DRS filename\n[%s] does not match NetCDF filename\n[%s]" %(suggestedFileName,baseName))
                return False
        
    ## Returns the global attributes for a netCDF4 dataset
    #  @param self The object pointer
    #  @param nc_fid The NetCDF4 dataset pointer
    def __getGlobalAttributes(self,nc_fid):
        nc_attrs = nc_fid.ncattrs()
        return nc_attrs

    ## Generate the DRS id
    #  @param self The object pointer
    #  @param nc_fid The NetCDF4 dataset pointer
    #  @param baseName The filename without the prefixed path
    #  @param currentDRSStandard The name of the current DRS standard,e.g. CLIPC or CORDEX
    def generateDRSDatasetIdentifier(self,nc_fid,currentDRSStandard):
        suggestedFileName,usedDRSFileNameMapping = self.__generateDRSName(nc_fid,currentDRSStandard,"dataset");
        self.DRSDatasetname = suggestedFileName
        self.printmessage("[INFO]\tUsed DRS dataset mapping: "+usedDRSFileNameMapping)
        self.printmessage("[INFO]\tDRS Dataset: %s"%suggestedFileName)
        return

    ## Check basic CF conventions
    # @param nc_fid The netcdf file object
    def checkCF(self,nc_fid):
      nc_attrs = nc_fid.ncattrs()
      
      hasCalendar = False
      if "time" not in nc_fid.variables:
        self.printerror("time variable not found");
        return

      if "calendar" in nc_fid.variables["time"].ncattrs():
        hasCalendar = True
        
      if "units" not in nc_fid.variables["time"].ncattrs():
        self.printerror("time variable has no units attribute");
        
      if "time_bnds" in nc_fid.variables:
        if "units" not in nc_fid.variables["time_bnds"].ncattrs():
          if fixFiles == False:
            self.printerror("time_bnds variable has no units attribute");
          else:
            nc_fid.variables["time_bnds"].setncattr("units",nc_fid.variables["time"].getncattr("units"))
            
        if hasCalendar:
          if "calendar" not in nc_fid.variables["time_bnds"].ncattrs():
            if fixFiles == False:
              self.printerror("time_bnds variable has no calendar attribute while time variable has a calendar attribute");
            else:
              nc_fid.variables["time_bnds"].setncattr("calendar",nc_fid.variables["time"].getncattr("calendar"))
        
      #Check variable units as well
      if "variable_name" not in nc_attrs:
        self.printerror("global attribute variable_name is not defined");
        return
      variable_name = nc_fid.getncattr("variable_name")
      if variable_name not in nc_fid.variables:
        self.printerror("Variable advertised in variable_name not found");
        return
      
      if "units" not in nc_fid.variables[variable_name].ncattrs():
        if fixFiles == False:
          self.printerror("units are missing for variable "+str(variable_name));
        else:
          nc_fid.variables[variable_name].setncattr("units","-")
          
      if "long_name" not in nc_fid.variables[variable_name].ncattrs():
        self.printerror("long_name are missing for variable "+str(variable_name));
          
      
        self.printerror("standard_name are missing for variable "+str(variable_name));
        
      return


    ## Checks a NetCDF file by a filename.
    #  @param fileName The filename or opendap url for the netcdf file
    #  @param projectName The name of the project,e.g. CLIPC or CORDEX
    def checkFile(self,fileName,projectName):

        self.nrOfErrors = 0
        self.errorString = ""
        self.stdOutString = ""
        self.DRSDatasetname=""
        self.DRSFilename=""

        baseName= os.path.basename(fileName)
        if fixFiles == True:
          nc_fid = netCDF4.Dataset(fileName,'a')  
        else:
          nc_fid = netCDF4.Dataset(fileName,'a')  
          
        nc_attrs = self.__getGlobalAttributes(nc_fid)
        
        currentDRSStandard= projectName
        
        if cfOnly == False:
          #if nc_attrs #TODO determine if this is the model version or the general version
          if projectName == "CLIPC":
              """ By default the CLIPCGeneralDRS is used """
              currentDRSStandard = "CLIPCGeneralDRS"
              
              """ Check if this is the MODELDRS """
              """ invar_rcm_model_driver','invar_reanalysis_id','invar_gcm_model_id' """
              try:
                  invar_rcm_model_driver = nc_fid.getncattr("invar_rcm_model_driver")
                  invar_reanalysis_id    = nc_fid.getncattr("invar_reanalysis_id")
                  invar_gcm_model_id     = nc_fid.getncattr("invar_gcm_model_id")
                  source_data_id         = nc_fid.getncattr("source_data_id")
                  
                  """ sourceDataID must be left empty if the model DRS is used. When sourceDataID is provided general DRS is used. """
                  if len(source_data_id) < 3:
                      currentDRSStandard = "CLIPCModelDRS"
                      self.printmessage("[INFO]\tDetected the CLIPC Model DRS standard because source_data_id is empty.")
                  else:
                      self.printmessage("[INFO]\tDetected the CLIPC General DRS standard because source_data_id is set to [%s]."%source_data_id)
                      
                  if len(invar_gcm_model_id) > 3 :
                      if len(invar_rcm_model_driver) > 3 :
                          self.printerror('invar_rcm_model_driver: Too many attributes composing the GCMName are defined. Please fill out either invar_rcm_model_driver, invar_reanalysis_id or invar_gcm_model_id')
                      if len(invar_reanalysis_id) > 3 :
                          self.printerror('invar_reanalysis_id: Too many attributes composing the GCMName are defined. Please fill out either invar_rcm_model_driver, invar_reanalysis_id or invar_gcm_model_id')

                      
              except:
                  self.printmessage(str(sys.exc_info()[0]))
                  pass
                  
              

              

          
          self.printmessage('[INFO]\tUsing %s standard'%currentDRSStandard)
          
          requiredGlobalAttributes =  self.DRS[currentDRSStandard]["requiredGlobalAttributes"]
          for nc_attr in requiredGlobalAttributes:
              if nc_attr in nc_attrs:
                  nc_attr_value = "Unable to read nc attribute value"
                  try:
                      nc_attr_value = nc_fid.getncattr(nc_attr)
                  except:
                      self.printerror('Unable to read netcdf attribute %s as string. Have you provided a string type in your netcdf attribute?' % (nc_attr))
                      pass
                    
                  validator = None
                  try:
                      validator = requiredGlobalAttributes[nc_attr]["validator"]
                  except:
                      pass
                  if validator!= None:
                      valid = True
                      for v in validator:
                        if self.__validate(nc_attr_value,v,nc_attr) == False:
                          #self.printerror('Validator [%s] failed\t"%s" = "%s"' % (v,nc_attr,nc_attr_value))
                          valid = False
                      if valid == True:
                        self.printmessage('[OK]\tValidated\t"%s" = "%s"' % (nc_attr,nc_attr_value))
                  else:
                      self.printmessage('[OK]\tFound\t\t"%s" = "%s" ' % (nc_attr,nc_attr_value))
              else:
                  self.printerror('%s is missing' % (nc_attr))
              
          #Validate filename
          self.__validateFileName(nc_fid,baseName,currentDRSStandard)
          
          #Generate the DRS id 
          self.generateDRSDatasetIdentifier(nc_fid,currentDRSStandard)
          
        
        #Check basic CF stuff
        self.checkCF(nc_fid)
        
        self.printmessage("[INFO]\tNr of found errors: %d" % self.nrOfErrors)
        
        if cfOnly == False:
          self.printmessage("[DRSFilename]   [%s]"%self.DRSFilename)
          self.printmessage("[DRSDatasetname][%s]"%self.DRSDatasetname)
        
        if self.nrOfErrors == 0:
            self.printmessage("[GOOD]\tFile has been validated with zero errors! Well done!")
        
        if self.nrOfErrors != 0:
            self.printmessage("[ERROR]\tFile is not conforming '%s' DRS standard. %d issue(s) found" % (currentDRSStandard,self.nrOfErrors))
            self.errorString = self.errorString+str("Please note: using [%s]." %(currentDRSStandard))

            
        return
