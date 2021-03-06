#!/usr/bin/env python
# -*- coding: latin-1 -*-
import ConfigParser
import logging
from camDisplay import DisplayController
from camGPS import GPSController
from camBME280 import BME280Controller
import time, sys
import picamera

try:
    from cloghandler import ConcurrentRotatingFileHandler as RFHandler
    ConcurrentLogHandler = True
except ImportError:
    from warnings import warn
    warn("ConcurrentLogHandler package not installed. Using builtin log handler")
    from logging.handlers import RotatingFileHandler as RFHandler
    ConcurrentLogHandler = False

logger = logging.getLogger(__name__)
eDisplay = None
nodeProps = None
gpsData =  None

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

    eDisplay = DisplayController(nodeProps)
    eDisplay.startProgressBar(2)
    eDisplay.updateProgressBar()
    eDisplay.updateProgressBar()
    logger.info("Bliknet MotorCam config")

    gpsContr = GPSController(nodeProps)
    bme280Contr = BME280Controller(nodeProps)

    camera = picamera.PiCamera()
    # TODO read settings for camera
    # TODO create Button thread
    # camera.resolution = (640, 480)
    # camera.start_recording('/mnt/videodrive/my_video.h264')
    # camera.wait_recording(10)
    # camera.stop_recording()
    eDisplay.bme280Controller = bme280Contr
    eDisplay.gpsController = gpsContr
    gpsContr.start()
    bme280Contr.start()
    eDisplay.systemUp = True
    eDisplay.start()
    while True:
        pass


def main():
    setup('settings/motorcam.properties')

if __name__ == '__main__':
    main()