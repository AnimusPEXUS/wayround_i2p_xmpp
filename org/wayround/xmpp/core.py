
import copy
import logging
import threading
import time
import re

import xml.sax.saxutils
import lxml.etree

import org.wayround.utils.error
import org.wayround.utils.stream
import org.wayround.utils.xml
import org.wayround.utils.signal


STREAM_ERROR_NAMES = [
    'bad-format',
    'bad-namespace-prefix',
    'conflict',
    'connection-timeout',
    'host-gone',
    'host-unknown',
    'improper-addressing',
    'internal-server-error',
    'invalid-from',
    'invalid-namespace',
    'invalid-xml',
    'not-authorized',
    'not-well-formed',
    'policy-violation',
    'remote-connection-failed',
    'reset',
    'resource-constraint',
    'restricted-xml',
    'see-other-host',
    'system-shutdown',
    'undefined-condition',
    'unsupported-encoding',
    'unsupported-feature',
    'unsupported-stanza-type',
    'unsupported-version'
    ]

SASL_ERRORS = [
    'aborted',
    'account-disabled',
    'credentials-expired',
    'encryption-required',
    'incorrect-encoding',
    'invalid-authzid',
    'invalid-mechanism',
    'malformed-request',
    'mechanism-too-weak',
    'not-authorized',
    'temporary-auth-failure'
    ]

STANZA_ERROR_NAMES = [
    'bad-request',
    'conflict',
    'feature-not-implemented',
    'forbidden',
    'gone',
    'internal-server-error',
    'item-not-found',
    'jid-malformed',
    'not-acceptable',
    'not-allowed',
    'not-authorized',
    'policy-violation',
    'recipient-unavailable',
    'redirect',
    'registration-required',
    'remote-server-not-found',
    'remote-server-timeout',
    'resource-constraint',
    'service-unavailable',
    'subscription-required',
    'undefined-condition',
    'unexpected-request'
    ]

class XMPPStreamSoftError:

    """
    Soft stream errors are 'Stream Errors' described in rfc6120
    """

    def __init__(self, name, message):
        self.name = name
        self.message = message

class JID:

    """
    Class for working with JID

    Domain and user parts are automatically converted to low register

    """

    def __init__(self, user='name', domain='domain', resource=None):

        self._values = {}

        if not isinstance(user, str):
            raise TypeError("`user' must be str")

        if not isinstance(domain, str):
            raise TypeError("`domain' must be str")


        self.user = user
        self.domain = domain
        self.resource = resource


    def __str__(self):
        return self.full()

    @property
    def user(self):
        return self._get('user')

    @user.setter
    def user(self, value):
        self._set('user', value)

    @property
    def domain(self):
        return self._get('domain')

    @domain.setter
    def domain(self, value):
        self._set('domain', value)

    @property
    def resource(self):
        return self._get('resource')

    @resource.setter
    def resource(self, value):
        self._values['resource'] = str(value)

    def _set(self, name, value):
        if value:
            self._values[name] = str(value).lower()
        else:
            self._values[name] = None

    def _get(self, name):

        ret = None

        if name in self._values:
            ret = self._values[name]

        return ret

    def bare(self):
        return '{user}@{domain}'.format(
            user=self.user,
            domain=self.domain
            )

    def full(self):
        return '{user}@{domain}/{resource}'.format(
            user=self.user,
            domain=self.domain,
            resource=self.resource or 'default'
            )

    def make_connection_info(self):
        """
        Tries to guess C2SConnectionInfo for current JID

        Some properties needs to be changed manually.
        """
        return C2SConnectionInfo(host=self.domain)

    def make_authentication(self):
        """
        Tries to guess Authentication for current JID

        Some properties needs to be changed manually.
        """
        return Authentication(
            service='xmpp',
            hostname=self.domain,
            authid=self.user,
            authzid=None,
            realm=self.domain,
            password=None
            )

class Authentication:

    def __init__(
        self,
        service='xmpp',
        hostname='localhost',
        authid='',
        authzid='',
        realm='',
        password=''
        ):

        self.service = service
        self.hostname = hostname
        self.authid = authid
        self.authzid = authzid
        self.realm = realm
        self.password = password

class C2SConnectionInfo:

    def __init__(
        self,
        host='localhost',
        port=5222,
        priority='default'
        ):

        self.host = host
        self.port = port
        self.priority = priority


class XMPPStreamParserTargetClosed(Exception):
    """
    This exception is rased in case of some one's trying to send some more data
    to parsed when it is closed already.
    """

class XMPPStreamParserTarget:

    """
    Target for lxml to build XML objects, which then sent to element hubs or
    stream event listeners
    """

    def __init__(
        self,
        on_stream_event=None,
        on_element_readed=None
        ):

        """
        :param on_stream_event: callback to call when stream starts, stops or
            fails (hard xml stream error. at this time, xml errors are separate
            from xmpp error. xmpp errors are recognised and generated by
            XMPPIOStreamRWMachine class)
        :param on_element_readed: callback to call when next stream element read
            complete
        """

        self._on_stream_event = on_stream_event
        self._on_element_readed = on_element_readed

        self.clear(init=True)

        return


    def clear(self, init=False):

        self._tree_builder = None
        self._tree_builder_start_depth = None

        self._depth_tracker = []
        self._stream_element = None

        self.target_closed = False

        return


    def start(self, name, attributes):

        """
        Target receiving tag starts
        """

        logging.debug(
            "{} :: start tag: `{}'; attrs: {}".format(
                type(self).__name__,
                name,
                attributes
                )
            )

        if self.target_closed:
            raise XMPPStreamParserTargetClosed()

        if name == '{http://etherx.jabber.org/streams}stream':
            self._depth_tracker = []
            self._stream_element = lxml.etree.Element(name, attrib=attributes)


        if len(self._depth_tracker) == 0:

            if name == '{http://etherx.jabber.org/streams}stream':
                if self._on_stream_event:
                    threading.Thread(
                        target=self._on_stream_event,
                        args=('start',),
                        kwargs={'attrs': attributes},
                        name="Stream Start Thread"
                        ).start()

            else:
                if self._on_stream_start_error:
                    threading.Thread(
                        target=self._on_stream_event,
                        args=('error',),
                        kwargs={'attrs':None},
                        name="Stream Start Error Thread"
                        ).start()

        else:

            if not self._tree_builder:

                self._tree_builder = lxml.etree.TreeBuilder()

            _l = len(self._depth_tracker)

            if _l == 1:
                self._tree_builder.start(
                    name,
                    attributes,
                    nsmap=self._stream_element.nsmap
                    )
            elif _l > 1:
                self._tree_builder.start(
                    name,
                    attributes
                    )

        self._depth_tracker.append(name)

        return

    def end(self, name):

        """
        Target receiving tag ends
        """

        logging.debug("{} :: end `{}'".format(type(self).__name__, name))

        if self.target_closed:
            raise XMPPStreamParserTargetClosed()

        if len(self._depth_tracker) > 1:
            self._tree_builder.end(name)

        del self._depth_tracker[-1]

        if len(self._depth_tracker) == 1:

            element = self._tree_builder.close()

            self._tree_builder = None

            if self._on_element_readed:
                threading.Thread(
                    target=self._on_element_readed,
                    args=(element,),
                    name='Element Building Complete Thread'
                    ).start()

        if len(self._depth_tracker) == 0:

            if name == '{http://etherx.jabber.org/streams}stream':
                logging.debug(
                    "{} :: end :: stream close tag received - closing parser target".format(
                        type(self).__name__
                        )
                    )
                self.close()

        return

    def data(self, data):

        """
        Target receiving data
        """

        logging.debug("{} :: data `{}'".format(type(self).__name__, data))

        if self.target_closed:
            raise XMPPStreamParserTargetClosed()

        if self._tree_builder:
            self._tree_builder.data(data)

        return

    def comment(self, text):

        """
        Target receiving comment
        """

        logging.debug("{} :: comment `{}'".format(type(self).__name__, text))

        if self.target_closed:
            raise XMPPStreamParserTargetClosed()

        if self._tree_builder:
            self._tree_builder.comment(text)

        return

    def close(self):

        """
        This target is reacting on stream end and calls callback function
        """

        logging.debug("{} :: close".format(type(self).__name__))

        if self.target_closed:
            raise XMPPStreamParserTargetClosed()

        if self._on_stream_event:

            self.target_closed = True

            threading.Thread(
                target=self._on_stream_event,
                args=('stop',),
                kwargs={'attrs':None},
                name="Stream Ended Thread"
                ).start()

        return




class XMPPInputStreamReader:

    def __init__(
        self,
        read_from,
        xml_parser
        ):
        """
        read_from - xml stream input
        """

        self._read_from = read_from

        self._xml_parser = xml_parser

        self._clear(init=True)

        self._stat = 'stopped'

        return


    def _clear(self, init=False):

        if not init:
            if not self.stat() == 'stopped':
                raise RuntimeError("Working. Cleaning not allowed")

        self._stream_reader_thread = None

        self._starting = False
        self._stopping = False

        self._termination_event = None

        self._stat = 'stopped'
        return

    def start(self):

        thread_name_in = 'Thread feeding data to XML parser'

        if not self._starting and not self._stopping and self.stat() == 'stopped':

            self._stat = 'starting'
            self._starting = True

            if not self._stream_reader_thread:

                self._termination_event = threading.Event()

                try:
                    self._stream_reader_thread = org.wayround.utils.stream.cat(
                        stdin=self._read_from,
                        stdout=self,
                        bs=(2 * 1024 ** 2),
                        threaded=True,
                        thread_name=thread_name_in,
                        verbose=True,
                        convert_to_str=False,
                        read_method_name='read',
                        write_method_name='_feed',
                        exit_on_input_eof=True,
                        flush_after_every_write=False,
                        flush_on_input_eof=False,
                        close_output_on_eof=False,
                        waiting_for_input=True,
                        waiting_for_output=False,
                        descriptor_to_wait_for_input=self._read_from.fileno(),
                        descriptor_to_wait_for_output=None,
                        apply_input_seek=False,
                        apply_output_seek=False,
                        standard_write_method_result=True,
                        termination_event=self._termination_event,
                        on_exit_callback=self._on_stream_reader_thread_exit
                        )
                except:
                    logging.exception("Error on starting {}".format(thread_name_in))
                else:
                    self._stream_reader_thread.start()

            self.wait('working')
            self._stat = 'started'
            self._starting = False

        return


    def stop(self):

        if not self._stopping and not self._starting and self.stat() == 'working':
            self._stat = 'stopping'
            self._stopping = True

            self._termination_event.set()

            self.wait('stopped')

            self._clear()

            self._stopping = False
            self._stat = 'stopped'

        return

    def stat(self):

        ret = None

        if bool(self._stream_reader_thread):
            ret = 'working'

        elif not bool(self._stream_reader_thread):
            ret = 'stopped'

        else:
            ret = self._stat

        return ret


    def wait(self, what='stopped'):

        allowed_what = ['stopped', 'working']

        if not what in allowed_what:
            raise ValueError("`what' must be in {}".format(allowed_what))

        while True:

            logging.debug("{} :: waiting for {}".format(type(self).__name__, what))

            if self.stat() == what:
                break

            time.sleep(0.1)

        return

    def _on_stream_reader_thread_exit(self):
        self._stream_reader_thread = None


    def _feed(self, bytes_text):

        logging.debug(
            "{} :: received feed of {}".format(
                type(self).__name__, repr(bytes_text)
                )
            )

        if not isinstance(bytes_text, bytes):
            raise TypeError("bytes_text must be bytes type")

        ret = 0

        try:
            self._xml_parser.feed(bytes_text)
        except:
            logging.exception(
                "{} :: _feed {}".format(
                    type(self).__name__, str(bytes_text, encoding='utf-8')
                    )
                )
            ret = 0
        else:
            ret = len(bytes_text)

        return ret




class XMPPOutputStreamWriter:

    """
    Class for functions related to writing data to socket streamer
    """

    def __init__(
        self,
        write_to,
        xml_parser
        ):
        """
        read_from - xml stream input
        """

        self._write_to = write_to

        self._xml_parser = xml_parser

        self._clear(init=True)

    def _clear(self, init=False):

        if not init:
            if not self.stat() == 'stopped':
                raise RuntimeError("Working. Cleaning not allowed")

        self._stop_flag = False

        self._starting = False
        self._stopping = False

        self._stream_writer_thread = None

        self._output_queue = []

        self._stat = 'stopped'
        return

    def start(self):

        if not self._starting and not self._stopping and self.stat() == 'stopped':

            thread_name_in = 'Thread feeding data to XML parser'

            self._stat = 'starting'
            self._starting = True
            self._stop_flag = False

            if not self._stream_writer_thread:

                try:
                    self._stream_writer_thread = threading.Thread(
                        target=self._output_worker,
                        name=thread_name_in,
                        args=tuple(),
                        kwargs=dict()
                        )
                except:
                    logging.exception(
                        "Error on creating thread {}".format(thread_name_in)
                        )
                else:
                    self._stream_writer_thread.start()

            self.wait('working')
            self._stat = 'started'
            self._starting = False

        return


    def stop(self):

        if not self._starting and not self._stopping:
            self._stopping = True
            self._stat = 'stopping'

            self._stop_flag = True

            self.wait('stopped')

            self._clear()

            self._stopping = False
            self._stat = 'stopped'

        return

    def stat(self):

        ret = 'unknown'

        if bool(self._stream_writer_thread):
            ret = 'working'

        elif not bool(self._stream_writer_thread):
            ret = 'stopped'

        else:
            ret = self._stat

        return ret


    def wait(self, what='stopped'):

        allowed_what = ['stopped', 'working']

        if not what in allowed_what:
            raise ValueError("`what' must be in {}".format(allowed_what))

        while True:

            logging.debug("{} :: waiting for {}".format(type(self).__name__, what))

            if self.stat() == what:
                break

            time.sleep(0.1)

        return

    def send(self, obj):

        if self._stop_flag:
            raise RuntimeError("Stopping. Sending not allowed")

        self._output_queue.append(obj)

        while True:

            if self._stop_flag:
                break

            if not obj in self._output_queue:
                break

            time.sleep(0.1)

        return

    def _output_worker(self):

        while True:
            if len(self._output_queue) != 0:

                while len(self._output_queue) != 0:
                    self._send_object(self._output_queue[0])
                    del self._output_queue[0]

            else:

                if self._stop_flag:
                    break

                time.sleep(0.1)

        self._stream_writer_thread = None

        return

    def _send_object(self, obj):

        snd_obj = None

        if isinstance(obj, bytes):
            snd_obj = obj
        elif isinstance(obj, str):
            snd_obj = bytes(obj, encoding='utf-8')
        elif type(obj) == lxml.etree._Element:
            snd_obj = bytes(
                lxml.etree.tostring(
                    obj,
                    encoding='utf-8'
                    ),
                encoding='utf-8'
                )
        else:
            raise Exception("Wrong obj type. Can be bytes, str or lxml.etree._Element")


        self._write_to.write(snd_obj)

        logging.debug("Feeding data to self._xml_parser.feed:\n{}".format(snd_obj))

        try:
            # Do not make this threaded or it will jam parser
            self._xml_parser.feed(snd_obj)
        except:
            logging.exception("Exception while starting thread of self._xml_parser.feed")

        return


class ConnectionEventsHub(org.wayround.utils.signal.Hub):

    def dispatch(self, event, sock):

        self._dispatch(event, sock)


class StreamEventsHub(org.wayround.utils.signal.Hub):

    def dispatch(self, event, attrs=None):

        self._dispatch(event, attrs)


class StreamObjectsHub(org.wayround.utils.signal.Hub):


    def dispatch(self, obj):

        self._dispatch(obj)



class XMPPStreamMachine:

    def __init__(self):

        self._clear(init=True)

    def _clear(self, init=False):

        if not init:
            if not self.stat() == 'stopped':
                raise RuntimeError("Working - Clearing Restricted")

        self._stopping = False
        self._starting = False

        self._xml_target = None
        self._xml_parser = None
        self._stream_worker = None

        self._sock_streamer = None
        self._stream_events_dispatcher = None
        self._stream_objects_dispatcher = None

    def set_objects(
        self,
        sock_streamer,
        stream_events_dispatcher,
        stream_objects_dispatcher
        ):

        self._sock_streamer = sock_streamer
        self._stream_events_dispatcher = stream_events_dispatcher
        self._stream_objects_dispatcher = stream_objects_dispatcher

    def start_stream_worker(self):

        raise RuntimeError("You need to override this")

    def start(self):

        if not self._starting and not self._stopping and self.stat() == 'stopped':

            self._starting = True

            self._xml_target = XMPPStreamParserTarget(
                on_stream_event=self._stream_events_dispatcher,
                on_element_readed=self._stream_objects_dispatcher
                )

            self._xml_parser = lxml.etree.XMLParser(
                target=self._xml_target
                )

            self.start_stream_worker()

            self._stream_worker.start()

            self._starting = False

    def stop(self):

        if not self._stopping and not self._starting and self.stat() == 'working':

            self._stopping = True

            self._stream_worker.stop()

            self.wait('stopped')
            self._clear()

            self._stopping = False

    def wait(self, what='stopped'):

        if self._stream_worker:
            self._stream_worker.wait(what=what)

    def stat(self):

        ret = None

        if self._stream_worker:
            ret = self._stream_worker.stat()

        if ret == None:
            ret = 'stopped'

        return ret

    def restart(self):
        self.stop()
        self.start()

    def restart_with_new_objects(
        self,
        sock_streamer,
        stream_events_dispatcher,
        stream_objects_dispatcher
        ):

        self.stop()

        self.set_objects(
            sock_streamer,
            stream_events_dispatcher,
            stream_objects_dispatcher
            )

        self.start()




class XMPPInputStreamReaderMachine(XMPPStreamMachine):

    """
    Machine for reading xml stream from socket streamer
    """

    def start_stream_worker(self):

        self._stream_worker = XMPPInputStreamReader(
            self._sock_streamer.strout,
            self._xml_parser
            )

class XMPPOutputStreamWriterMachine(XMPPStreamMachine):

    """
    Machine for writing xml objects to socket streamer
    """

    def start_stream_worker(self):

        self._stream_worker = XMPPOutputStreamWriter(
            self._sock_streamer.strin,
            self._xml_parser
            )

    def send(self, obj):

        threading.Thread(
            name="XMPPOutputStreamWriterMachine send thread",
            target=self._stream_worker.send,
            args=(obj,)
            ).start()

class XMPPIOStreamRWMachine:

    def __init__(self):

        self.in_machine = XMPPInputStreamReaderMachine()
        self.out_machine = XMPPOutputStreamWriterMachine()

        return

    def set_objects(
        self,
        sock_streamer,
        i_stream_events_dispatcher,
        i_stream_objects_dispatcher,
        o_stream_events_dispatcher,
        o_stream_objects_dispatcher
        ):

        self.in_machine.set_objects(
            sock_streamer,
            i_stream_events_dispatcher,
            i_stream_objects_dispatcher
            )

        self.out_machine.set_objects(
            sock_streamer,
            o_stream_events_dispatcher,
            o_stream_objects_dispatcher
            )

        return

    def start(self):

        logging.debug("{} :: received start call".format(type(self).__name__))

        self.in_machine.start()
        self.out_machine.start()

        return

    def stop(self):

        logging.debug("{} :: received stop call".format(type(self).__name__))

        self.in_machine.stop()
        self.out_machine.stop()

        return

    def restart(self):

        self.stop()
        self.start()

        return

    def restart_with_new_objects(
        self,
        sock_streamer,
        i_stream_events_dispatcher,
        i_stream_objects_dispatcher,
        o_stream_events_dispatcher,
        o_stream_objects_dispatcher
        ):

        self.in_machine.restart_with_new_objects(
            sock_streamer,
            i_stream_events_dispatcher,
            i_stream_objects_dispatcher
            )

        self.out_machine.restart_with_new_objects(
            sock_streamer,
            o_stream_events_dispatcher,
            o_stream_objects_dispatcher
            )

        return


    def wait(self, what='stopped'):

        self.in_machine.wait(what=what)
        self.out_machine.wait(what=what)

        return

    def stat(self):

        ret = 'various'

        v1 = self.in_machine.stat()
        v2 = self.out_machine.stat()

        logging.debug("""
IO Machine:
self.in_machine.stat()  == {}
self.out_machine.stat() == {}
""".format(v1, v2)
            )

        if v1 == v2 == 'working':
            ret = 'working'

        elif v1 == v2 == 'stopped':
            ret = 'stopped'

        elif v1 == v2 == None:
            ret = 'stopped'

        return ret

    def send(self, obj, response_callback=None, timeout=10):

        threading.Thread(
            target=self.out_machine.send,
            args=(obj,),
            name="XMPPIOStreamRWMachine send thread"
            ).start()

        return



class Driver:
    """
    Interface for writing feature drivers

    One of methods which will be used by external entities will be 'drive' which
    must wait until all operations done and must return result.
    """

    def __init__(self):

        self.title = 'Untitled'
        self.description = 'This driver has no description'

    def drive(self, obj):

        """
        Override this method
        """

        return 'success'




class StanzaElement: pass

class Stanza:

    def __init__(
        self,
        kind='message',
        ide=None,
        jid_from=None,
        jid_to=None,
        typ=None,
        xmllang=None,
        body=None
        ):

        self.kind = kind

        self.ide = ide

        self.jid_from = jid_from
        self.jid_to = jid_to
        self.typ = typ
        self.xmllang = xmllang
        self.body = body

    def __str__(self):
        return self.to_str()

    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, kind):

        if not kind in ['message', 'iq', 'presence']:
            raise WrongStanzaKind("Some one tried to make stanza of kind `{}'".format(kind))

        self._kind = kind

        return

    @property
    def body_element(self):
        # TODO: testing required
        b = self.body.find('body')
        return b

    def to_str(self):
        return stanza_tpl(
            self.kind,
            self.ide,
            self.typ,
            self.jid_from,
            self.jid_to,
            self.xmllang,
            self.body
            )

    def determine_error(self):
        return determine_stanza_error(self)

    def is_error(self):
        """
        Is stanza of 'error' type
        """
        return self.typ == 'error'

class StanzaHub(org.wayround.utils.signal.Hub):

    def dispatch(self, obj):

        self._dispatch(obj)

class StanzaProcessor:

    def __init__(
        self,
        ns='jabber:client'
        ):

        self.stanza_hub = StanzaHub()

        self._input_objects_hub = None
        self._io_machine = None

        self.response_cbs = {}

        self._stanza_id_generation_counter = 0

        self._wait_callbacks = {}


    def connect_input_object_stream_hub(self, hub_object, name='stanza_processor'):
        self._input_objects_hub = hub_object
        self._input_objects_hub.set_waiter(name, self._on_input_object)

    def disconnect_input_object_stream_hub(self, name='stanza_processor'):
        if self._input_objects_hub.get_waiter(name):
            self._input_objects_hub.del_waiter(name)

    def connect_io_machine(self, io_machine):
        self._io_machine = io_machine

    def disconnect_io_machine(self, io_machine):
        self._io_machine = None

    def send(
        self, stanza_obj, ide_mode='generate', ide=None, cb=None, wait=False
        ):
        """
        Sends pointed stanza object to connected peer

        wait can be a bool or int

        if wait < 0, wait = None

        if wait == True, wait = 10000

        if wait == False, wait = 0

        if wait == None or wait > 0, then cb must be None

        if wait == None or wait > 0, ide_mode = 'generate_implicit' and cb generated internally

        `wait' is timeout. it is passed to Event.wait(), so wait == None is wait
        forever. (which can lead to deadlock)

        ide_mode must be in ['from_stanza', 'generate', 'generate_implicit',
        'implicit'].

        if ide_mode == 'from_stanza', then id taken from stanza.

        if ide_mode == 'generate', then id generated for stanza if stanza has no
        it's own id.

        if ide_mode == 'generate_implicit', then id generated for stanza in any
        way

        if ide_mode == 'implicit', then id is taken from ide parameter in any
        way

        result:

        if wait == 0, then id of sent stanza is returned (accordingly to
        ide_mode described above)

        if wait != 0, then False is returned in case of timeout, or Stanza
        object is returned in case of success
        """


        ret = None

        new_stanza_ide = None

        self._stanza_id_generation_counter += 1

        if wait != None and not isinstance(wait, (bool, int,)):
            raise TypeError("`wait' must be None, bool or int")

        if wait == True:
            wait = 10000
            ide_mode = 'generate_implicit'

        elif wait == False:
            wait = 0

        elif wait < 0:
            wait = None

        if not ide_mode in ['from_stanza', 'generate', 'generate_implicit', 'implicit']:
            raise ValueError("wrong value for ide_mode parameter")

        if isinstance(wait, int) and wait > 0 and cb != None:
            raise ValueError("`cb' must be None if `wait' > 0")

        if ide_mode == 'from_stanza':
            new_stanza_ide = stanza_obj.ide

        elif ide_mode in ['generate', 'generate_implicit']:
            if ((not stanza_obj.ide and ide_mode == 'generate')
                or ide_mode == 'generate_implicit'):

                new_stanza_ide = hex(self._stanza_id_generation_counter)

        elif ide_mode == 'implicit':

            new_stanza_ide = ide

        stanza_obj.ide = new_stanza_ide

        if wait == None or (isinstance(wait, int) and wait > 0):
            cb = self._wait_callback

        if cb:
            if not new_stanza_ide:
                raise ValueError("callback provided but stanza has no id")

            self.response_cbs[stanza_obj.ide] = cb

        if wait == 0:
            ret = new_stanza_ide

        if wait == None or (isinstance(wait, int) and wait > 0):
            self._wait_callbacks[stanza_obj.ide] = {
                'event': threading.Event(),
                'response': None
                }

        self._io_machine.send(stanza_obj.to_str())

        if wait == None or (isinstance(wait, int) and wait > 0):
            wait_res = self._wait_callbacks[stanza_obj.ide]['event'].wait(wait)

            if wait_res == False:
                ret = False
            else:
                ret = self._wait_callbacks[stanza_obj.ide]['response']

            del self._wait_callbacks[stanza_obj.ide]
            self.delete_callback(stanza_obj.ide)

        return ret

    def delete_callback(self, ide):

        while ide in self.response_cbs:
            del self.response_cbs[ide]

        return

    def _wait_callback(self, obj):

        self._wait_callbacks[obj.ide]['response'] = obj
        self._wait_callbacks[obj.ide]['event'].set()

        return

    def _on_input_object(self, obj):

        threading.Thread(
            target=self._process_input_object,
            args=(obj,),
            name="Input Stanza Object Processing Thread"
            ).start()

        return

    def _process_input_object(self, obj):

        logging.debug(
            "_process_input_object :: received element `{}' :: `{}'".format(
                obj,
                obj.tag
                )
            )

        if is_stanza_element(obj):

            stanza = stanza_from_element(obj)

            if isinstance(stanza, Stanza):
                if stanza.ide in self.response_cbs:
                    self.response_cbs[stanza.ide](stanza)
                    del self.response_cbs[stanza.ide]
                else:

                    threading.Thread(
                        target=self.stanza_hub.dispatch,
                        name="Dispatching Stanza",
                        args=(stanza,)
                        ).start()

            else:
                logging.error("proposed object not a stanza({}):\n{}".format(stanza, obj))

        return

class Monitor:

    """
    Class for monitoring this module classes various events
    """

    def connection(self, event, sock):

        logging.debug("connection: {} {}".format(event, sock))

        return

    def stream_in(self, event, attrs):

        logging.debug("stream_in: {} {}".format(event, attrs))

        return

    def stream_out(self, event, attrs):

        logging.debug("stream_out: {} {}".format(event, attrs))

        return

    def object(self, obj):

        logging.debug("object: {}".format(obj))

        return

class WrongStanzaKind(Exception): pass

class WrongErrorStanzaStructure(Exception): pass


def stanza_from_element(element):

    """
    This function makes Stanza object from stanza of lxml.etree._Element type
    """

    ret = None

    tag_parsed = lxml.etree.QName(element)

    if not tag_parsed:
        ret = None

    else:

        ns = tag_parsed.namespace
        tag = tag_parsed.localname

        if not ns in ['jabber:client', 'jabber:server']:
            ret = None
        else:

            if not tag in ['message', 'iq', 'presence']:
                ret = None
            else:

                kind = tag

                ide = element.get('id')
                jid_from = element.get('from')
                jid_to = element.get('to')
                typ = element.get('type')
                xmllang = element.get('xml:lang')

                body = element

                try:
                    ret = Stanza(
                        kind,
                        ide,
                        jid_from,
                        jid_to,
                        typ,
                        xmllang,
                        body
                        )

                except WrongStanzaKind:
                    ret = None
                except WrongErrorStanzaStructure:
                    ret = None



    return ret


def stanza_tpl(
    kind=None,
    ide=None,
    typ=None,
    jid_from=None,
    jid_to=None,
    xmllang=None,
    body=None
    ):

    """
    Template for generating stanzas

    body can be one of (bytes, str, lxml.etree._Element, list,)

    if body is bytes, it's transformed to str

    if body is str, it's used as is

    if body is lxml.etree._Element or list, it's items must be in set of
    (bytes, str, lxml.etree._Element, StanzaElement,)

    if body is list of items:

        if list item is bytes or str, it is treated as described for body
        (above)

        if list item is lxml.etree._Element, it is rendered with
        lxml.etree.tostring()

        if list item is StanzaElement instance, it's .to_str() method is used to
        make string of it



        in case when body is list, all it's stringified items summarized to
        single string

    """

    ide_t = ''
    if ide:
        ide_t = ' id="{}"'.format(xml.sax.saxutils.escape(ide))

    typ_t = ''
    if typ:
        typ_t = ' type="{}"'.format(xml.sax.saxutils.escape(typ))

    jid_from_t = ''
    if jid_from:
        jid_from_t = ' from="{}"'.format(xml.sax.saxutils.escape(jid_from))

    jid_to_t = ''
    if jid_to:
        jid_to_t = ' to="{}"'.format(xml.sax.saxutils.escape(jid_to))

    xmllang_t = ''
    if xmllang:
        xmllang_t = ' xml:lang="{}"'.format(xml.sax.saxutils.escape(xmllang))

    body_t = ''

    if body != None:

        if (not isinstance(body, (bytes, str, list,))
            and not type(body) == lxml.etree._Element):

            raise TypeError("body must be None, bytes, str or lxml.etree._Element, list")

        if isinstance(body, list) or type(body) == lxml.etree._Element:

            for i in body:

                if isinstance(i, StanzaElement):
                    body_t += i.to_str()

                if type(i) == lxml.etree._Element:
                    body_t += str(lxml.etree.tostring(i), 'utf-8')

                if isinstance(i, bytes):
                    body_t += str(i, 'utf-8')

                if isinstance(i, str):
                    body_t += i


        if isinstance(body, bytes):

            body_t = str(body, 'utf-8')

        if isinstance(body, str):

            body_t = body

    ret = '<{kind}{ide_t}{typ_t}{jid_from_t}{jid_to_t}{xmllang_t}>{body_t}</{kind}>'.format(
        kind=xml.sax.saxutils.escape(kind),
        ide_t=ide_t,
        typ_t=typ_t,
        jid_from_t=jid_from_t,
        jid_to_t=jid_to_t,
        xmllang_t=xmllang_t,
        body_t=body_t
        )

    return ret


def start_stream_tpl(
    jid_from,
    jid_to,
    version='1.0',
    xmllang='en',
    xmlns='jabber:client',
    xmlns_stream='http://etherx.jabber.org/streams'
    ):

    """
    Standard XMPP stream begin template
    """

    ret = """\
<?xml version="1.0"?>\
 <stream:stream from="{jid_from}" to="{jid_to}" version="{version}"\
 xml:lang="{xmllang}" xmlns="{xmlns}"\
 xmlns:stream="{xmlns_stream}">""".format(
        jid_from=xml.sax.saxutils.escape(jid_from),
        jid_to=xml.sax.saxutils.escape(jid_to),
        version=xml.sax.saxutils.escape(version),
        xmllang=xml.sax.saxutils.escape(xmllang),
        xmlns=xml.sax.saxutils.escape(xmlns),
        xmlns_stream=xml.sax.saxutils.escape(xmlns_stream)
        )

    return ret

def stop_stream_tpl():
    """
    Standard XMPP stream end template
    """
    return '</stream:stream>'

def starttls_tpl():
    """
    Standard XMPP TLS layer start text
    """
    return '<starttls xmlns="urn:ietf:params:xml:ns:xmpp-tls"/>'

def bind_tpl(typ='resource', value=None):

    """
    Template for binding client to resource on server
    """

    if not typ in ['resource', 'fulljid']:
        raise ValueError("Wrong bind type")

    bind_value = ''
    if value:

        tag_name = ''

        if typ == 'resource':
            tag_name = 'resource'

        elif typ == 'fulljid':
            tag_name = 'jid'

        bind_value = '<{tag_name}>{value}</{tag_name}>'.format(
            value=xml.sax.saxutils.escape(value),
            tag_name=tag_name
            )

    ret = '<bind xmlns="urn:ietf:params:xml:ns:xmpp-bind">{}</bind>'.format(
        bind_value
        )

    return ret

def session_tpl():
    """
    Standard XMPP session begin text
    """
    return '<session xmlns="urn:ietf:params:xml:ns:xmpp-session"/>'


def jid_from_string(in_str):
    """
    Try to convert string to JID instance. Returns None in case of error.
    """

    ret = None

    res = re.match(
        r'^(?P<localpart>.+?)@(?P<domainpart>.+?)(/(?P<resourcepart>.+?))?$',
        in_str
        )

    if res:

        if len(res.group('localpart')) > 32:

            ret = None

        else:

            try:
                ret = JID(
                    res.group('localpart'),
                    res.group('domainpart'),
                    res.group('resourcepart')
                    )

            except:
                ret = None

    return ret

jid_from_str = jid_from_string
str_to_jid = jid_from_string
string_to_jid = jid_from_string

def determine_stream_error(xml_element):


    """
    Returns None if not isinstance(xml_element, lxml.etree._Element)

    Returns False if not {http://etherx.jabber.org/streams}error

    Returns dict(name='text', text='text') with name and text as described in
    paragraph 4.9. of rfc-6120 in case of successful error recognition

    dict['name'] can have additionally one of two special values, both of which
    means standard violation thus presume some kind of xmpp error:
        'non-standard-error-name' - issuer tries supply nonstandard name
        'error-name-absent'       - issuer did not supplied error name
    """

    ret = None

    if not type(xml_element) == lxml.etree._Element:
        ret = False

    else:

        if xml_element.name == '{http://etherx.jabber.org/streams}error':

            error_name = None
            error_text = None

            for i in xml_element:

                parsed_qn = lxml.etree.QName(i)
                ns = parsed_qn.namespace
                tag = parsed_qn.localname

                if tag == 'text':
                    if ns == 'http://etherx.jabber.org/streams':
                        error_text = i.text
                else:
                    if ns == 'http://etherx.jabber.org/streams':
                        error_name = tag

                        if not error_name in STREAM_ERROR_NAMES:
                            error_name = 'non-standard-error-name'

            if not error_name:
                error_name = 'error-name-absent'

            ret = dict(
                name=error_name,
                text=error_text
                )

    return ret

def determine_stanza_error(stanza):

    """
    If stanza is of error type and has correct structure, return is
        {
            'error_type':error_type,
            'condition':condition,
            'text':text
        }

    if `stanza' is stanza and has wrong structure (has no error element),
        return None

    if `stanza' is not stanza, return None

    if `stanza' is stanza and not of type error, return False

    if returned condition in ['invalid-condition', 'undefined-condition'] stanza
    must be considered wrong
    """

    ret = None
    condition = None
    text = None
    error_type = None


    if not isinstance(stanza, Stanza) and is_stanza_element(stanza):
        stanza = stanza_from_element(stanza)

    if not isinstance(stanza, Stanza):
        ret = None
    else:

        if stanza.typ == 'error':

            e1 = stanza.body.find('error')

            if e1 == None:
                ret = None
            else:

                if len(e1) == 0:
                    ret = None
                else:

                    error_type = e1.get('type')

                    if not error_type:
                        ret = None

                    else:

                        for i in e1:
                            tag_parsed = lxml.etree.QName(i)

                            ns = tag_parsed.namespace
                            tag = tag_parsed.localname

                            if ns == 'urn:ietf:params:xml:ns:xmpp-stanzas':

                                if tag == 'text':
                                    text = i.text
                                    break

                        for i in e1:
                            tag_parsed = lxml.etree.QName(i)

                            ns = tag_parsed.namespace
                            tag = tag_parsed.localname

                            if ns == 'urn:ietf:params:xml:ns:xmpp-stanzas':

                                if tag != 'text':
                                    condition = tag
                                    break

                        if not condition in STANZA_ERROR_NAMES:
                            condition = 'invalid-condition'

                        if condition == None:
                            condition = 'undefined-condition'

                        ret = {
                            'error_type':error_type,
                            'condition':condition,
                            'text':text
                            }

        else:
            ret = False

    return ret

def is_features_element(obj):
    return (type(obj) == lxml.etree._Element
        and obj.tag == '{http://etherx.jabber.org/streams}features')

def is_stanza_element(obj):

    """
    Determine is obj is stanza
    """
    ret = True

    if not type(obj) == lxml.etree._Element:
        ret = False

    else:

        tag_parsed = lxml.etree.QName(obj)

        if not tag_parsed:
            ret = False

        else:

            ns = tag_parsed.namespace
            tag = tag_parsed.localname

            if not ns in ['jabber:client', 'jabber:server']:
                ret = False
            else:

                if not tag in ['message', 'iq', 'presence']:
                    ret = False

    return ret

def is_stanza(obj):
    return isinstance(obj, Stanza)
