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
from xml.dom import minidom
import CGIRunner
import re

  
    
def daterange(start_date, end_date, delta):
  d = start_date
  while d <= end_date:
    yield d
    d += delta
    

  
def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None



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
  
def callADAGUC(adagucexecutable,tmpdir,LOGFILE,url,filetogenerate):
  env = {}
  if(LOGFILE != None):
    env["ADAGUC_ERRORFILE"]=LOGFILE
  try:
    os.remove(tmpdir+"/adaguclog.log")
  except:
    pass
  env["ADAGUC_LOGFILE"]=tmpdir+"/adaguclog.log"
  return CGIRunner.CGIRunner().run([adagucexecutable],url,out = filetogenerate,extraenv=env)  


def describeCoverage(adagucexecutable,tmpdir,LOGFILE,WCSURL,COVERAGE):
  
  filetogenerate = tmpdir+"/describecoverage.xml"
  url = WCSURL + "REQUEST=DescribeCoverage&";
  url = url + "COVERAGE="+COVERAGE+"&";
  status = callADAGUC(adagucexecutable,tmpdir,LOGFILE,url,filetogenerate);
  
  if(status != 0):
    adaguclog = openfile(tmpdir+"/adaguclog.log");
    raise ValueError( "Unable to retrieve "+url+"\n"+adaguclog+"\n");
  
  if(os.path.isfile(filetogenerate) != True):
    adaguclog = openfile(tmpdir+"/adaguclog.log");
    raise ValueError ("Succesfully completed WCS DescribeCoverage, but no data found. Log is: "+url+"\n"+adaguclog+"\n");
  

  try:
    xmldoc = minidom.parse(filetogenerate)
  except:
    adaguclog = openfile(tmpdir+"/adaguclog.log");
    raise ValueError ("Succesfully completed WCS DescribeCoverage, but no data found for "+url+"\n"+adaguclog+"\n");
  #print(itemlist[0].childNodes)
  try:
    itemlist = xmldoc.getElementsByTagName('gml:timePosition')
    if(len(itemlist)!=0):

      listtoreturn  = [];
      for s in itemlist:
        listtoreturn.append(isodate.parse_datetime(s.childNodes[0].nodeValue))
      return listtoreturn
    else:
      start_date = xmldoc.getElementsByTagName('gml:begin')[0].childNodes[0].nodeValue
      end_date = xmldoc.getElementsByTagName('gml:end')[0].childNodes[0].nodeValue
      res_date  = xmldoc.getElementsByTagName('gml:duration')[0].childNodes[0].nodeValue
      print start_date
      print end_date
      print res_date
      return list(daterange(isodate.parse_datetime(start_date),isodate.parse_datetime(end_date),isodate.parse_duration(res_date)));
  except:
    pass
  
  return []
  
"""
This requires a working ADAGUC server in the PATH environment, ADAGUC_CONFIG environment variable must point to ADAGUC's config file.
"""
def iteratewcs(TIME = "",BBOX = "-180,-90,180,90",CRS = "EPSG:4326",RESX=1,RESY=1,WCSURL="",TMP=".",COVERAGE="pr",LOGFILE=None,OUTFILE="out.nc",FORMAT="netcdf",callback=None):
  adagucexecutable='adagucserver'
  
  """ Check if adagucserver is in the path """
  if(which(adagucexecutable) == None):
    raise ValueError("ADAGUC Executable '"+adagucexecutable+"' not found in PATH");
  
  callback("Starting iterateWCS",1)
  tmpdir = TMP+"/iteratewcstmp";
  shutil.rmtree(tmpdir, ignore_errors=True)
  mkdir_p(tmpdir);
  
  """ Determine which dates to do based on describe coverage call"""
  callback("Starting WCS DescribeCoverage",1)
  founddates = describeCoverage(adagucexecutable,tmpdir,LOGFILE,WCSURL,COVERAGE);
  
  start_date=""
  end_date=""
  
  if len(TIME) > 0 :
    if len(TIME.split("/")) >= 2:
      start_date = isodate.parse_datetime(TIME.split("/")[0]);
      end_date = isodate.parse_datetime(TIME.split("/")[1]);

  
  
  callback("File has "+str(len(founddates))+" dates",1)
  datestodo = []
  
  
  if len(founddates) > 0:
        for date in founddates:
            if(date>=start_date and date<=end_date):
                datestodo.append(date)
  else:
    datestodo.append("*");
  
  callback("Found "+str(len(datestodo))+" dates",1)
  
  if(len(datestodo) == 0):
    raise ValueError("No data found in resource for given dates. Possible date range should be within "+str(founddates[0])+" and "+str(founddates[-1]))
  
  
  numdatestodo=len(datestodo);
  datesdone = 0;
  filetogenerate = ""
  callback("Starting Iterating WCS GetCoverage",1)
  """ Make the WCS GetCoverage calls """
  for single_date in datestodo:
 
    filetime=""
    wcstime=""
    
    
    url = WCSURL + "REQUEST=GetCoverage&";
    url = url + "FORMAT="+urllib.quote_plus(FORMAT)+"&";
    url = url + "COVERAGE="+urllib.quote_plus(COVERAGE)+"&";
    if single_date != "*":
      wcstime=time.strftime("%Y-%m-%dT%H:%M:%SZ", single_date.timetuple())
      filetime=time.strftime("%Y%m%dT%H%M%SZ", single_date.timetuple())
      url = url + "TIME="+urllib.quote_plus(wcstime)+"&";
        
    url = url + "BBOX="+BBOX+"&";
    url = url + "RESX="+str(RESX)+"&";
    url = url + "RESY="+str(RESY)+"&";
    url = url + "CRS="+urllib.quote_plus(CRS)+"&";
    

    
 
    
    filetogenerate = tmpdir+"/file"+filetime
    
    if(FORMAT == "netcdf"):
      filetogenerate = filetogenerate  + ".nc"
    if(FORMAT == "geotiff"):
      filetogenerate = filetogenerate  + ".tiff"
    if(FORMAT == "aaigrid"):
      filetogenerate = filetogenerate  + ".grd"
    
    status = callADAGUC(adagucexecutable,tmpdir,LOGFILE,url,filetogenerate);
    
    if(status != 0):
      adaguclog = openfile(tmpdir+"/adaguclog.log");
      raise ValueError( "Unable to retrieve "+url+"\n"+adaguclog+"\n");
    
    if(os.path.isfile(filetogenerate) != True):
      adaguclog = openfile(tmpdir+"/adaguclog.log");
      raise ValueError ("Succesfully completed WCS GetCoverage, but no data found for "+url+"\n"+adaguclog+"\n");
   
    if(callback==None):
      print str(int((float(datesdone)/numdatestodo)*90.))
    else:
      callback(wcstime,((float(datesdone)/float(numdatestodo))*90.))
        
        
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
    if datesdone > 1:
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
      shutil.copyfile(filetogenerate ,OUTFILE)
      
  else:
    makezip(tmpdir,OUTFILE)
    
    
    
  shutil.rmtree(tmpdir, ignore_errors=True)  
  return 0
  

