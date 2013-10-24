
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
import org.wayround.utils.types

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

    'stanza_processor_new_stanza' (self, stanza)
    'stanza_processor_response_stanza' (self, stanza)
    """

    def __init__(self, socket):
        """
        :param socket.socket socket:
        """

        self.socket = socket

        self.sock_streamer = org.wayround.utils.stream.SocketStreamer(
            self.socket,
            socket_transfer_size=4096,
            debug=False
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

        self.stanza_processor = org.wayround.xmpp.core.StanzaProcessor()
        self.stanza_processor.connect_io_machine(self.io_machine)
        self.stanza_processor.connect_signal(
            True,
            self._stanza_processor_proxy
            )

        super().__init__(
            self.sock_streamer.get_signal_names(add_prefix='streamer_') +
            self.io_machine.get_signal_names(add_prefix='io_') +
            self.stanza_processor.get_signal_names(
                add_prefix='stanza_processor_'
                )
            )

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

        if (not self._starting
            and not self._stopping
            and self.stat() == 'stopped'):

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

        if (not self._stopping
            and not self._starting
            and self.stat() == 'working'):
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
                    logging.debug(
                        "Input stream closed - ending shutdown timout"
                        )
                    break

                logging.debug(
                    "Timeout in {:3.2f} sec".format(timeout_sec - time_waited)
                    )
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

    def _stanza_processor_proxy(self, event, stanza_processor, stanza):
        self.emit_signal('stanza_processor_' + event, stanza_processor, stanza)


def can_drive_starttls(features_element):

    if not org.wayround.xmpp.core.is_features_element(features_element):
        raise ValueError("`features_element' must features element")

    return features_element.find(
        '{urn:ietf:params:xml:ns:xmpp-tls}starttls'
        ) != None


def drive_starttls(
    client,
    features_element,
    bare_from_jid,
    bare_to_jid,
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

    ret = None

    if not isinstance(client, XMPPC2SClient):
        raise TypeError("`client' must be of type XMPPC2SClient")

    if not org.wayround.xmpp.core.is_features_element(features_element):
        raise ValueError("`features_element' must features element")

    if not isinstance(bare_from_jid, str):
        raise TypeError("`bare_from_jid' must be str")

    if not isinstance(bare_to_jid, str):
        raise TypeError("`bare_to_jid' must be str")

    if not callable(controller_callback):
        raise ValueError("`controller_callback' must be callable")

    if not can_drive_starttls(features_element):
        ret = 'invalid features'

    if not isinstance(ret, str):

        logging.debug("STARTTLS routines beginning now")

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
            lxml.etree.tostring(
                org.wayround.xmpp.core.STARTTLS().gen_element()
                )
            )

        logging.debug("POP")
        c_r_w_result = client_reactions_waiter.pop()
        logging.debug("POP!")

        if not isinstance(c_r_w_result, dict):
            ret = 'error'
            logging.debug("POP exited with error")

    if not isinstance(ret, str):
        if c_r_w_result['event'] != 'io_in_element_readed':
            ret = 'invalid server action 1'
            logging.debug(ret)

    if not isinstance(ret, str):

        obj = c_r_w_result['args'][1]

        if not obj.tag.startswith('{urn:ietf:params:xml:ns:xmpp-tls}'):
            ret = 'invalid server action 2'
            logging.debug(ret)

    if not isinstance(ret, str):
        if not obj.tag == '{urn:ietf:params:xml:ns:xmpp-tls}proceed':
            ret = 'invalid server action 3'
            logging.debug(ret)

    if not isinstance(ret, str):

        logging.debug(
            "TLS request successful: proceed signal achieved"
            )
        logging.debug("Calling streamer to wrap socket with TLS")

        client.sock_streamer.start_ssl()

        logging.debug("POP")
        c_r_w_result = client_reactions_waiter.pop()
        logging.debug("POP!")

        if not isinstance(c_r_w_result, dict):
            ret = 'error'

    if not isinstance(ret, str):
        if c_r_w_result['event'] != 'streamer_ssl wrapped':
            ret = 'error'
            logging.debug(
                ("Some other stream event when "
                "`streamer_ssl wrapped': {}").format(c_r_w_result['event'])
                )

    if not isinstance(ret, str):

        logging.debug("Restarting IO Machine")
        client.io_machine.restart()

        if not client.io_machine.stat() == 'working':
            ret = 'error'
            logging.debug("IO Machine restart failed")

    if not isinstance(ret, str):

        logging.debug("IO Machine restarted")
        logging.debug("Starting new stream")

        client.io_machine.send(
            org.wayround.xmpp.core.start_stream_tpl(
                from_jid=bare_from_jid,
                to_jid=bare_to_jid
                )
            )

        logging.debug("POP")
        c_r_w_result = client_reactions_waiter.pop()
        logging.debug("POP!")

        if not isinstance(c_r_w_result, dict):
            ret = 'error'
            logging.debug("POP exited with error")

    if not isinstance(ret, str):
        if c_r_w_result['event'] != 'io_in_start':
            ret = 'invalid server action 4'
            logging.debug(ret)

    if not isinstance(ret, str):

        logging.debug("IO Machine inbound stream start signal received")
        logging.debug("Waiting for features")

        logging.debug("POP")
        c_r_w_result = client_reactions_waiter.pop()
        logging.debug("POP!")

        if not isinstance(c_r_w_result, dict):
            ret = 'error'
            logging.debug("POP exited with error")

    if not isinstance(ret, str):
        if c_r_w_result['event'] != 'io_in_element_readed':
            ret = 'invalid server action 4'
            logging.debug(ret)

    if not isinstance(ret, str):

        logging.debug("Received some element, analizing...")

        obj = c_r_w_result['args'][1]

        if not org.wayround.xmpp.core.is_features_element(obj):
            ret = 'error'
            logging.debug(
                "Server must been give us an stream features, but it's not"
                )

    if not isinstance(ret, str):
        logging.debug(
            "Stream features recognized. Time success to driver caller"
            )
        ret = obj

    client_reactions_waiter.stop()

    logging.debug("STARTTLS exit point reached")

    return ret


def can_drive_sasl(features_element, controller_callback):

    if not org.wayround.xmpp.core.is_features_element(features_element):
        raise ValueError("`features_element' must features element")

    if not callable(controller_callback):
        raise ValueError("`controller_callback' must be callable")

    ret = False

    mechanisms_element = features_element.find(
        '{urn:ietf:params:xml:ns:xmpp-sasl}mechanisms'
        )

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

        mechanism_name = controller_callback(
            'mechanism_name',
            {'mechanisms': mechanisms}
            )

        if mechanism_name in mechanisms:
            ret = True

    return ret


def drive_sasl(
    client,
    features_element,
    bare_from_jid,
    bare_to_jid,
    controller_callback
    ):

    ret = 'error'

    if not isinstance(client, XMPPC2SClient):
        raise TypeError("`client' must be of type XMPPC2SClient")

    if not org.wayround.xmpp.core.is_features_element(features_element):
        raise ValueError("`features_element' must features element")

    if not isinstance(bare_from_jid, str):
        raise TypeError("`bare_from_jid' must be str")

    if not isinstance(bare_to_jid, str):
        raise TypeError("`bare_to_jid' must be str")

    if not callable(controller_callback):
        raise ValueError("`controller_callback' must be callable")

    if not can_drive_starttls(features_element):
        ret = 'invalid features'
    else:

        mechanism_name = controller_callback('mechanism_name', None)

        logging.debug("SASL routines beginning now")

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

        logging.debug("Sending SASL mechanism start request")

        client.io_machine.send(
            ('<auth xmlns="urn:ietf:params:xml:ns:xmpp-sasl" '
            'mechanism="{}"/>').format(
                mechanism_name
                )
            )

        chall_failed = False

        while True:

            c_r_w_result = client_reactions_waiter.pop()

            if not isinstance(c_r_w_result, dict):
                ret = 'error'
                logging.debug("POP exited with error")
            else:
                if c_r_w_result['event'] != 'io_in_element_readed':
                    ret = 'invalid server action 1'
                    logging.debug(ret)
                else:

                    logging.debug("Received Some Element. Analyzing...")

                    obj = c_r_w_result['args'][1]

                    if (obj.tag ==
                        '{urn:ietf:params:xml:ns:xmpp-sasl}challenge'):

                        response = controller_callback(
                            'challenge', {'text': obj.text}
                            )

                        client.send(
                            ('<response xmlns="urn:ietf:params:xml:ns'
                             ':xmpp-sasl">'
                            '{}</response>').format(response)
                            )

                    elif (obj.tag ==
                            '{urn:ietf:params:xml:ns:xmpp-sasl}success'
                            ):
                        break
                    else:
                        chall_failed = True
                        break

        if chall_failed:
            ret = 'error'
            logging.debug("Received `{}' - so it's and error".format(obj.tag))
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
                        from_jid=bare_from_jid,
                        to_jid=bare_to_jid
                        )
                    )

                logging.debug("POP")
                c_r_w_result = client_reactions_waiter.pop()
                logging.debug("POP!")

                if not isinstance(c_r_w_result, dict):
                    ret = 'error'
                    logging.debug("POP exited with error")
                else:
                    ret = 'invalid server action 4'
                    if c_r_w_result['event'] == 'io_in_start':

                        logging.debug(
                            "IO Machine inbound stream start signal received"
                            )
                        logging.debug("Waiting for features")

                        logging.debug("POP")
                        c_r_w_result = client_reactions_waiter.pop()
                        logging.debug("POP!")

                        if not isinstance(c_r_w_result, dict):
                            ret = 'invalid server action 5'
                            logging.debug("POP exited with error")

                    if c_r_w_result['event'] == 'io_in_element_readed':

                        logging.debug("Received some element, analizing...")

                        obj = c_r_w_result['args'][1]

                        if not org.wayround.xmpp.core.is_features_element(obj):
                            ret = 'invalid server action 6'
                            logging.debug(
                                "Server must been give us an stream features, "
                                "but it's not"
                                )
                        else:
                            logging.debug(
                                "Stream features recognized. "
                                "Time to return success to driver caller"
                                )
                            ret = obj

        client_reactions_waiter.stop()

        logging.debug("STARTTLS exit point reached")

    return ret


def bind(client, resource=None, wait=True):

    """
    Driver for resource binding

    returns either resulted jid either determine_stanza_error() result

    if returned stanza has wrong stracture - None is returned
    """

    if not isinstance(client, XMPPC2SClient):
        raise TypeError("`client' must be a XMPPC2SClient")

    if resource and not isinstance(resource, str):
        raise TypeError("`resource' must be a str")

    binding_stanza = org.wayround.xmpp.core.Stanza(
        tag='iq',
        typ='set',
        objects=[org.wayround.xmpp.core.Bind(
            typ='resource',
            value=resource
            )]
        )

    ret = client.stanza_processor.send(
        binding_stanza,
        wait=wait
        )

    if isinstance(ret, org.wayround.xmpp.core.Stanza):
        if ret.is_error():
            ret = ret.gen_error()
        else:

            bind_tag = ret.get_element().find(
                '{urn:ietf:params:xml:ns:xmpp-bind}bind'
                )
            ret = None

            if bind_tag != None:

                jid_tag = bind_tag.find(
                    '{urn:ietf:params:xml:ns:xmpp-bind}jid'
                    )

                if jid_tag != None:

                    ret = jid_tag.text
                    ret = ret.strip()

    return ret


def session(client, to_jid, wait=True):

    """
    Driver for starting session. This is required by old protocol version
    (rfc 3920)
    """
    if not isinstance(client, XMPPC2SClient):
        raise TypeError("`client' must be a XMPPC2SClient")

    if to_jid and not isinstance(to_jid, str):
        raise TypeError("`resource' must be a str")

    session_starting_stanza = org.wayround.xmpp.core.Stanza(
        tag='iq',
        typ='set',
        to_jid=to_jid,
        objects=[org.wayround.xmpp.core.Session()]
        )

    ret = client.stanza_processor.send(
        session_starting_stanza,
        wait=wait
        )

    return ret

class Roster(org.wayround.utils.signal.Signal):

    """
    Signals:
    push_invalid (self, stanza) - stanza is normal core Stanza object
    push (self, roster_data)
    push_invalid_from (self, roster_data)


    roster_data - dict with key(jid) and dict of information:

    {
    'jid@example.org',
     {
        'groups':       set,
        'approved':     bool,
        'ask':          str,
        'name':         str,
        'subscription': str
        }
    }

    get result - dict with many keys(jids) each of which is corresponds to dict
    of information

    {
    'jid@example.org': {
        'groups':       set,
        'approved':     bool,
        'ask':          str,
        'name':         str,
        'subscription': str
        },
    'jid2@example.org': {
        'groups':       set,
        'approved':     bool,
        'ask':          str,
        'name':         str,
        'subscription': str
        }
    }
    """

    def __init__(self, client, client_jid):

        if not isinstance(client, XMPPC2SClient):
            raise TypeError("`client' must be of type XMPPC2SClient")

        if not isinstance(client_jid, org.wayround.xmpp.core.JID):
            raise TypeError(
                "`client_jid' must be of type org.wayround.xmpp.core.JID"
                )

        self.client = client
        self.client_jid = client_jid

        super().__init__(['push', 'push_invalid', 'push_invalid_from'])

        self.client.connect_signal('stanza_processor_new_stanza', self._push)

    def _item_element_to_dict(self, element):

        data = {
            'groups':       set(),
            'approved':     element.get('approved') == 'true',
            'ask':          element.get('ask'),
            'name':         element.get('name'),
            'subscription': element.get('subscription')
            }

        for j in element.findall('{jabber:iq:roster}group'):
            data['groups'].add(j.text)

        return element.get('jid'), data

    def get(self, from_jid=None, to_jid=None, wait=None):
        """
        :param str from_jid:
        :param str to_jid:
        """

        ret = None

        query = org.wayround.xmpp.core.IQRoster()

        stanza = org.wayround.xmpp.core.Stanza(
            tag='iq',
            from_jid=from_jid,
            to_jid=to_jid,
            typ='get',
            objects=[
                query
                ]
            )

        res = self.client.stanza_processor.send(
            stanza,
            wait=wait
            )

        if not isinstance(res, org.wayround.xmpp.core.Stanza):
            ret = None
        else:
            if res.is_error():
                ret = res
            else:

                query = res.get_element().find('{jabber:iq:roster}query')

                if query != None:
                    ret = org.wayround.xmpp.core.IQRoster.new_from_element(
                        query
                        )

                    ret = ret.get_item_dict()

        return ret

    def set(
        self,
        to_jid=False,
        from_jid=False,
        subject_jid=None,
        groups=None,
        name=None,
        subscription=None,
        wait=None
        ):

        """
        :param str from_jid:
        :param str to_jid:

        no 'approved', 'ask' parameters: read RFC-6121 and use subscription
        functionality
        """

        ret = None

        query = org.wayround.xmpp.core.IQRoster()

        item = org.wayround.xmpp.core.IQRosterItem()

        item.set_subscription(subscription)
        item.set_name(name)
        item.set_jid(subject_jid)
        item.set_groups(groups)

        query.set_item([item])

        if to_jid == False:
            to_jid = self.client_jid.bare()

        if from_jid == False:
            from_jid = self.client_jid.full()

        stanza = org.wayround.xmpp.core.Stanza(
            tag='iq',
            from_jid=from_jid,
            to_jid=to_jid,
            typ='set',
            objects=[
                query
                ]
            )

        res = self.client.stanza_processor.send(
            stanza,
            wait=wait
            )

        if not isinstance(res, org.wayround.xmpp.core.Stanza):
            ret = None
        else:
            if res.is_error():
                ret = res.gen_error()
            else:
                ret = True

        return ret

    def _push(self, event, stanza_processor, stanza):

        error = False

        wrong_from = False
        if (not stanza.get_from_jid()
            or stanza.get_from_jid() == self.client_jid.bare()):
            wrong_from = False
        else:
            wrong_from = True

        roster_data = None

        query = stanza.get_element().find('{jabber:iq:roster}query')

        if query == None:
            error = True
        else:

            try:
                roster = org.wayround.xmpp.core.IQRoster.new_from_element(
                    query
                    )
            except:
                roster_data = None
                error = True
            else:
                roster_data = roster.get_item_dict()

        if error:
            self.emit_signal('push_invalid', self, stanza)
        else:

            if wrong_from:
                self.emit_signal('push_invalid_from', self, roster_data)
            else:
                self.emit_signal('push', self, roster_data)

        return


class Presence(org.wayround.utils.signal.Signal):

    """
    Presence and subscription manipulations

    Since both subscription and presence using one stanza tag ('presence'),
    both of them are grouped in single class with same name - 'Presence'

    Signals:
        'subscribe', 'unsubscribe',
        'subscribed', 'unsubscribed',
        'presence'
        (self, stanza.from_jid, stanza.to_jid, stanza)

        'error' (self, stanza)
    """

    def __init__(self, client, client_jid):

        if not isinstance(client, XMPPC2SClient):
            raise TypeError("`client', must be of type XMPPC2SClient")

        if not isinstance(client_jid, org.wayround.xmpp.core.JID):
            raise TypeError(
                "`client_jid' must be of type org.wayround.xmpp.core.JID"
                )

        self.client = client
        self.client_jid = client_jid

        super().__init__([
            'presence', 'error',
            'subscription',
            ])

        self.client.connect_signal(
            'stanza_processor_new_stanza',
            self._in_stanza
            )

    def presence(
        self,
        to_full_or_bare_jid=None,
        typ=None,
        show=None,
        status=None,
        wait=False
        ):

        if to_full_or_bare_jid and not isinstance(to_full_or_bare_jid, str):
            raise TypeError("`to_bare_jid' must be a str")

        if not typ in [None, 'error', 'probe', 'subscribe', 'subscribed',
                       'unavailable', 'unsubscribe', 'unsubscribed']:
            raise ValueError("Invalid `typ' value")

        if not show in [None, 'away', 'chat', 'dnd', 'xa']:
            raise ValueError("Invalid `show' value")

        if status and not isinstance(status, str):
            raise ValueError("`status' must be str or None")

        stanza = org.wayround.xmpp.core.Stanza(
            tag='presence',
            from_jid=self.client_jid.bare(),
            to_jid=to_full_or_bare_jid
            )

        if typ:
            stanza.set_typ(typ)

        if show:
            stanza.set_show(org.wayround.xmpp.core.PresenceShow(show))

        if status:
            stanza.set_status([org.wayround.xmpp.core.PresenceStatus(status)])

        ret = self.client.stanza_processor.send(stanza, wait=wait)

        return ret

    def subscribe(self, to_bare_jid, show=None, status=None, wait=False):
        """
        Shortcut to presence method
        """
        ret = self.presence(
            to_full_or_bare_jid=to_bare_jid,
            typ='subscribe',
            show=show,
            status=status,
            wait=wait
            )
        return ret

    def unsubscribe(self, to_bare_jid, show=None, status=None, wait=False):
        """
        Shortcut to presence method
        """
        ret = self.presence(
            to_full_or_bare_jid=to_bare_jid,
            typ='unsubscribe',
            show=show,
            status=status,
            wait=wait
            )
        return ret

    def subscribed(self, to_bare_jid, show=None, status=None, wait=False):
        """
        Shortcut to presence method
        """
        ret = self.presence(
            to_full_or_bare_jid=to_bare_jid,
            typ='subscribed',
            show=show,
            status=status,
            wait=wait
            )
        return ret

    def unsubscribed(self, to_bare_jid, show=None, status=None, wait=False):
        """
        Shortcut to presence method
        """
        ret = self.presence(
            to_full_or_bare_jid=to_bare_jid,
            typ='unsubscribed',
            show=show,
            status=status,
            wait=wait
            )
        return ret

    def probe(self, to_full_or_bare_jid, wait=False):

        ret = self.presence(
            to_full_or_bare_jid,
            typ='probe',
            show=None,
            status=None,
            wait=wait
            )

        return ret

    def _in_stanza(self, event, client, stanza):

        """
        :param org.wayround.xmpp.core.Stanza stanza:
        """

        if event == 'stanza_processor_new_stanza':

            if stanza.get_tag() == 'presence':

                if stanza.is_error():

                    self.emit_signal('error', self, stanza)

                else:

                    self.emit_signal(
                        'presence',
                        self,
                        stanza.get_from_jid(),
                        stanza.get_to_jid(),
                        stanza
                        )

        return


class Message(org.wayround.utils.signal.Signal):

    def __init__(self, client, client_jid):

        if not isinstance(client, XMPPC2SClient):
            raise TypeError("`client', must be of type XMPPC2SClient")

        if not isinstance(client_jid, org.wayround.xmpp.core.JID):
            raise TypeError(
                "`client_jid' must be of type org.wayround.xmpp.core.JID"
                )

        self.client = client
        self.client_jid = client_jid

        super().__init__([
            'message', 'error'
            ])

        self.client.connect_signal(
            'stanza_processor_new_stanza',
            self._in_stanza
            )

    def message(
        self,
        to_jid=None, from_jid=None, typ=None, thread=None, subject=None,
        body=None, wait=False
        ):

        if not typ in [
            None, 'normal', 'chat', 'groupchat', 'headline', 'error'
            ]:
            raise ValueError("Wrong `typ' value")

        if to_jid == False:
            to_jid = self.client_jid.bare()

        if from_jid == False:
            from_jid = self.client_jid.full()

        stanza = org.wayround.xmpp.core.Stanza(
            tag='message',
            to_jid=to_jid,
            typ=typ
            )

        stanza.set_thread(org.wayround.xmpp.core.MessageThread(thread))
        stanza.set_subject([org.wayround.xmpp.core.MessageSubject(subject)])
        stanza.set_body([org.wayround.xmpp.core.MessageBody(body)])

        ret = self.client.stanza_processor.send(stanza, wait=wait)

        return ret

    def _in_stanza(self, event, client, stanza):

        """
        :param org.wayround.xmpp.core.Stanza stanza:
        """

        if event == 'stanza_processor_new_stanza':

            if stanza.get_tag() == 'message':

                if stanza.is_error():

                    self.emit_signal('error', self, stanza)

                else:

                    self.emit_signal(
                        'message',
                        self,
                        stanza
                        )

        return
