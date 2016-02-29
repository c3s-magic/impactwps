import socket
#timeout = 10

"""

"""
import urllib
from pywps.Process import WPSProcess
from os.path import expanduser

#import netcdftime

#import logging;

#import os

#import inspect


#for name, obj in inspect.getmembers(netcdftime):
    #if inspect.isclass(obj):
        #logging.debug(obj)
#for key in os.environ.keys():
    #logging.debug("export %s=%s " % (key,os.environ[key]))



home = expanduser("~")


class Process(WPSProcess):
     def __init__(self):
         # init process
         WPSProcess.__init__(self,
                             identifier="timeseries_avg2D", #the same as the file name
                             title="TimeSeries",
                             version = "1.0",
                             storeSupported = True,
                             statusSupported = True,
                             abstract="Displays timeseries plots averaged over user-defined regions.",
                             grassLocation =False)
         self.startIndex = self.addLiteralInput(identifier="startIndex",title = "Time start index",type="String",default=0)
         self.stopIndex = self.addLiteralInput(identifier="stopIndex",title = "Time stop index, 0 means to the end of the time dimension",type="String",default=0)
         self.tag = self.addLiteralInput(identifier="tag",title = "Specify a custom title for this process",type="String",default="unspecified")
         self.resource = self.addLiteralInput(identifier="resource",title = "resource",type="String",abstract="application/netcdf",minOccurs=0,maxOccurs=1024,
                                              default="http://albedo2.dkrz.de/thredds/dodsC/cmip5.output1.ICHEC.EC-EARTH.amip.day.atmos.day.r1i1p1.tas.20120617.aggregation.1,http://albedo2.dkrz.de/thredds/dodsC/cmip5.output1.ICHEC.EC-EARTH.amip.day.atmos.day.r1i1p1.tasmax.20120617.aggregation.1,http://albedo2.dkrz.de/thredds/dodsC/cmip5.output1.ICHEC.EC-EARTH.amip.day.atmos.day.r1i1p1.tasmin.20120617.aggregation.1")
         #self.variable = self.addLiteralInput(identifier="variable",title = "variable",type="String",default="temp2")
         self.processTitle = self.addLiteralOutput(identifier = "Title",title = "Title")
         self.outputRaster = self.addComplexOutput(identifier = "buffer",
                             title = "TimeseriesPlot",
                             formats = [
                                 {"mimeType":"image/png"}
                             ])
     
     def execute(self):
        self.status.set("Preparing....", 0)
        self.processTitle.setValue(self.tag.getValue())
        import time

        import pydap;
        import esgf
       

        cred = home+"/certs/creds.pem"
        logging.debug("Installing credentials: "+cred)

        try:
          esgf.install_esgf_client(cred,cred)
        except :
          print "Unable to install credentials"
          
        from pydap.client import open_dods
        from pydap.client import open_url
        import numpy as np
        # do this before importing pylab or pyplot
        import matplotlib
	#rc('text', usetex=True)
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import pylab
        import base64
        import sys, os
        import netcdftime
        pydap.lib.TIMEOUT = 120
        colors = ['b','g','r','c','m','y','k','w']



     


        myAxis=list();
        global myUnits,stopDate,startDate
        myUnits = "";
        start= int(self.startIndex.getValue());
        stop = int(self.stopIndex.getValue());

        defaultChunkSize = 32;

        def getAverage(resource,varname,start,stop,chunkSize,makeAxis,nrOfResources,currentResourceNr):
          datasetHeader = open_url(resource);
          #print datasetHeader[varname]
          maxLength = datasetHeader.time.shape[0];
          if(stop <=0 or stop > maxLength+1):
            stop = maxLength-1;
          if(start == -1):
            start = 0;
   
          if(chunkSize > stop-start):
            chunkSize = stop-start
            
          
          print "%d %d %d" % (start,stop,chunkSize)
          
         
          if makeAxis == True:
            global myUnits,startDate,stopDate
	    calendar = "standard"
	    try:
		calendar=datasetHeader.time.calendar
	    except:
		calendar = "standard"

            dateObjects = netcdftime.num2date(datasetHeader.time, units=datasetHeader.time.units,calendar=calendar)
            try:
              myUnits = str(datasetHeader[varname].units)
            except:
              myUnits = "-"

            startDate = dateObjects[start]
            stopDate = dateObjects[stop]
          
    
        
          
          
          result=list();
          subP = float(100/nrOfResources);
          pDone = float(subP*currentResourceNr);
          for i in range(start/chunkSize, (stop/chunkSize)+chunkSize):
            startTimeIndex=i*chunkSize;

            stopTimeIndex=i*chunkSize+chunkSize;
            if(stopTimeIndex > stop):
              stopTimeIndex = stop;

            if(startTimeIndex < stop and stopTimeIndex <= stop):
              
              dodsURL = resource+'.dods?'+varname+'['+str(startTimeIndex)+':1:'+str(stopTimeIndex)+']';
              self.status.set("Processing ("+str(currentResourceNr+1)+"/"+str(nrOfResources)+"), variable "+varname+" for "+dodsURL+" total = "+str(stop-start), round((float(i)/((stop-start)/chunkSize))*subP+pDone))
              #print dodsURL ;
              dataset = open_dods(dodsURL);
              #print "received!"

              for j in range(startTimeIndex,stopTimeIndex):
                data=dataset[varname][varname][j-startTimeIndex];
                #data=dataset.tas.tas;
                mean=np.mean(data[~np.isnan(data)]);
                result.append(mean);
                if makeAxis == True:
                  myAxis.append(dateObjects[j]);
              del dataset
          del datasetHeader
          return result

        fig = plt.figure()
        ax = fig.add_subplot(111)



        axisNotDone = True;
        resourceList = self.resource.getValue();
        resourceListItems = resourceList;
        varnameItems = [];
       
        nr = 0;
        plottedLines = []
        plottedResources = []
        
        for resource in resourceListItems:
          try:
            if(resource.index("$")!=-1):
              print "Defined"
              resource = resource.split("$")[0];
              varname= resource.split("$")[1];
          except :
            print "No variable provided, detecting from "+resource
            dataset = open_url(resource);
            variables = dataset.keys()
            varname = ""
            for v in dataset.keys():
              #print v + " "+ str(len(dataset[v].dimensions))
              if (len(dataset[v].dimensions) == 3):
                varname = v
                break;
              
            if(len(varname)==0):
              raise Exception("No variable with 3 dimensions found in "+resource)
            #len(dataset.temp2.dimensions)
            resourcename = os.path.basename(resource)
            print "Resourcename "+ resourcename + " with variable "+varname
            
            #exit()
          varnameItems.append(varname);
          nr = nr + 1
        
        nr = 0;
        for resource in resourceListItems:
          varname = varnameItems[nr]
          linetitle=""+resourcename+"/"+varname

          result = getAverage(resource,varname,start,stop,defaultChunkSize,axisNotDone,len(resourceListItems),nr);
          axisNotDone = False;
          line= ax.plot(myAxis,result,colors[nr%len(colors)],label=linetitle,linewidth=2)
          
          plottedLines.append(line)
          plottedResources.append(linetitle)
          nr = nr + 1
        
        
        print "Units = " + myUnits
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.2,box.width, box.height * 0.75])

        # Put a legend below current axis
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.125),fancybox=True, shadow=True, ncol=2)
        DPI=72;
        F = pylab.gcf();
        F.set_dpi(DPI);
        DPI=F.get_dpi();
        F.set_size_inches(int(float(1200)/float(DPI)),int(float(900)/float(DPI)))
        
          
          
        plt.title("Timeseries from \"%s\" till \"%s\"" % (startDate.strftime("%d %B %Y %I:%M"),stopDate.strftime("%d %B %Y %I:%M")));
        plt.ylabel(myUnits);
        plt.xlabel("Time index");
        plt.gcf().autofmt_xdate()

        plt.grid(True)
        fig.savefig('test.png',format='png',dpi=(DPI))
        self.outputRaster.setValue('test.png');
   
