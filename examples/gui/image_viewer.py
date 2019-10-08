#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

window for display of images and data

"""
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time

class ImageViewer(QMainWindow):
    
    def __init__(self, parent=None, params=None, resize=(500,500), img=None, xy=(100,600)):
        super(ImageViewer, self).__init__(parent)
        
        # setup two img and plot labels. choose which to disp. on main panel.
        self.xy = xy
        self.params = params # params for the display
        self.parent = parent
        self.add_img_label(img=img, size=resize)
        self.show()
        
    def add_img_label(self, img=None, size=(1500, 1500), ): 
        """ labels for image stream """ 
        img = rgb2pxmap(img)
        img = QPixmap(img).scaled(size[0], size[1], Qt.KeepAspectRatio, Qt.FastTransformation)
        label = QLabel(self)
        label.setPixmap(img)
        w, h = img.width(), img.height()
        print('height:', h, 'width:', w)
        label.resize(w, h)
        self.label = label
        self.setGeometry(self.xy[0], self.xy[1], w, h)
        
    def update_img_label(self, img=None, size=(500, 500), **kwargs): 
        """ callback to update the display window """    
        #size = kwargs['img_resize']
        img = rgb2pxmap(img)
        img = QPixmap(img).scaled(size[0], size[1], Qt.KeepAspectRatio, Qt.FastTransformation)
        self.label.setPixmap(img)
        time.sleep(0.01)
        self.show()
         
def rgb2pxmap(img=None): 
    height, width, channel = img.shape
    bytesPerLine = 3 * width        
    return QImage(img, width, height, bytesPerLine, QImage.Format_RGB888)
   
if __name__ == '__main__':
    print('testing')
    import skimage.io as sio
    D = WindowViewer(params={'img_resize': (1000, 1000),
                              'labels': ['img_raw', 'img_pro',],
                              'xpos': 1000,
                              'ypos': 1500,
                              })
    img_raw=sio.imread('../test.jpg')
    img_pro=sio.imread('../test.jpg')
    D.setup_window(img_raw=img_raw, img_pro=img_pro)
  