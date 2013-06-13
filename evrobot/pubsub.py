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
        '''subscribe subscriber to the list of provided topics'''
        self.logger.info('subscribe: subscriber=%s, topics=%s', subscriber,
                         topics)
        for topic in topics:
            self.subscribers[topic][subscriber] = self._listener(subscriber)

    def unsubscribe(self, subscriber, *topics):
        '''unsubscribe subscriber from the topics passed, if none are passed
        remove it from all topics'''
        self.logger.info('unsubscribe: subscriber=%s, topics=%s', subscriber,
                         topics)
        for topic in topics if len(topics) else self.subscribers.keys():
            self.subscribers[topic].pop(subscriber, None)

    def send(self, topic, *args, **kwargs):
        '''send a message to app subscribers listening to topic with the
        provided args and kwargs. if topic contains dots, first.second it will
        be considered a hierarchical topic and messages will be sent to both
        first.second and first. care is taken that a given subscriber will
        only see a message once'''
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
