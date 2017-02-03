from SimpleDRSChecker import SimpleDRSChecker

drsChecker = SimpleDRSChecker()

#drsChecker.checkFile("evspsbl_AFR-44i_ECMWF-ERAINT_evaluation_r1i1p1_KNMI-RACMO22T_v1_mon_200101-201012.nc","CORDEX")
drsChecker.checkFile("gsi_nco-4-4-8_CERFACS_multi-platform-tier2v1_day_19890101-20101231.nc","CLIPC")
#drsChecker.checkFile("tasmax_EUR-05_SMHI-HIRLAM_RegRean_v1d1-v1d2_SMHI-MESAN_v1_day_20100101-20101231.nc","CLIPC")
print drsChecker.stdOutString
print "DatasetDRS :"+drsChecker.DRSDatasetname
print "FilenameDRS:"+drsChecker.DRSFilename
print drsChecker.errorString    
