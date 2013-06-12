#
#
#

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from collections import namedtuple
import logging


Call = namedtuple('Call', ('method', 'args', 'kwargs'))


# TODO: thread safety, probably should just use a Queue object as that would
# allow us to block until there's work to be done, but that may tie us to being
# a thread more than makes sense...
class CallQueueMixin(object):
    logger = logging.getLogger('CommandsMixin')

    def __init__(self, *args, **kwargs):
        super(CallQueueMixin, self).__init__(*args, **kwargs)
        self.clear_queue()

    def enqueue_next(self, method, *args, **kwargs):
        '''add a method call to the front of the queue'''
        self.calls.insert(0, Call(method, args, kwargs))

    def enqueue(self, method, *args, **kwargs):
        '''add a method call to the back of the queue'''
        # TODO: record the current stacktrace so that we can include
        # information about the "real" source of the call if next throws
        self.calls.append(Call(method, args, kwargs))

    def clear_queue(self):
        '''clear all pending calls'''
        self.calls = []

    def invoke_next(self):
        '''invoke the next call, if any. returns False if nothing was called,
        True otherwise'''
        if not self.calls:
            return False
        call = self.calls.pop(0)
        getattr(self, call.method)(*call.args, **call.kwargs)
        return True
