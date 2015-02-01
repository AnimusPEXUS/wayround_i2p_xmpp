
"""
Implementation of XMPP Ad-Hoc commands protocol
"""

import lxml.etree

import wayround_org.utils.threading
import wayround_org.utils.lxml

import wayround_org.xmpp.core
import wayround_org.xmpp.disco


def get_commands_list(to_jid, from_jid, stanza_processor=None):

    ret = None

    q = wayround_org.xmpp.disco.get_info(
        to_jid, from_jid, None, stanza_processor
        )[0]

    if q is not None:

        if q.has_feature('http://jabber.org/protocol/commands'):
            q = wayround_org.xmpp.disco.get_items(
                to_jid,
                from_jid,
                'http://jabber.org/protocol/commands',
                stanza_processor
                )[0]

            if q is not None:

                items = q.get_item()

                ret = {}

                for i in items:

                    node = i.get_node()

                    if node is not None:

                        ret[node] = {
                            'jid': i.get_jid(),
                            'name':  '{} ({})'.format(i.get_name(), node)
                            }

    return ret


def is_command_element(element):
    return (
        wayround_org.utils.lxml.is_lxml_tag_element(element) and
        element.tag == '{http://jabber.org/protocol/commands}command'
        )


def extract_element_commands(element):

    if not wayround_org.utils.lxml.is_lxml_tag_element(element):
        raise TypeError("`element' must be of type lxml tag element")

    ret = []

    for i in element:
        if wayround_org.utils.lxml.is_lxml_tag_element(i):
            if is_command_element(i):
                ret.append(Command.new_from_element(i))

    return ret


class Command:

    def __init__(
            self, objects=None,

            note=None,

            sessionid=None, node=None, action=None, status=None,

            actions=None, execute=None,

            xdata=None
            ):

        if objects is None:
            objects = []

        if actions is None:
            actions = []

        if note is None:
            note = []

        if xdata is None:
            xdata = []

        self.set_element(None)
        self.set_objects(objects)

        self.set_note(note)

        self.set_sessionid(sessionid)
        self.set_node(node)
        self.set_action(action)
        self.set_status(status)

        self.set_actions(actions)
        self.set_execute(execute)

        self.set_xdata(xdata)

        return

    def check_element(self, value):
        if value is not None and not is_command_element(value):
            raise TypeError(
                "`element' must be stanza command lxml.etree.Element"
                )

    def check_objects(self, value):
        for i in value:
            if (not hasattr(i, 'gen_element')
                or not callable(getattr(i, 'gen_element'))):
                raise ValueError(
                    "all objects in `objects' must have gen_element() method"
                    )

    def check_note(self, value):
        if not wayround_org.utils.types.struct_check(
            value,
            {'t': list, '.': {'t': CommandNote}}
            ):
            raise ValueError("`note' must be list of CommandNote")

    def check_sessionid(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`sessionid' must be str")

    def check_node(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`node' must be None or str")

    def check_action(self, value):
        if not value in [
                None, 'cancel', 'complete', 'execute', 'next', 'prev'
                ]:
            raise ValueError("value is invalid")

    def check_status(self, value):
        if not value in [None, 'canceled', 'completed', 'executing']:
            raise ValueError("`value' is invalid")

    def check_actions(self, value):
        for i in value:
            if not i in ['cancel', 'complete', 'execute', 'next', 'prev']:
                raise ValueError("actions is invalid")

    def check_execute(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`execute' must be str")

    def check_xdata(self, value):
        if not wayround_org.utils.types.struct_check(
            value,
            {'t': list, '.': {'t': wayround_org.xmpp.xdata.XData}}
            ):
            raise ValueError(
                "`xdata' must be list of wayround_org.xmpp.xdata.XData"
                )

    @classmethod
    def new_from_element(cls, element):

        tag = wayround_org.utils.lxml.parse_element_tag(
            element, 'command', ['http://jabber.org/protocol/commands']
            )[0]

        if tag is None:
            raise ValueError("Invalid element")

        ret_class = cls()

        ret_class.set_element(element)

        wayround_org.utils.lxml.elem_props_to_object_props(
            element, ret_class,
            [
                ('sessionid', 'sessionid'),
                ('node', 'node'),
                ('action', 'action'),
                ('status', 'status')
                ]
            )

        wayround_org.utils.lxml.subelemsm_to_object_propsm(
            element, ret_class,
            [
             ('{http://jabber.org/protocol/commands}note',
              CommandNote,
              'note', 
              '*'
              ),
             ('{jabber:x:data}x',
              wayround_org.xmpp.xdata.XData,
              'xdata', 
              '*'
              )
             ]
            )

        ret_class.check()

        return ret_class

    def gen_element(self):

        self.check()

        ret_element = lxml.etree.Element('command')
        ret_element.set('xmlns', 'http://jabber.org/protocol/commands')

        wayround_org.utils.lxml.object_props_to_elem_props(
            self, ret_element,
            [
                ('sessionid', 'sessionid'),
                ('node', 'node'),
                ('action', 'action'),
                ('status', 'status')
                ]
            )

        wayround_org.utils.lxml.object_propsm_to_subelemsm(
            self, ret_element,
            ['note', 'xdata']
            )

        actions = self.get_actions()
        execute = self.get_execute()

        if actions or execute:
            new_element = lxml.etree.Element('actions')
            if execute:
                new_element.set('execute', execute)
            for i in actions:
                new_element.append(lxml.etree.Element(i))

            ret_element.append(new_element)

        objects = self.get_objects()
        for i in objects:
            ret_element.append(i.gen_element())

        return ret_element

wayround_org.utils.factory.class_generate_attributes(
    Command,
    ['element', 'objects', 'note', 'sessionid', 'node', 'action', 'status',
     'actions', 'execute', 'xdata']
    )
wayround_org.utils.factory.class_generate_check(
    Command,
    ['element', 'objects', 'note', 'sessionid', 'node', 'action', 'status',
     'actions', 'execute', 'xdata']
    )


class CommandNote:

    def __init__(self, text='', typ='info'):

        self.set_text(text)
        self.set_typ(typ)

    def check_text(self, value):
        if not isinstance(value, str):
            raise ValueError("`text' must be str")

    def check_typ(self, value):
        if not value in ['info', 'error', 'warn']:
            raise ValueError("`typ' must be in ['info', 'error', 'warn']")

    @classmethod
    def new_from_element(cls, element):

        tag = wayround_org.utils.lxml.parse_element_tag(
            element, 'note', ['http://jabber.org/protocol/commands']
            )[0]

        if tag is None:
            raise ValueError("Invalid element")

        cl = cls()

        wayround_org.utils.lxml.elem_props_to_object_props(
            element, cl,
            [
             ('type', 'typ')
             ]
            )

        cl.set_text(element.text)

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        element = lxml.etree.Element('note')

        wayround_org.utils.lxml.object_props_to_elem_props(
            self, element,
            [
             ('typ', 'type')
             ]
            )

        element.text = self.get_text()

        return element

wayround_org.utils.factory.class_generate_attributes(
    CommandNote,
    ['text', 'typ']
    )
wayround_org.utils.factory.class_generate_check(
    CommandNote,
    ['text', 'typ']
    )
