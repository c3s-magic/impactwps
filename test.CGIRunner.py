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
import zipfile
from xml.sax.saxutils import escape
import os
import CGIRunner

        

def wf(data):
  sys.stdout.write(data)
  return
   

#  print data

a = CGIRunner.CGIRunner()
f = open('test.CGIRunner.data', 'r')

start_index = 0

statinfo = os.stat('test.CGIRunner.data')

while(start_index<statinfo.st_size):
  end_index = start_index+10
  f.seek(start_index)
  data = f.read(end_index - start_index)
  a.filterHeader(data,wf)
  start_index = end_index 

print "ready"        
        


