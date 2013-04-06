
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

        self._starting = False
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

            logging.debug("Stopping client correctly")

            if not self._stream_stop_sent:
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


def client_starttls(
    client,
    jid,
    connection_info,
    features_element
    ):

    i = STARTTLSClientDriver(
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

    i = SASLClientDriver(
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

    i = ResourceBindClientDriver(
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

    i = SessionClientDriver(
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


class STARTTLSClientDriver(org.wayround.xmpp.core.Driver):

    """
    Driver for starting STARTTLS on client side conection part
    """

    def __init__(self, jid, connection_info):

        """
        Initiates object using :meth:`_clear`
        """
        self._jid = jid
        self._connection_info = connection_info

        self._clear(init=True)

    def set_objects(
        self,
        sock_streamer,
        io_machine,
        connection_events_hub,
        input_stream_events_hub,
        input_stream_objects_hub,
        output_stream_events_hub
        ):

        """
        Set objects to work with

        :param sock_streamer: instance of class
            :class:`org.wayround.utils.stream.SocketStreamer`

        :param io_machine: instance of class
            :class:`XMPPIOStreamRWMachine`

        :param connection_events_hub: hub to route connection events
            :class:`ConnectionEventsHub`

        :param input_stream_events_hub: hub to route input stream events
            :class:`StreamEventsHub`

        :param output_stream_events_hub: hub to route output stream events
            :class:`StreamEventsHub`
        """

        self._sock_streamer = sock_streamer
        self._io_machine = io_machine
        self._connection_events_hub = connection_events_hub
        self._input_stream_events_hub = input_stream_events_hub
        self._input_stream_objects_hub = input_stream_objects_hub
        self._output_stream_events_hub = output_stream_events_hub

    def _clear(self, init=False):
        """
        Clears instance, setting default values for all attributes
        """

        self._sock_streamer = None
        self._io_machine = None
        self._input_stream_events_hub = None
        self._input_stream_objects_hub = None
        self._output_stream_events_hub = None

        self._driving = False
        self._exit_event = threading.Event()
        self._exit_event.clear()

        self.status = 'just created'

        self.result = None

        return

    def _start(self):

        """
        Started by :meth:`self.drive`

        If not already ``self._driving``, then drive!: register own waiters for

        * ``self._connection_events_hub`` - :meth:`_connection_events_waiter`
        * ``self._input_stream_events_hub`` - :meth:`_input_stream_events_waiter`
        * ``self._input_stream_objects_hub`` - :meth:`_stream_objects_waiter`
        """

        if not self._driving:

            self._driving = True

            logging.debug("STARTTLS Driver driving now! B-)")

            self._connection_events_hub.set_waiter(
                'tls_driver', self._connection_events_waiter
                )

            self._input_stream_events_hub.set_waiter(
                'tls_driver', self._input_stream_events_waiter
                )

            self._input_stream_objects_hub.set_waiter(
                'tls_driver', self._stream_objects_waiter
                )

        return


    def _stop(self):

        """
        If ``self._driving``, then stop it. And don't listen hubs any more!
        """

        if self._driving:

            self._connection_events_hub.del_waiter('tls_driver')

            self._input_stream_events_hub.del_waiter('tls_driver')

            self._input_stream_objects_hub.del_waiter('tls_driver')

            logging.debug("STARTTLS Driver stopped with result `{}'".format(self.result))

            self._driving = False

            self._exit_event.set()

        return

    def stop(self):

        """
        Stop driver work. Just calls :meth:`_stop`
        """
        self._stop()

        return

    def drive(self, obj):

        """
        Drives to STARTTLS, basing on ``obj``, which must be an XML element
        instance with features.

        If ``obj.tag`` is ``{http://etherx.jabber.org/streams}features`` and
        it is contains ``{urn:ietf:params:xml:ns:xmpp-tls}starttls`` element,
        then:

        #. switch ``self.status`` to ``'requesting tls'``

        #. run :meth:`_start`

        #. start STARTTLS sequence sending starttls element

        #. wait while ``self._driving`` == True

        #. return ``self.result``

        :rtype: ``str``

        Return can be one of following values:

        =================== ============================================
        value               meaning
        =================== ============================================
        'no tls'            TLS not proposed by server
        'success'           TLS layer engaged
        'stream stopped'    stream was closed by server
        'stream error'      some stream error encountered
        'failure'           server returned
                            ``{urn:ietf:params:xml:ns:xmpp-tls}failure``
        'response error'    wrong server response
        'programming error' if you received this - mail me a bug report
        =================== ============================================
        """

        if obj.tag == '{http://etherx.jabber.org/streams}features':
            self.status = 'looking for tls'

            if obj.find('{urn:ietf:params:xml:ns:xmpp-tls}starttls') != None:

                self._start()

                self.status = 'requesting tls'

                logging.debug("Sending STARTTLS request")
                self._io_machine.send(
                    org.wayround.xmpp.core.starttls()
                    )

                self._exit_event.wait()

            else:

                logging.debug("TLS not proposed")

                self.result = 'no tls'

        ret = self.result

        return ret

    def _connection_events_waiter(self, event, sock):

        """
        If driving, then look for event == ``'ssl wrapped'`` and then:

        #. restart input machine with driven socket streamer, input event and
           objects hubs;

        #. restart output machine with driven streamer and output event hub

        #. wait till machines working

        #. restart stream with start_stream command
        """

        if self._driving:

            logging.debug("_connection_events_waiter :: `{}' `{}'".format(event, sock))

            if event == 'ssl wrapped':

                logging.debug("Socket streamer threads restarted")
                logging.debug("Restarting Machines")
                self._io_machine.restart_with_new_objects(
                    self._sock_streamer,
                    self._input_stream_events_hub.dispatch,
                    self._input_stream_objects_hub.dispatch,
                    self._output_stream_events_hub.dispatch,
                    None
                    )

                logging.debug("Waiting machines restart")
                self._io_machine.wait('working')
                logging.debug("Machines restarted")

                logging.debug("Starting new stream")
                self._io_machine.send(
                    org.wayround.xmpp.core.start_stream(
                        jid_from=self._jid.bare(),
                        jid_to=self._connection_info.host
                        )
                    )

        return


    def _input_stream_events_waiter(self, event, attrs=None):

        if self._driving:

            logging.debug(
                "_input_stream_events_waiter :: `{}', `{}'".format(
                    event,
                    attrs
                    )
                )

            if event == 'start':

                self.result = 'success'

            elif event == 'stop':

                self.result = 'stream stopped'

            elif event == 'error':

                self.result = 'stream error'

            self._stop()


        return

    def _stream_objects_waiter(self, obj):

        if self._driving:

            logging.debug("_stream_objects_waiter :: `{}'".format(obj))

            if self.status == 'requesting tls':

                if obj.tag.startswith('{urn:ietf:params:xml:ns:xmpp-tls}'):

                    self.tls_request_result = obj.tag

                    if self.tls_request_result == '{urn:ietf:params:xml:ns:xmpp-tls}proceed':

                        self._sock_streamer.start_ssl()

                    else:

                        self.result = 'failure'

                        self._stop()

            else:
                self.result = 'programming error'

                self._stop()

        return


class SASLClientDriver(org.wayround.xmpp.core.Driver):

    """
    Driver for authenticating client on server
    """

    def __init__(
        self,
        cb_mech_select,
        cb_auth,
        cb_response,
        cb_challenge,
        cb_success,
        cb_failure,
        cb_text,
        jid,
        connection_info
        ):

        """
        Initiates object using :meth:`_clear`
        """

        for i in [
            'cb_mech_select',
            'cb_auth',
            'cb_response',
            'cb_challenge',
            'cb_success',
            'cb_failure',
            'cb_text',
            ]:
            if not callable(eval(i)):
                raise ValueError("{} must be provided and be callable".format(i))


        self.cb_mech_select = cb_mech_select
        self.cb_auth = cb_auth
        self.cb_response = cb_response
        self.cb_challenge = cb_challenge
        self.cb_success = cb_success
        self.cb_failure = cb_failure
        self.cb_text = cb_text

        self._jid = jid
        self._connection_info = connection_info

        self._clear(init=True)

    def set_objects(
        self,
        sock_streamer,
        io_machine,
        connection_events_hub,
        input_stream_events_hub,
        input_stream_objects_hub,
        output_stream_events_hub
        ):

        """
        Set objects to work with

        :param sock_streamer: instance of class
            :class:`org.wayround.utils.stream.SocketStreamer`

        :param io_machine: instance of class
            :class:`XMPPIOStreamRWMachine`

        :param connection_events_hub: hub to route connection events
            :class:`ConnectionEventsHub`

        :param input_stream_events_hub: hub to route input stream events
            :class:`StreamEventsHub`

        :param output_stream_events_hub: hub to route output stream events
            :class:`StreamEventsHub`

        """

        self._sock_streamer = sock_streamer
        self._io_machine = io_machine
        self._connection_events_hub = connection_events_hub
        self._input_stream_events_hub = input_stream_events_hub
        self._input_stream_objects_hub = input_stream_objects_hub
        self._output_stream_events_hub = output_stream_events_hub

    def _clear(self, init=False):
        """
        Clears instance, setting default values for all attributes
        """

        self._sock_streamer = None
        self._io_machine = None
        self._input_stream_events_hub = None
        self._input_stream_objects_hub = None
        self._output_stream_events_hub = None

        self._driving = False
        self._exit_event = threading.Event()
        self._exit_event.clear()

        self.status = 'just created'

        self.result = None

        return

    def _start(self):

        """
        Started by :meth:`self.drive`

        If not already ``self._driving``, then drive!: register own waiters for

        * ``self._connection_events_hub`` - :meth:`_connection_events_waiter`
        * ``self._input_stream_events_hub`` - :meth:`_input_stream_events_waiter`
        * ``self._input_stream_objects_hub`` - :meth:`_stream_objects_waiter`
        """

        if not self._driving:

            self._driving = True

            logging.debug("SASL Driver driving now! B-)")

            self._connection_events_hub.set_waiter(
                'sasl_driver', self._connection_events_waiter
                )

            self._input_stream_events_hub.set_waiter(
                'sasl_driver', self._input_stream_events_waiter
                )

            self._input_stream_objects_hub.set_waiter(
                'sasl_driver', self._stream_objects_waiter
                )

        return


    def _stop(self):

        """
        If ``self._driving``, then stop it. And don't listen hubs any more!
        """

        if self._driving:

            self._connection_events_hub.del_waiter('sasl_driver')

            self._input_stream_events_hub.del_waiter('sasl_driver')

            self._input_stream_objects_hub.del_waiter('sasl_driver')

            logging.debug("SASL Driver stopped with result `{}'".format(self.result))

            self._driving = False

            self._exit_event.set()

        return

    def stop(self):

        """
        Stop driver work. Just calls :meth:`_stop`
        """
        self._stop()

        return

    def drive(self, obj):


        if obj.tag == '{http://etherx.jabber.org/streams}features':
            self.status = 'looking for sasl mechanisms'

            mechanisms_element = obj.find('{urn:ietf:params:xml:ns:xmpp-sasl}mechanisms')

            if mechanisms_element != None:

                self.status = 'looking for DIGEST-MD5 mechanism'

                mechanisms = mechanisms_element.findall('{urn:ietf:params:xml:ns:xmpp-sasl}mechanism')

                _mechanisms = []
                for i in mechanisms:
                    _mechanisms.append(i.text)

                mechanisms = _mechanisms


                logging.debug("Proposed mechanisms are:")
                for i in mechanisms:
                    logging.debug("    {}".format(i))

                sel_mechanism = self.cb_mech_select(mechanisms)

                if not sel_mechanism in mechanisms:
                    logging.error("Server not proposed mechanism `{}'".format(sel_mechanism))
                    self.result = 'no required mechanism'

                else:

                    self._start()

                    logging.debug("Sending SASL mechanism start request")

                    self.status = 'waiting for server sasl response'

                    self._io_machine.send(
                        '<auth xmlns="urn:ietf:params:xml:ns:xmpp-sasl" mechanism="{}"/>'.format(sel_mechanism)
                        )

                    self._exit_event.wait()

            else:

                logging.debug("SASL mechanisms not proposed")

                self.result = 'no mechanisms'

        ret = self.result

        return ret

    def _connection_events_waiter(self, event, sock):

        if self._driving:

            logging.debug("_connection_events_waiter :: `{}' `{}'".format(event, sock))

        return


    def _input_stream_events_waiter(self, event, attrs=None):

        if self._driving:

            logging.debug(
                "_input_stream_events_waiter :: `{}', `{}'".format(
                    event,
                    attrs
                    )
                )

            if event == 'start':

                self.result = 'success'

            elif event == 'stop':

                self.result = 'stream stopped'

            elif event == 'error':

                self.result = 'stream error'

            self._stop()


        return

    def _stream_objects_waiter(self, obj):

        if self._driving:

            logging.debug("_stream_objects_waiter :: `{}'".format(obj))

            if self.status == 'waiting for server sasl response':

                if obj.tag.startswith('{urn:ietf:params:xml:ns:xmpp-sasl}'):

                    if obj.tag == '{urn:ietf:params:xml:ns:xmpp-sasl}challenge':

                        response = self.cb_challenge(obj.text)

                        self._io_machine.send(
                            '<response xmlns="urn:ietf:params:xml:ns:xmpp-sasl">{}</response>'.format(response)
                            )

                    if obj.tag == '{urn:ietf:params:xml:ns:xmpp-sasl}success':

                        threading.Thread(
                            target=self.cb_success,
                            args=(obj.text,),
                            name="SASL auth success signal"
                            ).start()

                        self.result = 'success'

                        logging.debug("Authentication successful")

                        logging.debug("Restarting Machines")
                        self._io_machine.restart_with_new_objects(
                            self._sock_streamer,
                            self._input_stream_events_hub.dispatch,
                            self._input_stream_objects_hub.dispatch,
                            self._output_stream_events_hub.dispatch,
                            None
                            )

                        logging.debug("Waiting machines restart")
                        self._io_machine.wait('working')
                        logging.debug("Machines restarted")

                        logging.debug("Starting new stream")
                        self._io_machine.send(
                            org.wayround.xmpp.core.start_stream(
                                jid_from=self._jid.bare(),
                                jid_to=self._connection_info.host
                                )
                            )

                        self.stop()

                    if obj.tag == '{urn:ietf:params:xml:ns:xmpp-sasl}failure':

                        threading.Thread(
                            target=self.cb_failure,
                            args=(obj.text,),
                            name="SASL auth failure signal"
                            ).start()

                        self.result = 'failure'

                        self.stop()

        return

class ResourceBindClientDriver(org.wayround.xmpp.core.Driver):

    """
    Driver for authenticating client on server
    """

    def __init__(self, jid):

        """
        Initiates object using :meth:`_clear`
        """

        self._jid = jid

        self._clear(init=True)

    def set_objects(
        self,
        sock_streamer,
        io_machine,
        connection_events_hub,
        input_stream_events_hub,
        input_stream_objects_hub,
        output_stream_events_hub,
        stanza_processor
        ):

        """
        Set objects to work with

        :param sock_streamer: instance of class
            :class:`org.wayround.utils.stream.SocketStreamer`

        :param io_machine: instance of class
            :class:`XMPPIOStreamRWMachine`

        :param connection_events_hub: hub to route connection events
            :class:`ConnectionEventsHub`

        :param input_stream_events_hub: hub to route input stream events
            :class:`StreamEventsHub`

        :param output_stream_events_hub: hub to route output stream events
            :class:`StreamEventsHub`

        """

        self._sock_streamer = sock_streamer
        self._io_machine = io_machine
        self._connection_events_hub = connection_events_hub
        self._input_stream_events_hub = input_stream_events_hub
        self._input_stream_objects_hub = input_stream_objects_hub
        self._output_stream_events_hub = output_stream_events_hub
        self._stanza_processor = stanza_processor

    def _clear(self, init=False):
        """
        Clears instance, setting default values for all attributes
        """

        self._sock_streamer = None
        self._io_machine = None
        self._input_stream_events_hub = None
        self._input_stream_objects_hub = None
        self._output_stream_events_hub = None

        self._driving = False
        self._exit_event = threading.Event()
        self._exit_event.clear()

        self.status = 'just created'

        self.result = None

        return

    def _start(self):

        """
        Started by :meth:`self.drive`

        If not already ``self._driving``, then drive!: register own waiters for

        * ``self._connection_events_hub`` - :meth:`_connection_events_waiter`
        * ``self._input_stream_events_hub`` - :meth:`_input_stream_events_waiter`
        * ``self._input_stream_objects_hub`` - :meth:`_stream_objects_waiter`
        """

        if not self._driving:

            self._driving = True

            logging.debug("Resource binding Driver driving now! B-)")

            self._connection_events_hub.set_waiter(
                'resource_binder', self._connection_events_waiter
                )

            self._input_stream_events_hub.set_waiter(
                'resource_binder', self._input_stream_events_waiter
                )


        return


    def _stop(self):

        """
        If ``self._driving``, then stop it. And don't listen hubs any more!
        """

        if self._driving:

            self._connection_events_hub.del_waiter('resource_binder')

            self._input_stream_events_hub.del_waiter('resource_binder')

            logging.debug(
                "Resource binding Driver stopped with result `{}'".format(
                    self.result
                    )
                )

            self._driving = False

            self._exit_event.set()

        return

    def stop(self):

        """
        Stop driver work. Just calls :meth:`_stop`
        """
        self._stop()

        return

    def drive(self, obj):

        if obj.tag == '{http://etherx.jabber.org/streams}features':
            self.status = 'looking for bind feature'

            bind_proposition = obj.find('{urn:ietf:params:xml:ns:xmpp-bind}bind')

            if bind_proposition != None:

                self.status = 'waiting for bind result'

                self._start()


                binding_stanza = org.wayround.xmpp.core.Stanza(
                    kind='iq',
                    typ='set',
                    body=org.wayround.xmpp.core.bind(
                        typ='resource',
                        value=self._jid.resource
                        )
                    )

                stanza_id = self._stanza_processor.send(
                    binding_stanza,
                    cb=self._bind_stanza_callback
                    )

                logging.debug("stanza sending returned: {}".format(stanza_id))

                if not self._exit_event.wait(10000):

                    self.result = 'bind response timeout'
                else:

                    logging.debug("waiting exited with True")

                self._stanza_processor.delete_callback(stanza_id)

            else:

                logging.debug("Server does not proposing resource binding")

                self.result = 'bind not available'

        ret = self.result

        return ret

    def _bind_stanza_callback(self, response):

        if self._driving:

            if self.status == 'waiting for bind result':

                self._stanza_processor.delete_callback(response.ide)

                logging.debug("Received stanza:\n{}".format(response.to_str()))

                if response.typ == 'error':

                    error = org.wayround.xmpp.core.determine_stanza_error(response)

                    if not error:
                        logging.debug("Error determining error")
                        self.result = 'malformed error result'
                    else:
                        logging.debug("Error determined: {}".format(error))
                        self.result = error[1]

                elif response.typ == 'result':

                    bind_elment = response.body.find('{urn:ietf:params:xml:ns:xmpp-bind}bind')

                    if bind_elment == None:
                        self.result = 'malformed bind response'

                    else:
                        jid_element = bind_elment.find('{urn:ietf:params:xml:ns:xmpp-bind}jid')

                        if jid_element == None:
                            self.result = 'malformed bind response'
                        else:
                            result_jid = jid_element.text
                            result_jid = result_jid.strip()

                            logging.debug("Stripped jid {}".format(result_jid))

                            jid = org.wayround.xmpp.core.jid_from_string(result_jid)

                            self._jid.resource = jid.resource

                            self.result = 'success'

                else:
                    self.result = 'malformed error result'

        self.stop()

        return

    def _connection_events_waiter(self, event, sock):

        if self._driving:

            logging.debug("_connection_events_waiter :: `{}' `{}'".format(event, sock))

        return


    def _input_stream_events_waiter(self, event, attrs=None):

        if self._driving:

            logging.debug(
                "_input_stream_events_waiter :: `{}', `{}'".format(
                    event,
                    attrs
                    )
                )

            if event == 'start':

                self.result = 'success'

            elif event == 'stop':

                self.result = 'stream stopped'

            elif event == 'error':

                self.result = 'stream error'

            self._stop()


        return

class SessionClientDriver(org.wayround.xmpp.core.Driver):

    """
    Driver for authenticating client on server
    """

    def __init__(self, jid):

        """
        Initiates object using :meth:`_clear`
        """

        self._jid = jid

        self._clear(init=True)

    def set_objects(
        self,
        sock_streamer,
        io_machine,
        connection_events_hub,
        input_stream_events_hub,
        input_stream_objects_hub,
        output_stream_events_hub,
        stanza_processor
        ):

        """
        Set objects to work with

        :param sock_streamer: instance of class
            :class:`org.wayround.utils.stream.SocketStreamer`

        :param io_machine: instance of class
            :class:`XMPPIOStreamRWMachine`

        :param connection_events_hub: hub to route connection events
            :class:`ConnectionEventsHub`

        :param input_stream_events_hub: hub to route input stream events
            :class:`StreamEventsHub`

        :param output_stream_events_hub: hub to route output stream events
            :class:`StreamEventsHub`

        """

        self._sock_streamer = sock_streamer
        self._io_machine = io_machine
        self._connection_events_hub = connection_events_hub
        self._input_stream_events_hub = input_stream_events_hub
        self._input_stream_objects_hub = input_stream_objects_hub
        self._output_stream_events_hub = output_stream_events_hub
        self._stanza_processor = stanza_processor

    def _clear(self, init=False):
        """
        Clears instance, setting default values for all attributes
        """

        self._sock_streamer = None
        self._io_machine = None
        self._input_stream_events_hub = None
        self._input_stream_objects_hub = None
        self._output_stream_events_hub = None

        self._driving = False
        self._exit_event = threading.Event()
        self._exit_event.clear()

        self.status = 'just created'

        self.result = None

        return

    def _start(self):

        """
        Started by :meth:`self.drive`

        If not already ``self._driving``, then drive!: register own waiters for

        * ``self._connection_events_hub`` - :meth:`_connection_events_waiter`
        * ``self._input_stream_events_hub`` - :meth:`_input_stream_events_waiter`
        * ``self._input_stream_objects_hub`` - :meth:`_stream_objects_waiter`
        """

        if not self._driving:

            self._driving = True

            logging.debug("Resource binding Driver driving now! B-)")

            self._connection_events_hub.set_waiter(
                'resource_binder', self._connection_events_waiter
                )

            self._input_stream_events_hub.set_waiter(
                'resource_binder', self._input_stream_events_waiter
                )


        return

    def _stop(self):

        """
        If ``self._driving``, then stop it. And don't listen hubs any more!
        """

        if self._driving:

            self._connection_events_hub.del_waiter('resource_binder')

            self._input_stream_events_hub.del_waiter('resource_binder')

            logging.debug(
                "Resource binding Driver stopped with result `{}'".format(
                    self.result
                    )
                )

            self._driving = False

            self._exit_event.set()

        return

    def stop(self):

        """
        Stop driver work. Just calls :meth:`_stop`
        """
        self._stop()

        return

    def drive(self, obj):

        if obj.tag == '{http://etherx.jabber.org/streams}features':
            self.status = 'looking for session feature'

            session_proposition = obj.find('{urn:ietf:params:xml:ns:xmpp-session}session')

            if session_proposition != None:

                self.status = 'waiting for session result'

                self._start()


                session_starting_stanza = org.wayround.xmpp.core.Stanza(
                    kind='iq',
                    typ='set',
                    jid_to=self._jid.domain,
                    body=org.wayround.xmpp.core.session()
                    )

                stanza_id = self._stanza_processor.send(
                    session_starting_stanza,
                    cb=self._session_stanza_callback
                    )


                if not self._exit_event.wait(10000):

                    self.result = 'session response timeout'

                self._stanza_processor.delete_callback(stanza_id)

            else:

                logging.debug("Server does not proposing session start")

                self.result = 'session not available'

        ret = self.result

        return ret

    def _session_stanza_callback(self, response):

        if self._driving:

            if self.status == 'waiting for session result':

                self._stanza_processor.delete_callback(response.ide)

                logging.debug("Received stanza:\n{}".format(response.to_str()))

                if response.typ == 'error':

                    error = org.wayround.xmpp.core.determine_stanza_error(response)

                    if not error:
                        logging.debug("Error determining error")
                        self.result = 'malformed error result'
                    else:
                        logging.debug("Error determined: {}".format(error))
                        self.result = error[1]

                elif response.typ == 'result':

                    self.result = 'success'

                else:
                    self.result = 'malformed error result'

        self.stop()

        return

    def _connection_events_waiter(self, event, sock):

        if self._driving:

            logging.debug("_connection_events_waiter :: `{}' `{}'".format(event, sock))

        return


    def _input_stream_events_waiter(self, event, attrs=None):

        if self._driving:

            logging.debug(
                "_input_stream_events_waiter :: `{}', `{}'".format(
                    event,
                    attrs
                    )
                )

            if event == 'start':

                self.result = 'success'

            elif event == 'stop':

                self.result = 'stream stopped'

            elif event == 'error':

                self.result = 'stream error'

            self._stop()


        return
