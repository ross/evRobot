#!/usr/bin/env python

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from evrobot import Robot, Roomba
from math import sqrt
from serial import Serial
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(threadName)-10s %(name)-9s %(message)s')
logger = logging.getLogger(__name__)


class DummySerial(object):

    def write(self, byte):
        pass


serial = Serial('/dev/ttyAMA0', baudrate=115200, timeout=0.5)
#serial = DummySerial()
roomba = Roomba(serial)
robot = Robot(roomba)

# queue up some commands
robot.move_by(1, 0.5, 2 / 5.0)
robot.move_by(-sqrt(1.25), 0, 0.5)
robot.rotate_by(163)
robot.shutdown()
