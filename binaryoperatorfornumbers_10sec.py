

from pywps.Process.Process import WPSProcess                                
class Process(WPSProcess):
    def __init__(self):
        # init process
        WPSProcess.__init__(self,
                            identifier="binaryoperatorfornumbers_10sec", #the same as the file name
                            title="Perform operation on two numbers 10 seconds",
                            version = "1.0",
                            storeSupported = "true",
                            statusSupported = "true",
                          abstract="Performs operation on two numbers and returns the answer, updates every second its status for 10 seconds.",
                          grassLocation =False)
        
        self.inputa = self.addLiteralInput(identifier="inputa",
                                                title="Input 1",
                                                abstract="Input 1",
                                                default = 2.0,
                                                type = type(1.2))   
        self.inputb = self.addLiteralInput(identifier="inputb",
                                                title="Input 2",
                                                abstract="Input 2",
                                                default = 3.0,
                                                type = type(1.2))   
        self.operator = self.addLiteralInput(identifier = 'operator',
                                              title = 'operator',
                                              type=type("String"),
                                              default = 'add')        


        self.operator.values = ["add","substract","divide","multiply"]

        self.Answer=self.addLiteralOutput(identifier = "answer",
                                          title = "Binary operator result")

                                          
    def execute(self):
        import time
        self.status.set("Preparing....", 0)
        for i in xrange(1, 11):
            time.sleep(1)
            self.status.set("Thinking.....", (i-1)*10) 
        
        answer = 0
        if(self.operator.getValue() == "add"):
          answer = self.inputa.getValue()+self.inputb.getValue()
        
        if(self.operator.getValue() == "substract"):
          answer = self.inputa.getValue()-self.inputb.getValue()
        
        if(self.operator.getValue() == "multiply"):
          answer = self.inputa.getValue()*self.inputb.getValue()
          
        if(self.operator.getValue() == "divide"):
          answer = self.inputa.getValue()/self.inputb.getValue()


        #The final answer    
        self.Answer.setValue(answer)
      
