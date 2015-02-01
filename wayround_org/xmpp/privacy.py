
import logging
import threading

import lxml.etree

import wayround_org.utils.factory
import wayround_org.utils.types

import wayround_org.xmpp.core


class Query:

    def __init__(self, active=None, default=None, lst=None):

        if lst is None:
            lst = []

        self.set_active(active)
        self.set_default(default)
        self.set_lst(lst)

    def check_active(self, value):
        if value is not None and not isinstance(value, Active):
            raise ValueError("`active' must be None or Active")

    def check_default(self, value):
        if value is not None and not isinstance(value, Default):
            raise ValueError("`default' must be None or Default")

    def check_lst(self, value):
        if not wayround_org.utils.types.struct_check(
            value,
            {'t': list, '.': {'t': List}}
            ):
            raise ValueError("`lst' must be list of List")

    @classmethod
    def new_from_stanza_lxml(cls, element):
        # TODO: add analogical methods to other modules
        """
        Return list of newly creates Query elements
        """

        if not wayround_org.xmpp.core.is_stanza_element(element):
            raise ValueError("not a stanza element")

        ret = []

        res = element.findall('{jabber:iq:privacy}query')

        for i in res:
            ret.append(cls.new_from_element(i))

        return ret

    @classmethod
    def new_from_element(cls, element):

        tag = wayround_org.utils.lxml.parse_element_tag(
            element, 'query', ['jabber:iq:privacy']
            )[0]

        if tag is None:
            raise ValueError("invalid element")

        cl = cls()

        wayround_org.utils.lxml.subelems_to_object_props(
            element, cl,
            [
             ('{jabber:iq:privacy}active', Active, 'active', '*'),
             ('{jabber:iq:privacy}default', Default, 'default', '*')
             ]
            )

        wayround_org.utils.lxml.subelemsm_to_object_propsm(
            element, cl,
            [
             ('{jabber:iq:privacy}list', List, 'lst', '*')
             ]
            )

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('query')
        el.set('xmlns', 'jabber:iq:privacy')

        wayround_org.utils.lxml.object_props_to_subelems(
            self, el,
            ['active', 'default']
            )

        wayround_org.utils.lxml.object_propsm_to_subelemsm(
            self, el,
            ['lst']
            )

        return el

wayround_org.utils.factory.class_generate_attributes(
    Query,
    ['active', 'default', 'lst']
    )
wayround_org.utils.factory.class_generate_check(
    Query,
    ['active', 'default', 'lst']
    )


class ActiveAndDefault:

    def __init__(self, name=None, token=None):

        # TODO: I don't like this
        impl = self.impl_check()

        if not impl in ['active', 'default']:
            raise ValueError("invalid `impl'")

        self.set_name(name)
        self.set_token(token)

        self._actual_impl = impl

    def check_token(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`token' must be None or str")

    def check_name(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`name' must be None or str")

    @classmethod
    def impl_check(cls):
        impl = None
        if cls == Active:
            impl = 'active'
        elif cls == Default:
            impl = 'default'
        else:
            raise Exception("DNA Error")
        return impl

    @classmethod
    def new_from_element(cls, element):

        impl = cls.impl_check()

        if not impl in ['active', 'default']:
            raise ValueError("invalid `impl'")

        tag = wayround_org.utils.lxml.parse_element_tag(
            element, impl, ['jabber:iq:privacy']
            )[0]

        if tag is None:
            raise ValueError("invalid element")

        cl = cls()

        cl.set_token(element.text)
        cl.set_name(element.get('name'))

        cl.check()

        return cl

    def gen_element(self):

        impl = self.impl_check()

        self.check()

        el = lxml.etree.Element(impl)

        el.text = self.get_token()

        name = self.get_name()
        if name is not None:
            el.set('name', name)

        return el

wayround_org.utils.factory.class_generate_attributes(
    ActiveAndDefault,
    ['token', 'name']
    )
wayround_org.utils.factory.class_generate_check(
    ActiveAndDefault,
    ['token', 'name']
    )


class Active(ActiveAndDefault):
    pass
#    def __init__(self, name=None, token=None):
#        super().__init__(name, token, 'active')

#    @classmethod
#    def new_from_element(cls, element):
#        return super().new_from_element(element)


class Default(ActiveAndDefault):
    pass
#    def __init__(self, name=None, token=None):
#        super().__init__(name, token, 'default')

#    @classmethod
#    def new_from_element(cls, element):
#        return super().new_from_element(element)


class List:

    def __init__(self, name, item=None):

        if item is None:
            item = []

        self.set_name(name)
        self.set_item(item)

    def check_name(self, value):
        if not isinstance(value, str):
            raise ValueError("`name' must be str")

    def check_item(self, value):
        if not wayround_org.utils.types.struct_check(
            value,
            {'t': list, '.': {'t': Item}}
            ):
            raise ValueError("`item' must be list of Item")

    @classmethod
    def new_from_element(cls, element):

        tag = wayround_org.utils.lxml.parse_element_tag(
            element, 'list', ['jabber:iq:privacy']
            )[0]

        if tag is None:
            raise ValueError("invalid element")

        cl = cls(element.get('name'))

        wayround_org.utils.lxml.subelemsm_to_object_propsm(
            element, cl,
            [
             ('{jabber:iq:privacy}item', Item, 'item', '*')
             ]
            )

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('list')

        wayround_org.utils.lxml.object_propsm_to_subelemsm(
            self, el,
            ['item']
            )

        name = self.get_name()
        if name is not None:
            el.set('name', name)

        return el

wayround_org.utils.factory.class_generate_attributes(
    List,
    ['item', 'name']
    )
wayround_org.utils.factory.class_generate_check(
    List,
    ['item', 'name']
    )


class Item:

    def __init__(
        self,
        action, order, typ=None, value=None,
        iq=False, message=False, presence_in=False, presence_out=False,
        ):

        self.set_action(action)
        self.set_order(order)
        self.set_typ(typ)
        self.set_value(value)
        self.set_iq(iq)
        self.set_message(message)
        self.set_presence_in(presence_in)
        self.set_presence_out(presence_out)

    def check_bool(self, value, name):
        if not isinstance(value, bool):
            raise ValueError("`{}' must be bool".format(name))

    def check_iq(self, value):
        self.check_bool(value, 'iq')

    def check_message(self, value):
        self.check_bool(value, 'message')

    def check_presence_in(self, value):
        self.check_bool(value, 'presence_in')

    def check_presence_out(self, value):
        self.check_bool(value, 'presence_out')

    def check_action(self, value):
        if not value in ['allow', 'deny']:
            raise ValueError("`action' must be in ['allow', 'deny']")

    def check_order(self, value):
        if not isinstance(value, int):
            raise ValueError("`order' must be int")

        if value < 0:
            raise ValueError("`order' must be unsigned")

    def check_typ(self, value):
        if value is not None and not value in ['group', 'jid', 'subscription']:
            raise ValueError(
                "`typ' must be in ['group', 'jid', 'subscription']"
                )

    def check_value(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`value' must be None or str")

    @classmethod
    def new_from_element(cls, element):

        tag = wayround_org.utils.lxml.parse_element_tag(
            element, 'item', ['jabber:iq:privacy']
            )[0]

        if tag is None:
            raise ValueError("invalid element")

        cl = cls(element.get('action'), int(element.get('order')))

        for i in ['iq', 'message', 'presence_in', 'presence_out']:

            nn = i.replace('_', '-')

            set_func = getattr(cl, 'set_{}'.format(i))
            set_func(
                element.find('{{jabber:iq:privacy}}{}'.format(nn)) != None
                )

        wayround_org.utils.lxml.elem_props_to_object_props(
            element, cl,
            [
             ('type', 'typ'),
             ('value', 'value')
             ]
            )

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('item')

        for i in ['iq', 'message', 'presence_in', 'presence_out']:

            nn = i.replace('_', '-')

            get_func = getattr(self, 'get_{}'.format(i))
            val = get_func()
            if val is not None and val == True:
                el.append(lxml.etree.Element(nn))

        val = self.get_order()
        if val is not None:
            el.set('order', str(val))

        wayround_org.utils.lxml.object_props_to_elem_props(
            self, el,
            [
             ('action', 'action'),
             ('typ', 'type'),
             ('value', 'value')
             ]
            )

        return el

wayround_org.utils.factory.class_generate_attributes(
    Item,
    ['iq', 'message', 'presence_in', 'presence_out', 'action', 'order', 'typ',
     'value']
    )
wayround_org.utils.factory.class_generate_check(
    Item,
    ['iq', 'message', 'presence_in', 'presence_out', 'action', 'order', 'typ',
     'value']
    )


class PrivacyClient:

    def __init__(self, client, jid):

        self._from_jid = jid
        self._client = client

        self.signal = wayround_org.utils.threading.Signal(
            self, ['push']
            )

        self._client.signal.connect(
            'stanza_processor_new_stanza',
            self._push
            )

    def _push(self, event, client, stanza):

        if event == 'stanza_processor_new_stanza':

#            logging.debug("{}::Got stanza".format(self))

            if (stanza.get_from_jid() in [None, self._from_jid.bare()]
                and stanza.get_to_jid() == str(self._from_jid)):

                for i in Query.new_from_stanza_lxml(stanza.get_element()):

                    new_stanza = wayround_org.xmpp.core.Stanza(
                        tag='iq',
                        to_jid=stanza.get_from_jid(),
                        from_jid=str(self._from_jid),
                        typ='result',
                        ide=stanza.get_ide()
                        )

                    threading.Thread(
                        target=self._client.stanza_processor.send,
                        args=(new_stanza,),
                        kwargs={
                            'ide_mode': 'from_stanza',
                            'wait': False
                            }
                        ).start()

                    self.signal.emit('push', i)

        return


def _make_stanza(from_jid, to_jid):
    return wayround_org.xmpp.core.Stanza(
        tag='iq',
        from_jid=from_jid,
        to_jid=to_jid
        )


def _result(stanza, stanza_processor, wait):

    res = stanza_processor.send(stanza, wait=wait)

    ret = None

    if isinstance(res, wayround_org.xmpp.core.Stanza):
        if res.is_error():
            ret = res.gen_error()
        else:
            ret = Query.new_from_stanza_lxml(res.get_element())

    return ret


def get_privacy_lists(to_jid, from_jid, stanza_processor, wait=None):

    query = Query()

    stanza = _make_stanza(from_jid, to_jid)
    stanza.set_typ('get')
    stanza.set_objects([query])

    return _result(stanza, stanza_processor, wait)


def set_active_list(name, to_jid, from_jid, stanza_processor, wait=None):

    query = Query(active=Active(name=name))

    stanza = _make_stanza(from_jid, to_jid)
    stanza.set_objects([query])
    stanza.set_typ('set')

    return _result(stanza, stanza_processor, wait)


def set_default_list(name, to_jid, from_jid, stanza_processor, wait=None):

    query = Query(default=Default(name=name))

    stanza = _make_stanza(from_jid, to_jid)
    stanza.set_objects([query])
    stanza.set_typ('set')

    return _result(stanza, stanza_processor, wait)


def get_list(name, to_jid, from_jid, stanza_processor, wait=None):

    query = Query(lst=[List(name=name)])

    stanza = _make_stanza(from_jid, to_jid)
    stanza.set_objects([query])
    stanza.set_typ('get')

    return _result(stanza, stanza_processor, wait)


def set_list(name, items, to_jid, from_jid, stanza_processor, wait=None):

    if not wayround_org.utils.types.struct_check(
        items,
        {'t': list, '.': {'t': Item}}
        ):
        raise ValueError("`items' must be list of Item")

    query = Query(lst=[List(name, items)])

    stanza = _make_stanza(from_jid, to_jid)
    stanza.set_objects([query])
    stanza.set_typ('set')

    return _result(stanza, stanza_processor, wait)


def delete_list(name, to_jid, from_jid, stanza_processor, wait=None):
    return set_list(name, [], to_jid, from_jid, stanza_processor, wait)
