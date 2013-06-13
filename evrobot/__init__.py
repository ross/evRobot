#
#
#

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from .device import Roomba
from .robot import Robot

# quell warnings
Robot
Roomba

#from Queue import Queue
#from collections import defaultdict
#from datetime import datetime
#from math import atan, degrees, sqrt
#from pprint import pprint
#from serial import Serial
#from threading import Thread
#from time import sleep
#import logging
#
#topics = {'robot',
#          'robot.ready',
#          'robot.done',
#          'robot.move.started',
#          'robot.move.failed',
#          'robot.move.finished'}
#
#
#class Robot(object):
#    logger = logging.getLogger('Robot')
#
#    def __init__(self, device):
#        self.logger.info('__init__: device=%s', device)
#
#        # init our subscription system
#        self.subscribers = defaultdict(set)
#
#        # create a queue for communicating with our device
#        queue = Queue()
#        self.queue = queue
#
#        # give our device access to our queue
#        device.queue = queue
#        self.device = device
#
#    def subscribe(self, topic, subscriber):
#        if topic not in topics:
#            raise Exception('unknown topic')
#        self.subscribers[topic].add(subscriber)
#
#    def unsubscribe(self, subscriber, topic=None):
#        for topic in [topic] if topic else topics:
#            self.subscribers[topic].remove(subscriber)
#
#    def start(self):
#        self.logger.info('start:')
#        self.device.start()
#
#    def end(self):
#        self.logger.info('end:')
#        self.device.end()
#
#    def run(self):
#        self.logger.info('run:')
#        self.start()
#        while True:
#            topic, message = self.queue.get(True)
#            self._send('robot.{0}'.format(topic), message)
#            if topic == 'done':
#                break
#
#    def moveby(self, x, y, speed=1):
#        self.logger.info('moveby: %fm, %fm, %f', x, y, speed)
#        self.device.moveby(x, y, speed)
#
#    def rotateby(self, a, speed=1):
#        self.logger.info('rotateby: %fd, %f', a, speed)
#        self.device.rotateby(a, speed)
#
#    def wait(self):
#        self.logger.info('wait: ')
#        self.device.wait()
#
#    def _send(self, topic, message):
#        self.logger.info('_send: topic=%s, message=%s', topic, message)
#        while True:
#            self.logger.debug('_send: topic=%s', topic)
#            # we need to make a copy of the set b/c it can be modified during
#            # the iteration, both by unsubs and new subscribers
#            for subscriber in set(self.subscribers[topic]):
#                if subscriber(self, message):
#                    self.logger.debug('_send: unsub requested')
#                    self.unsubscribe(subscriber, topic)
#            if '.' not in topic:
#                break
#            topic = topic[:topic.rfind('.')]
#
#
#class Device(Thread):
#    logger = logging.getLogger('Device')
#
#    def __init__(self):
#        super(Device, self).__init__()
#        self._running = True
#
#    def run(self):
#        self.logger.info('run:')
#        self._send('ready', None)
#        last = datetime.now()
#        while self._running:
#            now = datetime.now()
#            elapsed = now - last
#            elapsed = elapsed.seconds + (elapsed.microseconds / 1000000.0)
#            self.tick(elapsed)
#            last = now
#
#    def end(self):
#        self.logger.info('end:')
#        self._running = False
#        self.join()
#        self.logger.info('end: joined')
#        self._send('done', None)
#
#    def _send(self, topic, message):
#        self.queue.put((topic, message))
#
#
#class Simulator(Device):
#    logger = logging.getLogger('Simulator')
#
#    def __init__(self, width, height, x, y, a):
#        super(Simulator, self).__init__()
#
#        self._active_move = None
#
#        self.width = width
#        self.height = height
#        self.logger.info('__init__: room(%f, %f)', self.width, self.height)
#        self.x = x
#        self.y = y
#        self.a = a
#        self.logger.info('__init__: roomba(%f, %f, %f)', self.x, self.y,
#                         self.a)
#
#    def tick(self, elapsed):
#        self._move()
#        sleep(1)
#
#    def _move(self):
#        move = self._active_move
#
#        if not move:
#            return
#
#        def failed():
#            self.logger.warn('_move: failed at %fm, %fm', self.x, self.y)
#            self._active_move = None
#            self._send('move.failed', None)
#
#        self.logger.debug('_move: %fm, %fm, %f, %fd', *move)
#
#        ma = 10
#        if move[3] != 0:
#            d = move[3]
#            if abs(d) > ma:
#                d = ma if d > 0 else -ma
#            move[3] -= d
#            self.a += d
#        else:
#            if move[0] != 0:
#                d = move[0]
#                if abs(d) > move[2]:
#                    d = move[2] if d > 0 else -move[2]
#                move[0] -= d
#                f = self.x + d
#                if 0 <= f and f <= self.width:
#                    self.x = f
#                else:
#                    self.x = self.width
#                    failed()
#                    return
#
#            if move[1] != 0:
#                d = move[1]
#                if abs(d) > move[2]:
#                    d = move[2] if d > 0 else -move[2]
#                move[1] -= d
#                f = self.y + d
#                if 0 <= f and f <= self.height:
#                    self.y = f
#                else:
#                    self.y = self.height
#                    move = None
#
#        self.logger.debug('_move: at %fm, %fm, %fd', self.x, self.y, self.a)
#
#        if move[0] == 0 and move[1] == 0 and move[3] == 0:
#            self._active_move = None
#            self._send('move.finished', None)
#
#    def moveby(self, x, y, speed):
#        ad = degrees(atan((self.y + y) / (self.x + x))) - self.a
#        self.logger.debug('moveby: ad=%fd', ad)
#        self._active_move = [x, y, speed, ad]
#        self._move()
#
#    def wait(self):
#        # kill all active actions
#        self._active_move = None
#
#
#class _Command(object):
#
#    def __init__(self, method, params, duration):
#        self.method = method
#        self.params = params
#        self.duration = duration
#
#    def __repr__(self):
#        return '<Command: {method}, ({params}), {duration}>' \
#            .format(**self.__dict__)
#
#
#mm_p_deg = 2.2515
#
#
#class Roomba(Device):
#    logger = logging.getLogger('Roomba')
#
#    def __init__(self, tty, baud):
#        super(Roomba, self).__init__()
#        self.serial = Serial(tty, baudrate=baud, timeout=0.5)
#        self._commands = []
#        self._current_command = None
#
#        self._write(128)
#        self._write(131)
#        self._stop()
#
#        self._commands.append(_Command('_beep', tuple(), 0.5))
#
#    def _write(self, *bytes):
#        for byte in bytes:
#            self.serial.write(chr(byte))
#
#    def _read(self, n):
#        return None
#        data = port.read(n)
#        n = len(data)
#        ret = 0
#        # TODO: handle sign
#        for i, c in enumerate(data):
#                ret |= ord(c) << (8 * (n - i))
#        return ret
#
#    def rotateby(self, a, speed):
#        speed *= 200
#        self.logger.debug('rotateby: rotate=%fd', a)
#        self._commands.append(_Command('_drive', (speed, 1 if a > 0 else -1),
#                                       mm_p_deg * (abs(a) / speed)))
#        self._commands.append(_Command('_stop', tuple(), 0))
#        self._commands.append(_Command('_move_finished', tuple(), 0))
#
#    def moveby(self, x, y, speed):
#        speed *= 200
#        a = degrees(atan(y / float(x)))
#        # if we're moving backwards
#        if x < 0:
#            # we need to adjust the angle
#            if y < 0:
#                # rotate clockwise
#                a = a - 180
#            else:
#                # rotate counter-clockwise
#                a = 180 + a
#        d = sqrt((x * x) + (y * y))
#        self.logger.debug('moveby: rotate=%fd, travel=%fm', a, d)
#        self._commands.append(_Command('_drive', (speed, 1 if a > 0 else -1),
#                                       mm_p_deg * (abs(a) / speed)))
#        self._commands.append(_Command('_drive', (speed, 32768),
#                                       (d * 1000) / speed))
#        self._commands.append(_Command('_stop', tuple(), 0))
#        self._commands.append(_Command('_move_finished', tuple(), 0))
#
#    def _next_command(self):
#        self.logger.info('_next_command:')
#        if len(self._commands) == 0:
#            # no commands left
#            return None
#
#        # get the next command
#        command = self._commands.pop(0)
#        self.logger.info('_next_command:     command=%s', command)
#
#        # start it
#        getattr(self, command.method)(*command.params)
#
#        # TODO: we could optimize 0 duration commands here
#
#        return command
#
#    def tick(self, elapsed):
#        ret = False
#
#        if self._current_command:
#            self._current_command.duration -= elapsed
#            if self._current_command.duration <= 0:
#                self.logger.debug('tick: finished, command=%s, overage=%f',
#                                  self._current_command,
#                                  abs(self._current_command.duration))
#                self._current_command = self._next_command()
#            ret = True
#        elif len(self._commands):
#            self._current_command = self._next_command()
#            ret = True
#
#        sleep(0.05)
#        return ret
#
#    def _beep(self):
#        self._write(140, 0, 1, 79, 32, 141, 0)
#
#    def _drive(self, velocity, radius):
#        self.logger.info('_drive: velocity=%f, radius=%f', velocity, radius)
#        velocity = int(velocity)
#        radius = int(radius)
#        self._write(137,
#                    velocity >> 8 & 0xff, velocity & 0xff,
#                    radius >> 8 & 0xff, radius & 0xff)
#
#    def _stop(self):
#        self.logger.info('_stop:')
#        self._write(137, 0, 0, 0, 0)
#
#    def _move_finished(self):
#        self._send('move.finished', None)
#
#
#class Roomba700(Roomba):
#
#    def __init__(self, tty):
#        super(Roomba700, self).__init__(tty, 115200)
