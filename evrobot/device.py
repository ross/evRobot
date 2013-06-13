#
#
#

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from math import atan, degrees, sqrt
from threading import Thread
from time import sleep
from .callqueue import CallQueueMixin
import logging


class Device(CallQueueMixin, Thread):
    logger = logging.getLogger('Device')

    def __init__(self):
        super(Device, self).__init__()
        self.messenger = None
        self.running = True

    ## commands

    def reset(self):
        self.logger.debug('reset:')
        # TODO: stop current actions now, interrupt sleep?
        self.clear_queue()

    def shutdown(self, finish):
        self.logger.debug('shutdown:')
        if not finish:
            self.reset()
        self.enqueue('_quit')

    ## actions

    def _quit(self):
        self.logger.debug('_quit:')
        self.running = False

    ## Thread

    def start(self):
        Thread.start(self)

    def join(self):
        Thread.join(self)

    def run(self):
        self.logger.debug('run:')
        while self.running:
            # TODO: we should switch to a blocking Queue to avoid sleeping
            if not self.invoke_next():
                sleep(1)



class Roomba(Device):
    max_speed = 200
    mm_p_deg = 2.2515

    def __init__(self, serial):
        super(Roomba, self).__init__()
        self.serial = serial

        self._init()
        self._safe()
        self._stop()
        self.enqueue('_beep')

    ## commands

    def move_by(self, x, y, speed):
        speed = min(self.max_speed, speed * self.max_speed)

        a = degrees(atan(y / float(x)))
        # if we're moving backwards
        if x < 0:
            # we need to adjust the angle
            if y < 0:
                # rotate clockwise
                a = a - 180
            else:
                # rotate counter-clockwise
                a = 180 + a
        d = sqrt((x * x) + (y * y))
        self.logger.debug('move_by: rotate=%fd, travel=%fm, speed=%d', a, d,
                          speed)

        self.enqueue('_move_started', 'move_by', x, y, speed)

        # point ourselves in the right direction
        self.enqueue('_drive', speed, 1 if a > 0 else -1)
        self.enqueue('_sleep', self.mm_p_deg * (abs(a) / speed))

        # move ourselves to the right point
        self.enqueue('_drive', speed, 32768)
        self.enqueue('_sleep', (d * 1000) / speed)
        self.enqueue('_stop')
        self.enqueue('_move_finished', 'move_by', x, y, speed)

    def rotate_by(self, degrees, speed):
        speed = min(self.max_speed, speed * self.max_speed)
        self.logger.debug('rotate_by: rotate=%fd, speed=%d', degrees, speed)
        self.enqueue('_move_started', 'rotate_by', degrees, speed)
        self.enqueue('_drive', speed, 1 if degrees > 0 else -1)
        self.enqueue('_sleep', self.mm_p_deg * (abs(degrees) / speed))
        self.enqueue('_stop')
        self.enqueue('_move_finished', 'rotate_by', degrees, speed)

    ## actions

    def _init(self):
        self._write(128)

    def _safe(self):
        self._write(131)

    def _beep(self):
        self.logger.info('_beep')
        self._write(140, 0, 1, 79, 32, 141, 0)

    def _drive(self, velocity, radius):
        self.logger.info('_drive: velocity=%f, radius=%f', velocity, radius)
        velocity = int(velocity)
        radius = int(radius)
        self._write(137, velocity >> 8 & 0xff, velocity & 0xff,
                    radius >> 8 & 0xff, radius & 0xff)

    def _sleep(self, duration):
        sleep(duration)

    def _stop(self):
        self.logger.info('_stop:')
        self._write(137, 0, 0, 0, 0)

    ## messages

    def _move_started(self, *args, **kwargs):
        self.messenger.send('robot.move.started', *args, **kwargs)

    def _move_finished(self, *args, **kwargs):
        self.messenger.send('robot.move.finished', *args, **kwargs)

    ## io

    def _write(self, *bytes):
        for byte in bytes:
            self.serial.write(chr(byte))
