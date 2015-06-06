"""Class for cameras connected to framegrabbers run by Taco Device Servers
"""
from HardwareRepository import BaseHardwareObjects
import logging
import os
import gevent
import time
import numpy
from PIL import Image
import cStringIO
import gevent.event
import cv2
import time
import base64
import numpy
import zlib
import subprocess

WEBCAM_ENCODED_JPEG=None
WEBCAM_IMAGE=gevent.event.AsyncResult()

class Webcam(BaseHardwareObjects.Device):

    def __init__(self,name):
        BaseHardwareObjects.Device.__init__(self,name)
        self.liveState = False

    def _init(self):
        self.setIsReady(True)

    def init(self):
        self.imagegen = None

    def imageGenerator(self, delay):
        global WEBCAM_ENCODED_JPEG
        webcam = cv2.VideoCapture(0)
        while True:
             _, frame = webcam.read()
             h,w,depth = frame.shape
             im = Image.fromarray(frame)
             # too bad it has to be converted from BGR to RGB :(
             b,g,r = im.split()
             rgb_im = Image.merge("RGB", (r,g,b))
             jpeg_file = cStringIO.StringIO()
             rgb_im.save(jpeg_file, format="JPEG")
             self.emit("imageReceived", jpeg_file.getvalue(), w, h)
             time.sleep(delay)

    def contrastExists(self):
        return False
    def brightnessExists(self):
        return False
    def gainExists(self):
        return False

    def setLive(self, live):
        print "Setting camera live ", live
        if live and self.liveState == live:
            return
        
        if live:
            self.imagegen = gevent.spawn(self.imageGenerator,  (self.getProperty("interval") or 500)/1000.0 )
            self.liveState = live
        else:
            self.imagegen.kill()
            self.liveState = live
        return True

    def imageType(self):
        return None

    def takeSnapshot(self, *args):
      jpeg_data=self.getOneImage()
      f = open(*(args + ("w",)))
      f.write("".join(map(chr, jpeg_data)))
      f.close()       
