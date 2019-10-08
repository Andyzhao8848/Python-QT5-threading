"""

threading module.
 
based on QT5 thread class, can be used with or without a GUI

Make a ThreadQueue object, then add functions to be executed

Three classes work together: 
    QueueThreads, Worker, WorkerSignals

Each is subclassing QT objects.

add_to_queue function extends QueueThreads and permits connectin to custom 
slots by passing a string to getattr  
        
"""

import traceback
import sys

import random
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class QueueThreads(QThreadPool): 
    """
    general threadpool for the main GUI and other components
    """
    def __init__(self):
        super(QueueThreads, self).__init__()   
        print("Multithreading with maximum %d threads" % self.maxThreadCount())

    def add_to_queue(self, 
                     function=None,
                     signal=None,
                     slot=None, 
                     **kwargs):
        """ function: to be executed in a new thread
            signal: accesible in the function 
            slot: passed as string, connected in thread_queue with getattr 
            kwargs: will be passed to the function
        """
       
        worker = Worker(function=function, signal=signal, slot=slot, **kwargs)
        
        # signals connected inside this class
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)   
        
        # signals may also be connected to function passed in slot
        # not every function added to queue requires signal/slot
        # signal must be passed as string to getattr
        if slot != None: 
            sig = getattr(worker.signals, signal)
            sig.connect(slot)
        
        self.start(worker)

    def print_output(self, s):
        print(s)
    
    def thread_complete(self):
        print("THREAD COMPLETE!")
        
    def progress_fn(self, n):
        print("%d%% done" % n)

class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """
    def __init__(self, 
                 function=None, 
                 signal=None,
                 slot=None,
                 **kwargs):
        
        super(Worker, self).__init__()
        
        # Store constructor arguments (re-used for processing)
        print('signal passed:', signal)
        
        self.function = function
        self.kwargs = kwargs
        
        self.signals = WorkerSignals()        
        self.kwargs['progress_callback'] = self.signals.progress
        self.kwargs['result_callback'] = self.signals.result
        self.kwargs['obj_callback'] = self.signals.obj
        self.kwargs['info_callback'] = self.signals.info
        self.kwargs['imgtime_callback'] = self.signals.imgtime
          
    @pyqtSlot()
    def run(self):
        """ Initialise runner function with passed args, kwargs.
            The current use doesnt implement this part very well, aside
            from the result = self.function(**self.kwargs) part
        """
        try:
            result = self.function(**self.kwargs)
            
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
            
class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    Use class (w/o __init__) to ensure the signals are bound objects
    """
    finished = pyqtSignal()
    result = pyqtSignal(object)
    progress = pyqtSignal(int)   
    error = pyqtSignal(tuple)
    
    imgtime = pyqtSignal((object, str))
    obj = pyqtSignal(object)
    info = pyqtSignal(str)




if __name__ == '__main__':
    print('A simple example')
    import time
    
    
    def countdown(imgtime_callback, cdownv, **kwargs):
        print('counting from %s' % int(cdownv))
        for i in range(cdownv):
            time.sleep(3)
            print(i)
        imgtime_callback.emit(1234, 'done')

    @pyqtSlot(object, str)
    def countdown_finished(number, status):
        # the function to be carried out when the function completes
        print('Job %d is %s' % (number, status))
    
    Q = QueueThreads()
    
    # pass the signal by the name in the WorkerSignals class
    # add signals as necessary
    # this ensure they are 'bound'
    for i in range(4):
        Q.add_to_queue(function=countdown, 
                       cdownv=random.randint(1,10),
                       signal='imgtime', 
                       slot=countdown_finished)   




