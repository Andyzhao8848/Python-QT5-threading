#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

threaded_img_gui.py

m.r maciver
rmcmaciver@hotmail.com

7 Oct 2019

"""
import sys
import time
import random
from queue import Queue
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import skimage.io as sio
import skimage.data 

from queue_threads import QueueThreads
from image_viewer import ImageViewer

class ThreadedImgGui(QMainWindow):
    
    def __init__(self, params=None, parent=None, *args, **kwargs):
        super(ThreadedImgGui, self).__init__(*args, **kwargs)
    
        # setup the threadpool
        self.params = params
        self.threadpool = QueueThreads() 
        
        # queues to collect images from stream 
        # the image queue will be polled in a thread and displayed if 
        # an image is available
        if 'qsize' in self.params:
            qsize = self.params['qsize']
        else: 
            qsize = 50
            
        self.raw_queue = ImgQueue(obj_type='raw img', maxsize=qsize)

        self.parent = parent
        self.setWindowTitle('Threaded GUI Example')
        app.aboutToQuit.connect(self.closeEvent)

        self.layout = QGridLayout()
        self.layout_buttons()
        
        w = QWidget()
        w.setLayout(self.layout)
        self.setCentralWidget(w)
        
        self.setGeometry(100, 100, 50,50)
        self.show()

    
    def layout_buttons(self):
        top_layout_2 = QHBoxLayout()
        
        ctrl_groupbox = QGroupBox('Image Stream Controls')
        ctrl_groupbox.setAlignment(Qt.AlignCenter)

        start = QPushButton('start', clicked=self.click_start)        
        view_raw = QPushButton('view raw', clicked=self.click_view_raw, )
        stop = QPushButton('stop', clicked=self.click_stop, )
        
        top_layout_2.addWidget(start)
        top_layout_2.addWidget(view_raw)
        top_layout_2.addWidget(stop)
        ctrl_groupbox.setLayout(top_layout_2)
        self.layout.addWidget(ctrl_groupbox, 1, 0)
        
        self.buttons = {'start': start,
                        'view_raw': view_raw,
                        'stop': stop,
                        }
        
    def click_start(self):
        """ start fake image stream in a thread """
        
        # add_to_queue 
        # function: to be executed in a new thread
        # tsignal: accesible in the function 
        # slot: passed as string, connected in thread_queue with getattr 
        # kwargs: will be passed to the function
        
        # this is a signal defined in the thread_queue
        # with a custom signature (object, str)
        if 'delay' in self.params: 
            delay = self.params['delay']
        else: 
            delay = 0.5
        self.threadpool.add_to_queue(function=fakestream,
                                     signal='imgtime',
                                     slot=self.add_to_raw_queue,
                                     delay=delay,
                                     stop=self.buttons['stop'])
        
        self.buttons['start'].setEnabled(False)
        self.buttons['stop'].setEnabled(True)
        
    @pyqtSlot(object, str)
    def add_to_raw_queue(self, image, timestamp): 
        # this is the slot for the add_to_queue call with function=fakestream
        # the decorator @pyqtSlot(object, str) matches the signal 
        # of the 
        self.raw_queue.check_full()
        self.threadpool.add_to_queue(function=self.raw_queue.add2queue,
                                     img=image, 
                                     time_stamp=timestamp)
        
    def click_view_raw(self):
        """ view the image stream """
        img = getattr(skimage.data, 'rocket')()
        self.viewer_raw = ImageViewer(img=img, resize=(600, 600), xy=(100,600))
        self.vraw = True
        
        self.threadpool.add_to_queue(function=self.raw_queue_poll,
                                     delay=0.1,
                                     stop=self.buttons['stop'])
        
    def raw_queue_poll(self, delay, stop, **kwargs):
        # run in a thread from click_view_raw
        # note there was no signal or slot connected
        # but it is necessary to include the **kwargs
        # poll the raw image queue
        while stop.isEnabled() == True:
            time.sleep(delay)
            self.update_view_raw()
            
    def update_view_raw(self):
        # not very useful in this example, because FPS is low, but
        while not self.raw_queue.empty():
            img, timestamp = self.raw_queue.get()
            self.viewer_raw.update_img_label(img)
        
    def click_stop(self):
        print('\nStop the stream') 
        self.buttons['stop'].setEnabled(False)
        self.buttons['start'].setEnabled(True)

        
    def closeEvent(self, event=None):
        #Your desired functionality here
        print('\nClose button pressed')
        self.destroy()
        if self.parent is None:
            sys.exit(0)

class ImgQueue(Queue):
    def  __init__(self, maxsize=20, obj_type='object'):
        super(ImgQueue, self).__init__(maxsize=maxsize)    
        self.framecount = 0
        self.obj_type=obj_type
        
    def add2queue(self, img, time_stamp, **kwargs):
        if self.framecount == 0: 
            self.t0 = time.time()
            
        self.put((img, time_stamp))
        self.framecount += 1
        self.ti = time.time() - self.t0
        
        msg = '%s in queue [N]: %d\n' % (self.obj_type, self.qsize())
        msg += 'current frame rate [FPS]:' % self.framecount/self.ti
        print(msg)
        self.msg = msg
        
    def check_full(self): 
        if self.full(): 
            print('Queue is full, clearing queue and lowering process FPS')
            with self.mutex:
                self.queue.clear()
    
"""
setup a fake image stream using data from skimage.data

"""
test_imgs  = ['astronaut',
             'chelsea',
             'coffee',
             'hubble_deep_field',
             'immunohistochemistry',
             'retina',
             'rocket',
             ]

def fakestream(imgtime_callback, stop, delay=0.1, **kwargs):
    """ stream of images from skimage.data """
    # Added to thread pool with add_to_queue as a function 
    # Keyword arguments passed with the function are available in the function
    # **kwargs must be added as it holds the other callbacks defined in the Worker
    while stop.isEnabled() == True:
        time.sleep(delay)
        img = random.choice(test_imgs)
        print('image name:', img)
        img = getattr(skimage.data,img)()
        timestamp = make_time_stamp()
        imgtime_callback.emit(img, timestamp)
       
def make_time_stamp():
   now = time.time()
   localtime = time.localtime(now)
   milliseconds = '%05d' % int((now - int(now)) * 1000)
   return time.strftime('%Y-%m-%d_%H-%M-%S', localtime) + milliseconds    
    
def main(params=None): 
    global app
    app = QApplication([])
    window = ThreadedImgGui(params=params)
    app.exec_()

if __name__ == '__main__':
    params = {'delay': 0.005,
              'qsize': 20}
    main(params=params)

    
    
        
    