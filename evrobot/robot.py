#
#
#

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from .pubsub import PubSubMixin
import logging


class Robot(PubSubMixin):
    logger = logging.getLogger('Robot')

    def __init__(self, *devices):
        self.logger.info('__init__: devices=%s', devices)
        super(Robot, self).__init__()

        # provide access to ourself (as the messenger)
        for device in devices:
            device.messenger = self
            device.start()

        self.devices = devices

    def move_by(self, x, y, speed=1):
        # TODO: what if multiple devices support...
        for device in self.devices:
            if hasattr(device, 'move_by'):
                device.move_by(x, y, speed)

    def rotate_by(self, degrees, speed=1):
        for device in self.devices:
            if hasattr(device, 'rotate_by'):
                device.rotate_by(degrees, speed)

    def reset(self):
        for device in self.devices:
            device.reset()

    def shutdown(self, finish=True):
        self.logger.info('shutdown: finish=%s', finish)
        self.send('robot.shutdown.started')
        for device in self.devices:
            self.logger.debug('shutdown: send shutdown to device=%s', device)
            device.shutdown(finish)
        for device in self.devices:
            self.logger.debug('shutdown: wait for device=%s', device)
            device.join()
        self.logger.info('shutdown: finished')
        self.send('robot.shutdown.finished')
