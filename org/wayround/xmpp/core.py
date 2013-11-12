
import logging
import threading
import queue
import time
import re
import uuid

import xml.sax.saxutils
import lxml.etree

import org.wayround.utils.error
import org.wayround.utils.stream
import org.wayround.utils.signal
import org.wayround.utils.factory
import org.wayround.utils.lxml


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


class JID:

    """
    Class for working with JID

    Domain and user parts are automatically converted to low register

    """

    def __init__(self, user=None, domain=None, resource=None):

        self._values = {}

        self.user = user
        self.domain = domain
        self.resource = resource

    @classmethod
    def new_from_string(cls, in_str):
        """
        Try to convert string to JID instance. Returns None in case of error.
        """

        ret = None

        res = re.match(
            (r'^((?P<localpart>.+?)@)?(?P<domainpart>.+?)'
            r'(/(?P<resourcepart>.+?))?$'),
            in_str
            )

        if res:

            ret = cls(
                res.group('localpart'),
                res.group('domainpart'),
                res.group('resourcepart')
                )

        return ret

    new_from_str = new_from_string

    def __str__(self):

        ret = None

        if self.is_bare():
            ret = self.bare()
        elif self.is_full():
            ret = self.full()
        elif self.is_domain():
            ret = self.domain
        else:
            ret = None

        return ret

    @property
    def user(self):
        return self._get('user')

    @user.setter
    def user(self, value):

        if value == '':
            value = None
        self._set('user', value)

    @property
    def domain(self):
        return self._get('domain')

    @domain.setter
    def domain(self, value):
        if value == '':
            value = None
        self._set('domain', value)

    @property
    def resource(self):
        return self._get('resource')

    @resource.setter
    def resource(self, value):
        if value == '':
            value = None

        if value != None:
            self._values['resource'] = str(value)
        else:
            self._values['resource'] = value
        return

    def _set(self, name, value):
        if value != None:
            self._values[name] = str(value).lower()
        else:
            self._values[name] = None
        return

    def _get(self, name):

        ret = None

        if name in self._values:
            ret = self._values[name]

        return ret

    def _bare_part(self, user, domain):

        if user == None:
            user = ''

        if domain == None:
            domain = ''

        at = '@'

        if self.user == '' or self.user == None:
            at = ''

        return user, domain, at

    def bare(self):

        user, domain, at = self._bare_part(self.user, self.domain)

        return '{user}{at}{domain}'.format(
            user=user,
            domain=domain,
            at=at
            )

    def full(self):

        user, domain, at = self._bare_part(self.user, self.domain)
        resource = self.resource or 'default'

        return '{user}{at}{domain}/{resource}'.format(
            user=user,
            domain=domain,
            resource=resource,
            at=at
            )

    def get_type(self):

        ret = 'unknown'

        if (self.user == None
            and self.domain != None
            and self.resource == None):
            ret = 'domain'

        elif (self.user == None
              and self.domain != None
              and self.resource == None):
            ret = 'domain_res'

        elif (self.user != None
              and self.domain != None
              and self.resource == None):
            ret = 'bare'

        elif (self.user != None
              and self.domain != None
              and self.resource != None):
            ret = 'full'

        else:
            ret = 'unknown'

        return ret

    def is_full(self):
        return self.get_type() == 'full'

    def is_bare(self):
        return self.get_type() == 'bare'

    def is_domain(self):
        return self.get_type() == 'domain'

    def is_domain_res(self):
        return self.get_type() == 'domain_res'

    def is_unknown(self):
        return self.get_type() == 'unknown'

    def update(self, jid_obj):

        if not isinstance(jid_obj, JID):
            raise TypeError("`jid_obj' must be of type JID")

        self.user = jid_obj.user
        self.domain = jid_obj.domain
        self.resource = jid_obj.resource

        return self

    def copy(self):
        return JID().update(self)

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
    This exception is raised in case of some one's trying to send some more
    data to parsed when it is closed already.
    """


class XMPPStreamParserTarget(org.wayround.utils.signal.Signal):

    """
    Target for lxml to build XML objects, which then sent to element hubs or
    stream event listeners

    Signals:
    'start'(self, attrs=attributes)
    'error' (self, attrs=attributes)
    'element_readed' (self, element)
    'stop' (self, attrs=attributes)
    """

    def __init__(self):

        """
        :param on_stream_event: callback to call when stream starts, stops or
            fails (hard xml stream error. at this time, xml errors are separate
            from xmpp error. xmpp errors are recognised and generated by
            XMPPIOStreamRWMachine class)
        :param on_element_readed: callback to call when next stream element
            read complete
        """

        super().__init__(['start', 'stop', 'error', 'element_readed'])

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

                self.emit_signal('start', self, attrs=attributes)

            else:

                self.emit_signal('error', self, attrs=attributes)

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

            self.emit_signal('element_readed', self, element)

        if len(self._depth_tracker) == 0:

            if name == '{http://etherx.jabber.org/streams}stream':
                logging.debug(
                    ("{} :: end :: stream close tag received "
                    "- closing parser target").format(
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

        self.target_closed = True

        self.emit_signal('stop', self, attrs=None)

        return


class XMPPInputStreamReader:

    def __init__(self, read_from, xml_parser):
        """
        read_from - xml stream input
        """

        self._read_from = read_from
        self._xml_parser = xml_parser

        self._clear(init=True)

        self._feed_pool = queue.Queue()
#        self._feed_lock = threading.Lock()
        self._feed_pool_thread = None

        return

    def _clear(self, init=False):

        if not init:
            if not self.stat() == 'stopped':
                raise RuntimeError("Working. Cleaning not allowed")

        self._stream_reader_thread = None

        self._starting = False
        self._stopping = False

        self._termination_event = threading.Event()

        self._stat = 'stopped'

        return

    def start(self):
        """
        Synchronous
        """

        thread_name_in = 'Thread feeding data to XML parser'

        if (not self._starting
            and not self._stopping
            and self.stat() == 'stopped'):

            self._stat = 'starting'
            self._starting = True

            if not self._stream_reader_thread:

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
                    logging.exception(
                        "Error on starting {}".format(thread_name_in)
                        )
                else:
                    self._stream_reader_thread.start()

            if self._feed_pool_thread == None:
                self._feed_pool_thread = threading.Thread(
                    name="{} _feed pool worker".format(type(self).__name__),
                    target=self._feed_pool_worker_thread
                    )
                self._feed_pool_thread.start()

            self.wait('working')
            self._stat = 'started'
            self._starting = False

        return

    def stop(self):
        """
        Synchronous
        """

        if (not self._stopping
            and not self._starting
            and self.stat() == 'working'):
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

            logging.debug(
                "{} :: waiting for {}".format(type(self).__name__, what)
                )

            if self.stat() == what:
                break

            time.sleep(0.1)

        return

    def _on_stream_reader_thread_exit(self):
        self._stream_reader_thread = None

    def _feed(self, bytes_text):

        if not isinstance(bytes_text, bytes):
            raise TypeError("bytes_text must be bytes type")

        self._feed_pool.put(bytes_text)

        return len(bytes_text)

    def _feed_pool_worker_thread(self):

        while True:

            while not self._feed_pool.empty():

                try:
                    bb = self._feed_pool.get()
                except queue.Empty:
                    pass
                else:
                    logging.debug(
                        "{}::\n--in---\n{}\n-------".format(
                            type(self).__name__, repr(bb)
                            )
                        )

                    try:
                        self._xml_parser.feed(bb)
                    except:
                        logging.exception(
                            "{} :: _feed {}".format(
                                type(self).__name__, str(bb, encoding='utf-8')
                                )
                            )

            time.sleep(0.2)

            if self._termination_event.is_set():
                break

        self._feed_pool_thread = None

        return


class XMPPOutputStreamWriter:

    """
    Class for functions related to writing data to socket streamer
    """

    def __init__(self, write_to, xml_parser):

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
        """
        Synchronous
        """

        if (not self._starting
            and not self._stopping
            and self.stat() == 'stopped'):

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
        """
        Synchronous
        """

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

            logging.debug(
                "{} :: waiting for {}".format(type(self).__name__, what)
                )

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
            raise Exception(
                "Wrong obj type. Can be bytes, str or lxml.etree.Element"
                )

        self._write_to.write(snd_obj)

        logging.debug(
            "Feeding data to self._xml_parser.feed:"
            "\n--out--\n{}\n-------".format(
                snd_obj
                )
            )

        try:
            # Do not make this threaded or it will jam parser
            self._xml_parser.feed(snd_obj)
        except:
            logging.exception(
                "Exception while starting thread of self._xml_parser.feed"
                )

        return


class XMPPStreamMachine(org.wayround.utils.signal.Signal):

    """
    Signals:
    'start'(self, attrs=attributes)
    'error' (self, attrs=attributes)
    'element_readed' (self, element)
    'stop' (self, attrs=attributes)
    """

    def __init__(self, mode='reader'):

        if not mode in ['reader', 'writer']:
            raise ValueError("Invalid Mode selected")

        self.mode = mode

        super().__init__(['start', 'stop', 'error', 'element_readed'])

        self._clear(init=True)

    def _clear(self, init=False):

        if not init:
            if not self.stat() == 'stopped':
                raise RuntimeError("Working - Clearing Restricted")

        self._stopping = False
        self._starting = False

        self._xml_target = None
        self._xml_parser = None

        self.stream_worker = None

    def set_objects(self, sock_streamer):

        self._sock_streamer = sock_streamer

    def _signal_proxy(self, signal_name, *args, **kwargs):

        self.emit_signal(signal_name, *args, **kwargs)

    def send(self, obj):

        if (self.stream_worker
            and hasattr(self.stream_worker, 'send')
            and callable(self.stream_worker.send)
            ):

            threading.Thread(
                target=self.stream_worker.send,
                args=(obj,)
                ).start()

        else:
            raise Exception(
                "Current stream worker doesn't support send function"
                )

        return

    def start(self):
        """
        Synchronous
        """

        if not hasattr(self, 'stream_worker'):
            raise Exception("self.stream_worker must be defined")

        if (not self._starting
            and not self._stopping
            and self.stat() == 'stopped'):

            self._starting = True

            self._xml_target = XMPPStreamParserTarget()

            self._xml_target.connect_signal(True, self._signal_proxy)

            self._xml_parser = lxml.etree.XMLParser(
                target=self._xml_target,
                huge_tree=True
#                strip_cdata=False,
#                resolve_entities=False
                )

            self.stream_worker = None

            if self.mode == 'reader':
                self.stream_worker = XMPPInputStreamReader(
                    self._sock_streamer.strout,
                    self._xml_parser
                    )

            elif self.mode == 'writer':
                self.stream_worker = XMPPOutputStreamWriter(
                    self._sock_streamer.strin,
                    self._xml_parser
                    )

            else:
                # only two modes allowed
                raise Exception("Programming error")

            self.stream_worker.start()

            self._starting = False

    def stop(self):
        """
        Synchronous
        """

        if (not self._stopping
            and not self._starting
            and self.stat() == 'working'):

            self._stopping = True

            self.stream_worker.stop()

            self._xml_target.disconnect_signal(self._signal_proxy)

            self.wait('stopped')
            self._clear()

            self._stopping = False

    def wait(self, what='stopped'):

        if self.stream_worker:
            self.stream_worker.wait(what=what)

    def stat(self):

        ret = None

        if self.stream_worker:
            ret = self.stream_worker.stat()

        if ret == None:
            ret = 'stopped'

        return ret

    def restart(self):
        """
        Synchronous
        """
        self.stop()
        self.start()
        return


class XMPPIOStreamRWMachine(org.wayround.utils.signal.Signal):
    """
    Signals:

    'in_start'          (parser_target, attrs=attributes)
    'in_error'          (parser_target, attrs=attributes)
    'in_element_readed' (parser_target, element)
    'in_stop'           (parser_target, attrs=attributes)

    'out_start'          (parser_target, attrs=attributes)
    'out_error'          (parser_target, attrs=attributes)
    'out_element_readed' (parser_target, element)
    'out_stop'           (parser_target, attrs=attributes)
    """

    def __init__(self):

        self.in_machine = XMPPStreamMachine(mode='reader')
        self.out_machine = XMPPStreamMachine(mode='writer')

        logging.debug("XMPPIOStreamRWMachine __init__()")
        super().__init__(
            self.in_machine.get_signal_names(add_prefix='in_')
            + self.in_machine.get_signal_names(add_prefix='out_')
            )

        self.in_machine.connect_signal(True, self._in_stream_signal_proxy)
        self.out_machine.connect_signal(True, self._out_stream_signal_proxy)

        return

    def set_objects(self, sock_streamer):
        self.in_machine.set_objects(sock_streamer)
        self.out_machine.set_objects(sock_streamer)
        return

    def _in_stream_signal_proxy(self, signal_name, *args, **kwargs):
        self.emit_signal('in_' + signal_name, *args, **kwargs)

    def _out_stream_signal_proxy(self, signal_name, *args, **kwargs):
        self.emit_signal('out_' + signal_name, *args, **kwargs)

    def start(self):
        """
        Synchronous
        """
        self.in_machine.start()
        self.out_machine.start()
        return

    def stop(self):
        """
        Synchronous
        """
        self.in_machine.stop()
        self.out_machine.stop()
        return

    def restart(self):
        """
        Synchronous
        """
        self.in_machine.restart()
        self.out_machine.restart()
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

    One of methods which will be used by external entities will be 'drive'
    which must wait until all operations done and must return result.

    DEVELOPER NOTE: Currently I can't even hardly imagine usage of this class
    out of this XMPP implementation, so it will remain her for now
    """

    def __init__(self):

        self.title = 'Untitled'
        self.description = 'This driver has no description'

    def drive(self, features_element):

        """
        Override this method
        """

        return 'success'


class StanzaMalformed(Exception):
    """
    For stanza parsing errors
    """


class Stanza:

    def __init__(
        self,

        tag=None, ide=None, from_jid=None, to_jid=None, typ=None,
        xmllang=None, xmlns='jabber:client',

        thread=None, subject=None, body=None, objects=None,

        priority=None, show=None, status=None
        ):

        if body == None:
            body = []

        if subject == None:
            subject = []

        if objects == None:
            objects = []

        if status == None:
            status = []

        self.set_element(None)
        self.set_objects(objects)

        self.set_tag(tag)
        self.set_ide(ide)
        self.set_from_jid(from_jid)
        self.set_to_jid(to_jid)
        self.set_typ(typ)
        self.set_xmlns(xmlns)
        self.set_xmllang(xmllang)

        self.set_thread(thread)
        self.set_subject(subject)
        self.set_body(body)

        self.set_show(show)
        self.set_status(status)
        self.set_priority(priority)

        return

    def __str__(self):
        return self.to_str()

    def check_element(self, value):
        if value != None and not is_stanza_element(value):
            raise TypeError("`element' must be stanza lxml.etree.Element")

    def check_objects(self, value):
        for i in value:
            if (not hasattr(i, 'gen_element')
                or not callable(getattr(i, 'gen_element'))):
                raise ValueError(
                    "all objects in `objects' must have gen_element() method"
                    " ({} has not)".format(i)
                    )

    def check_tag(self, value):
        if not value in ['message', 'iq', 'presence']:
            raise ValueError("`tag' must be in ['message', 'iq', 'presence']")

    def check_ide(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`ide' must be None or str")

    def check_from_jid(self, value):
        if value != None:
            JID.new_from_str(value)

    def check_to_jid(self, value):
        if value != None:
            JID.new_from_str(value)

    def check_typ(self, value):

        if value != None and not value in [
            'error', 'get', 'result', 'set', 'chat', 'error', 'groupchat',
            'headline', 'normal', 'error', 'probe', 'subscribe',
            'subscribed', 'unavailable', 'unsubscribe', 'unsubscribed'
            ]:
            raise ValueError("invalid `typ'")

        return

    def check_xmlns(self, value):
        if not value in ['jabber:client', 'jabber:server']:
            raise ValueError(
                "`xmlns' must be in ['jabber:client', 'jabber:server']"
                )

    def check_xmllang(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`xmllang' must be None or str")

    def check_thread(self, value):
        if value != None and not isinstance(value, MessageThread):
            raise ValueError("`thread' must be MessageThread")

    def check_subject(self, value):
        if not org.wayround.utils.types.struct_check(
            value,
            {'t': list, '.': {'t': MessageSubject}}
            ):
            raise ValueError("`subject' must be list of MessageSubject")

    def check_body(self, value):
        if not org.wayround.utils.types.struct_check(
            value,
            {'t': list, '.': {'t': MessageBody}}
            ):
            raise ValueError("`body' must be list of MessageBody")

    def check_show(self, value):
        if value != None and not isinstance(value, PresenceShow):
            raise ValueError("`show' must be PresenceShow")

    def check_status(self, value):
        if not org.wayround.utils.types.struct_check(
            value,
            {'t': list, '.': {'t': PresenceStatus}}
            ):
            raise ValueError("`status' must be list of PresenceStatus")

    def check_priority(self, value):
        if (value != None
            and (not isinstance(value, int) or not value in range(255))):
            raise ValueError("`priority' must be byte")

    @classmethod
    def new_from_element(cls, element):

        if type(element) != lxml.etree._Element:
            raise TypeError("`element' must be lxml.etree.Element")

        qname = lxml.etree.QName(element)

        ns = qname.namespace

        cl = cls(
            tag=qname.localname,
            xmlns=qname.namespace
            )

        cl.set_element(element)

        org.wayround.utils.lxml.subelems_to_object_props(
            element, cl,
            [
             ('{{{}}}thread'.format(ns), MessageThread, 'thread'),
             ('{{{}}}show'.format(ns), PresenceShow, 'show'),
             ]
            )

        org.wayround.utils.lxml.subelemsm_to_object_propsm(
            element, cl,
            [
             ('{{{}}}status'.format(ns), PresenceStatus, 'status'),
             ('{{{}}}subject'.format(ns), MessageSubject, 'subject'),
             ('{{{}}}body'.format(ns), MessageBody, 'body')
             ]
            )

        org.wayround.utils.lxml.elem_props_to_object_props(
            element, cl,
            [
             ('id', 'ide'),
             ('from', 'from_jid'),
             ('to', 'to_jid'),
             ('type', 'typ'),
             ('xml:lang', 'xmllang')
             ]
            )

        priority_el = element.find('{{{}}}priority'.format(ns))
        if priority_el != None:
            cl.set_priority(int(priority_el.text))

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element(self.get_tag())

        org.wayround.utils.lxml.object_props_to_elem_props(
            self, el,
            [
             # ('xmlns', 'xmlns'),
             ('ide', 'id'),
             ('from_jid', 'from'),
             ('to_jid', 'to'),
             ('xmllang', 'xml:lang'),
             ('typ', 'type')
             ]
            )

        org.wayround.utils.lxml.object_props_to_subelems(
            self, el,
            [
             ('thread'),
             ('show'),
             ]
            )

        org.wayround.utils.lxml.object_propsm_to_subelemsm(
            self, el,
            [
             ('status'),
             ('subject'),
             ('body')
             ]
            )

        objects = self.get_objects()
        for i in objects:
            el.append(i.gen_element())

        priority = self.get_priority()
        if priority:
            priority_el = lxml.etree.Element('priority')
            priority_el.text = priority
            el.append(priority_el)

        return el

    def to_str(self):
        ret = lxml.etree.tostring(self.gen_element())
        if isinstance(ret, bytes):
            ret = str(ret, 'utf-8')
        return ret

    to_string = to_str

    def gen_error(self):
        return StanzaError.new_from_stanza(self)

    def is_error(self):
        """
        Is stanza of 'error' type
        """
        return self.get_typ() == 'error'

org.wayround.utils.factory.class_generate_attributes(
    Stanza,
    [
     'element', 'objects', 'tag', 'ide', 'from_jid', 'to_jid', 'typ',
     'xmlns', 'xmllang', 'thread', 'subject', 'body', 'show', 'status',
     'priority']
    )
org.wayround.utils.factory.class_generate_check(
    Stanza,
    [
     'element', 'objects', 'tag', 'ide', 'from_jid', 'to_jid', 'typ',
     'xmlns', 'xmllang', 'thread', 'subject', 'body', 'show', 'status',
     'priority']
    )


class MessageBody:

    def __init__(self, text, xmllang=None):

        self.set_text(text)
        self.set_xmllang(xmllang)

    def check_text(self, value):
        if not isinstance(value, str):
            raise ValueError("`text' must be str")

    def check_lang(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`lang' must be str")

    @classmethod
    def new_from_element(cls, element):

        if type(element) != lxml.etree._Element:
            raise ValueError("`element' must be lxml.etree.Element")

        tag = org.wayround.utils.lxml.parse_element_tag(
            element, 'body', None
            )[0]

        if tag == None:
            raise ValueError("invalid tag")

        cl = cls()
        cl.set_text(element.text)
        cl.set_lang(element.get('xml:lang'))

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('body')

        text = self.get_text()
        if text:
            el.text = text

        lang = self.get_lang()
        if lang:
            el.set('xml:lang', lang)

        return el

org.wayround.utils.factory.class_generate_attributes(
    MessageBody,
    ['xmllang', 'text']
    )
org.wayround.utils.factory.class_generate_check(
    MessageBody,
    ['xmllang', 'text']
    )


class MessageSubject:

    def __init__(self, text, xmllang=None):

        self.set_text(text)
        self.set_xmllang(xmllang)

    def check_text(self, value):
        if not isinstance(value, str):
            raise ValueError("`text' must be str")

    def check_lang(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`lang' must be str")

    @classmethod
    def new_from_element(cls, element):

        if type(element) != lxml.etree._Element:
            raise ValueError("`element' must be lxml.etree.Element")

        tag = org.wayround.utils.lxml.parse_element_tag(
            element, 'subject', None
            )[0]

        if tag == None:
            raise ValueError("invalid tag")

        cl = cls()
        cl.set_text(element.text)
        cl.set_lang(element.get('xml:lang'))

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('subject')

        text = self.get_text()
        if text:
            el.text = text

        lang = self.get_lang()
        if lang:
            el.set('xml:lang', lang)

        return el

org.wayround.utils.factory.class_generate_attributes(
    MessageSubject,
    ['xmllang', 'text']
    )
org.wayround.utils.factory.class_generate_check(
    MessageSubject,
    ['xmllang', 'text']
    )


class MessageThread:

    def __init__(self, thread, parent=None):

        self.set_thread(thread)
        self.set_parent(parent)

    def check_thread(self, value):
        if not isinstance(value, str):
            raise ValueError("`thread' must be str")

    def check_parent(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`parent' must be str")

    @classmethod
    def new_from_element(cls, element):

        if type(element) != lxml.etree._Element:
            raise ValueError("`element' must be lxml.etree.Element")

        tag = org.wayround.utils.lxml.parse_element_tag(
            element, 'thread', None
            )[0]

        if tag == None:
            raise ValueError("invalid tag")

        cl = cls(thread=element.text)
        cl.set_parent(element.get('parent'))

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('thread')

        thread = self.get_thread()
        if thread:
            el.text = thread

        parent = self.get_parent()
        if parent:
            el.set('parent', parent)

        return el

org.wayround.utils.factory.class_generate_attributes(
    MessageThread,
    ['parent', 'thread']
    )
org.wayround.utils.factory.class_generate_check(
    MessageThread,
    ['parent', 'thread']
    )


class PresenceShow:

    def __init__(self, text):

        self.set_text(text)

    def check_text(self, value):
        if not value in ['away', 'chat', 'dnd', 'xa']:
            raise ValueError("`show' must be in ['away', 'chat', 'dnd', 'xa']")

    @classmethod
    def new_from_element(cls, element):

        if type(element) != lxml.etree._Element:
            raise ValueError("`element' must be lxml.etree.Element")

        tag = org.wayround.utils.lxml.parse_element_tag(
            element, 'show', None
            )[0]

        if tag == None:
            raise ValueError("invalid tag")

        cl = cls(text=element.text)

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('show')

        text = self.get_text()
        if text:
            el.text = text

        return el

org.wayround.utils.factory.class_generate_attributes(
    PresenceShow,
    ['text']
    )
org.wayround.utils.factory.class_generate_check(
    PresenceShow,
    ['text']
    )


class PresenceStatus:

    def __init__(self, text=None, xmllang=None):

        self.set_text(text)
        self.set_xmllang(xmllang)

    def check_text(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`text' must be str")

    def check_xmllang(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`xmllang' must be str")

    @classmethod
    def new_from_element(cls, element):

        if type(element) != lxml.etree._Element:
            raise ValueError("`element' must be lxml.etree.Element")

        tag = org.wayround.utils.lxml.parse_element_tag(
            element, 'status', None
            )[0]

        if tag == None:
            raise ValueError("invalid tag")

        cl = cls(text=element.text)
        cl.set_xmllang(element.get('xml:lang'))

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('status')

        text = self.get_text()
        if text:
            el.text = text

        lang = self.get_xmllang()
        if lang:
            el.set('xml:lang', lang)

        return el

org.wayround.utils.factory.class_generate_attributes(
    PresenceStatus,
    ['xmllang', 'text']
    )
org.wayround.utils.factory.class_generate_check(
    PresenceStatus,
    ['xmllang', 'text']
    )


class StanzaErrorMalformed(Exception):
    pass


class StanzaError:

    def __init__(
        self,
        xmlns=None, error_type=None, condition=None, text=None, code=None
        ):

        self.set_xmlns(xmlns)
        self.set_error_type(error_type)
        self.set_condition(condition)
        self.set_text(text)
        self.set_code(code)

    def check_xmlns(self, value):
        if not value in ['jabber:client', 'jabber:server']:
            raise ValueError(
                "`xmlns' must be in ['jabber:client', 'jabber:server']"
                )

    def check_error_type(self, value):
        if not value in ['auth', 'cancel', 'continue', 'modify', 'wait']:
            raise ValueError("invalid `error_type'")

    def check_condition(self, value):
        if not value in STANZA_ERROR_NAMES:
            raise ValueError(
                "invalid error `condition'"
                )

    def check_text(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`text' must be None or str")

    def check_code(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`code' must be None or str")

    @classmethod
    def new_from_element(cls, element):

        if not is_stanza_element(element):
            raise ValueError("Not a stanza element")

        found = False
        qname = None
        for i in element:
            qname = lxml.etree.QName(i)
            if (qname.localname == 'error'
                and qname.namespace in ['jabber:client', 'jabber:server']):
                element = i
                found = True

        if not found:
            raise ValueError("Stanza has no error element")

        condition = None
        text = None

        if len(element) == 0:
            raise StanzaErrorMalformed("error element has no children")

        error_type = element.get('type')
        code = element.get('code')

        if not error_type:
            raise StanzaErrorMalformed("error element has no type")

        for i in element:
            tag_parsed = lxml.etree.QName(i)

            ns = tag_parsed.namespace
            tag = tag_parsed.localname

            if ns == 'urn:ietf:params:xml:ns:xmpp-stanzas':

                if tag == 'text':
                    text = i.text
                    break

        for i in element:
            tag_parsed = lxml.etree.QName(i)

            ns = tag_parsed.namespace
            tag = tag_parsed.localname

            if ns == 'urn:ietf:params:xml:ns:xmpp-stanzas':

                if tag != 'text':
                    condition = tag
                    break

        if not condition in STANZA_ERROR_NAMES:
            raise StanzaErrorMalformed(
                "Stanza error has invalid condition"
                )

        cl = cls(
            xmlns=qname.namespace,
            error_type=error_type,
            condition=condition,
            text=text,
            code=code
            )

        cl.check()

        return cl

    @classmethod
    def new_from_stanza(cls, stanza):

        if not isinstance(stanza, Stanza):
            raise ValueError("`stanza' must be Stanza")

        return cls.new_from_element(stanza.get_element())

    def to_text(self):

        return """\
Error Type: {}
Condition: {}
Code: {}
Text:
{}
""".format(
        self.get_error_type(),
        self.get_condition(),
        self.get_code(),
        self.get_text()
        )

    gen_text = to_text

org.wayround.utils.factory.class_generate_attributes(
    StanzaError,
    ['xmlns', 'error_type', 'condition', 'text', 'code']
    )
org.wayround.utils.factory.class_generate_check(
    StanzaError,
    ['xmlns', 'error_type', 'condition', 'text', 'code']
    )


# TODO: what is this? and what for?
def element_add_object(element, obj):

    if type(element) != lxml.etree._Element:
        raise TypeError("`element' must be lxml.etree._Element")

    if not isinstance(obj, list):
        obj = [obj]

    for i in obj:

        if type(i) == lxml.etree._Element:
            element.append(i)

        elif isinstance(i, bytes):
            element.append(
                lxml.etree.fromstring(str(i, 'utf-8'))
                )

        elif isinstance(i, str):
            element.append(
                lxml.etree.fromstring(i)
                )

        else:
            logging.warning(
                "Adding directly unsupported element"
                " type as element child {}".format(type(i))
                )
            element.append(
                lxml.etree.fromstring(str(i))
                )
    return


class StanzaProcessor(org.wayround.utils.signal.Signal):

    """
    Signals:
    ('new_stanza', self, stanza)
    ('new_stanza_to_send, self, stanza')
    ('response_stanza', self, stanza)
    """

    def __init__(self):

        super().__init__(['new_stanza', 'response_stanza'])

        self._io_machine = None

        self.response_cbs = {}

        self._stanza_id_generation_unifire = uuid.uuid4().hex
        self._stanza_id_generation_counter = 0

        self._wait_callbacks = {}

    def connect_io_machine(self, io_machine):
        """
        :param XMPPIOStreamRWMachine io_machine:
        """
        self._io_machine = io_machine
        self._io_machine.connect_signal(
            'in_element_readed',
            self._on_input_object
            )

    def disconnect_io_machine(self):
        """
        :param XMPPIOStreamRWMachine io_machine:
        """
        self._io_machine.disconnect_signal(self._on_input_object)
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

        if wait == None or wait > 0, ide_mode = 'generate_implicit' and cb
        generated internally

        `wait' is timeout. it is passed to Event.wait(), so wait == None is
        wait forever. (which can lead to deadlock)

        ide_mode must be in ['from_stanza', 'generate', 'generate_implicit',
        'implicit'].

        if ide_mode == 'from_stanza', then id taken from stanza.

        if ide_mode == 'generate', then id generated for stanza if stanza has
        no it's own id.

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

        new_stanza_ide = stanza_obj.get_ide()

        self._stanza_id_generation_unifire = uuid.uuid4().hex
        self._stanza_id_generation_counter += 1

        if wait != None and not isinstance(wait, (bool, int,)):
            raise TypeError("`wait' must be None, bool or int")

        if wait == True:
            wait = 10
            ide_mode = 'generate_implicit'

        elif wait == False:
            wait = 0

        elif isinstance(wait, int) and wait < 0:
            wait = None

        if not ide_mode in [
            'from_stanza', 'generate', 'generate_implicit', 'implicit'
            ]:
            raise ValueError("wrong value for ide_mode parameter")

        if isinstance(wait, int) and wait > 0 and cb != None:
            raise ValueError("`cb' must be None if `wait' > 0")

        if ide_mode == 'from_stanza':
            new_stanza_ide = stanza_obj.get_ide()

        elif ide_mode in ['generate', 'generate_implicit']:
            if ((not stanza_obj.get_ide() and ide_mode == 'generate')
                or ide_mode == 'generate_implicit'):

                new_stanza_ide = '{}-stanza-{}'.format(
                    self._stanza_id_generation_unifire,
                    hex(self._stanza_id_generation_counter)
                    )

        elif ide_mode == 'implicit':

            new_stanza_ide = ide
        else:
            raise Exception("Programming error")

        stanza_obj.set_ide(new_stanza_ide)

        if wait == None or (isinstance(wait, int) and wait > 0):
            cb = self._wait_callback

        if cb:
            if not new_stanza_ide:
                raise ValueError("callback provided but stanza has no id")

            self.response_cbs[new_stanza_ide] = cb

        if wait == 0:
            ret = new_stanza_ide

        if wait == None or (isinstance(wait, int) and wait > 0):
            self._wait_callbacks[new_stanza_ide] = {
                'event': threading.Event(),
                'response': None
                }

        self._io_machine.send(stanza_obj.to_str())

        if wait == None or (isinstance(wait, int) and wait > 0):
            wait_res = self._wait_callbacks[new_stanza_ide]['event'].wait(wait)

            if wait_res == False:
                ret = False
            else:
                ret = self._wait_callbacks[new_stanza_ide]['response']

            del self._wait_callbacks[new_stanza_ide]
            self.delete_callback(new_stanza_ide)

        return ret

    def delete_callback(self, ide):

        while ide in self.response_cbs:
            del self.response_cbs[ide]

        return

    def _wait_callback(self, obj):

        ide = obj.get_ide()
        self._wait_callbacks[ide]['response'] = obj
        self._wait_callbacks[ide]['event'].set()

        return

    def _on_input_object(self, signal_name, io_machine, obj):

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

            stanza = Stanza.new_from_element(obj)

            if isinstance(stanza, Stanza):

                ide = stanza.get_ide()

                if ide in self.response_cbs:

                    self.response_cbs[ide](stanza)

                    del self.response_cbs[ide]

                    self.emit_signal('response_stanza', self, stanza)

                else:

                    self.emit_signal('new_stanza', self, stanza)

            else:
                logging.error(
                    "proposed object not a stanza({}):\n{}".format(stanza, obj)
                    )

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


def start_stream_tpl(
    from_jid,
    to_jid,
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
<stream:stream from="{from_jid}" to="{to_jid}" version="{version}"\
 xml:lang="{xmllang}" xmlns="{xmlns}"\
 xmlns:stream="{xmlns_stream}">""".format(
        from_jid=xml.sax.saxutils.escape(from_jid),
        to_jid=xml.sax.saxutils.escape(to_jid),
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


class STARTTLS:

    @classmethod
    def new_from_element(cls, element):

        if type(element) != lxml.etree._Element:
            raise ValueError("`element' must be lxml.etree.Element")

        tag = org.wayround.utils.lxml.parse_element_tag(
            element, 'starttls', ['urn:ietf:params:xml:ns:xmpp-tls']
            )[0]

        if tag is None:
            raise ValueError("Invalid element")

        return cls()

    def gen_element(self):
        ret = lxml.etree.Element('starttls')
        ret.set('xmlns', 'urn:ietf:params:xml:ns:xmpp-tls')
        return ret


class Bind:

    def __init__(self, typ='resource', value=None):

        self.set_typ(typ)
        self.set_value(value)

    def check_typ(self, value):
        if not value in ['resource', 'fulljid']:
            raise ValueError("Wrong bind type")

    def check_value(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`value' must be None or str")

    @classmethod
    def new_from_element(cls, element):
        # TODO: to do
        pass

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('bind')
        el.set('xmlns', 'urn:ietf:params:xml:ns:xmpp-bind')

        value = self.get_value()

        if value != None:
            tag_name = ''

            typ = self.get_typ()

            if typ == 'resource':
                tag_name = 'resource'

            elif typ == 'fulljid':
                tag_name = 'jid'

            add_value = lxml.etree.Element(tag_name)
            add_value.text = value

            el.append(add_value)

        return el

org.wayround.utils.factory.class_generate_attributes(
    Bind,
    ['typ', 'value']
    )
org.wayround.utils.factory.class_generate_check(
    Bind,
    ['typ', 'value']
    )


class Session:

    @classmethod
    def new_from_element(cls, element):

        if type(element) != lxml.etree._Element:
            raise ValueError("`element' must be lxml.etree.Element")

        tag = org.wayround.utils.lxml.parse_element_tag(
            element, 'session', ['urn:ietf:params:xml:ns:xmpp-session']
            )[0]

        if tag is None:
            raise ValueError("Invalid element")

        return cls()

    def gen_element(self):
        ret = lxml.etree.Element('session')
        ret.set('xmlns', 'urn:ietf:params:xml:ns:xmpp-session')
        return ret


class IQRoster:

    def __init__(self, item=None, ver=None):
        if item is None:
            item = []

        self.set_item(item)
        self.set_ver(ver)

    def check_item(self, value):
        if not org.wayround.utils.types.struct_check(
            value,
            {'t': list, '.': {'t': IQRosterItem}}
            ):
            raise ValueError("`item' must be list of IQRosterItem")

    def check_ver(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`ver' must be None or str")

    def get_item_dict(self):

        items = self.get_item()
        ret = {}
        for i in items:
            ret[i.get_jid()] = i

        return ret

    @classmethod
    def new_from_element(cls, element):

        tag = org.wayround.utils.lxml.parse_element_tag(
            element,
            'query',
            ['jabber:iq:roster']
            )[0]

        if tag == None:
            raise ValueError("Invalid roster query `element'")

        cl = cls()

        org.wayround.utils.lxml.elem_props_to_object_props(
            element, cl,
            [
             ('ver', 'ver')
             ]
            )

        org.wayround.utils.lxml.subelemsm_to_object_propsm(
            element, cl,
            [
             ('{jabber:iq:roster}item', IQRosterItem, 'item')
             ]
            )

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        element = lxml.etree.Element('query')
        element.set('xmlns', 'jabber:iq:roster')

        org.wayround.utils.lxml.object_props_to_elem_props(
            self, element,
            [
             ('ver', 'ver')
             ]
            )

        org.wayround.utils.lxml.object_propsm_to_subelemsm(
            self, element,
            ['item']
            )

        return element


org.wayround.utils.factory.class_generate_attributes(
    IQRoster,
    ['item', 'ver']
    )
org.wayround.utils.factory.class_generate_check(
    IQRoster,
    ['item', 'ver']
    )


class IQRosterItem:

    def __init__(
        self,
        group=None, approved=None, ask=None, jid=None,
        name=None, subscription=None
        ):

        if group is None:
            group = []

        self.set_group(group)
        self.set_approved(approved)
        self.set_ask(ask)
        self.set_jid(jid)
        self.set_name(name)
        self.set_subscription(subscription)

    def check_group(self, value):
        if not org.wayround.utils.types.struct_check(
            value,
            {'t': list, '.': {'t': str}}
            ):
            raise ValueError("`groups' must be list of str")

    def check_approved(self, value):
        if value is not None and not isinstance(value, bool):
            raise ValueError("`approved' must be None or bool")

    def check_ask(self, value):
        if value is not None and value != 'subscribe':
            raise ValueError("`ask' can be None or 'subscribe'")

    def check_jid(self, value):
        if not isinstance(value, str):
            raise ValueError("`jid' must be str")

    def check_name(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`name' must be str")

    def check_subscription(self, value):
        if not value in [
            None, 'both', 'from', 'none', 'remove', 'to'
            ]:
            raise ValueError(
    "`subscription' must be in [None, 'both','from','none','remove','to']"
                )

    @classmethod
    def new_from_element(cls, element):

        tag = org.wayround.utils.lxml.parse_element_tag(
            element,
            'item',
            ['jabber:iq:roster']
            )[0]

        if tag == None:
            raise ValueError("Invalid roster query `element'")

        cl = cls(jid=element.get('jid'))

        cl.set_approved(element.get('approved') in ['1', 'true'])

        org.wayround.utils.lxml.elem_props_to_object_props(
            element, cl,
            [
             ('ask', 'ask'),
             ('name', 'name'),
             ('subscription', 'subscription')
             ]
            )

        groups = cl.get_group()
        groups_els = element.findall('{jabber:iq:roster}group')
        for i in groups_els:
            groups.append(i.text)

        cl.check()

        return cl

    def gen_element(self):

        element = lxml.etree.Element('item')

        org.wayround.utils.lxml.object_props_to_elem_props(
            self, element,
            [
             ('ask', 'ask'),
             ('jid', 'jid'),
             ('name', 'name'),
             ('subscription', 'subscription')
             ]
            )

        approved = '0'
        if self.get_approved():
            approved = '1'

        element.set('approved', approved)

        groups = self.get_groups()
        for i in groups:
            group_el = lxml.etree.Element('group')
            group_el.text = i
            element.append(group_el)

        return element

org.wayround.utils.factory.class_generate_attributes(
    IQRosterItem,
    ['group', 'approved', 'ask', 'jid', 'name', 'subscription']
    )
org.wayround.utils.factory.class_generate_check(
    IQRosterItem,
    ['group', 'approved', 'ask', 'jid', 'name', 'subscription']
    )


def determine_stream_error(xml_element):

    """
    Returns None if not isinstance(xml_element, lxml.etree._Element)

    Returns False if not {http://etherx.jabber.org/streams}error

    Returns dict(name='text', text='text') with name and text as described in
    paragraph 4.9. of rfc-6120 in case of successful error recognition

    dict['name'] can have additionally one of two special values, both of which
    means standard violation thus presume some tag of xmpp error:
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

    if returned condition in ['invalid-condition', 'undefined-condition']
    stanza must be considered wrong
    """

    ret = None

    if not isinstance(stanza, Stanza) and is_stanza_element(stanza):
        stanza = Stanza.new_from_element(stanza)

    if not isinstance(stanza, Stanza):
        ret = None
    else:

        if stanza.get_typ() == 'error':
            e1 = stanza.get_element().find('{jabber:client}error')
            ret = determine_stanza_element_error(e1)
        else:
            ret = False

    return ret


def determine_stanza_element_error(element):

    if type(element) != lxml.etree._Element:
        raise TypeError("`element' must be lxml.etree._Element")

    if not element.tag == '{jabber:client}error':
        raise ValueError("`element' must be {jabber:client}error")

    ret = None

    condition = None
    text = None
    error_type = None
    code = None

    e1 = element

    if e1 == None:
        ret = None
    else:

        if len(e1) == 0:
            ret = None
        else:

            error_type = e1.get('type')
            code = e1.get('code')

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
                    'error_type': error_type,
                    'condition': condition,
                    'text': text,
                    'code': code
                    }

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
