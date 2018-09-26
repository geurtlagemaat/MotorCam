#!/usr/bin/env python
# -*- coding: latin-1 -*-
import ConfigParser
import logging

import time, sys
from includes.text import Text

try:
    from cloghandler import ConcurrentRotatingFileHandler as RFHandler
    ConcurrentLogHandler = True
except ImportError:
    from warnings import warn
    warn("ConcurrentLogHandler package not installed. Using builtin log handler")
    from logging.handlers import RotatingFileHandler as RFHandler
    ConcurrentLogHandler = False

from PIL import Image

import spidev as SPI
from includes.epd import Epd
from includes.progressbar import ProgressBar
from includes.icon import Icon

DISPLAY_TYPE = "EPD_1X54"
WHITE = 1
BLACK = 0

logger = logging.getLogger(__name__)
eDisplay = None
nodeProps = None

def setup(propertiesfile):
    if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
        logging.basicConfig(level=logging.DEBUG)
    nodeProps = ConfigParser.ConfigParser()
    nodeProps.read(propertiesfile)

    if nodeProps.has_option('log', 'logLevel'):
        logMode = nodeProps.get('log', 'logLevel')
        if logMode.upper() == 'DEBUG':
            logLevel = logging.DEBUG
        elif logMode.upper() == 'INFO':
            logLevel = logging.INFO
        elif logMode.upper() == 'WARNING':
            logLevel = logging.WARNING
        elif logMode.upper() == 'ERROR':
            logLevel = logging.ERROR
        else:
            logLevel = logging.INFO
    else:
        logLevel = logging.INFO
    logger.setLevel(logLevel)

    if nodeProps.has_option('log', 'logFile'):
        logFile = nodeProps.get('log', 'logFile')
    else:
        logFile = 'logs/MotorCam.log'

    if nodeProps.has_option('log', 'logFiles'):
        maxLogFiles = nodeProps.getint('log', 'logFiles')
    else:
        maxLogFiles = 5
    if nodeProps.has_option('log', 'logSize'):
        maxLogfileSize = nodeProps.getint('log', 'logSize') * 1024
    else:
        maxLogfileSize = 512 * 1024

    handler = RFHandler(logFile, maxBytes=maxLogfileSize, backupCount=maxLogFiles)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(process)-5d [%(module)s.%(funcName)s:%(lineno)d] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info("Bliknet MotorCam config")

    try:
        spi = SPI.SpiDev(0, 0)
        eDisplay = Epd(spi, DISPLAY_TYPE)

        # Init and clear part screen
        eDisplay.clearDisplayPart()
        eDisplay.showString(40, 80, "BLIKNET MOTORCAM", "Font16")

        progress = ProgressBar(eDisplay, 10)
        for i in range(0, 10):
            progress.showProgress(i)
        eDisplay.clearDisplayPart()

        image = Image.new('1', eDisplay.size, WHITE)

        Icon(image, 'icons_48-48/check.png', xstart=14, ystart=0)
        Icon(image, 'icons_48-48/usb.png', xstart=76, ystart=0)
        Icon(image, 'icons_48-48/rotating.png', xstart=138, ystart=0)

        height, width = eDisplay.size
        tempText = Text(width, height, "28.5°", chars=24)
        image.paste(tempText.image, (5, 120), mask=BLACK)
        tempText = Text(width, height, "3208m", chars=24)
        image.paste(tempText.image, (30, 120), mask=BLACK)
        Icon(image, 'icons_48-48/thermometer.png', xstart=14, ystart=65)

        Icon(image, 'icons_48-48/happy.png', xstart=138, ystart=65)
        Icon(image, 'icons_48-48/gps.png', xstart=138, ystart=130)

        eDisplay.showImageFull(eDisplay.imageToPixelArray(image))
    except Exception, e:
        print e
        logger.error('Error Display init: ', exc_info=True)

def main():
    setup('settings/motorcam.properties')

if __name__ == '__main__':
    main()