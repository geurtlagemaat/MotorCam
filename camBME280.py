#!/usr/bin/env python
# -*- coding: latin-1 -*-
import logging
import threading
from Adafruit_BME280 import *

logger = logging.getLogger(__name__)

class BME280Controller(threading.Thread):
    def __init__(self, nodeProps):
        threading.Thread.__init__(self)
        self._timeToSleep = 60
        if nodeProps.has_option('sensors', 'bm280-readingInterval'):
            self._timeToSleep = nodeProps.getint('sensors', 'bm280-readingInterval')
        self._degrees = None
        self._pascals = None
        self._hectopascals = None
        self._humidity = None
        self._bme280Sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
        self._updateTemp()
        self._running = False

    def run(self):
        self._running = True
        while self._running:
            self._updateTemp()
            time.sleep(self._timeToSleep)
        self._running = False

    def stopController(self):
        self._running = False

    @property
    def degrees(self):
        return self._degrees

    @property
    def pascals(self):
        return self._pascals

    @property
    def hectopascals(self):
        return self._hectopascals

    @property
    def humidity(self):
        return self._humidity

    def _updateTemp(self):
        try:
            self._degrees = self._bme280Sensor.read_temperature()
            self._pascals = self._bme280Sensor.read_pressure()
            self._hectopascals = self._pascals / 100
            self._humidity = self._bme280Sensor.read_humidity()
            logger.debug("BM280 readings. Degrees: %s, pascals: %s, hectopascals: %s and humidity:%s." % (
                self._degrees, self._pascals, self._hectopascals, self._humidity))
        except:
            logger.error('Error reading BME280: ', exc_info=True)