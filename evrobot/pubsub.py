#
#
#

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from collections import defaultdict
import logging


class PubSubMixin(object):
    logger = logging.getLogger('PubSubMixin')

    def __init__(self, *args, **kwargs):
        super(PubSubMixin, self).__init__(*args, **kwargs)
        # we're storing them in a dict so that they can be keyed with the
        # original subscriber if/when we wrap subscriber to handle bound
        # methods
        self.subscribers = defaultdict(dict)

    def _listener(self, subscriber):
        # if it's a bound method, we need to wrap it
        if hasattr(subscriber, '__self__'):
            # bound method python >= 2.6
            orig = subscriber
            def wrapper(*args, **kwargs):
                return orig.__func__(orig.__self__, *args, **kwargs)
            subscriber = wrapper
        elif hasattr(subscriber, 'im_self'):
            # bound method python < 2.6
            orig = subscriber
            def wrapper(*args, **kwargs):
                return orig.im_func(orig.im_self, *args, **kwargs)
            subscriber = wrapper

        return subscriber

    def subscribe(self, subscriber, *topics):
        self.logger.info('subscribe: subscriber=%s, topics=%s', subscriber,
                         topics)
        for topic in topics:
            self.subscribers[topic][subscriber] = self._listener(subscriber)

    def unsubscribe(self, subscriber, *topics):
        self.logger.info('unsubscribe: subscriber=%s, topics=%s', subscriber,
                         topics)
        for topic in topics:
            self.subscribers[topic].pop(subscriber, None)

    def send(self, topic, *args, **kwargs):
        self.logger.info('send: topic=%s, args=%s, kwargs=%s', topic, args,
                         kwargs)
        seen = set()
        while True:
            self.logger.debug('_send: topic=%s', topic)
            # we need to make a copy of the set b/c it can be modified during
            # the iteration, both by unsubs and new subscribers
            for orig, subscriber in self.subscribers[topic].items():
                # don't sent the message to subscribers who've already seen it
                if orig in seen:
                    continue
                seen.add(orig)
                if subscriber(*args, **kwargs):
                    self.logger.debug('_send: unsub requested')
                    self.unsubscribe(orig, topic)
            if '.' not in topic:
                break
            topic = topic[:topic.rfind('.')]

