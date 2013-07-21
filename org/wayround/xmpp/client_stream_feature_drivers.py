
import logging
import threading

import org.wayround.xmpp.core



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
        self.controller_callback = None
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

    def set_controller(self, controller_callback):

        """
        controller_callback must be a callable with following parameters:

            - this object reference
            - status
            - dict with additional status specific data

            must return True, False. return None in case of error

        """

        self.controller_callback = controller_callback

    def can_drive(self, obj):
        return (org.wayround.xmpp.core.is_features_element(obj)
            and obj.find('{urn:ietf:params:xml:ns:xmpp-tls}starttls') != None)

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

        if self.can_drive(obj):

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
        jid,
        connection_info,
        mechanism_name
        ):

        """
        Initiates object using :meth:`_clear`
        """
        self._jid = jid
        self._connection_info = connection_info
        self.mechanism_name = mechanism_name

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

        self.controller_callback = None
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

    def set_controller(self, controller_callback):

        """
        controller_callback must be a callable with following parameters:

            - this object reference
            - status. possible statuses are:
                'auth',
                'response',
                'challenge',
                'success',
                'failure',
                'text'
            - dict with additional status specific data

            must return True, False. return None in case of error

        """

        self.controller_callback = controller_callback

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
    Driver for binding resource
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

        self.controller_callback = None
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

    def can_drive(self, obj):
        return (org.wayround.xmpp.core.is_features_element(obj) and
            obj.find('{urn:ietf:params:xml:ns:xmpp-bind}bind') != None)

    def drive(self, obj):

        if not self.can_drive(obj):
            self.result = 'bind not available'
        else:

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
    Driver for starting session. This is required by old protocol version
    (rfc 3920)
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

        self.controller_callback = None
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

    def can_drive(self, obj):
        return (org.wayround.xmpp.core.is_features_element(obj) and
            obj.find('{urn:ietf:params:xml:ns:xmpp-session}session') != None)

    def drive(self, obj):

        if not self.can_drive(obj):
            self.result = 'session not available'
        else:

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
