#!/usr/bin/env python
# -*- coding: latin-1 -*-
import logging
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

class CamDisplay(object):

    def __init__(self):
        self._systemUp = False
        self._gpsFix = False
        self._altitude = None
        self._temp = None
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
    def systemUp(self):
        return self._systemUp

    @systemUp.setter
    def systemUp(self, value):
        self._systemUp = value
        self._updateDisplay()

    @property
    def gpsFix(self):
        return self._gpsFix

    @gpsFix.setter
    def gpsFix(self, value):
        self._gpsFix = value
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

    @property
    def temp(self):
        return self._temp

    @temp.setter
    def temp(self, value):
        self._temp = value
        self._updateDisplay()

    @property
    def altitude(self):
        return self._altitude

    @altitude.setter
    def altitude(self, value):
        self._altitude = value
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
                Icon(image, 'icons_48-48/exclamation.png', xstart=76, ystart=0) # TODO ICON USB CROSS

            if self._camRecording:
                Icon(image, 'icons_48-48/rotating.png', xstart=138, ystart=0)
            else:
                Icon(image, 'icons_48-48/exclamation.png', xstart=138, ystart=0) # TODO ICON CAM CROSS

            height, width = self._display.size
            if self._temp is not None:
                tempText = Text(width, height, "%d°" % self._temp, chars=24)
                image.paste(tempText.image, (5, 120), mask=BLACK)
            if self._altitude is not None:
                tempText = Text(width, height, "%d m." % self._altitude, chars=24)
                image.paste(tempText.image, (30, 120), mask=BLACK)

            Icon(image, 'icons_48-48/thermometer.png', xstart=14, ystart=65)

            if self._camTOIMode:
                Icon(image, 'icons_48-48/happy.png', xstart=138, ystart=65)
            else:
                Icon(image, 'icons_48-48/exclamation.png', xstart=138, ystart=65) # TODO ICON HAPPY CROSS

            if self._gpsFix:
                Icon(image, 'icons_48-48/gps.png', xstart=138, ystart=130)
            else:
                Icon(image, 'icons_48-48/exclamation.png', xstart=138, ystart=130)  # TODO ICON GPS CROSS

            self._display.clearDisplayPart()
            self._display.showImageFull(self._display.imageToPixelArray(image))
        except Exception, e:
            print e
            logger.error('Error updating display: ', exc_info=True)