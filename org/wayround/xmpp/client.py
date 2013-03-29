
"""
XMPP client class to be used by users
"""

import logging
import select
import threading
import time

import lxml.etree

import org.wayround.utils.stream

import org.wayround.xmpp.core


class XMPPC2SClient:

    def __init__(self, socket):

        self.socket = socket

        self._clear(init=True)

    def _clear(self, init=False):

        if not init:
            if not self.stat() == 'stopped':
                raise RuntimeError("Working. Cleaning restricted")

        self.connection = False

        self._starting = False
        self._stop_flag = False
        self._stopping = False
        self._stream_stop_sent = False

        self.sock_streamer = None

        self.io_machine = None

        self.connection_events_hub = None
        self.input_stream_events_hub = None
        self.input_stream_objects_hub = None
        self.output_stream_events_hub = None

        if self.connection_events_hub:
            self.connection_events_hub.clear()
        else:
            self.connection_events_hub = org.wayround.xmpp.core.ConnectionEventsHub()

        if self.input_stream_events_hub:
            self.input_stream_events_hub.clear()
        else:
            self.input_stream_events_hub = org.wayround.xmpp.core.StreamEventsHub()

        if self.input_stream_objects_hub:
            self.input_stream_objects_hub.clear()
        else:
            self.input_stream_objects_hub = org.wayround.xmpp.core.StreamObjectsHub()

        if self.output_stream_events_hub:
            self.output_stream_events_hub.clear()
        else:
            self.output_stream_events_hub = org.wayround.xmpp.core.StreamEventsHub()


    def start(self):

        if not self._starting and not self._stopping and self.stat() == 'stopped':

            self._starting = True

            ######### SOCKET

            logging.debug('sock is {}'.format(self.socket))

            ######### STREAMS

            self.sock_streamer = org.wayround.utils.stream.SocketStreamer(
                self.socket,
                socket_transfer_size=4096,
                on_connection_event=self.connection_events_hub.dispatch
                )

            threading.Thread(
                name="Socket Streamer Starting Thread",
                target=self.sock_streamer.start
                ).start()

            ######### MACHINES

            threading.Thread(
                target=self._start_io_machine,
                name="IO Machine Starting Thread"
                ).start()

            self._starting = False

        return

    def stop(self):

        if not self._stopping and not self._starting:
            self._stopping = True

            logging.debug("Starting shutdown sequence")
            self._shutdown(_forced=True)
            self.stop_violent(_forced=True)

        return

    def stop_violent(self, _forced=False):


        if (not self._stopping and not self._starting) or _forced:
            self._stopping = True

            stop_list = [
                self._stop_io_machine
                ]

            if self.sock_streamer:
                stop_list.append(self.sock_streamer.stop)

            for i in stop_list:
                threading.Thread(
                    target=i,
                    name="Stopping Thread ({})".format(i)
                    ).start()

            self.wait('stopped')

            logging.debug("Cleaning client instance")

            self._clear()

            self._stopping = False

            logging.debug('sock is {}'.format(self.socket))

        return

    def _shutdown(self, timeout_sec=5.0, _forced=False):

        time_waited = 0.0

        if (not self._stopping and not self._starting) or _forced:

            self._stop_flag = True

            logging.debug("Stopping client correctly")

            if self.connection and not self._stream_stop_sent:
                logging.debug("Sending end of stream")
                self.io_machine.send(
                    org.wayround.xmpp.core.stop_stream()
                    )
                self._stream_stop_sent = True


            while True:
                if self.stat() == 'stopped':
                    break

                logging.debug("Timeout in {:3.2f} sec".format(timeout_sec - time_waited))
                if time_waited >= timeout_sec:
                    break

                time.sleep(1.0)
                time_waited += 1.0


    def wait(self, what='stopped'):

        allowed_what = ['stopped', 'working']

        if not what in allowed_what:
            raise ValueError("`what' must be in {}".format(allowed_what))

        while True:
            time.sleep(0.1)
            if self.stat() == what:
                break

        return

    def stat(self):

        ret = 'various'

        v1 = None
        v2 = None

        if self.sock_streamer:
            v1 = self.sock_streamer.stat()

        if self.io_machine:
            v2 = self.io_machine.stat()

        logging.debug("""
self.sock_streamer.stat() == {}
self.io_machine.stat() == {}
""".format(v1, v2)
            )

        if v1 == v2 == 'working':
            ret = 'working'

        elif v1 == v2 == 'stopped':
            ret = 'stopped'

        elif v1 == v2 == None:
            ret = 'stopped'

        return ret

    def _start_io_machine(self):
        self.io_machine = org.wayround.xmpp.core.XMPPIOStreamRWMachine()
        self.io_machine.set_objects(
            self.sock_streamer,
            i_stream_events_dispatcher=self.input_stream_events_hub.dispatch,
            i_stream_objects_dispatcher=self.input_stream_objects_hub.dispatch,
            o_stream_events_dispatcher=self.output_stream_events_hub.dispatch,
            o_stream_objects_dispatcher=None
            )

        self.io_machine.start()

    def _stop_io_machine(self):
        if self.io_machine:
            self.io_machine.stop()

    def _restart_io_machine(self):
        self._stop_io_machine()
        self._start_io_machine()

