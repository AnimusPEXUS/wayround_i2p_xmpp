
import datetime

import lxml.etree
import org.wayround.utils.factory
import org.wayround.utils.lxml
import org.wayround.utils.types

import org.wayround.xmpp.core
import org.wayround.xmpp.xdata

NAMESPACE = 'http://jabber.org/protocol/muc'
NAMESPACE_LENGTH = len(NAMESPACE)

X_XMLNS = ['', '#user']
QUERY_XMLNS = ['#admin', '#owner']
UNIQUE_XMLNS = ['#unique']

NAMESPACES = []
for i in X_XMLNS + QUERY_XMLNS + UNIQUE_XMLNS:
    NAMESPACES.append(NAMESPACE + i)
del i


class X:

    def __init__(
        self,
        xmlns='',
        history=None, password=None,

        decline=None, destroy=None, invite=None, item=None, status=None
        ):

        if invite == None:
            invite = []

        if status == None:
            status = []

        self.set_xmlns(xmlns)

        self.set_history(history)
        self.set_password(password)

        self.set_decline(decline)
        self.set_destroy(destroy)
        self.set_invite(invite)
        self.set_item(item)
        self.set_status(status)

        return

    def check_xmlns(self, value):
        if not value in X_XMLNS:
            raise ValueError(
            "`xmlns' must be in ['', '#user']"
            )

    def check_history(self, value):
        if value != None and not isinstance(value, History):
            raise ValueError("`history' must be History or None")

    def check_password(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`password' must be None or str")

    def check_decline(self, value):
        if value != None and not isinstance(value, Decline):
            raise ValueError("`decline' must be None or Decline")

    def check_destroy(self, value):
        if value != None and not isinstance(value, Destroy):
            raise ValueError("`destroy' must be None or Destroy")

    def check_invite(self, value):
        if not org.wayround.utils.types.struct_check(
            value,
            {'t': list, '.': {'t': Invite}}
            ):
            raise ValueError("`invite' must be list of Invite")

    def check_item(self, value):
        if value != None and not isinstance(value, Item):
            raise ValueError("`item' must be None or Item")

    def check_status(self, value):
        if not org.wayround.utils.types.struct_check(
            value,
            {'t': list, '.': {'t': int}}
            ):
            raise ValueError("`value' must be list of Status")

    @classmethod
    def new_from_element(cls, element):

        xmlns = check_element_and_namespace(element, 'x')

        cl = cls()
        cl.set_xmlns(xmlns)

        org.wayround.utils.lxml.subelems_to_object_props(
            element, cl,
            [
             ('{{http://jabber.org/protocol/muc{}}}history'.format(xmlns),
              History,
              'history'),
             ('{{http://jabber.org/protocol/muc{}}}decline'.format(xmlns),
              Decline,
              'decline'),
             ('{{http://jabber.org/protocol/muc{}}}destroy'.format(xmlns),
              Destroy,
              'destroy'),
             ('{{http://jabber.org/protocol/muc{}}}item'.format(xmlns),
              Item,
              'item')
             ]
            )

        org.wayround.utils.lxml.subelemsm_to_object_propsm(
            element, cl,
            [
             ('{{http://jabber.org/protocol/muc{}}}invite'.format(xmlns),
              Invite,
              'invite')
             ]
            )

        status = []

        for i in element:
            if i.tag == '{{http://jabber.org/protocol/muc{}}}status'.format(
                xmlns
                ):
                status.append(int(i.get('code')))

        cl.set_status(status)

        password_el = element.find(
            '{{http://jabber.org/protocol/muc{}}}password'.format(xmlns)
            )
        if password_el != None:
            cl.set_password(password_el.text)

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('x')
        el.set(
            'xmlns',
            'http://jabber.org/protocol/muc{}'.format(self.get_xmlns())
            )

        org.wayround.utils.lxml.object_props_to_subelems(
            self, el, ['history', 'decline', 'destroy', 'item']
            )

        password = self.get_password()
        if password != None:
            password_el = lxml.etree.Element('password')
            password_el.text = password
            el.append(password_el)

        org.wayround.utils.lxml.object_propsm_to_subelemsm(
            self, el, ['invite']
            )

        for i in self.get_status():

            e = lxml.etree.Element('status')
            e.set('code', '{:03d}'.format(i.get_code()))
            el.append(e)

        return el

org.wayround.utils.factory.class_generate_attributes(
    X,
    ['xmlns', 'history', 'password', 'decline', 'destroy', 'invite',
     'item', 'password', 'status']
    )
org.wayround.utils.factory.class_generate_check(
    X,
    ['xmlns', 'history', 'password', 'decline', 'destroy', 'invite',
     'item', 'password', 'status']
    )


class Query:

    def __init__(self, xmlns='#owner', item=None, destroy=None, xdata=None):

        if item == None:
            item = []

        self.set_xmlns(xmlns)
        self.set_item(item)
        self.set_destroy(destroy)
        self.set_xdata(xdata)

    def check_xmlns(self, value):
        if not value in QUERY_XMLNS:
            raise ValueError(
            "`xmlns' must be in ['#admin', '#owner']"
            )

    def check_item(self, value):
        if not org.wayround.utils.types.struct_check(
            value, {'t': list, '.': {'t': Item}}
            ):
            raise ValueError("`item' must be list of Item")

    def check_destroy(self, value):
        if value != None and not isinstance(value, Destroy):
            raise ValueError("`destroy' must be None or Destroy")

    def check_xdata(self, value):
        if (value != None
            and not isinstance(value, org.wayround.xmpp.xdata.XData)):
            raise ValueError(
                "`xdata' must be None or org.wayround.xmpp.xdata.XData"
                )

    @classmethod
    def new_from_element(cls, element):

        xmlns = check_element_and_namespace(element, 'query')

        cl = cls()
        cl.set_xmlns(xmlns)

        org.wayround.utils.lxml.subelemsm_to_object_propsm(
            element, cl,
            [('{{http://jabber.org/protocol/muc{}}}item'.format(xmlns),
             Item,
             'item'
             )]
            )

        org.wayround.utils.lxml.subelems_to_object_props(
            element, cl,
            [('{{http://jabber.org/protocol/muc{}}}destroy'.format(xmlns),
             Destroy,
             'destroy'),
            ('{jabber:x:data}x',
             org.wayround.xmpp.xdata.XData,
             'xdata'
             )]
            )

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('query')
        el.set(
            'xmlns',
            'http://jabber.org/protocol/muc{}'.format(self.get_xmlns())
            )

        org.wayround.utils.lxml.object_propsm_to_subelemsm(
            self, el, ['item']
            )

        org.wayround.utils.lxml.object_props_to_subelems(
            self, el, ['destroy', 'xdata']
            )

        return el


org.wayround.utils.factory.class_generate_attributes(
    Query,
    ['xmlns', 'item', 'destroy', 'xdata']
    )
org.wayround.utils.factory.class_generate_check(
    Query,
    ['xmlns', 'item', 'destroy', 'xdata']
    )


class Unique:

    def __init__(self, text):

        self.set_text(text)

    def check_text(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`text' must be None or str")

    @classmethod
    def new_from_element(cls, element):

        xmlns = check_element_and_namespace(element, 'unique')

        if not xmlns == '#unique':
            raise ValueError("`invalid' namespace")

        return cls(element.text)

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('unique')
        el.text = self.get_text()

        return el

org.wayround.utils.factory.class_generate_attributes(
    Unique,
    ['text']
    )
org.wayround.utils.factory.class_generate_check(
    Unique,
    ['text']
    )


class History:

    def __init__(
        self,
        maxchars=None, maxstanzas=None, seconds=None, since=None
        ):

        self.set_maxchars(maxchars)
        self.set_maxstanzas(maxstanzas)
        self.set_seconds(seconds)
        self.set_since(since)

    def check_maxchars(self, value):
        if value != None and not isinstance(value, int):
            raise TypeError("`maxchars' must be None or int")

    def check_maxstanzas(self, value):
        if value != None and not isinstance(value, int):
            raise TypeError("`maxstanzas' must be None or int")

    def check_seconds(self, value):
        if value != None and not isinstance(value, int):
            raise TypeError("`seconds' must be None or int")

    def check_since(self, value):
        if value != None and not isinstance(value, datetime.datetime):
            raise TypeError("`seconds' must be None or datetime.datetime")

    @classmethod
    def new_from_element(cls, element):

        xmlns = check_element_and_namespace(element, 'history')

        cl = cls()
        cl.set_xmlns(xmlns)

        org.wayround.utils.lxml.elem_props_to_object_props(
            element, cl,
            [
             ('maxchars', 'maxchars'),
             ('maxstanzas', 'maxstanzas'),
             ('seconds', 'seconds'),
             ('since', 'since')
             ]
            )

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('history')

        org.wayround.utils.lxml.object_props_to_elem_props(
            self, el,
            [
             ('maxchars', 'maxchars'),
             ('maxstanzas', 'maxstanzas'),
             ('seconds', 'seconds'),
             ('since', 'since')
             ]
            )

        return el

org.wayround.utils.factory.class_generate_attributes(
    History, ['maxchars', 'maxstanzas', 'seconds', 'since']
    )
org.wayround.utils.factory.class_generate_check(
    History, ['maxchars', 'maxstanzas', 'seconds', 'since']
    )


class Decline:

    def __init__(self, reason=None, from_jid=None, to_jid=None):

        self.set_reason(reason)
        self.set_from_jid(from_jid)
        self.set_to_jid(to_jid)

    def check_reason(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`reason' must be None or str")

    def check_from_jid(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`from_jid' must be None or str")

    def check_to_jid(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`to_jid' must be None or str")

    @classmethod
    def new_from_element(cls, element):

        xmlns = check_element_and_namespace(element, 'decline')

        cl = cls()
        cl.set_xmlns(xmlns)

        reason_el = element.find(
            '{{http://jabber.org/protocol/muc{}}}reason'.format(xmlns)
            )
        if reason_el != None:
            cl.set_reason(reason_el.text)

        org.wayround.utils.lxml.elem_props_to_object_props(
            element, cl,
            [
             ('from', 'from_jid'),
             ('to', 'to_jid')
             ]
            )

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('decline')

        org.wayround.utils.lxml.object_props_to_elem_props(
            self, el,
            [
             ('from_jid', 'from'),
             ('to_jid', 'to')
             ]
            )

        reason = self.get_reason()
        if reason != None:
            reason_el = lxml.etree.Element('reason')
            reason_el.text = reason
            el.append(reason_el)

        return el

org.wayround.utils.factory.class_generate_attributes(
    Decline,
    ['reason', 'from_jid', 'to_jid']
    )
org.wayround.utils.factory.class_generate_check(
    Decline,
    ['reason', 'from_jid', 'to_jid']
    )


class Destroy:

    def __init__(self, jid=None, password=None, reason=None):

        self.set_jid(jid)
        self.set_reason(reason)
        self.set_password(password)

    def check_jid(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`jid' must be None or str")

    def check_reason(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`reason' must be None or str")

    def check_password(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`password' must be None or str")

    @classmethod
    def new_from_element(cls, element):

        xmlns = check_element_and_namespace(element, 'destroy')

        cl = cls()
        cl.set_xmlns(xmlns)

        reason_el = element.find(
            '{{http://jabber.org/protocol/muc{}}}reason'.format(xmlns)
            )
        if reason_el != None:
            cl.set_reason(reason_el.text)

        password_el = element.find(
            '{{http://jabber.org/protocol/muc{}}}password'.format(xmlns)
            )
        if password_el != None:
            cl.set_password(password_el.text)

        org.wayround.utils.lxml.elem_props_to_object_props(
            element, cl,
            [
             ('jid', 'jid'),
             ]
            )

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('destroy')

        org.wayround.utils.lxml.object_props_to_elem_props(
            self, el,
            [
             ('jid', 'jid'),
             ]
            )

        reason = self.get_reason()
        if reason != None:
            reason_el = lxml.etree.Element('reason')
            reason_el.text = reason
            el.append(reason_el)

        password = self.get_password()
        if password != None:
            password_el = lxml.etree.Element('password')
            password_el.text = password
            el.append(password_el)

        return el


org.wayround.utils.factory.class_generate_attributes(
    Destroy,
    ['reason', 'jid', 'password']
    )
org.wayround.utils.factory.class_generate_check(
    Destroy,
    ['reason', 'jid', 'password']
    )


class Invite:

    def __init__(self, reason=None, from_jid=None, to_jid=None):

        self.set_reason(reason)
        self.set_from_jid(from_jid)
        self.set_to_jid(to_jid)

    def check_reason(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`reason' must be None or str")

    def check_from_jid(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`from_jid' must be None or str")

    def check_to_jid(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`to_jid' must be None or str")

    @classmethod
    def new_from_element(cls, element):

        xmlns = check_element_and_namespace(element, 'invite')

        cl = cls()
        cl.set_xmlns(xmlns)

        reason_el = element.find(
            '{{http://jabber.org/protocol/muc{}}}reason'.format(xmlns)
            )
        if reason_el != None:
            cl.set_reason(reason_el.text)

        org.wayround.utils.lxml.elem_props_to_object_props(
            element, cl,
            [
             ('from', 'from_jid'),
             ('to', 'to_jid')
             ]
            )

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('invite')

        org.wayround.utils.lxml.object_props_to_elem_props(
            self, el,
            [
             ('from_jid', 'from'),
             ('to_jid', 'to')
             ]
            )

        reason = self.get_reason()
        if reason != None:
            reason_el = lxml.etree.Element('reason')
            reason_el.text = reason
            el.append(reason_el)

        return el

org.wayround.utils.factory.class_generate_attributes(
    Invite,
    ['reason', 'from_jid', 'to_jid']
    )
org.wayround.utils.factory.class_generate_check(
    Invite,
    ['reason', 'from_jid', 'to_jid']
    )


class Item:

    def __init__(
        self,
        actor=None, reason=None, contin=None, affiliation=None,
        jid=None, nick=None, role=None
        ):

        self.set_actor(actor)
        self.set_reason(reason)
        self.set_contin(contin)
        self.set_affiliation(affiliation)
        self.set_jid(jid)
        self.set_nick(nick)
        self.set_role(role)

    def check_actor(self, value):
        if value != None and not isinstance(value, Actor):
            raise ValueError("`actor' must be None or Actor")

    def check_reason(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`reason' must be None or str")

    def check_contin(self, value):
        if value != None and not isinstance(value, Continue):
            raise ValueError("`contin' must be None or Continue")

    def check_affiliation(self, value):
        if not value in [None, 'admin', 'member', 'none', 'outcast', 'owner']:
            raise ValueError(
                "`affiliation' must be None or one of "
                "['admin', 'member', 'none', 'outcast', 'owner']"
                )

    def check_jid(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`jid' must be None or str")

    def check_nick(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`nick' must be None or str")

    def check_role(self, value):
        if not value in [None, 'moderator', 'none', 'participant', 'visitor']:
            raise ValueError(
                "`role' must be None or one of "
                "['moderator', 'none', 'participant', 'visitor']"
                )

    @classmethod
    def new_from_element(cls, element):

        xmlns = check_element_and_namespace(element, 'item')

        cl = cls()

        reason_el = element.find(
            '{{http://jabber.org/protocol/muc{}}}reason'.format(xmlns)
            )
        if reason_el != None:
            cl.set_reason(reason_el.text)

        org.wayround.utils.lxml.subelems_to_object_props(
            element, cl,
            [
             ('{{http://jabber.org/protocol/muc{}}}actor'.format(xmlns),
              Actor,
              'actor'),
             ('{{http://jabber.org/protocol/muc{}}}continue'.format(xmlns),
              Continue,
              'contin'
              )
             ]
            )

        org.wayround.utils.lxml.elem_props_to_object_props(
            element, cl,
            [
             ('affiliation', 'affiliation'),
             ('jid', 'jid'),
             ('nick', 'nick'),
             ('role', 'role')
             ]
            )

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('item')

        org.wayround.utils.lxml.object_props_to_subelems(
            self, el, ['actor', 'contin']
            )

        reason = self.get_reason()
        if reason != None:
            reason_el = lxml.etree.Element('reason')
            reason_el.text = reason
            el.append(reason_el)

        org.wayround.utils.lxml.object_props_to_elem_props(
            self, el,
            [
             ('affiliation', 'affiliation'),
             ('jid', 'jid'),
             ('nick', 'nick'),
             ('role', 'role')
             ]
            )

        return el

org.wayround.utils.factory.class_generate_attributes(
    Item,
    ['actor', 'reason', 'contin', 'affiliation', 'jid', 'nick', 'role']
    )
org.wayround.utils.factory.class_generate_check(
    Item,
    ['actor', 'reason', 'contin', 'affiliation', 'jid', 'nick', 'role']
    )


class Actor:

    def __init__(self, jid):

        self.set_jid(jid)

    def check_jid(self, value):
        if not isinstance(value, str):
            raise ValueError("`jid' must be str")

    @classmethod
    def new_from_element(cls, element):

        check_element_and_namespace(element, 'actor')

        cl = cls()

        cl.set_jid(element.get('jid'))

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('actor')

        el.set('jid', self.get_jid())

        return el

org.wayround.utils.factory.class_generate_attributes(
    Actor,
    ['jid']
    )
org.wayround.utils.factory.class_generate_check(
    Actor,
    ['jid']
    )


class Continue:

    def __init__(self, thread=None):

        self.set_thread(thread)

    def check_thread(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`thread' must be None or str")

    @classmethod
    def new_from_element(cls, element):

        check_element_and_namespace(element, 'continue')

        cl = cls()

        cl.set_thread(element.get('thread'))

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('continue')

        el.set('thread', self.get_thread())

        return el

org.wayround.utils.factory.class_generate_attributes(
    Continue,
    ['thread']
    )
org.wayround.utils.factory.class_generate_check(
    Continue,
    ['thread']
    )


#class Status:
#
#    def __init__(self, code):
#
#        self.set_code(code)
#
#    def check_code(self, value):
#        if not isinstance(value, int):
#            raise ValueError("`code' must be int")
#
#    @classmethod
#    def new_from_element(cls, element):
#
#        check_element_and_namespace(element, 'status')
#
#        cl = cls()
#
#        cl.set_code(element.get('code'))
#
#        cl.check()
#
#        return cl
#
#    def gen_element(self):
#
#        self.check()
#
#        el = lxml.etree.Element('status')
#
#        #        <xs:restriction base='xs:int'>
#        #        <xs:length value='3'/>
#        #        </xs:restriction>
#
#        el.set('code', '{:03d}'.format(self.get_code()))
#
#        return el
#
#org.wayround.utils.factory.class_generate_attributes(
#    Status,
#    ['code']
#    )
#org.wayround.utils.factory.class_generate_check(
#    Status,
#    ['code']
#    )


# misc

def check_element_and_namespace(element, tag_localname):

    if type(element) != lxml.etree._Element:
        raise TypeError("`element' must be lxml.etree.Element")

    if not isinstance(tag_localname, str):
        raise TypeError("`tag_localname' must be str")

    xmlns = None

    qname = lxml.etree.QName(element)

    if qname.localname != tag_localname:
        raise ValueError("Invalid element")
    else:
        xmlns = qname.namespace

        if not xmlns.startswith(NAMESPACE):
            raise ValueError("Invalid element namespace")

        else:
            xmlns = xmlns[NAMESPACE_LENGTH:]

    if not xmlns in [
        '', '#owner', '#admin', '#user', '#unique'
        ]:
        raise ValueError("invalid namespace")

    return xmlns


# mechanics

class Server:

    def __init__(self):
        pass

    def connect_stanza_processor(self, stanza_processor):
        pass

    def disconnect_stanza_processor(self):
        pass


# TODO: remove?
class Client:

    def __init__(self, client, client_jid):

        self._stanza_processor = None
        self._client_jid = client_jid
        self._client = client

    def connect_stanza_processor(self, stanza_processor):

        self._stanza_processor = stanza_processor

    def disconnect_stanza_processor(self):
        pass


def create_room_instantly(room_bare_jid, from_full_jid, stanza_processor):

    xdata = org.wayround.xmpp.xdata.XData(typ='submit')

    stanza = org.wayround.xmpp.core.Stanza('iq')

    stanza.set_from_jid(from_full_jid)
    stanza.set_to_jid(room_bare_jid)
    stanza.set_typ('set')

    query = Query(xmlns='#owner', xdata=xdata)

    stanza.get_objects().append(query)

    ret = stanza_processor.send(stanza, wait=None)
    return ret


def discover_room_nickname(room_bare_jid, from_full_jid, stanza_processor):

    stanza = org.wayround.xmpp.core.Stanza('iq')

    stanza.set_from_jid(from_full_jid)
    stanza.set_to_jid(room_bare_jid)
    stanza.set_typ('get')

    query = org.wayround.xmpp.disco.IQDisco(
        mode='info', node='x-roomuser-item'
        )

    stanza.get_objects().append(query)

    ret = stanza_processor.send(stanza, wait=None)

    return ret


def request_room_configuration(room_bare_jid, from_full_jid, stanza_processor):

    stanza = org.wayround.xmpp.core.Stanza('iq')

    stanza.set_from_jid(from_full_jid)
    stanza.set_to_jid(room_bare_jid)
    stanza.set_typ('get')

    query = Query(xmlns='#owner')

    stanza.get_objects().append(query)

    ret = stanza_processor.send(stanza, wait=None)
    return ret


def submit_room_configuration(
        room_bare_jid, from_full_jid, stanza_processor, x_data
        ):

    stanza = org.wayround.xmpp.core.Stanza('iq')

    stanza.set_from_jid(from_full_jid)
    stanza.set_to_jid(room_bare_jid)
    stanza.set_typ('set')

    query = Query(xmlns='#owner', xdata=x_data)

    stanza.get_objects().append(query)

    ret = stanza_processor.send(stanza, wait=None)
    return ret


def destroy_room(
    room_bare_jid, from_full_jid, stanza_processor,
    reason=None, alternate_venue_jid=None
    ):

    query = Query(
        xmlns='#owner',
        destroy=Destroy(
            jid=alternate_venue_jid,
            reason=reason
            )
        )

    stanza = org.wayround.xmpp.core.Stanza('iq')

    stanza.set_from_jid(from_full_jid)
    stanza.set_to_jid(room_bare_jid)
    stanza.set_typ('set')

    stanza.get_objects().append(query)

    ret = stanza_processor.send(stanza, wait=None)
    return ret


def get_room_identies(mode, room_bare_jid, from_full_jid, stanza_processor):

    if not mode in [
        'voice', 'ban', 'member', 'moderator', 'admin', 'owner'
        ]:
        raise ValueError("`mode' is invalid")

    affiliation = None
    role = None

    if mode in ['owner', 'admin', 'member']:
        affiliation = mode
    elif mode == 'ban':
        affiliation = 'outcast'
    elif mode == 'moderator':
        role = 'moderator'
    elif mode == 'voice':
        role = 'participant'
    else:
        raise Exception("DNA Error")

    query = Query(
        xmlns='#admin',
        item=[
            Item(
                affiliation=affiliation,
                role=role
                )
            ]
        )

    stanza = org.wayround.xmpp.core.Stanza('iq')

    stanza.set_from_jid(from_full_jid)
    stanza.set_to_jid(room_bare_jid)
    stanza.set_typ('get')

    stanza.get_objects().append(query)

    ret = stanza_processor.send(stanza, wait=None)

    return ret


def get_muc_elements(element):

    ret = []

    for i in NAMESPACES:
        ret += element.findall('{{}}x'.format(i))
        ret += element.findall('{{}}query'.format(i))
        ret += element.findall('{{}}unique'.format(i))

    return ret


def has_muc_elements(element):
    return len(get_muc_elements(element)) != 0
