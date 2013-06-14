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

serial = Serial('/dev/ttyAMA0', baudrate=115200, timeout=0.5)
roomba = Roomba(serial)
robot = Robot(roomba)


def bumper(which):
    if bumper.remaining:
        roomba.debump()
        bumper.remaining -= 1
    else:
        robot.shutdown()

bumper.remaining = 4


# listen for bumper events
robot.subscribe(bumper, 'robot.obstacle.bumping')


def move_finished(type, *args):
    if type == 'debump':
        # rotate a random amount between -180 and 180
        if random() > 0.5:
            roomba.rotate_by(randrange(45, 180, 1), 0.5)
        else:
            roomba.rotate_by(randrange(-180, -45, 1), 0.5)
        # start moving again
        roomba.move_by(100, 0, 0.8)

# listen for move finished
robot.subscribe(move_finished, 'robot.move.finished')

# start our inital move
roomba.move_by(100, 0, 0.8)

robot.run()
