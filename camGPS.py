#!/usr/bin/env python
# -*- coding: latin-1 -*-
import logging
from gps import *
import threading
logger = logging.getLogger(__name__)
import pytz
import datetime

local_tz = pytz.timezone('Europe/Amsterdam')

gpsd = None # gps deamon
gpsp = None # poller instance

class GPSPoller(threading.Thread):
    def __init__(self, updateGPSDataHandler):
        threading.Thread.__init__(self)
        global gpsd  # bring it in scope
        self._updateGPSDataHandler = updateGPSDataHandler
        gpsd = gps(mode=WATCH_ENABLE)  # starting the stream of info
        self.current_value = None
        self.running = True

    def run(self):
        global gpsd
        while gpsp.running:
            gpsd.next()  # grab EACH set of gpsd info to clear the buffer
            self._updateGPSDataHandler(gpsd)
            logger.debug(gpsd.fix)

class GPSData(object):
    def __init__(self):
        self._gpsFix = None
        self._time = None
        self._utcTime = None
        self.startGPS()

    def startGPS(self):
        global gpsp
        gpsp = GPSPoller(self._updateGPSDataHandler)  # create the thread
        try:
            gpsp.start()
        except Exception, e:
            print e
            gpsp.running = False
            gpsp.join()

    def stopGPS(self):
        gpsp.running = False
        gpsp.join()

    @property
    def gpsFix(self):
        return self._gpsFix

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    @property
    def altitude(self):
        return self._altitude

    @property
    def speed(self):
        return self._speed

    @property
    def climb(self):
        return self._climb

    @property
    def track(self):
        return self._track

    @property
    def time(self):
        return self._time

    @property
    def utcTime(self):
        return self._utcTime

    def _updateGPSDataHandler(self, myGpsd):
        self._gpsFix = (myGpsd.fix.latitude is not NaN and \
                        myGpsd.fix.latitude != 0.0 and\
                        myGpsd.fix.longitude is not NaN and\
                        myGpsd.fix.longitude != 0.0)
        if self._gpsFix:
            self._latitude = myGpsd.fix.latitude
            self._longitude = myGpsd.fix.longitude
            self._altitude = myGpsd.fix.altitude
            self._speed = myGpsd.fix.speed * MPS_TO_KPH
            self._climb = myGpsd.fix.climb
            self._track = myGpsd.fix.track
            self._time = myGpsd.fix.time
            self._utcTime = myGpsd.utc
            self._localDateTime = "TODO!" # TODO!
