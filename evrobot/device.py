#
#
#

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from datetime import datetime
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
        self.reset()

    ## commands

    def reset(self):
        self.logger.debug('reset:')
        self.clear_queue()
        self.time_remaining = 0

    def shutdown(self, finish):
        self.logger.debug('shutdown:')
        if not finish:
            self.reset()
        self.enqueue('_quit')

    ## actions

    def _quit(self):
        self.logger.debug('_quit:')
        self.running = False

    def _sleep(self, duration):
        self.time_remaining = duration

    ## Thread

    def start(self):
        Thread.start(self)

    def join(self):
        Thread.join(self)

    def run(self):
        self.logger.debug('run:')
        last = datetime.now()
        while self.running:
            now = datetime.now()
            # determine how much time has elapsed since our last tick
            elapsed = now - last
            elapsed = elapsed.seconds + (elapsed.microseconds / 1000000.0)
            # subtract the elapsed from our time remaining
            self.time_remaining -= elapsed
            # if its' <= 0 invoke the next command, this will invoke one
            # command per tick until time_remaining is set > 0
            if self.time_remaining <= 0:
                self.invoke_next()
            # tick things
            self.tick(elapsed)
            # record the time at which we ran
            last = now

    def tick(self, elapsed):
        '''called once on each run loop. tick is responsible for consuming an
        appropriate/reasonable amount of time, through a combination of
        processing and sleeping so that threads don't continually run and peg
        the cpu'''
        # TODO: we should switch to a blocking Queue to avoid sleeping
        sleep(0.25)


class Roomba(Device):
    max_speed = 300
    mm_p_deg = 2.2515

    def __init__(self, serial):
        self.serial = serial
        self._init()
        self._safe()
        self.bumping = False
        self.dropping = False
        super(Roomba, self).__init__()
        self.enqueue('_beep')

        self.reset_on_bump = True

    ## commands

    def reset(self):
        super(Roomba, self).reset()
        self._stop()

    def move_by(self, x, y, speed=1):
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

    def rotate_by(self, degrees, speed=1):
        speed = min(self.max_speed, speed * self.max_speed)
        self.logger.debug('rotate_by: rotate=%fd, speed=%d', degrees, speed)
        self.enqueue('_move_started', 'rotate_by', degrees, speed)
        self.enqueue('_drive', speed, 1 if degrees > 0 else -1)
        self.enqueue('_sleep', self.mm_p_deg * (abs(degrees) / speed))
        self.enqueue('_stop')
        self.enqueue('_move_finished', 'rotate_by', degrees, speed)

    def debump(self):
        self.logger.debug('debump:')
        self.enqueue('_drive', self.max_speed * -0.5, 32768)
        self.enqueue('_sleep', 0.25)
        self.enqueue('_move_finished', 'debump')

    def vacuum(self, on=True):
        self.enqueue('_vacuum', on)

    def main_brush(self, on=True):
        self.enqueue('_main_brush', on)

    def side_brush(self, on=True):
        self.enqueue('_side_brush', on)

    def clean(self):
        self.enqueue('_clean')

    def dock(self):
        self.enqueue('_dock')

    def spot(self):
        self.enqueue('_spot')

    def power(self):
        self.enqueue('_power')

    # TODO: LEDs

    ## actions

    def _init(self):
        self._write(128)

    def _safe(self):
        self._write(131)

    def _beep(self):
        self.logger.info('_beep')
        self._write(140, 0, 1, 79, 32, 141, 0)

    def _clean(self):
        self._write(135)

    def _dock(self):
        self._write(143)

    def _spot(self):
        self._write(134)

    def _power(self):
        self._Write(133)

    def _vacuum(self, on):
        self._write(138, self._motor_state & 0xff if on else 0xfd)

    def _main_brush(self, on):
        self._write(138, self._motor_state & 0xff if on else 0xfb)

    def _side_brush(self, on):
        self._write(138, self._motor_state & 0xff if on else 0xfe)

    def _drive(self, velocity, radius):
        self.logger.info('_drive: velocity=%f, radius=%f', velocity, radius)
        velocity = int(velocity)
        radius = int(radius)
        self._write(137, velocity >> 8 & 0xff, velocity & 0xff,
                    radius >> 8 & 0xff, radius & 0xff)

    def _stop(self):
        self.logger.info('_stop:')
        self._write(137, 0, 0, 0, 0)

    ## state

    def _check_sensors(self):
        # read sensor data
        # TODO: add
        # * 45 - light bump sensor
        # * 18 - buttons
        # * 9-12 - clif left, front left, front right, right
        # * 13/27 - virtual wall?
        # * 14 - wheel overcurrent
        # * 21 - charging
        # * 22 - ballery voltage
        # * 23 - current flow
        # * 24 - battery temp
        # * 25 - battery charge
        # * 26 - battery capacity
        # *
        # * ir codes
        self._write(149, 2, 7, 8)
        sensors = self._read(2)

        # we'll only send out the first thing we see bump
        bumpers = sensors[0] & 0x03
        if bumpers:
            if not self.bumping:
                self.bumping = 'left'
                if bumpers == 0x01:
                    self.bumping = 'right'
                if bumpers == 0x03:
                    self.bumping = 'both'
                if self.reset_on_bump:
                    self.reset()
                self.messenger.send('robot.obstacle.bumping', self.bumping)
        else:
            self.bumping = False

        drops = sensors[0] & 0x0c
        if drops:
            if not self.dropping:
                self.dropping = 'left'
                if drops == 0x08:
                    self.dropping = 'right'
                elif drops == 0xc:
                    self.dropping = 'both'
                if self.reset_on_drop:
                    self.reset()
                self.messenger.send('robot.obstacle.dropping', self.dropping)
        else:
            self.dropping = False

    def tick(self, elapsed):
        print('elapsed')
        self._check_sensors()

        # roomba updates it's information every 15ms so ideally we'd poll at
        # that rate. our run loop will take a bit of time so we'll subtract the
        # elapsed time for this round from that ideal so that we get as close
        # to 15ms as possible between rounds
        duration = (15 / 1000.0) - elapsed
        if duration > 0:
            sleep(duration)

    def _motor_state(self):
        # TODO: read motor state
        return 0x00

    ## messages

    def _move_started(self, *args, **kwargs):
        self.messenger.send('robot.move.started', *args, **kwargs)

    def _move_finished(self, *args, **kwargs):
        self.messenger.send('robot.move.finished', *args, **kwargs)

    ## io

    def _write(self, *bytes):
        for byte in bytes:
            self.serial.write(chr(byte))

    def _read(self, n):
        return map(ord, self.serial.read(n))
