#!/usr/bin/env python

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from evrobot import Robot, Roomba
from random import random, randrange
from serial import Serial
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(threadName)-10s %(name)-9s '
                    '%(message)s')
logger = logging.getLogger(__name__)


class BumpingRobot(Robot):

    def __init__(self):
        serial = Serial('/dev/ttyAMA0', baudrate=115200, timeout=0.5)
        self.roomba = Roomba(serial)
        super(BumpingRobot, self).__init__(self.roomba)

        self.bumps_remaining = 4

        # listen for bumper events
        self.subscribe(self.bumping, 'robot.obstacle.bumping')
        # listen for move finished
        self.subscribe(self.move_finished, 'robot.move.finished')

    def go(self):
        # start our inital move
        self.roomba.move_by(100, 0, 0.8)

    def bumping(self, whichi):
        if self.bumps_remaining:
            self.roomba.debump()
            self.bumps_remaining -= 1
        else:
            self.shutdown()

    def move_finished(type, *args):
        if type == 'debump':
            # rotate a random amount between -180 and 180
            if random() > 0.5:
                self.roomba.rotate_by(randrange(45, 180, 1), 0.5)
            else:
                self.roomba.rotate_by(randrange(-180, -45, 1), 0.5)
            # start moving again
            self.roomba.move_by(100, 0, 0.8)


robot = BumpingRobot()
robot.go()
robot.wait()
