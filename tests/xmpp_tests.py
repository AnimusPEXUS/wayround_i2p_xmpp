
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

        self._cell_seq = 0

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

        ret = ''

        if self._cell_seq == 0:
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
        pass

    def run(self):

        self._driven = False
        self.connection = False
        self._stream_in = False
        self._stream_out = False

        fdstw = org.wayround.utils.file.FDStatusWatcher(
            on_status_changed=org.wayround.utils.file.print_status_change
        )

        self.jid = org.wayround.xmpp.core.JID(
            user='test',
            domain='wayround.org'
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

        self.local_auth_drv = AuthLocalDriver(self)
        self.local_auth_drv.start()

        self.features_drivers = [
            org.wayround.xmpp.core.STARTTLSClientDriver(
                self.jid,
                self.connection_info
                ),

            org.wayround.xmpp.core.SASLClientDriver(
                cb_mech_select=self.local_auth_drv.mech_select,
                cb_auth=self.local_auth_drv.auth,
                cb_response=self.local_auth_drv.response,
                cb_challenge=self.local_auth_drv.challenge,
                cb_success=self.local_auth_drv.success,
                cb_failure=self.local_auth_drv.failure,
                cb_text=self.local_auth_drv.text,
                jid=self.jid,
                connection_info=self.connection_info
                )
            ]

        logging.debug("Starting socket watcher")
        fdstw.set_fd(self.sock.fileno())
        fdstw.start()

        self.client = org.wayround.xmpp.client.XMPPC2SClient(
            self.sock
            )

        self.reset_hubs()

        self.client.start()

        print("Threads alive1:")
        for i in threading.enumerate():
            print("    {}".format(repr(i)))

        try:
            self.client.wait('stopped')
        except KeyboardInterrupt:
            logging.info("Stroke. exiting")
        except:
            logging.exception("Error")


        print("Threads alive2:")
        for i in threading.enumerate():
            print("    {}".format(repr(i)))

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

        for i in self.features_drivers:
            i.stop()

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
                        fro=self.jid.bare(),
                        to=self.connection_info.host
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

            if not self._driven:

                self._driven = True

                self._start_drivers()

    def _start_drivers(self):

        for i in self.features_drivers:

            logging.debug("Preparing Driver `{}'".format(type(i).__name__))

            i.set_objects(
                self.client.sock_streamer,
                self.client.io_machine,
                self.client.connection_events_hub,
                self.client.input_stream_events_hub,
                self.client.input_stream_objects_hub,
                self.client.output_stream_events_hub,
                )

            logging.debug("Starting Driver  `{}'".format(type(i).__name__))

            res = i.drive(self._last_features)

            if res != 'success':
                logging.error("Driver `{}' failed with result: {}".format(type(i).__name__, res))
                break



logging.basicConfig(level='DEBUG', format="%(levelname)s :: %(threadName)s :: %(message)s")

exit(RealClient().run())
