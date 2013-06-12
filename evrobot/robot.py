#
#
#

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from .pubsub import PubSubMixin
import logging


class Robot(PubSubMixin):
    logger = logging.getLogger('Robot')

    def __init__(self, device):
        self.logger.info('__init__: device=%s', device)
        super(Robot, self).__init__()
