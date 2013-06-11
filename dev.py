#!/usr/bin/env python

from evrobot import Robot, Roomba700
from math import sqrt
from time import sleep
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(threadName)-10s %(name)-9s %(message)s')
logger = logging.getLogger(__name__)


def ready(robot, message):
    logger.info('ready')
    robot.moveby(1, 0.5, 1)
    return True

def move_3_finished(robot, message):
    logger.info('move 2 finished')
    robot.end()
    return True

def move_2_finished(robot, message):
    logger.info('move 2 finished')
    robot.rotateby(163, 1)
    robot.subscribe('robot.move.finished', move_3_finished)
    return True

def move_finished(robot, message):
    logger.info('move finished')
    robot.moveby(-sqrt(1.25), 0)
    robot.subscribe('robot.move.finished', move_2_finished)
    return True

roomba = Roomba700('/dev/ttyAMA0')
robot = Robot(roomba)
robot.subscribe('robot.ready', ready)
robot.subscribe('robot.move.finished', move_finished)
robot.run()
