import urllib
import isodate 
import time
import netCDF4
from netCDF4 import MFDataset
import sys
from subprocess import PIPE, Popen, STDOUT
from threading  import Thread
import json
import os
import shutil
from mkdir_p import *
import zipfile
from xml.sax.saxutils import escape
import CGIRunner

def daterange(start_date, end_date, delta):
  d = start_date
  while d < end_date:
    yield d
    d += delta
    

  




def cleanlog(tmpdir):
  try:
    os.remove(tmpdir+"/iteratewcs.log")
  except:
    pass
    

def dolog(tmpdir, data):
  with open(tmpdir+"/iteratewcs.log", "a") as myfile:
      myfile.write(str(data)+"\n")
      myfile.flush();

def openfile(file):
  with open (file, "r") as myfile:
    data = myfile.read()
    return data
  
def getlog(tmpdir):
  return openfile(tmpdir+"/iteratewcs.log")
  
  
def makezip(tmpdir,OUTFILE):
  currentpath=os.getcwd()
  os.chdir(tmpdir)
  """ Otherwise, make a zipfile of all files """
  zipf = zipfile.ZipFile(OUTFILE, 'w',zipfile.ZIP_DEFLATED)
  for root, dirs, files in os.walk("."):
    for file in files:
      zipf.write(os.path.join(root, file))
  zipf.close()
  os.chdir(currentpath)

"""
This requires a working ADAGUC server in the PATH environment, ADAGUC_CONFIG environment variable must point to ADAGUC's config file.
"""

def iteratewcs(TIME = "",BBOX = "-180,-90,180,90",CRS = "EPSG:4326",RESX=1,RESY=1,WCSURL="",TMP=".",COVERAGE="pr",LOGFILE=None,OUTFILE="out.nc",FORMAT="NetCDF",callback=None):
  tmpdir = TMP+"/iteratewcstmp";
  shutil.rmtree(tmpdir, ignore_errors=True)
  mkdir_p(tmpdir);
  
  start_date = isodate.parse_datetime(TIME.split("/")[0]);
  end_date = isodate.parse_datetime(TIME.split("/")[1]);
  timeres = isodate.parse_duration(TIME.split("/")[2]);
  
  datestodo = list(daterange(start_date, end_date, timeres));
  
  if(len(datestodo) == 0):
    datestodo.append(start_date)
  
  
  numdatestodo=len(datestodo);
  datesdone = 0;
    
  for single_date in datestodo:
 
    wcstime=time.strftime("%Y-%m-%dT%H:%M:%SZ", single_date.timetuple())
    single_date2 = single_date;
    single_date2 += timeres
    wcstime2=time.strftime("%Y-%m-%dT%H:%M:%SZ", single_date2.timetuple())
    
    filetime=time.strftime("%Y%m%dT%H%M%SZ", single_date.timetuple())
    url = WCSURL + "REQUEST=GetCoverage&";
    url = url + "FORMAT="+FORMAT+"&";
    url = url + "COVERAGE="+COVERAGE+"&";
    url = url + "TIME="+wcstime+"&";
    #url = url + "TIME="+wcstime+"/"+wcstime2+"&";
    url = url + "BBOX="+BBOX+"&";
    url = url + "RESX="+str(RESX)+"&";
    url = url + "RESY="+str(RESY)+"&";
    url = url + "CRS="+CRS+"&";
    
    
    
    cmds=['adagucserver']
    
    filetogenerate = tmpdir+"/file"+filetime
    #filetogenerate = "/tmp"+"/file"+filetime
    
    if(FORMAT == "netcdf"):
      filetogenerate = filetogenerate  + ".nc"
    if(FORMAT == "geotiff"):
      filetogenerate = filetogenerate  + ".tiff"
    if(FORMAT == "aaigrid"):
      filetogenerate = filetogenerate  + ".grd"
      
    env = {}
    if(LOGFILE != None):
      env["ADAGUC_ERRORFILE"]=LOGFILE
    
    try:
      os.remove(tmpdir+"/adaguclog.log")
    except:
      pass
    env["ADAGUC_LOGFILE"]=tmpdir+"/adaguclog.log"
    
    status = CGIRunner.CGIRunner().run(cmds,url,out = filetogenerate,extraenv=env)

    adaguclog = openfile(tmpdir+"/adaguclog.log");
    
    if(status != 0):
      raise ValueError( "Unable to retrieve "+url+"\n"+adaguclog+"\n");
    
    if(os.path.isfile(filetogenerate) != True):
      raise ValueError ("Succesfully completed WCS, but no data found for "+url+"\n"+adaguclog+"\n");
   
    if(callback==None):
      print str(int((float(datesdone)/numdatestodo)*90.))
    else:
      callback(wcstime,((float(datesdone)/float(numdatestodo))*90.))
        
        
    #shutil.copyfile(filetogenerate ,"/tmp/test/"+filetime+".nc")
    datesdone=datesdone+1;
  
 
  def monitor2(line):
    dolog(tmpdir,line);
    try:
      data = json.loads(line)
      if(callback == None):
        print float(data["percentage"])*(1./10)+90
      else:
        callback(data["message"],float(data["percentage"])*(1./10)+90)
    except:
      callback(line,50)
  
  
  """ If it is netcdf, make a new big netcdf file """
  if(FORMAT == "netcdf"):
    cleanlog(tmpdir);
    dolog(tmpdir,tmpdir)
    dolog(tmpdir,OUTFILE)
    cmds=['aggregate_time',tmpdir,OUTFILE]
    dolog(tmpdir,cmds)
    status = CGIRunner.CGIRunner().startProcess(cmds,monitor2)
    
    if(status != 0):
      dolog(tmpdir,"statuscode: "+str(status))
      
      data = getlog(tmpdir)
      
      raise ValueError('Unable to aggregate: statuscode='+str(status)+"\n"+data)
  else:
    makezip(tmpdir,OUTFILE)
    
    
    
  shutil.rmtree(tmpdir, ignore_errors=True)  
  return 0
  
def test():  
  def callback(m,p):
    print p
    
  TIME = "2006-01-01T12:00:00Z/2006-02-01T12:00:00Z/PT24H";
  BBOX = "-179.4375,-89.702158,180.5625,89.7021580";
  CRS = "EPSG:4326";
  WCSURL = "source=http://opendap.knmi.nl/knmi/thredds/dodsC/IS-ENES/TESTSETS/tasmax_day_EC-EARTH_rcp26_r8i1p1_20060101-20251231.nc&SERVICE=WCS&";
  RESX=1.125;
  RESY=1.121276975;
  ##BBOX="0,50,5,55"
  ##RESX=1;
  ##RESY=1
  #os.remove("/nobackup/users/plieger/projects/data/sdpkdc/test/interpolfix.nc")
  iteratewcs(TIME=TIME,BBOX=BBOX,COVERAGE="tasmax",CRS=CRS,WCSURL=WCSURL,RESX=RESX,RESY=RESY,LOGFILE="/tmp/log.txt",callback=callback,OUTFILE="/nobackup/users/plieger/projects/data/sdpkdc/test/interpolfix.nc")

#test()