#!/usr/bin/env python
# -*- coding: latin-1 -*-
import logging
import threading

import time
from PIL import Image

import spidev as SPI

from includes.epd import Epd
from includes.progressbar import ProgressBar
from includes.icon import Icon
from includes.text import Text


DISPLAY_TYPE = "EPD_1X54"
WHITE = 1
BLACK = 0

logger = logging.getLogger(__name__)

class DisplayController(threading.Thread):

    def __init__(self, nodeProps):
        threading.Thread.__init__(self)
        self._running = False
        self._updateInterval = 5
        if nodeProps.has_option('display', 'updateInterval'):
            self._updateInterval = nodeProps.getint('display', 'updateInterval')
        self._gpsController = None
        self._bme280Controller = None
        self._systemUp = False
        self._camTOIMode = False
        self._camRecording = False
        self._usbMounted = False

        try:
            spi = SPI.SpiDev(0, 0)
            self._display = Epd(spi, DISPLAY_TYPE)

            self._display.clearDisplayPart()
            self._display.showString(40, 80, "BLIKNET MOTORCAM", "Font16")

        except Exception, e:
            logger.error('Error Display init: ', exc_info=True)
            raise Exception('Display init error.') # stop startup sequence

    def run(self):
        self._running = True
        while self._running:
            self._updateDisplay()
            time.sleep(self._updateInterval)
        self.running = False

    def stopController(self):
        self._running = False

    def startProgressBar(self, steps):
        self._progressSteps = steps
        self._currProgressStep = 0
        self._progress = ProgressBar(self._display, self._progressSteps)
        self._progress.showProgress(self._currProgressStep)

    def updateProgressBar(self):
        if self._currProgressStep+1 <= self._progressSteps:
            self._currProgressStep += 1
            self._progress.showProgress(self._currProgressStep)
        else:
            logger.error('Display progress bar max. steps (%d) exceeded.' % self._progressSteps)

    @property
    def gpsController(self):
        return self._gpsController

    @gpsController.setter
    def gpsController(self, value):
        self._gpsController = value

    @property
    def bme280Controller(self):
        return self._bme280Controller

    @bme280Controller.setter
    def bme280Controller(self, value):
        self._bme280Controller = value

    @property
    def systemUp(self):
        return self._systemUp

    @systemUp.setter
    def systemUp(self, value):
        self._systemUp = value
        self._updateDisplay()

    @property
    def usbMounted(self):
        return self._usbMounted

    @usbMounted.setter
    def usbMounted(self, value):
        self._usbMounted = value
        self._updateDisplay()

    @property
    def camRecording(self):
        return self._camRecording

    @camRecording.setter
    def camRecording(self, value):
        self._camRecording = value
        self._updateDisplay()

    @property
    def camTOIMode(self):
        return self._camTOIMode

    @camTOIMode.setter
    def camTOIMode(self, value):
        self._camTOIMode = value
        self._updateDisplay()

    def _updateDisplay(self):
        try:
            image = Image.new('1', self._display.size, WHITE)

            if self._systemUp:
                Icon(image, 'icons_48-48/check.png', xstart=14, ystart=0)
            else:
                Icon(image, 'icons_48-48/exclamation.png', xstart=14, ystart=0)

            if self._usbMounted:
                Icon(image, 'icons_48-48/usb.png', xstart=76, ystart=0)
            else:
                Icon(image, 'icons_48-48/usb-cross.png', xstart=76, ystart=0)

            if self._camRecording:
                Icon(image, 'icons_48-48/videocamera.png', xstart=138, ystart=0)
            else:
                Icon(image, 'icons_48-48/videocamera-cross.png', xstart=138, ystart=0)

            height, width = self._display.size
            if self._bme280Controller is not None and self._bme280Controller.degrees is not None:
                tempText = Text(width, height, "%d°" % self._bme280Controller.degrees, chars=24)
                image.paste(tempText.image, (5, 120), mask=BLACK)
            if self._gpsController is not None and  self._gpsController.gpsReady and self._gpsController.gpsFix.altitude is not None:
                tempText = Text(width, height, "%d m." % self._gpsController.gpsFix.altitude, chars=24)
                image.paste(tempText.image, (30, 120), mask=BLACK)

            if self._bme280Controller is not None and self._bme280Controller.degrees is not None:
                Icon(image, 'icons_48-48/thermometer.png', xstart=14, ystart=65)
            else:
                Icon(image, 'icons_48-48/thermometer-cross.png', xstart=14, ystart=65)

            if self._camTOIMode:
                Icon(image, 'icons_48-48/happy.png', xstart=138, ystart=65)
            else:
                Icon(image, 'icons_48-48/happy-cross.png', xstart=138, ystart=65)

            if self._gpsController is not None and  self._gpsController.gpsReady:
                Icon(image, 'icons_48-48/gps.png', xstart=138, ystart=130)
            else:
                Icon(image, 'icons_48-48/gps-cross.png', xstart=138, ystart=130)

            self._display.clearDisplayPart()
            self._display.showImageFull(self._display.imageToPixelArray(image))
        except Exception, e:
            print e
            logger.error('Error updating display: ', exc_info=True)