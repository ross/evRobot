#
#
#

from __future__ import absolute_import, division, print_function, \
    unicode_literals


from evrobot.pubsub import PubSubMixin
from unittest2 import TestCase


class PubSubMixinTest(PubSubMixin, TestCase):

    def subscribing_method(self, message):
        self._subscribing_method_message = message

    def removing_subscribing_method(self):
        self.count += 1
        return True

    def test_params(self):

        def subscriber(*args, **kwargs):
            self.count += 1
            self.args = args
            self.kwargs = kwargs

        self.subscribe(subscriber, 'callme')

        self.count = 0
        # no params
        self.send('callme')
        self.assertEquals(1, self.count)
        self.assertEquals(tuple(), self.args)
        self.assertEquals({}, self.kwargs)

        # one args
        self.send('callme', 42)
        self.assertEquals(2, self.count)
        self.assertEquals((42,), self.args)
        self.assertEquals({}, self.kwargs)

        # two args
        self.send('callme', 43, 44)
        self.assertEquals(3, self.count)
        self.assertEquals((43, 44), self.args)
        self.assertEquals({}, self.kwargs)

        # one arg, one kwarg
        self.send('callme', 45, kw=46)
        self.assertEquals(4, self.count)
        self.assertEquals((45,), self.args)
        self.assertEquals({'kw': 46}, self.kwargs)

        # two kwargs
        self.send('callme', kw1=47, kw2=48)
        self.assertEquals(5, self.count)
        self.assertEquals(tuple(), self.args)
        self.assertEquals({'kw1': 47, 'kw2': 48}, self.kwargs)

    def test_dotted(self):

        def subscriber():
            self.count += 1

        self.subscribe(subscriber, 'first.second')

        self.count = 0
        self.assertEquals(0, self.count)
        self.send('other')
        self.assertEquals(0, self.count)
        self.send('first')
        self.assertEquals(0, self.count)
        self.send('first.second')
        self.assertEquals(1, self.count)
        self.send('first.second.third')
        self.assertEquals(2, self.count)
        self.send('first.second.third.fourth')
        self.assertEquals(3, self.count)

        # subscribe again at the top level
        self.subscribe(subscriber, 'first')

        self.count = 0
        self.assertEquals(0, self.count)
        self.send('other')
        self.assertEquals(0, self.count)
        self.send('first')
        self.assertEquals(1, self.count)
        self.send('first.second')
        self.assertEquals(2, self.count)
        self.send('first.second.third')
        self.assertEquals(3, self.count)
        self.send('first.second.third.fourth')
        self.assertEquals(4, self.count)
        self.send('first.other')
        self.assertEquals(5, self.count)

        # unsubscribe from the top level
        self.unsubscribe(subscriber, 'first')

        self.count = 0
        self.assertEquals(0, self.count)
        self.send('other')
        self.assertEquals(0, self.count)
        self.send('first')
        self.assertEquals(0, self.count)
        self.send('first.second')
        self.assertEquals(1, self.count)
        self.send('first.second.third')
        self.assertEquals(2, self.count)
        self.send('first.second.third.fourth')
        self.assertEquals(3, self.count)

        # unsubscribe from the second level
        self.unsubscribe(subscriber, 'first.second')

        self.count = 0
        self.assertEquals(0, self.count)
        self.send('other')
        self.assertEquals(0, self.count)
        self.send('first')
        self.assertEquals(0, self.count)
        self.send('first.second')
        self.assertEquals(0, self.count)

    def test_double_subscribe(self):

        def subscriber():
            self.count += 1

        # subscribe twice
        self.subscribe(subscriber, 'first')
        self.subscribe(subscriber, 'first')

        self.count = 0
        self.assertEquals(0, self.count)
        self.send('first')
        # only got the message once
        self.assertEquals(1, self.count)

    def test_remove(self):

        def subscriber():
            self.count += 1

        def nonremoving_subscriber():
            self.count += 1
            return False

        def removing_subscriber():
            self.count += 1
            return True

        self.subscribe(subscriber, 'callme')
        self.subscribe(nonremoving_subscriber, 'callme')
        self.subscribe(removing_subscriber, 'callme')
        self.subscribe(self.removing_subscribing_method, 'callme')

        self.count = 0
        self.send('callme')
        # all got it
        self.assertEquals(4, self.count)

        self.count = 0
        self.send('callme')
        # the removing subscribers didn't get it
        self.assertEquals(2, self.count)

    def test_method(self):
        self.subscribe(self.subscribing_method, 'callme')
        message = 'hello world!'
        self.send('callme', message)
        self.assertEquals(message, self._subscribing_method_message)

        self.unsubscribe(self.subscribing_method, 'callme')
        self.send('callme', 'another')
        # didn't get the 2nd message, so we still see the first
        self.assertEquals(message, self._subscribing_method_message)

    def test_pre_2_6_method(self):
        '''this is a HACK to test out the pre-2.6 mechinism for calling
        methods'''

        class Listener(object):

            def __init__(self):
                self.count = 0

            def listen(self):
                self.count += 1

        # an object that we can stuff im_self and im_func on to and pretend
        # like it's a pre-2.6 bound method
        class Helper(object):
            im_self = None
            im_func = None

        listener = Listener()

        method = Helper()
        # the listener instance is self
        method.im_self = listener
        # the the class method (not instance)
        method.im_func = Listener.listen

        self.subscribe(method, 'callme')

        self.assertEquals(0, listener.count)
        self.send('callme')
        self.assertEquals(1, listener.count)
