
"""
XMPP Disco protocol implementation
"""

import lxml.etree

import org.wayround.xmpp.core
import org.wayround.utils.timer


class IQDisco:

    def __init__(
        self,
        mode='info', node=None, identity=None, feature=None, item=None,
        xdata=None
        ):

        if identity is None:
            identity = []

        if feature is None:
            feature = []

        if item is None:
            item = []

        if xdata is None:
            xdata = []

        self.set_mode(mode)
        self.set_node(node)
        self.set_identity(identity)
        self.set_feature(feature)
        self.set_item(item)
        self.set_xdata(xdata)

    def check_mode(self, value):
        if not value in ['info', 'items']:
            raise ValueError("`mode' must be in ['info', 'items']")

    def check_node(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`node' must be None or str")

    def check_identity(self, value):
        if not org.wayround.utils.types.struct_check(
            value,
            {'t': list, '.': {'t': IQDiscoIdentity}}
            ):
            raise ValueError("`identity' must be list of IQDiscoIdentity")

    def check_item(self, value):
        if not org.wayround.utils.types.struct_check(
            value,
            {'t': list, '.': {'t': IQDiscoItem}}
            ):
            raise ValueError("`item' must be list of IQDiscoIdentity")

    def check_feature(self, value):
        if not org.wayround.utils.types.struct_check(
            value,
            {'t': list, '.': {'t': str}}
            ):
            raise ValueError("`feature' must be list of str")

    def check_xdata(self, value):
        if not org.wayround.utils.types.struct_check(
            value,
            {'t': list, '.': {'t': org.wayround.xmpp.xdata.XData}}
            ):
            raise ValueError(
                "`xdata' must be list of org.wayround.xmpp.xdata.XData"
                )

    def has_feature(self, name):
        return name in self.get_feature()

    @classmethod
    def new_from_element(cls, element):

        tag, ns = org.wayround.utils.lxml.parse_element_tag(
            element,
            'query',
            [
             'http://jabber.org/protocol/disco#info',
             'http://jabber.org/protocol/disco#items'
             ]
            )

        if tag is None:
            raise ValueError("invalid element tag or namespace")

        cl = cls()

        cl.set_mode(ns[33:])

        org.wayround.utils.lxml.subelemsm_to_object_propsm(
            element, cl,
            [
             ('{http://jabber.org/protocol/disco#info}identity',
              IQDiscoIdentity,
              'identity'),
             ('{http://jabber.org/protocol/disco#items}item',
              IQDiscoItem,
              'item'),
             ('{jabber:x:data}x',
              org.wayround.xmpp.xdata.XData,
              'xdata')
             ]
            )

        org.wayround.utils.lxml.elem_props_to_object_props(
            element, cl,
            [
             ('node', 'node')
             ]
            )

        features_els = element.findall(
            '{http://jabber.org/protocol/disco#info}feature'
            )

        features = []

        for i in features_els:

            t = i.get('var')
            if not isinstance(t, str):
                raise ValueError("feature element must have var attribute")

            features.append(t)

        cl.set_feature(features)

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        element = lxml.etree.Element('query')
        element.set(
            'xmlns',
            'http://jabber.org/protocol/disco#{}'.format(
                self.get_mode()
                )
            )

        org.wayround.utils.lxml.object_props_to_elem_props(
            self, element,
            [
             ('node', 'node')
             ]
            )

        org.wayround.utils.lxml.object_propsm_to_subelemsm(
            self, element,
            ['identity', 'item', 'xdata']
            )

        features = self.get_feature()
        for i in features:
            el = lxml.etree.Element('feature')
            el.set('var', i)
            element.append(el)

        return element

org.wayround.utils.factory.class_generate_attributes(
    IQDisco,
    ['mode', 'node', 'identity', 'feature', 'item', 'xdata']
    )
org.wayround.utils.factory.class_generate_check(
    IQDisco,
    ['mode', 'node', 'identity', 'feature', 'item', 'xdata']
    )


class IQDiscoIdentity:

    def __init__(self, category=None, typ=None, name=None):

        self.set_category(category)
        self.set_typ(typ)
        self.set_name(name)

    def check_category(self, value):
        if not isinstance(value, str):
            raise ValueError("`category' must be str")

    def check_typ(self, value):
        if not isinstance(value, str):
            raise ValueError("`typ' must be str")

    def check_name(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`name' must be str")

    @classmethod
    def new_from_element(cls, element):

        tag = org.wayround.utils.lxml.parse_element_tag(
            element,
            'identity',
            [
             'http://jabber.org/protocol/disco#info'
             ]
            )[0]

        if tag == None:
            raise ValueError("invalid element")

        cl = cls(category=element.get('category'), typ=element.get('type'))

        org.wayround.utils.lxml.elem_props_to_object_props(
            element, cl,
            [
             ('name', 'name')
             ]
            )

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        element = lxml.etree.Element('identity')

        org.wayround.utils.lxml.object_props_to_elem_props(
            self, element,
            [
             ('category', 'category'),
             ('typ', 'type'),
             ('name', 'name')
             ]
            )

        return element

org.wayround.utils.factory.class_generate_attributes(
    IQDiscoIdentity,
    ['category', 'typ', 'name']
    )
org.wayround.utils.factory.class_generate_check(
    IQDiscoIdentity,
    ['category', 'typ', 'name']
    )


class IQDiscoItem:

    def __init__(self, jid=None, node=None, name=None):

        self.set_jid(jid)
        self.set_node(node)
        self.set_name(name)

    def check_jid(self, value):
        try:
            org.wayround.xmpp.core.JID.new_from_string(value)
        except:
            raise ValueError("`jid' must be str with valid jid")

    def check_node(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`node' must be None or str")

    def check_name(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`name' must be None or str")

    @classmethod
    def new_from_element(cls, element):

        tag = org.wayround.utils.lxml.parse_element_tag(
            element,
            'item',
            ['http://jabber.org/protocol/disco#items']
            )[0]

        if tag == None:
            raise ValueError("invalid element")

        cl = cls(jid=element.get('jid'))

        org.wayround.utils.lxml.elem_props_to_object_props(
            element, cl,
            [
             ('node', 'node'),
             ('name', 'name')
             ]
            )

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        element = lxml.etree.Element('item')

        org.wayround.utils.lxml.object_props_to_elem_props(
            self, element,
            [
             ('jid', 'jid'),
             ('node', 'node'),
             ('name', 'name')
             ]
            )

        return element

org.wayround.utils.factory.class_generate_attributes(
    IQDiscoItem,
    ['jid', 'node', 'name']
    )
org.wayround.utils.factory.class_generate_check(
    IQDiscoItem,
    ['jid', 'node', 'name']
    )


def _x(to_jid, from_jid, node=None, stanza_processor=None, mode='info'):
    """
    :param org.wayround.xmpp.core.StanzaProcessor stanza_processor:
    """

    if not mode in ['info', 'items']:
        raise ValueError("`mode' invalid")

    if not isinstance(
            stanza_processor, org.wayround.xmpp.core.StanzaProcessor
            ):
        raise TypeError(
            "`stanza_processor' must be of type "
            "org.wayround.xmpp.core.StanzaProcessor"
            )

    q = IQDisco(mode)
    q.set_node(node)

    stanza = org.wayround.xmpp.core.Stanza(
        tag='iq',
        from_jid=from_jid,
        to_jid=to_jid,
        typ='get',
        objects=[
            q
            ]
        )

    ret = stanza_processor.send(stanza, wait=None)

    return ret


def get_info(to_jid, from_jid, node=None, stanza_processor=None):

    ret = None

    res = _x(
        to_jid, from_jid=from_jid, node=node,
        stanza_processor=stanza_processor, mode='info'
        )

    if isinstance(res, org.wayround.xmpp.core.Stanza):
        element = res.get_element().find(
            '{http://jabber.org/protocol/disco#info}query'
            )

        if element != None:
            ret = IQDisco.new_from_element(element)

    return ret, res


def get_items(to_jid, from_jid, node=None, stanza_processor=None):

    ret = None

    res = _x(
        to_jid, from_jid=from_jid, node=node,
        stanza_processor=stanza_processor, mode='items'
        )

    if isinstance(res, org.wayround.xmpp.core.Stanza):
        element = res.get_element().find(
            '{http://jabber.org/protocol/disco#items}query'
            )

        if element != None:
            ret = IQDisco.new_from_element(element)

    return ret, res


def get(to_jid, from_jid, node=None, stanza_processor=None):
    return {
        'info': get_info(
            to_jid, from_jid=from_jid, node=node,
            stanza_processor=stanza_processor
            ),
        'items': get_items(
            to_jid, from_jid=from_jid, node=node,
            stanza_processor=stanza_processor
            )
        }


class DiscoService:

    def __init__(self, stanza_processor, own_jid, info, items):

        self._info = info
        self._items = items
        self._own_jid = own_jid

        stanza_processor.connect_signal(
            'new_stanza',
            self._in_stanza
            )

    def _in_stanza(self, event, stanza_processor, stanza):

        """
        :param org.wayround.xmpp.core.Stanza stanza:
        """

        if event == 'new_stanza':

            if stanza.get_tag() == 'iq' and stanza.get_typ() == 'get':

                if not stanza.is_error():

                    query = stanza.get_element().find(
                        '{http://jabber.org/protocol/disco#info}query'
                        )

                    if query != None:

                        if len(query) == 0:

                            rstanza = org.wayround.xmpp.core.Stanza('iq')
                            rstanza.set_ide(stanza.get_ide())
                            rstanza.set_typ('result')
                            rstanza.set_from_jid(self._own_jid.full())
                            rstanza.set_to_jid(stanza.get_from_jid())

                            rstanza.set_objects(
                                [self._info]
                                )
                            stanza_processor.send(rstanza, wait=False)

        return
