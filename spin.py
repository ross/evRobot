#!/usr/bin/env python

from evrobot import Robot, Roomba700
from time import sleep
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(threadName)-10s %(name)-9s %(message)s')
logger = logging.getLogger(__name__)


def ready(robot, message):
    logger.info('ready')
    robot.rotateby(180, 1)
    return True

def move_finished(robot, message):
    logger.info('move finished')
    robot.end()
    return True

roomba = Roomba700('/dev/ttyAMA0')
robot = Robot(roomba)
robot.subscribe('robot.ready', ready)
robot.subscribe('robot.move.finished', move_finished)
robot.run()
