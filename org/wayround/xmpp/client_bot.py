
"""
XMPP bot
"""

import logging
import socket
import threading

import lxml.etree
import org.wayround.gsasl.gsasl
import org.wayround.utils.file
import org.wayround.utils.program
import org.wayround.utils.shlex
import org.wayround.xmpp.client
import org.wayround.xmpp.core


class AuthLocalDriver:

    def __init__(self, real_client):

        self.real_client = real_client

        self._result_ready = threading.Event()
        self._result_ready.clear()

        self.result = 'clean'

        self._simple_gsasl = None

    def start(self):

        if not self._simple_gsasl:
            self._simple_gsasl = org.wayround.gsasl.gsasl.GSASLSimple(
                mechanism='DIGEST-MD5',
                callback=self._gsasl_cb
                )

    def wait(self):

        self._result_ready.wait()

        return self.result

    def wait_abort(self):
        self.result = 'error'
        self._result_ready.set()
        return

    def mech_select(self, mechanisms):

        ret = None

        if 'DIGEST-MD5' in mechanisms:
            ret = 'DIGEST-MD5'

        return ret

    def auth(self, mechanism):
        pass

    def response(self, text):
        pass

    def challenge(self, text):

        res = self._simple_gsasl.step64(text)

        if res[0] == org.wayround.gsasl.gsasl.GSASL_OK:
            pass
        elif res[0] == org.wayround.gsasl.gsasl.GSASL_NEEDS_MORE:
            pass
        else:
            raise Exception(
                "step64 returned error: {}".format(
                    org.wayround.gsasl.gsasl.strerror_name(res[0])
                    )
                )

        ret = str(res[1], 'utf-8')

        return ret

    def success(self, text):

        self.result = 'success'
        self._result_ready.set()

    def failure(self, name, text):

        self.result = 'failure'
        self._result_ready.set()

    def text(self):
        pass

    def _gsasl_cb(self, context, session, prop):
        ret = org.wayround.gsasl.gsasl.GSASL_OK

        logging.debug(
            "SASL client requested for: {} ({}) {}".format(
                org.wayround.gsasl.gsasl.strproperty_name(prop),
                prop,
                org.wayround.gsasl.gsasl.strproperty(prop)
                )
            )

        if prop == org.wayround.gsasl.gsasl.GSASL_QOP:

            server_allowed_qops = str(
                session.property_get(
                    org.wayround.gsasl.gsasl.GSASL_QOPS
                    ),
                'utf-8'
                ).split(',')

            value = ''
            if not 'qop-auth' in server_allowed_qops:
                value = ''
            else:
                value = 'qop-auth'

            session.property_set(
                org.wayround.gsasl.gsasl.GSASL_QOP,
                bytes(value, 'utf-8')
                )

        elif prop == org.wayround.gsasl.gsasl.GSASL_AUTHID:

            value = None
            if self.real_client.auth_info.authid:
                value = bytes(self.real_client.auth_info.authid, 'utf-8')

            session.property_set(prop, value)

        elif prop == org.wayround.gsasl.gsasl.GSASL_SERVICE:

            value = None
            if self.real_client.auth_info.service:
                value = bytes(self.real_client.auth_info.service, 'utf-8')

            session.property_set(prop, value)

        elif prop == org.wayround.gsasl.gsasl.GSASL_HOSTNAME:

            value = None
            if self.real_client.auth_info.hostname:
                value = bytes(self.real_client.auth_info.hostname, 'utf-8')

            session.property_set(prop, value)

        elif prop == org.wayround.gsasl.gsasl.GSASL_REALM:

            value = None
            if self.real_client.auth_info.realm:
                value = bytes(self.real_client.auth_info.realm, 'utf-8')

            session.property_set(prop, value)

        elif prop == org.wayround.gsasl.gsasl.GSASL_AUTHZID:

            value = None
            if self.real_client.auth_info.authzid:
                value = bytes(self.real_client.auth_info.authzid, 'utf-8')

            session.property_set(prop, value)

        elif prop == org.wayround.gsasl.gsasl.GSASL_PASSWORD:

            value = None
            if self.real_client.auth_info.password:
                value = bytes(self.real_client.auth_info.password, 'utf-8')

            session.property_set(prop, value)

        else:
            logging.error("Requested SASL property not available")
            ret = 1

        return ret


class Bot:

    def __init__(self):

        """
        :param org.wayround.pyabber.main.ProfileSession profile:
        """

        self.self_disco_info = org.wayround.xmpp.disco.IQDisco(mode='info')

        self.self_disco_info.set_identity(
            [
             org.wayround.xmpp.disco.IQDiscoIdentity(
                'client', 'bot', 'simplybot'
                )
             ]
            )

        self.clear(init=True)

        return

    def clear(self, init=False):

        self._simple_gsasl = None
        self.auth_info = None
        self.client = None
        self.connection_info = None
        self.is_driven = False
        self.jid = None
        self.message_client = None
        self.presence_client = None
        self.privacy_client = None
        self.roster_client = None
        self.roster_storage = None
        self.sock = None

        if init:
            self._disconnection_flag = threading.Event()
        else:
            self._disconnection_flag.clear()

        self._incomming_message_lock = threading.RLock()

    def set_commands(self, commands):
        self._commands = commands

    def connect(self, jid, connection_info, auth_info):

        ret = 0

        if not isinstance(jid, org.wayround.xmpp.core.JID):
            raise TypeError(
                "`jid' must be of type org.wayround.xmpp.core.JID"
                )

        self.disconnect()

        self.jid = jid

        self.connection_info = connection_info

        self.auth_info = auth_info

        self.sock = socket.create_connection(
            (
             self.connection_info.host,
             self.connection_info.port
             )
            )

        # make non-blocking socket
        self.sock.settimeout(0)

        self.client = org.wayround.xmpp.client.XMPPC2SClient(
            self.sock
            )

        self.message_client = org.wayround.xmpp.client.Message(
            self.client,
            self.jid
            )

        self.roster_client = org.wayround.xmpp.client.Roster(
            self.client,
            self.jid
            )

        self.presence_client = org.wayround.xmpp.client.Presence(
            self.client,
            self.jid
            )

        self.client.sock_streamer.signal.connect(
            ['start', 'stop', 'error'],
            self._on_connection_event
            )

        logging.debug("streamer connected")

        self.client.io_machine.signal.connect(
            ['in_start', 'in_stop', 'in_error',
             'out_start', 'out_stop', 'out_error'],
            self._on_stream_io_event
            )

        features_waiter = org.wayround.utils.threading.SignalWaiter(
            self.client.signal,
            'features'
            )
        features_waiter.start()

        self.is_driven = True

        self.client.start(
            from_jid=self.jid.bare(),
            to_jid=self.connection_info.host
            )
        self.client.wait('working')

        res = None

        if ret == 0:

            features = features_waiter.pop()
            features_waiter.stop()

            if features == None:
                logging.error(
                    "Timedout waiting for initial server features"
                    )
                ret = 1
            else:
                last_features = features['args'][1]

        if (not self._disconnection_flag.is_set()
            and ret == 0):

            logging.debug("Starting TLS")

            res = org.wayround.xmpp.client.drive_starttls(
                self.client,
                last_features,
                self.jid.bare(),
                self.connection_info.host,
                self._auto_starttls_controller
                )

            if not org.wayround.xmpp.core.is_features_element(res):
                logging.debug("Can't establish TLS encryption")
                ret = 2
            else:
                logging.debug("Encryption established")
                last_features = res

        if (not self._disconnection_flag.is_set()
            and ret == 0):

            logging.debug("Logging in")

            if not self._simple_gsasl:
                self._simple_gsasl = (
                    org.wayround.gsasl.gsasl.GSASLSimple(
                        mechanism='DIGEST-MD5',
                        callback=self._gsasl_cb
                        )
                    )

            logging.debug(
                "Passing following features to sasl driver:\n{}".format(
                    lxml.etree.tostring(last_features)
                    )
                )

            res = org.wayround.xmpp.client.drive_sasl(
                self.client,
                last_features,
                self.jid.bare(),
                self.connection_info.host,
                self._auto_auth_controller
                )

            self._simple_gsasl = None

            if not org.wayround.xmpp.core.is_features_element(res):
                logging.debug("Can't authenticate: {}".format(res))
                ret = 3
            else:
                logging.debug("Authenticated")
                last_features = res

        if (not self._disconnection_flag.is_set()
            and ret == 0):

            res = org.wayround.xmpp.client.bind(
                self.client,
                self.jid.resource
                )
            if not isinstance(res, str):
                logging.debug("bind error {}".format(res.gen_error()))
                ret = 4
            else:
                self.jid.update(
                    org.wayround.xmpp.core.JID.new_from_str(res)
                    )
                logging.debug(
                    "Bound jid is: {}".format(self.jid.full())
                    )

        if (not self._disconnection_flag.is_set()
            and ret == 0):

            logging.debug("Starting session")

            res = org.wayround.xmpp.client.session(
                self.client,
                self.jid.domain
                )

            if (not isinstance(res, org.wayround.xmpp.core.Stanza)
                or res.is_error()):
                logging.debug("Session establishing error")
                ret = 5
            else:
                logging.debug("Session established")

        if (not self._disconnection_flag.is_set()
            and ret == 0):

            self.message_client.signal.connect(
                ['message'], self._on_message
                )

            self.presence_client.presence()

            logging.info("XMPP bot connected")

        self.is_driven = False

        if ret != 0:
            logging.info("error connecting XMPP bot")
            threading.Thread(
                target=self.disconnect,
                name="Disconnecting by connection error"
                ).start()

        return ret

    def disconnect(self):
        if not self._disconnection_flag.is_set():
            self._disconnection_flag.set()

            if self.client != None:

                self.client.stop()
                logging.debug("Now waiting for client to stop...")
                self.client.wait('stopped')

                sock = self.client.get_socket()

                logging.debug("Shutting down socket")
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except:
                    logging.exception(
                        "Can't shutdown socket. Maybe it's already dead"
                        )

                logging.debug("Closing socket object")
                try:
                    sock.close()
                except:
                    logging.exception(
                        "Can't close socket. Maybe it's already dead"
                        )

            self.clear()

    def _on_connection_event(self, event, streamer, sock):

        if not self.is_driven:

            logging.debug(
                "_on_connection_event `{}', `{}'".format(event, sock)
                )

            if event == 'start':
                logging.debug("Connection started")

            elif event == 'stop':
                logging.debug("Connection stopped")
                self.disconnect()

            elif event == 'error':
                logging.debug("Connection error")
                self.disconnect()

        return

    def _on_stream_io_event(self, event, io_machine, attrs=None):

        if not self.is_driven:

            logging.debug("Stream io event `{}' : `{}'".format(event, attrs))

            if event == 'in_start':
                pass

            elif event == 'in_stop':
                self.disconnect()

            elif event == 'in_error':
                self.disconnect()

            elif event == 'out_start':
                pass

            elif event == 'out_stop':
                self.disconnect()

            elif event == 'out_error':
                self.disconnect()

        return

    def _auto_starttls_controller(self, status, data):

        logging.debug("_auto_starttls_controller {}, {}".format(status, data))

        ret = None

        raise ValueError("status `{}' not supported".format(status))

        return ret

    def _auto_auth_controller(self, status, data):

        ret = ''

        logging.debug("_auto_auth_controller {}, {}".format(status, data))

        if status == 'mechanism_name':
            ret = 'DIGEST-MD5'

        elif status == 'bare_from_jid':
            ret = self.jid.bare()

        elif status == 'bare_to_jid':
#            TODO: fix self.connection_info.host
            ret = self.connection_info.host

        elif status == 'sock_streamer':
            ret = self.client.sock_streamer

        elif status == 'io_machine':
            ret = self.client.io_machine

        elif status == 'challenge':
            res = self._simple_gsasl.step64(data['text'])

            if res[0] == org.wayround.gsasl.gsasl.GSASL_OK:
                pass
            elif res[0] == org.wayround.gsasl.gsasl.GSASL_NEEDS_MORE:
                pass
            else:
                # TODO: this is need to be hidden
                raise Exception(
                    "step64 returned error: {}".format(
                        org.wayround.gsasl.gsasl.strerror_name(res[0])
                        )
                    )

            ret = str(res[1], 'utf-8')

        elif status == 'success':
            pass

        else:
            raise ValueError("status `{}' not supported".format(status))

        return ret

    def _gsasl_cb(self, context, session, prop):

        # TODO: maybe all this method need to be separated and standardized

        ret = org.wayround.gsasl.gsasl.GSASL_OK

        logging.debug(
            "SASL client requested for: {} ({}) {}".format(
                org.wayround.gsasl.gsasl.strproperty_name(prop),
                prop,
                org.wayround.gsasl.gsasl.strproperty(prop)
                )
            )

        if prop == org.wayround.gsasl.gsasl.GSASL_QOP:

            server_allowed_qops = str(
                session.property_get(
                    org.wayround.gsasl.gsasl.GSASL_QOPS
                    ),
                'utf-8'
                ).split(',')

            value = ''
            if not 'qop-auth' in server_allowed_qops:
                value = ''
            else:
                value = 'qop-auth'

            session.property_set(
                org.wayround.gsasl.gsasl.GSASL_QOP,
                bytes(value, 'utf-8')
                )

        elif prop == org.wayround.gsasl.gsasl.GSASL_AUTHID:

            value = None
            if self.auth_info.authid:
                value = bytes(self.auth_info.authid, 'utf-8')

            session.property_set(prop, value)

        elif prop == org.wayround.gsasl.gsasl.GSASL_SERVICE:

            value = None
            if self.auth_info.service:
                value = bytes(self.auth_info.service, 'utf-8')

            session.property_set(prop, value)

        elif prop == org.wayround.gsasl.gsasl.GSASL_HOSTNAME:

            value = None
            if self.auth_info.hostname:
                value = bytes(self.auth_info.hostname, 'utf-8')

            session.property_set(prop, value)

        elif prop == org.wayround.gsasl.gsasl.GSASL_REALM:

            value = None
            if self.auth_info.realm:
                value = bytes(self.auth_info.realm, 'utf-8')

            session.property_set(prop, value)

        elif prop == org.wayround.gsasl.gsasl.GSASL_AUTHZID:

            value = None
            if self.auth_info.authzid:
                value = bytes(self.auth_info.authzid, 'utf-8')

            session.property_set(prop, value)

        elif prop == org.wayround.gsasl.gsasl.GSASL_PASSWORD:

            value = None
            if self.auth_info.password:
                value = bytes(self.auth_info.password, 'utf-8')

            session.property_set(prop, value)

        else:
            logging.error("Requested SASL property not available")
            ret = 1

        return ret

    def _on_message(self, event, message_client, stanza):
        self._inbound_stanzas(stanza)

    def _inbound_stanzas(self, obj):

        if not isinstance(obj, org.wayround.xmpp.core.Stanza):
            raise TypeError("`obj' must be org.wayround.xmpp.core.Stanza inst")

        if obj.get_tag() == 'message' and obj.get_typ() == 'chat':

            # FIXME: get_body()[0] - is incorrect
            cmd_line = org.wayround.utils.shlex.split(
                obj.get_body()[0].get_text().splitlines()[0]
                )

            if len(cmd_line) == 0:
                pass
            else:

                messages = []

                ret_stanza = org.wayround.xmpp.core.Stanza(
                    from_jid=self.jid.bare(),
                    to_jid=obj.get_from_jid(),
                    tag='message',
                    typ='chat',
                    body=[
                        org.wayround.xmpp.core.MessageBody(
                            text=''
                            )
                        ]
                    )

                asker_jid = org.wayround.xmpp.core.JID.new_from_str(
                    obj.get_from_jid()
                    ).bare()

                res = org.wayround.utils.program.command_processor(
                    command_name=None,
                    commands=self._commands,
                    opts_and_args_list=cmd_line,
                    additional_data={
                        'asker_jid': asker_jid,
                        'stanza': obj,
                        'messages': messages,
                        'ret_stanza': ret_stanza
                        }
                    )

                messages_text = ''

                for i in messages:

                    typ = i['type']
                    text = i['text']

                    messages_text += '[{typ}]: {text}\n'.format(
                        typ=typ,
                        text=text
                        )

                for i in ret_stanza.get_body():

                    if isinstance(i, org.wayround.xmpp.core.MessageBody):

                        t = ''

                        if messages_text != '':
                            t += messages_text
                            t += '\n'

                        tt = i.get_text()
                        if tt != '':
                            t += tt
                            t += '\n'

                        tt = res['message']
                        if tt != '':
                            t += tt
                            t += '\n'

                        t += 'Exit Code: {}\n'.format(res['code'])

                        i.set_text(t)

                        break

                self.client.stanza_processor.send(ret_stanza)
