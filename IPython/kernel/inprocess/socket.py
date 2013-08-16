""" Defines a dummy socket implementing (part of) the zmq.Socket interface. """

#-----------------------------------------------------------------------------
#  Copyright (C) 2012  The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports.
import abc
try:
    import queue  # Python 3
except:
    import Queue as queue  # Python 2

# System library imports.
import zmq

# Local imports.
from IPython.utils.traitlets import HasTraits, Instance, Int
import six
from six.moves import map

#-----------------------------------------------------------------------------
# Generic socket interface
#-----------------------------------------------------------------------------

class SocketABC(six.with_metaclass(abc.ABCMeta, object)):
    @abc.abstractmethod
    def recv_multipart(self, flags=0, copy=True, track=False):
        raise NotImplementedError

    @abc.abstractmethod
    def send_multipart(self, msg_parts, flags=0, copy=True, track=False):
        raise NotImplementedError

SocketABC.register(zmq.Socket)

#-----------------------------------------------------------------------------
# Dummy socket class
#-----------------------------------------------------------------------------

class DummySocket(HasTraits):
    """ A dummy socket implementing (part of) the zmq.Socket interface. """
    
    queue = Instance(queue.Queue, ())
    message_sent = Int(0) # Should be an Event

    #-------------------------------------------------------------------------
    # Socket interface
    #-------------------------------------------------------------------------

    def recv_multipart(self, flags=0, copy=True, track=False):
        return self.queue.get_nowait()

    def send_multipart(self, msg_parts, flags=0, copy=True, track=False):
        msg_parts = list(map(zmq.Message, msg_parts))
        self.queue.put_nowait(msg_parts)
        self.message_sent += 1

SocketABC.register(DummySocket)
