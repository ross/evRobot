#!/usr/bin/env python

from evrobot import Robot, Simulator
from time import sleep
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(threadName)-10s %(name)-9s %(message)s')

# create our callbacks
def ready(robot, message):
    robot.moveby(2.2, 3.3, 0.5)


def move2_finished(robot, message):
    robot.stop()
    return True

def move_failed(robot, message):
    robot.wait()
    robot.stop()

def move1_finished(robot, message):
    robot.subscribe('robot.move.finished', move2_finished)
    robot.moveby(12, 0, 1)
    return True


def done(robot, message):
    pass


# create our device
simulator = Simulator(10, 10, 5.5, 2.4, 45)
# create our robot
robot = Robot(simulator)

# subscribe to things
robot.subscribe('robot.ready', ready)
robot.subscribe('robot.move.finished', move1_finished)
robot.subscribe('robot.move.failed', move_failed)
robot.subscribe('robot.done', done)

# start things running
robot.run()
