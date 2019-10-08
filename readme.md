# queue_thread
The module queue_thread.py can be used to create multi-threaded applications in python with QT5.

## Overview
A threaded QT5 application allows multiple processes to run concurrently without blocking the GUI. Here, an example is given of a GUI with threading in python-QT5. A fake image stream is generated from images inside the skimage.data module and optionally displayed to the screen. A good explanation of threading, and the preferred method of  threading in QT5 -- with working code -- can be found here:

https://www.learnpyqt.com/courses/concurrent-execution/multithreading-pyqt-applications-qthreadpool/


## Examples: threaded_img_gui.py
'threaded_img_gui.py' demonstrates threading with python-QT5. It is slightly more complicated that the examples in the link above. It is not optimized, but demonstrated the principle.

The commands are:
1.  Press 'start' to start reading images from the 'fakestream' to a queue.
2. Press 'view raw' to see the images in the queue.
3. Press 'stop' to stop adding to the stream.

You will notice that the buttons in the GUI are still available while a several tasks are happening in the background. Open your system settings to see multi-threading at work.

## Examples: color example
To use this module, import QueueThreads and create a new instance. New processes can be launched with the add_to_queue method. Here is an example:

``` python
import random
import time
from PyQt5.QtCore import *
from queue_threads import QueueThreads

def change_color_update(info_callback, **kwargs):
  color = random.choice(['r','g','b','y','c','k'])
  print('The new color is:', color)
  info_callback.emit(color)

@pyqtSlot(str)
def print_result(color, **kwargs):
  print('The color was updated to:', color)

Q = QueueThreads()

for i in range(100):
    Q.add_to_queue(function=change_color_update, signal='info' , slot=print_result)

```

Note:
1. The 'signal' must be one in the WorkerSignals class inside the queue_threads module.
2. To have access to the callback in the executed function, it is necessary to place a positional argument with the same name as in the Worker class. i.e. 'info_callback' is connected to the 'info' signal in the Worker class.
3. The magic here is that the run function of the QRunnable class automatically passes callbacks added as kwargs in the Worker class.   

Alternatively, add_to_queue can be used with no signal or slot:

``` python
def change_color(**kwargs):
  color = random.choice(['r','g','b','y','c','k'])
  print('The color was updated to:', color)

for i in range(100):
    Q.add_to_queue(function=change_color, signal='info' , slot=print_result)

```

Here is an example of passing a keyword argument to the function. A new function, selective_change_color is defined. This will allow an input color (string) to be rejected:

``` python

def selective_change_color(info_callback, not_color, **kwargs):
    color = not_color
    while color == not_color:
        color = random.choice(['r','g','b','y','c','k'])
        if color == 'r':
            print('Color is r, choose again')
        else:
            print('Color is:', color)

    info_callback.emit(color)

for i in range(100):
    Q.add_to_queue(function=selective_change_color, not_color='r', signal='info' , slot=print_result)

```

These examples are not CPU intensive and probably do not need to be threaded. But the concept of how to use threading to pass objects safely between threads was demonstrated.

## Why three classes in QueueThreads?
An informal explanation of the interaction of the three classes is given below.

**QueueThreads** subclasses Qthreadpool. It is the 'threadpool' or manager (informally) that will launch the passed functions in new threads. The add_to_queue function allows the user to pass signals (as a string) and connect them to any slot (with a matching signature.)

**Worker** subclasses Qrunnable. The run method will be called automatically when the worker is started by the Qthreadpool. The callbacks are passed as kwargs inside the Worker class. These are then accessible inside the function.

**WorkerSignals** subclasses Qobject. For the signals to be acccessible, they must be 'bound' objects, which is achieved by instatiating them inside a QObject class.
