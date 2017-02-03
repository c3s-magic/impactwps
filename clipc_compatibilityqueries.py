import netCDF4

import logging;

## The clipc_compatibilityqueries class
#
# Use testfiles method.
class clipc_compatibilityqueries:

    ## The constructor.
    def __init__(self):
        return

    messageString = ""
    numErrors = 0

    def _debug(self,message):
      logging.debug(message)
      print(message)

    def _addMessage(self,message):
      self.messageString = self.messageString +message+"\n"
      
    def getMessages(self):
      return self.messageString
    
    def getNumErrors(self):
      return self.numErrors
    
    ## Identical query that only compares if the full entry of a particular attribute field is identical or not identical for two datasets
    # @param attrname The attribute name to check
    # @param message The message to log if something is wrong
    # @return True if error occured, False if OK
    def _typeAQuery(self,attrname,message):
      if attrname in self.nc_attrs_a and attrname in self.nc_attrs_b :
        attribute_value_a = self.nc_fid_a.getncattr(attrname)
        attribute_value_b = self.nc_fid_b.getncattr(attrname)
        if attribute_value_a != attribute_value_b:
          self._addMessage("%s: \n"
          "%s A: [%s]\n"
          "%s B: [%s]" % (message,attrname,attribute_value_a,attrname,attribute_value_b))
          self.numErrors+=1
          return True
        else:
          self._debug("%s is OK" % attrname)
      else:
        self._debug("Unable to find %s. No error!" % attrname);
      return False

   ## The contains query is necessary if the information of interest is only a small part of a longer text in a particular attribute field.
    # @param attrname The attribute name to check
    # @param checkforvalue Check if this value occurs in only one of the attributes
    # @param message The message to log if something is wrong
    # @return True if error occured, False if OK
    def _typeBQuery(self,attrname,checkforvalue,message):
      if attrname in self.nc_attrs_a and attrname in self.nc_attrs_b :
        attribute_value_a = self.nc_fid_a.getncattr(attrname)
        attribute_value_b = self.nc_fid_b.getncattr(attrname)
        counter=0
        self._debug(attribute_value_a);
        self._debug(attribute_value_b);
        if checkforvalue in attribute_value_a:
          counter+=1
        if checkforvalue in attribute_value_b:
          counter+=1
        if counter == 1:
          self._addMessage("%s: \n"
          "%s A: [%s]\n"
          "%s B: [%s]" % (message,attrname,attribute_value_a,attrname,attribute_value_b))
          self.numErrors+=1
          return True
        else:
          self._debug("%s is OK" % attrname)
      else:
        self._debug("Unable to find %s. No error!" % attrname);
      return False
      
    ## The conditional query is necessary if the information in two attributes need to be checked
    # @param attrname The attribute name to check
    # @param doesnotcontain_attrname The other attribute that should not contain doesnotcontain_attrvalue
    # @param doesnotcontain_attrvalue The other attribute value that should not occur.
    # @param message The message to log if something is wrong
    # @return True if error occured, False if OK
    def _typeCQuery(self,attrname,doesnotcontain_attrname,doesnotcontain_attrvalue,message):
      if attrname in self.nc_attrs_a and attrname in self.nc_attrs_b and doesnotcontain_attrname in self.nc_attrs_a and doesnotcontain_attrname in self.nc_attrs_b :
        attribute_value_a = self.nc_fid_a.getncattr(attrname)
        attribute_value_b = self.nc_fid_b.getncattr(attrname)
        dnc_attribute_value_a = self.nc_fid_a.getncattr(doesnotcontain_attrname)
        dnc_attribute_value_b = self.nc_fid_b.getncattr(doesnotcontain_attrname)
        counter=0
        self._debug(attribute_value_a);
        self._debug(attribute_value_b);
        self._debug("Checking if %s not in file_a and not in file_b" % doesnotcontain_attrvalue)
        if doesnotcontain_attrvalue not in dnc_attribute_value_a and doesnotcontain_attrvalue not in dnc_attribute_value_b:
          #Both sets could be bias corrected. E.g. nonClimatic-derived is not in one them. Now check if they use the same.
          self._debug("Both sets could be bias corrected");
          if attribute_value_a != attribute_value_b:
            #Bias correction methods are not the same
            self._debug("Bias correction methods are not the same");
            self._addMessage("%s: \n"
            "%s A: [%s]\n"
            "%s B: [%s]" % (message,attrname,attribute_value_a,attrname,attribute_value_b))
            self.numErrors+=1
            return True
          else:
            # Bias correction methods are the same 
            self._debug("OK Found %s in both and they are the same. Is OK" % doesnotcontain_attrvalue)
        else:
          # One of the files is not bias corrected.
          self._debug("%s in one of the files" % doesnotcontain_attrvalue)
      else:
        # Unable to find attributes
        self._debug("Unable to find %s. No error!" % attrname);
      return False
          
    ## main function to use
    # @param filea Netcdf file location or url
    # @param fileb Netcdf file location or url
    def testfiles(self,filea,fileb):
      self.messageString = ""
      self.numErrors = 0
      self.nc_fid_a = netCDF4.Dataset(filea,'r')
      self.nc_fid_b = netCDF4.Dataset(fileb,'r')  
      self.nc_attrs_a = self.nc_fid_a.ncattrs()
      self.nc_attrs_b = self.nc_fid_b.ncattrs()
      
      ## Type A Identical query: Compare time frequency ##
      self._typeAQuery("output_frequency","Your combination is based on two datasets with different temporal resolutions")
        
      ### Type B contains query
      self._typeBQuery("source_data_id","ens-multiModel-mean","Your combination is based on two datasets with different data source id's");
      
      ### Type C conditional query
      self._typeCQuery("invar_bc_method_id","source_data_id","nonClimatic-derived","Your combination is based on two datasets with different characteristics regarding bias-correction");

