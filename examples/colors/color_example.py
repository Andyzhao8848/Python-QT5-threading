#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

pass message example
"""

import random
import time
from PyQt5.QtCore import *
from queue_threads import QueueThreads


def change_color(info_callback, **kwargs):
  color = random.choice(['r','g','b','y','c','k'])
  print('The new color is:', color)
  info_callback.emit(color)
  
def selective_change_color(info_callback, not_color, **kwargs):
    color = not_color
    while color == not_color:
        color = random.choice(['r','g','b','y','c','k'])
        if color == 'r': 
            print('Color is r, choose again')
        else: 
            print('Color is:', color)

    info_callback.emit(color)

@pyqtSlot(str)
def print_result(color, **kwargs):
  print('The color was updated to:', color)
  
Q = QueueThreads()

for i in range(100):
    Q.add_to_queue(function=selective_change_color, not_color='r', signal='info' , slot=print_result)
  


