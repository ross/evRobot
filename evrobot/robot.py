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
        self.running = True
        self.devices = devices

        # provide access to ourself (as the messenger)
        for device in devices:
            device.messenger = self
            device.start()

    def shutdown(self, finish=True):
        self.logger.info('shutdown: finish=%s', finish)
        self.send('robot.shutdown.started')
        for device in self.devices:
            self.logger.debug('shutdown: send shutdown to device=%s', device)
            device.shutdown(finish)

    def wait(self):
        self.logger.info('wait: started')
        for device in self.devices:
            self.logger.debug('shutdown: wait for device=%s', device)
            device.join()
        self.logger.info('wait: finished')
