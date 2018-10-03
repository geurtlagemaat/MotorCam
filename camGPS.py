#!/usr/bin/env python
# -*- coding: latin-1 -*-
import logging
from gps import *
import threading
logger = logging.getLogger(__name__)
import pytz
import datetime
from datetime import datetime

class GPSController(threading.Thread):
    def __init__(self, nodeProps):
        threading.Thread.__init__(self)
        self._timezone = None
        if nodeProps.has_option('localize', 'timezone'):
            self._timezone = nodeProps.get('localize', 'timezone')
        # self._gpsd = gps(mode=WATCH_ENABLE)
        self._gpsd = gps("localhost", "2947")
        self._gpsd.stream(WATCH_ENABLE | WATCH_NEWSTYLE)
        self._running = False

    def run(self):
        self._running = True
        while self._running:
            self._gpsd.next()  # grab EACH set of gpsd info to clear the buffer

    def stopController(self):
        self._running = False

    @property
    def gpsFix(self):
        return self._gpsd.fix

    @property
    def satellites(self):
        return self._gpsd.satellites

    @property
    def utc(self):
        return self._gpsd.utc

    @property
    def localDateTime(self):
        try:
            if self._gpsd.fix.mode != 1:
                UTCTime = time.strptime(elf._gpsd.utc, "%Y-%m-%dT%H:%M:%S.%fz")
                tmp = datetime.fromtimestamp(time.mktime(UTCTime))
                return self._datetime_from_utc_to_local(tmp)
        except:
            return None

    @property
    def gpsReady(self):
        return self._gpsd.fix.mode != 1

    def _datetime_from_utc_to_local(self, utc_datetime):
        if self._timezone is not None:
            try:
                return pytz.utc.localize(utc_datetime, is_dst=None).astimezone(self._timezone)
            except Exception, e:
                logger.error('Error converting UTC to local date time: ', exc_info=True)
                return None
        else:
            logger.error('No timezone set, returning UTC date/time. ')
            return utc_datetime
