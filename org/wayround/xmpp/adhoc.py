
import uuid

import lxml.etree

import org.wayround.utils.signal

import org.wayround.xmpp.core
import org.wayround.xmpp.xdata
import org.wayround.xmpp.disco

def get_commands_list(jid_to, jid_from, stanza_processor=None):

    q = org.wayround.xmpp.disco.get_info(
        jid_to, jid_from, None, stanza_processor
        )

    ret = None

    if q != None:
        r = q.find(
            "{http://jabber.org/protocol/disco#info}feature[@var='http://jabber.org/protocol/commands']"
            )

        if r != None:
            q = org.wayround.xmpp.disco.get_items(
                jid_to,
                jid_from,
                'http://jabber.org/protocol/commands',
                stanza_processor
                )

            if q != None:

                items = q.findall('{http://jabber.org/protocol/disco#items}item')

                ret = {}

                for i in items:

                    ret[i.get('node')] = {
                        'jid': i.get('jid'),
                        'name': i.get('name')
                        }

    return ret


def is_command_element(element):
    return (
        type(element) == lxml.etree._Element and
        element.tag == '{http://jabber.org/protocol/commands}command'
        )

def extract_element_commands(element):

    if type(element) != lxml.etree._Element:
        raise TypeError("`element' must be of type lxml.etree._Element")

    ret = []

    for i in element:
        if is_command_element(i):
            ret.append(i)

    return ret

class Command:

    def __init__(
        self,
        node=None,
        sessionid=None,
        action=None,
        actions=None,
        execute=None,
        status=None,
        body=None
        ):

        aa = is_command_element(body)

        if aa:

            if node or sessionid or action or actions or execute or status:
                raise ValueError(
"if `body' is XML command element, then all other parameters must be not set"
                    )

        self.body = body

        if not aa:

            self.node = node
            self.sessionid = sessionid
            self.action = action
            self.actions = actions
            self.execute = execute
            self.status = status

        return

    node = None
    sessionid = None
    action = None
    status = None

    for i in [
        ('node', 'node'),
        ('sessionid', 'sessionid'),
        ('action', 'action'),
        ('status', 'status')
        ]:
        check = ''
        if i[0] == 'action':
            check = 'self._action_check(value)'
        if i[0] == 'status':
            check = 'self._status_check(value)'
        exec(
"""
@property
def {meth_name}(self):

    ret = self._body.get('{elem_attr}')

    return ret

@{meth_name}.setter
def {meth_name}(self, value):

    {check}

    if value == None:
        if '{elem_attr}' in self._body.attrib:
            del self._body.attrib['{elem_attr}']
    else:
        self._body.set('{elem_attr}', value)

    return
""".format(meth_name=i[0], elem_attr=i[1], check=check)
        )

    def _action_check(self, action):
        if not action in [None, 'cancel', 'complete', 'execute', 'next', 'prev']:
            raise ValueError("action is invalid")
        return

    def _status_check(self, status):
        if not status in [None, 'canceled', 'completed', 'executing']:
            raise ValueError("`status' is invalid")
        return

    @property
    def actions(self):

        ret = None

        a = self._body.findall('{http://jabber.org/protocol/commands}actions')

        if a != None and len(a) != 0:
            a = a[0]

            lst = set()

            for i in a:
                res = lxml.etree.QName(i)
                tag = res.localname

                lst.add(tag)

            lst = list(a)
            ret = lst

        return ret

    @actions.setter
    def actions(self, val):

        if val != None:
            if not isinstance(val, list):
                raise TypeError("value must be list")
            else:
                for i in val:
                    self._action_check(i)

        e = self.execute

        a = self._body.findall('{http://jabber.org/protocol/commands}actions')

        for i in a[:]:
            self._body.remove(i)

        if isinstance(val, list):

            el = lxml.etree.Element('{http://jabber.org/protocol/commands}actions')
            for i in val:
                el.append(lxml.etree.Element(i))

            self._body.insert(0, el)

            self.execute = e

        return

    @property
    def execute(self):
        ret = None

        a = self._body.findall('{http://jabber.org/protocol/commands}actions')

        if a != None and len(a) != 0:
            a = a[0]
            ret = a.get('execute')

        return ret

    @execute.setter
    def execute(self, val):
        if val != None and not isinstance(val, str):
            raise TypeError("value must be str or None")

        a = self._body.findall('{http://jabber.org/protocol/commands}actions')

        if len(a) == 0:
            pass
        else:
            a = a[0]

            if val == None:
                if 'execute' in a.attrib:
                    del a.attrib['execute']
            else:
                a.set('execute', val)

        return

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, obj):

        if obj == None:
            obj = []

        if is_command_element(obj):
            self._body = obj
        else:

            self._body = lxml.etree.Element('command')
            self._body.set('xmlns', 'http://jabber.org/protocol/commands')

            org.wayround.xmpp.core.element_add_object(self._body, obj)

        return

    def __str__(self):
        return self.to_str()

    def to_str(self):
        ret = lxml.etree.tostring(self._body)
        if isinstance(ret, bytes):
            ret = str(ret, 'utf-8')
        return ret


class CommandProcessor(org.wayround.utils.signal.Signal):

    """
    Signals:
    """

    def __init__(self):

        super().__init__([])

        self._io_machine = None

        self.response_cbs = {}

        self._stanza_id_generation_unifire = uuid.uuid4().hex
        self._stanza_id_generation_counter = 0

        self._wait_callbacks = {}


    def connect_stanza_processor(self, stanza_processor):
        """
        :param XMPPIOStreamRWMachine stanza_processor:
        """
        self._stanza_processor = stanza_processor
        self._stanza_processor.connect_signal(
            'new_stanza',
            self._on_new_stanza
            )

    def disconnect_stanza_processor(self):
        """
        :param XMPPIOStreamRWMachine stanza_processor:
        """
        self._stanza_processor.disconnect_signal(self._on_input_object)
        self._stanza_processor = None


    def _on_new_stanza(self):
        pass


