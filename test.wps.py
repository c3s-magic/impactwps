import clipc_combine_execute
from pywps.Process import WPSProcess
from pywps.Process import Status

#Override status class and method in order to print to stdout directly.
class MyStatus(Status):
  def set(self,string,p):
    print(string)
status = MyStatus();

p=clipc_combine_execute.Process()
p.status=status

opendap_url1 =	'http://opendap.knmi.nl/knmi/thredds/dodsC/CLIPC/tier1_indicators/icclim_cerfacs/vDTR/MPI-M-MPI-ESM-LR_rcp45_r1i1p1_SMHI-RCA4_v1-SMHI-DBS43-MESAN-1989-2010/vDTR_OCT_MPI-M-MPI-ESM-LR_rcp45_r1i1p1_SMHI-RCA4_v1-SMHI-DBS43-MESAN-1989-2010_EUR-11_2006-2100.nc'
opendap_url2 =  'http://opendap.knmi.nl/knmi/thredds/dodsC/CLIPC/tier1_indicators/icclim_cerfacs/TNn/MPI-M-MPI-ESM-LR_rcp85_r1i1p1_SMHI-RCA4_v1/TNn_OCT_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_SMHI-RCA4_v1_EUR-11_2006-2100.nc'

leftbb = "0"
botmbb = "30"
rghtbb = "30"
topbb  = "50" 

bbox = [ leftbb, botmbb, rghtbb , topbb] #None
time1 = '2010-10-16T00:00:00Z' #None
time2 = '2011-10-16T00:00:00Z' #None

  
#["add","substract","divide","multiply"] 
#["normnone" , "normzero", "normminmax", "normstndrd"]

# Set input of pyWPS process
p.inputa.default=opendap_url1;
p.inputb.default=opendap_url2;

p.operator.default="subtract"#"multiply"#"subtract"

p.bbox.default=bbox;

p.timea.default=time1;
p.timeb.default=time2;

p.width.default = 350
p.height.default = 350

p.norm1.default="normnone"
p.norm2.default="normzero"

p.execute()