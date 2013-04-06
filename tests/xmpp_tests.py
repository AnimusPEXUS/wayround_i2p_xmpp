
"""
Test xmpp client implementation. mainly a bot, doing nothing spetial, except
senging some greetings to some jabber users.

This implementation is non-normative, so experimenting and chemistring is on
client and core components is normal.
"""

import logging
import lxml.etree
import socket
import threading


import org.wayround.gsasl.gsasl

import org.wayround.xmpp.core
import org.wayround.xmpp.client
import org.wayround.utils.file

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

class RealClient:

    def __init__(self):

        self._clean(init=True)

    def _clean(self, init=False):

        self._driven = False
        self.connection = False
        self._stream_in = False
        self._stream_out = False
        self._features_recieved = threading.Event()
        self._stop_flag = False

    def run(self):

        fdstw = org.wayround.utils.file.FDStatusWatcher(
            on_status_changed=org.wayround.utils.file.print_status_change
        )

        self.jid = org.wayround.xmpp.core.JID(
            user='test',
            domain='wayround.org',
            resource='home'
            )

        self.connection_info = org.wayround.xmpp.core.C2SConnectionInfo(
            host='wayround.org',
            port=5222,
            )

        self.auth_info = org.wayround.xmpp.core.Authentication(
            service='xmpp',
            hostname='wayround.org',
            authid='test',
            authzid='',
            realm='wayround.org',
            password='Az9bblTgiCQZ9yUAK/WGp9cz4F8='
            )

        self.sock = socket.create_connection(
            (
             self.connection_info.host,
             self.connection_info.port
             )
            )


        logging.debug("Starting socket watcher")
        fdstw.set_fd(self.sock.fileno())
        fdstw.start()

        self.client = org.wayround.xmpp.client.XMPPC2SClient(
            self.sock
            )

        self.reset_hubs()

        self.client.start()

        self.client.wait('working')

        self.stanza_processor = org.wayround.xmpp.core.StanzaProcessor()
        self.stanza_processor.connect_input_object_stream_hub(
            self.client.input_stream_objects_hub
            )
        self.stanza_processor.connect_io_machine(self.client.io_machine)

        self._driven = True

        while True:

            if self._features_recieved.wait(200):
                break

            if self._stop_flag:
                break

        self._features_recieved.clear()

        if not self._stop_flag:

            res = org.wayround.xmpp.client.client_starttls(
                self.client,
                self.jid,
                self.connection_info,
                self._last_features
                )

            if res != 'success':
                pass
            else:

                while True:

                    if self._features_recieved.wait(200):
                        break

                    if self._stop_flag:
                        break

                self._features_recieved.clear()

                if not self._stop_flag:

                    local_auth = AuthLocalDriver(self)
                    local_auth.start()

                    res = org.wayround.xmpp.client.client_sasl_auth(
                        self.client,
                        local_auth.mech_select,
                        local_auth.auth,
                        local_auth.response,
                        local_auth.challenge,
                        local_auth.success,
                        local_auth.failure,
                        local_auth.text,
                        self.jid,
                        self.connection_info,
                        self._last_features
                        )

                    if res != 'success':
                        pass
                    else:

                        while True:

                            if self._features_recieved.wait(200):
                                break

                            if self._stop_flag:
                                break

                        self._features_recieved.clear()

                        if not self._stop_flag:

                            res = org.wayround.xmpp.client.client_resource_bind(
                                self.client,
                                self.jid,
                                self.connection_info,
                                self._last_features,
                                self.stanza_processor
                                )


                            if res == 'success':

                                while True:

                                    if self._features_recieved.wait(200):
                                        break

                                    if self._stop_flag:
                                        break

                                self._features_recieved.clear()

                                if not self._stop_flag:

                                    res = org.wayround.xmpp.client.client_session_start(
                                        self.client,
                                        self.jid,
                                        self.connection_info,
                                        self._last_features,
                                        self.stanza_processor
                                        )


                                    if res == 'success':

                                        self._driven = False

                                        self.stanza_processor.send(
                                            org.wayround.xmpp.core.Stanza(
                                                kind='presence',
                                                jid_from=self.jid.full(),
                                                body='<show>online</show><status>Test status</status>'
                                                )
                                            )

                                        self.stanza_processor.send(
                                            org.wayround.xmpp.core.Stanza(
                                                kind='message',
                                                typ='normal',
                                                jid_from=self.jid.full(),
                                                jid_to='animus@wayround.org',
                                                body='<body>test message</body>'
                                                )
                                            )

                                        try:
                                            self.client.wait('stopped')
                                        except KeyboardInterrupt:
                                            logging.info("Stroke. exiting")
                                        except:
                                            logging.exception("Error")

        self.stop()

        self._driven = False


        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except:
                print("Socket shutdown error. maybe it's closed already")

            try:
                self.sock.close()
            except:
                print("Socket close error")

        logging.debug(
            "Reached the end. socket is {} {}".format(
                self.client.socket,
                self.client.socket._closed
                )
            )

        print("Threads alive3:")
        for i in threading.enumerate():
            print("    {}".format(repr(i)))

        fdstw.stop()

        return 0

    def stop(self):

        self._stop_flag = True

        self.client.stop()


    def reset_hubs(self):

        self.client.connection_events_hub.clear()
        self.client.input_stream_events_hub.clear()
        self.client.input_stream_objects_hub.clear()
        self.client.output_stream_events_hub.clear()

        self.client.connection_events_hub.set_waiter(
            'main', self._on_connection_event,
            )

        self.client.input_stream_events_hub.set_waiter(
            'main', self._on_stream_in_event,
            )

        self.client.input_stream_objects_hub.set_waiter(
            'main', self._on_stream_object,
            )

        self.client.output_stream_events_hub.set_waiter(
            'main', self._on_stream_out_event,
            )

    def _on_connection_event(self, event, sock):

        self.socket = sock

        if not self._driven:

            logging.debug("_on_connection_event `{}', `{}'".format(event, sock))

            if event == 'start':
                print("Connection started")

                self.connection = True

                self.client.wait('working')

                logging.debug("Ended waiting for connection. Opening output stream")


                self.client.io_machine.send(
                    org.wayround.xmpp.core.start_stream(
                        jid_from=self.jid.bare(),
                        jid_to=self.connection_info.host
                        )
                    )

                logging.debug("Stream opening tag was started")

            elif event == 'stop':
                print("Connection stopped")
                self.connection = False
                self.stop()

            elif event == 'error':
                print("Connection error")
                self.connection = False
                self.stop()


    def _on_stream_in_event(self, event, attrs=None):

        if not self._driven:

            logging.debug("Stream in event `{}' : `{}'".format(event, attrs))

            if event == 'start':

                self._stream_in = True

            elif event == 'stop':
                self._stream_in = False
                self.stop()

            elif event == 'error':
                self._stream_in = False
                self.stop()

    def _on_stream_out_event(self, event, attrs=None):

        if not self._driven:

            logging.debug("Stream out event `{}' : `{}'".format(event, attrs))

            if event == 'start':

                self._stream_out = True

            elif event == 'stop':
                self._stream_out = False
                self.stop()

            elif event == 'error':
                self._stream_out = False
                self.stop()

    def _on_stream_object(self, obj):

        logging.debug("_on_stream_object (first 255 bytes):`{}'".format(repr(lxml.etree.tostring(obj)[:255])))

        if obj.tag == '{http://etherx.jabber.org/streams}features':

            self._last_features = obj

            self._features_recieved.set()


logging.basicConfig(level='DEBUG', format="%(levelname)s :: %(threadName)s :: %(message)s")

exit(RealClient().run())
