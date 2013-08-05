
"""
XMPP client class to be used by users
"""

import logging
import select
import threading
import time

import lxml.etree

import org.wayround.utils.stream
import org.wayround.utils.signal

import org.wayround.xmpp.core


class XMPPC2SClient(org.wayround.utils.signal.Signal):
    """
    General XMPP Client Class

    It presumed to be used in implementing xmpp functionalities

    Signals: following signals are proxyfied:

    'streamer_start' (self, self.socket)
    'streamer_stop' (self, self.socket)
    'streamer_error' (self, self.socket)
    'streamer_restart' (self, self.socket)
    'streamer_ssl wrap error' (self, self.socket)
    'streamer_ssl wrapped' (self, self.socket)
    'streamer_ssl ununwrapable' (self, self.socket)
    'streamer_ssl unwrap error' (self, self.socket)
    'streamer_ssl unwrapped' (self, self.socket)


    'io_in_start'(self, attrs=attributes)
    'io_in_error' (self, attrs=attributes)
    'io_in_element_readed' (self, element)
    'io_in_stop' (self, attrs=attributes)

    'io_out_start'(self, attrs=attributes)
    'io_out_error' (self, attrs=attributes)
    'io_out_element_readed' (self, element)
    'io_out_stop' (self, attrs=attributes)
    """

    def __init__(self, socket):
        """
        :param socket.socket socket:
        """

        self.socket = socket

        self.sock_streamer = org.wayround.utils.stream.SocketStreamer(
            self.socket,
            socket_transfer_size=4096
            )

        self.sock_streamer.connect_signal(
            True,
            self._connection_event_proxy
            )

        self.io_machine = org.wayround.xmpp.core.XMPPIOStreamRWMachine()

        self.io_machine.set_objects(self.sock_streamer)

        self.io_machine.connect_signal(
            True,
            self._io_event_proxy
            )


        super().__init__(
            self.sock_streamer.get_signal_names(add_prefix='streamer_') +
            self.io_machine.get_signal_names(add_prefix='io_')
            )

        print("Client supported signals: {}".format(self.get_signal_names()))

        self._clear(init=True)

    def _clear(self, init=False):

        if not init:
            if not self.stat() == 'stopped':
                raise RuntimeError("Working. Cleaning restricted")

        self._starting = False
        self._stopping = False
        self._stream_stop_sent = False
        self._input_stream_closed_event = threading.Event()


    def start(self):

        if not self._starting and not self._stopping and self.stat() == 'stopped':

            self._starting = True

            ######### SOCKET

            logging.debug('sock is {}'.format(self.socket))

            ######### STREAMS

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

                self.io_machine.connect_signal(
                    'in_stop',
                    self._input_stream_close_waiter
                    )

                logging.debug("Sending end of stream")
                self.io_machine.send(
                    org.wayround.xmpp.core.stop_stream_tpl()
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

            self.io_machine.disconnect_signal(self._input_stream_close_waiter)

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

    def restart(self):
        self.io_machine.restart()

    def send(self, data):
        threading.Thread(
            target=self.io_machine.send,
            args=(data,)
            ).start()


    def _start_io_machine(self):
        self.io_machine.start()

    def _stop_io_machine(self):
        if self.io_machine:
            self.io_machine.stop()

    def _restart_io_machine(self):
        self._stop_io_machine()
        self._start_io_machine()

    def _input_stream_close_waiter(self, signal_name, io_machine, attrs):

        self._input_stream_closed_event.set()

    def _connection_event_proxy(self, event, streamer, sock):
        self.emit_signal('streamer_' + event, streamer, sock)

    def _io_event_proxy(self, event, io_machine, attrs):
        self.emit_signal('io_' + event, io_machine, attrs)

def can_drive_starttls(features_element):

    if not org.wayround.xmpp.core.is_features_element(features_element):
        raise ValueError("`features_element' must features element")

    return features_element.find('{urn:ietf:params:xml:ns:xmpp-tls}starttls') != None

def drive_starttls(
    client,
    features_element,
    bare_jid_from,
    bare_jid_to,
    controller_callback
    ):

    """
    Drives to STARTTLS, basing on ``features_element``, which must be an XML
    element instance with features.

    If ``features_element.tag`` is
    ``{http://etherx.jabber.org/streams}features`` and it is contains
    ``{urn:ietf:params:xml:ns:xmpp-tls}starttls`` element, then:

    #. switch ``self.status`` to ``'requesting tls'``

    #. run :meth:`_start`

    #. start STARTTLS sequence sending starttls element

    #. wait while ``self._driving`` == True

    #. return ``self.result``

    :rtype: ``str``

    controller_callback will be used in questionable situations, for
    instance: when certificate need to be checked, in which case user
    interaction may be needed

    Return can be one of following values:

    =================== ============================================
    value               meaning
    =================== ============================================
    'no tls'            TLS not proposed by server
    features_object     TLS layer engaged
    'stream stopped'    stream was closed by server
    'stream error'      some stream error encountered
    'failure'           server returned
                        ``{urn:ietf:params:xml:ns:xmpp-tls}failure``
    'response error'    wrong server response
    'programming error' if you received this - mail me a bug report
    =================== ============================================
    """

    # TODO: update help

    if not isinstance(client, XMPPC2SClient):
        raise TypeError("`client' must be of type XMPPC2SClient")

    if not org.wayround.xmpp.core.is_features_element(features_element):
        raise ValueError("`features_element' must features element")

    if not isinstance(bare_jid_from, str):
        raise TypeError("`bare_jid_from' must be str")

    if not isinstance(bare_jid_to, str):
        raise TypeError("`bare_jid_to' must be str")

    if not callable(controller_callback):
        raise ValueError("`controller_callback' must be callable")

    if not can_drive_starttls(features_element):
        ret = 'invalid features'
    else:

        logging.debug("STARTTLS routines begining now")

        logging.debug("Connecting SignalWaiter")

        client_reactions_waiter = org.wayround.utils.signal.SignalWaiter(
            client,
            list(
                set(client.get_signal_names())
                - set(
                      ['io_out_element_readed',
                       'io_out_start',
                       'io_out_stop'
                       # NOTE: 'io_out_error' not needed here
                       ])
                ),
            debug=True
            )

        client_reactions_waiter.start()

        logging.debug("Sending STARTTLS request")

        client.send(
            org.wayround.xmpp.core.starttls_tpl()
            )

        logging.debug("POP")
        c_r_w_result = client_reactions_waiter.pop(timeout=3)
        logging.debug("POP!")

        if not isinstance(c_r_w_result, dict):
            ret = 'error'
            logging.debug("POP exited with error")
        else:
            if c_r_w_result['event'] != 'io_in_element_readed':
                ret = 'invalid server action 1'
                logging.debug(ret)
            else:

                obj = c_r_w_result['args'][1]

                if not obj.tag.startswith('{urn:ietf:params:xml:ns:xmpp-tls}'):
                    ret = 'invalid server action 2'
                    logging.debug(ret)
                else:
                    if not obj.tag == '{urn:ietf:params:xml:ns:xmpp-tls}proceed':
                        ret = 'invalid server action 3'
                        logging.debug(ret)
                    else:

                        logging.debug("Calling streamer to wrap socket with TLS")

                        client.sock_streamer.start_ssl()

                        logging.debug("POP")
                        c_r_w_result = client_reactions_waiter.pop()
                        logging.debug("POP!")

                        if not isinstance(c_r_w_result, dict):
                            ret = 'error'
                        else:
                            if c_r_w_result['event'] != 'streamer_ssl wrapped':
                                ret = 'error'
                                logging.debug("Some other stream event when `streamer_ssl wrapped': {}".format(c_r_w_result['event']))
                            else:

                                logging.debug("Restarting IO Machine")
                                client.io_machine.restart()

                                if not client.io_machine.stat() == 'working':
                                    ret = 'error'
                                    logging.debug("IO Machine restart failed")
                                else:

                                    logging.debug("IO Machine restarted")
                                    logging.debug("Starting new stream")

                                    client.io_machine.send(
                                        org.wayround.xmpp.core.start_stream_tpl(
                                            jid_from=bare_jid_from,
                                            jid_to=bare_jid_to
                                            )
                                        )


                                    logging.debug("POP")
                                    c_r_w_result = client_reactions_waiter.pop()
                                    logging.debug("POP!")

                                    if not isinstance(c_r_w_result, dict):
                                        ret = 'error'
                                        logging.debug("POP exited with error")
                                    else:
                                        if c_r_w_result['event'] != 'io_in_start':
                                            ret = 'invalid server action 4'
                                            logging.debug(ret)
                                        else:

                                            logging.debug("IO Machine inbound stream start signal received")
                                            logging.debug("Waiting for features")

                                            logging.debug("POP")
                                            c_r_w_result = client_reactions_waiter.pop()
                                            logging.debug("POP!")

                                            if not isinstance(c_r_w_result, dict):
                                                ret = 'error'
                                                logging.debug("POP exited with error")
                                            else:
                                                if c_r_w_result['event'] != 'io_in_element_readed':
                                                    ret = 'invalid server action 4'
                                                    logging.debug(ret)
                                                else:

                                                    logging.debug("Received some element, analizing...")

                                                    obj = c_r_w_result['args'][1]

                                                    if not org.wayround.xmpp.core.is_features_element(obj):
                                                        ret = 'error'
                                                        logging.debug("Server must been give us an stream features, but it's not")
                                                    else:
                                                        logging.debug("Stream features recognized. Time to return success to driver caller")
                                                        ret = obj

        client_reactions_waiter.stop()

        logging.debug("STARTTLS exit point reached")

    return ret




class SASLClientDriver(org.wayround.xmpp.core.Driver):

    """
    Driver for authenticating client on server
    """

    def __init__(self, controller_callback):

        """
        Initiates object using :meth:`_clear`

        _controller_callback must be a callable with following parameters:

            - this object reference
            - status. possible statuses are:
                possible statuses:

                    corresponding instances needed:
                    'sock_streamer'
                    'io_machine'
                    'connection_events_hub'
                    'input_stream_events_hub'
                    'input_stream_objects_hub'
                    'output_stream_events_hub'

                    others:
                    'auth',

                        TODO: can't remember probably same as 'response'

                    'response',

                        server responses to client (this is to be used in server
                        implementations)

                    'challenge',
                        server asks controller

                        data: 'text' - string with challenge
                        return: string with response

                    'success',
                        auth is ok

                        return value does not matter

                    'failure',
                        auth failed
                        data:
                            'condition': text
                            'text': None or str

                        return value does not matter

                    'mechanism_name'
                        must return string containing name of one of client
                        mechanisms supported by GSASL

                    'bare_jid_from'

                    'bare_jid_to'

            - dict with additional status specific data
        """

        self._controller_callback = controller_callback
        self._clear(init=True)


    def _set_objects(self):

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

        self._sock_streamer = self._controller_callback(
            self, 'sock_streamer', None
            )

        self._io_machine = self._controller_callback(
            self, 'io_machine', None
            )

        self._connection_events_hub = self._controller_callback(
            self, 'connection_events_hub', None
            )

        self._input_stream_events_hub = self._controller_callback(
            self, 'input_stream_events_hub', None)

        self._input_stream_objects_hub = self._controller_callback(
            self, 'input_stream_objects_hub', None
            )

        self._output_stream_events_hub = self._controller_callback(
            self, 'output_stream_events_hub', None
            )

        return

    def _clear(self, init=False):
        """
        Clears instance, setting default values for all attributes
        """

        self.mechanism_name = None
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

            self._set_objects()

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

    def can_drive(self, obj):

        ret = False

        if org.wayround.xmpp.core.is_features_element(obj):

            mechanisms_element = obj.find('{urn:ietf:params:xml:ns:xmpp-sasl}mechanisms')

            if mechanisms_element != None:

                mechanisms = mechanisms_element.findall(
                    '{urn:ietf:params:xml:ns:xmpp-sasl}mechanism'
                    )

                _mechanisms = []
                for i in mechanisms:
                    _mechanisms.append(i.text)

                mechanisms = _mechanisms


                logging.debug("Proposed mechanisms are:")
                for i in mechanisms:
                    logging.debug("    {}".format(i))

                self.mechanism_name = self._controller_callback(self, 'mechanism_name', None)
                sel_mechanism = self.mechanism_name

                if sel_mechanism in mechanisms:
                    ret = True

        return ret

    def drive(self, obj):

        if not self.can_drive(obj):
            self.result = "can't drive"
        else:

            self._start()

            logging.debug("Sending SASL mechanism start request")

            self.status = 'waiting for server sasl response'

            self._io_machine.send(
                '<auth xmlns="urn:ietf:params:xml:ns:xmpp-sasl" mechanism="{}"/>'.format(
                    self.mechanism_name
                    )
                )

            self._exit_event.wait()

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

                self._stop()

            elif event == 'error':

                self.result = 'stream error'

                self._stop()


        return

    def _stream_objects_waiter(self, obj):

        if self._driving:

            logging.debug("_stream_objects_waiter :: `{}'".format(obj))

            if org.wayround.xmpp.core.is_features_element(obj):
                logging.error("SASL driver received stream features")
                self.result = obj
                self._stop()
            else:

                if self.status == 'waiting for server sasl response':

                    if obj.tag.startswith('{urn:ietf:params:xml:ns:xmpp-sasl}'):

                        if obj.tag == '{urn:ietf:params:xml:ns:xmpp-sasl}challenge':

                            response = self._controller_callback(
                                self, 'challenge', {'text': obj.text}
                                )

                            self._io_machine.send(
                                '<response xmlns="urn:ietf:params:xml:ns:xmpp-sasl">{}</response>'.format(response)
                                )

                        elif obj.tag == '{urn:ietf:params:xml:ns:xmpp-sasl}success':

                            threading.Thread(
                                target=self._controller_callback,
                                args=(self, 'success', None,),
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
                                org.wayround.xmpp.core.start_stream_tpl(
                                    jid_from=self._controller_callback(
                                        self, 'bare_jid_from', None
                                        ),
                                    jid_to=self._controller_callback(
                                        self, 'bare_jid_to', None
                                        )
                                    )
                                )

#                            self.stop()

                        elif obj.tag == '{urn:ietf:params:xml:ns:xmpp-sasl}failure':

                            condition = None
                            text = None
                            for i in obj:

                                print("condition tag: {}".format(i.tag))

                                if i.tag != 'text':
                                    condition = i.tag
                                    break

                            for i in obj:

                                print("condition tag: {}".format(i.tag))

                                if i.tag == 'text':
                                    text = i.text
                                    break

                            threading.Thread(
                                target=self._controller_callback,
                                args=(
                                    self,
                                    'failure',
                                    {'condition':condition,
                                     'text': text
                                     },
                                      ),
                                name="SASL auth failure signal"
                                ).start()

                            self.result = 'failure'

                            self.stop()

        return

def bind(stanza_processor, resource=None, wait=True):

    """
    Driver for resource binding

    returns either resulted jid either determine_stanza_error() result

    if returned stanza has wrong stracture - None is returned
    """

    binding_stanza = org.wayround.xmpp.core.Stanza(
        kind='iq',
        typ='set',
        body=org.wayround.xmpp.core.bind_tpl(
            typ='resource',
            value=resource
            )
        )

    ret = stanza_processor.send(
        binding_stanza,
        wait=wait
        )

    if org.wayround.xmpp.core.is_stanza(ret):
        if ret.is_error():
            ret = ret.determine_error()
        else:

            bind_tag = ret.body.find('{urn:ietf:params:xml:ns:xmpp-bind}bind')
            ret = None

            if bind_tag != None:

                jid_tag = bind_tag.find('{urn:ietf:params:xml:ns:xmpp-bind}jid')

                if jid_tag != None:

                    ret = jid_tag.text
                    ret = ret.strip()


    return ret

def session(stanza_processor, jid_to, wait=True):

    """
    Driver for starting session. This is required by old protocol version
    (rfc 3920)
    """

    session_starting_stanza = org.wayround.xmpp.core.Stanza(
        kind='iq',
        typ='set',
        jid_to=jid_to,
        body=org.wayround.xmpp.core.session_tpl()
        )

    ret = stanza_processor.send(
        session_starting_stanza,
        wait=wait
        )

    return ret

class Roster:

    def __init__(self, client):

        self.client = client

    def get(self, jid_from, jid_to, stanza_processor, wait=None):
        """
        :param org.wayround.xmpp.core.StanzaProcessor stanza_processor:
        :param str jid_from:
        :param str jid_to:
        """

        ret = None

        query = lxml.etree.Element()
        query.set('xmlns', 'jabber:iq:roster')

        stanza = org.wayround.xmpp.core.Stanza(
            kind='iq',
            jid_from=jid_from,
            jid_to=jid_to,
            typ='get',
            body=[
                query
                ]
            )

        res = stanza_processor.send(
            stanza,
            wait=wait
            )

        if not org.wayround.xmpp.core.is_stanza(res):
            ret = None
        else:
            if res.is_error():
                ret = res.determine_error()
            else:
                ret = {}

                query = res.body.find('{jabber:iq:roster}query')

                for i in query:
                    if i.tag == 'item':

                        jid = i.get('jid')

                        if not jid in ret:
                            ret[jid] = {
                                'groups':set(),
                                'approved': None,
                                'ask': None,
                                'name': None,
                                'subscription': None
                                }

                        groups = set()

                        for j in i.findall('group'):
                            groups.add(j.text)

                        ret[jid]['groups'] = groups
