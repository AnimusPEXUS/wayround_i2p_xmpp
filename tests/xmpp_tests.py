
"""
Test xmpp client implementation. mainly a bot, doing nothing spetial, except
senging some greetings to some jabber users.

This implementation is non-normative, so experimenting and chemistring is on
client and core components is normal.
"""

import logging
import lxml.etree
import socket


import org.wayround.xmpp.core
import org.wayround.xmpp.client
import org.wayround.utils.file

class AuthLocalDriver:

    def __init__(self):
        pass

    def start(self):

        self._simple_gsasl = org.wayround.gsasl.gsasl.GSASLSimple(
            mechanism='DIGEST-MD5',
            callback=self._gsasl_cb
            )

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
        pass

    def success(self, text):
        pass

    def failure(self, name, text):
        pass

    def text(self):
        pass

    def join(self):
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
            pass
        elif prop == org.wayround.gsasl.gsasl.GSASL_QOP:
            pass
        elif prop == org.wayround.gsasl.gsasl.GSASL_QOP:
            pass
        elif prop == org.wayround.gsasl.gsasl.GSASL_QOP:
            pass
        elif prop == org.wayround.gsasl.gsasl.GSASL_QOP:
            pass
        elif prop == org.wayround.gsasl.gsasl.GSASL_QOP:
            pass
        else:
            value = input('input value->')
            session.property_set(prop, bytes(value, 'utf-8'))

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

        self.features_drivers = [
            org.wayround.xmpp.core.STARTTLSClientDriver(
                self.connection_info,
                self.jid
                )
        #    org.wayround.xmpp.core.SASLClientDriver()
            ]

        logging.debug("Starting socket watcher")
        fdstw.set_fd(self.sock.fileno())
        fdstw.start()

        self.client = org.wayround.xmpp.client.XMPPC2SClient(
            self.sock
            )

        self.client.start()

        try:
            self.client.wait('stopped')
        except:
            logging.exception("Error")



        self.client.stop()

        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except:
                print("Socket shutdown error")

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

        fdstw.stop()

        return 0

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

                self.wait('working')

                logging.debug("Ended waiting for connection. Opening output stream")


                self.io_machine.send(
                    org.wayround.xmpp.core.start_stream(
                        fro=self.jid.bare(),
                        to=self.connection_info.host
                        )
                    )

                logging.debug("Stream opening tag was started")

            elif event == 'stop':
                print("Connection stopped")
                self.connection = False
                self.client.stop()

            elif event == 'error':
                print("Connection error")
                self.connection = False
                self.client.stop()


    def _on_stream_in_event(self, event, attrs=None):

        if not self._driven:

            logging.debug("Stream in event `{}' : `{}'".format(event, attrs))

            if event == 'start':

                self._stream_in = True

            elif event == 'stop':
                self._stream_in = False
                self.client.stop()

            elif event == 'error':
                self._stream_in = False
                self.client.stop()

    def _on_stream_out_event(self, event, attrs=None):

        if not self._driven:

            logging.debug("Stream out event `{}' : `{}'".format(event, attrs))

            if event == 'start':

                self._stream_out = True

            elif event == 'stop':
                self._stream_out = False
                self.client.stop()

            elif event == 'error':
                self._stream_out = False
                self.client.stop()

    def _on_stream_object(self, obj):

        logging.debug("_on_stream_object (first 255 bytes):`{}'".format(repr(lxml.etree.tostring(obj)[:255])))

        if obj.tag == '{http://etherx.jabber.org/streams}features':

            self._last_features = obj

            if not self._driven:

                self._driven = True

                self._start_drivers()

    def _start_drivers(self):

        for i in self.features_drivers:

            i.set_objects(
                self.sock_streamer,
                self.io_machine,
                self.connection_events_hub,
                self.input_stream_events_hub,
                self.input_stream_objects_hub,
                self.output_stream_events_hub,
                )

            res = i.drive(self._last_features)

            if res != 'success':
                logging.error("Driver `{}' failed to drive features".format(i.__name__))
                break

logging.basicConfig(level='DEBUG', format="%(levelname)s :: %(threadName)s :: %(message)s")

exit(RealClient().run())
