from clipc_compatibilityqueries import clipc_compatibilityqueries

checker = clipc_compatibilityqueries()

# See for data catalog here: http://opendap.knmi.nl/knmi/thredds/catalog/CLIPC/catalog.html

checker.testfiles("http://opendap.knmi.nl/knmi/thredds/dodsC/CLIPC/jrc/ano_FAPARMean_pheno_JRC_1.0_EC-JRC_FAPAR_JRC_yr_19980101-20111231_1998-2011.nc",
                  "http://opendap.knmi.nl/knmi/thredds/dodsC/CLIPC/tudo/tier3/waterb_arcgis-10-4-0_IRPUD_JRC-LUISA-Landuse_10yr_20100101-20501231.nc")

print("------- START MESSAGE --------");
print(checker.getMessages())
print("------- END MESSAGE --------");
print("Numer of errors: "+str(checker.getNumErrors()))

