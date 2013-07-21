
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
import org.wayround.xmpp.client_stream_feature_drivers


class XMPPC2SClient:

    def __init__(self, socket):

        self.socket = socket

        self._clear(init=True)

    def _clear(self, init=False):

        if not init:
            if not self.stat() == 'stopped':
                raise RuntimeError("Working. Cleaning restricted")

        self._starting = False
        self._stopping = False
        self._stream_stop_sent = False
        self._input_stream_closed_event = threading.Event()

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

        if not self._stopping and not self._starting and self.stat() == 'working':
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

            logging.debug("Stopping client correctly")

            if not self._stream_stop_sent:
                self.input_stream_events_hub.set_waiter(
                    'client_stream_close_waiter',
                    self._input_stream_close_waiter
                    )
                logging.debug("Sending end of stream")
                self.io_machine.send(
                    org.wayround.xmpp.core.stop_stream()
                    )
                self._stream_stop_sent = True


            while True:
                if self.stat() == 'stopped':
                    break

                if self._input_stream_closed_event.is_set():
                    logging.debug("Input stream closed - ending shutdown timout")
                    break

                logging.debug("Timeout in {:3.2f} sec".format(timeout_sec - time_waited))
                if time_waited >= timeout_sec:
                    break

                time.sleep(1.0)
                time_waited += 1.0

            self.input_stream_events_hub.del_waiter(
                    'client_stream_close_waiter'
                    )

        return


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
Client stat:
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

    def _input_stream_close_waiter(self, event, attrs):

        if event == 'stop':
            self._input_stream_closed_event.set()


def client_starttls(
    client,
    jid,
    connection_info,
    features_element
    ):

    i = org.wayround.xmpp.client_stream_feature_drivers.STARTTLSClientDriver(
        jid,
        connection_info
        )

    i.set_objects(
        sock_streamer=client.sock_streamer,
        io_machine=client.io_machine,
        connection_events_hub=client.connection_events_hub,
        input_stream_events_hub=client.input_stream_events_hub,
        input_stream_objects_hub=client.input_stream_objects_hub,
        output_stream_events_hub=client.output_stream_events_hub
        )

    ret = i.drive(features_element)

    return ret

def client_sasl_auth(
    client,
    cb_mech_select,
    cb_auth,
    cb_response,
    cb_challenge,
    cb_success,
    cb_failure,
    cb_text,
    jid,
    connection_info,
    features_element
    ):

    i = org.wayround.xmpp.client_stream_feature_drivers.SASLClientDriver(
        cb_mech_select,
        cb_auth,
        cb_response,
        cb_challenge,
        cb_success,
        cb_failure,
        cb_text,
        jid,
        connection_info
        )

    i.set_objects(
        sock_streamer=client.sock_streamer,
        io_machine=client.io_machine,
        connection_events_hub=client.connection_events_hub,
        input_stream_events_hub=client.input_stream_events_hub,
        input_stream_objects_hub=client.input_stream_objects_hub,
        output_stream_events_hub=client.output_stream_events_hub
        )

    ret = i.drive(features_element)

    return ret

def client_resource_bind(
    client,
    jid,
    connection_info,
    features_element,
    stanza_processor
    ):

    i = org.wayround.xmpp.client_stream_feature_drivers.ResourceBindClientDriver(
        jid
        )

    i.set_objects(
        sock_streamer=client.sock_streamer,
        io_machine=client.io_machine,
        connection_events_hub=client.connection_events_hub,
        input_stream_events_hub=client.input_stream_events_hub,
        input_stream_objects_hub=client.input_stream_objects_hub,
        output_stream_events_hub=client.output_stream_events_hub,
        stanza_processor=stanza_processor
        )

    ret = i.drive(features_element)

    return ret

def client_session_start(
    client,
    jid,
    connection_info,
    features_element,
    stanza_processor
    ):

    i = org.wayround.xmpp.client_stream_feature_drivers.SessionClientDriver(
        jid
        )

    i.set_objects(
        sock_streamer=client.sock_streamer,
        io_machine=client.io_machine,
        connection_events_hub=client.connection_events_hub,
        input_stream_events_hub=client.input_stream_events_hub,
        input_stream_objects_hub=client.input_stream_objects_hub,
        output_stream_events_hub=client.output_stream_events_hub,
        stanza_processor=stanza_processor
        )

    ret = i.drive(features_element)

    return ret
