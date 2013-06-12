#
#
#

from __future__ import absolute_import, division, print_function, \
    unicode_literals


from evrobot.callqueue import CallQueueMixin
from unittest2 import TestCase


class CallQueueMixinTest(CallQueueMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super(CallQueueMixinTest, self).__init__(*args, **kwargs)
        self.record = []

    def test_aaa_smoke(self):
        # smoke test our call recording
        self.assertEquals(0, len(self.record))
        self.one_param('hello')
        self.assertCallEquals(0, 'one_param', ('hello',))

    def test_params(self):
        self.enqueue('no_params')
        self.invoke_next()
        self.assertCallEquals(0, 'no_params')

        self.enqueue('one_param', 42)
        self.invoke_next()
        self.assertCallEquals(0, 'one_param', (42,))

        self.enqueue('one_param', one=43)
        self.invoke_next()
        self.assertCallEquals(0, 'one_param', (43,))

        self.enqueue('optional_param')
        self.invoke_next()
        self.assertCallEquals(0, 'optional_param', ('optional',))

        self.enqueue('optional_param', 44)
        self.invoke_next()
        self.assertCallEquals(0, 'optional_param', (44,))

        self.enqueue('two_params', 45, 46)
        self.invoke_next()
        self.assertCallEquals(0, 'two_params', (45, 46))

        self.enqueue('two_params', 47, two=48)
        self.invoke_next()
        self.assertCallEquals(0, 'two_params', (47, 48))

        self.enqueue('two_params', two=50, one=49)
        self.invoke_next()
        self.assertCallEquals(0, 'two_params', (49, 50))

    def test_multiple(self):

        self.enqueue('no_params')
        self.enqueue('one_param', 42)
        self.enqueue('one_param', one=43)
        self.enqueue('optional_param')
        self.enqueue('optional_param', 44)
        self.enqueue('two_params', 45, 46)
        self.enqueue('two_params', 47, two=48)
        self.enqueue('two_params', two=50, one=49)

        # make sure we have the expected number of calls
        self.assertEquals(8, len(self.calls))

        # invoke the first two
        self.invoke_next()
        self.invoke_next()
        # check on things
        self.assertEquals(6, len(self.calls))
        self.assertCallEquals(1, 'no_params')
        self.assertCallEquals(0, 'one_param', (42,))

        # invoke the rest
        while self.invoke_next():
            pass

        self.assertEquals(0, len(self.calls))
        self.assertCallEquals(5, 'one_param', (43,))
        self.assertCallEquals(4, 'optional_param', ('optional',))
        self.assertCallEquals(3, 'optional_param', (44,))
        self.assertCallEquals(2, 'two_params', (45, 46))
        self.assertCallEquals(1, 'two_params', (47, 48))
        self.assertCallEquals(0, 'two_params', (49, 50))

    def test_enqueue_next(self):
        # insert two things
        self.enqueue('one_param', 42)
        self.enqueue('one_param', one=43)
        # stick one in front of them
        self.enqueue_next('no_params')

        # invoke them all
        while self.invoke_next():
            pass

        # check that the one we expected to run first did
        self.assertCallEquals(2, 'no_params')
        self.assertCallEquals(1, 'one_param', (42,))
        self.assertCallEquals(0, 'one_param', (43,))

    def test_clear_queue(self):
        # insert some things
        self.enqueue_next('no_params')
        self.enqueue('one_param', 42)
        self.enqueue('one_param', one=43)
        self.assertEquals(3, len(self.calls))
        self.clear_queue()
        self.assertEquals(0, len(self.calls))

    def assertCallEquals(self, index, method, args=None):
        '''helper method to see if a call is what we expect, index starts at
        0 and the most recent call made will live at 0, one before that at 1,
        ...'''
        index = -index - 1
        # reverse indexing since we're appending
        record = self.record[index]
        self.assertEquals(method, record[0])
        self.assertEquals(tuple() if args is None else args, record[1])

    # methods to be called in tests

    def _record(self, method, *args):
        self.record.append((method, args))

    def no_params(self):
        self._record('no_params')

    def optional_param(self, optional='optional'):
        self._record('optional_param', optional)

    def one_param(self, one):
        self._record('one_param', one)

    def two_params(self, one, two):
        self._record('two_params', one, two)
