
import collections

import lxml.etree
import org.wayround.utils.factory
import org.wayround.utils.lxml
import org.wayround.xmpp.oob
import org.wayround.xmpp.xdata


REGISTRATION_INPUT_FIELDS = [
    'username',
    'nick',
    'password',
    'name',
    'first',
    'last',
    'email',
    'address',
    'city',
    'state',
    'zip',
    'phone',
    'url',
    'date',
    'misc',
    'text',
    'key'
    ]

REGISTRATION_FIELDS = [
    'registered', 'instructions'
    ] + REGISTRATION_INPUT_FIELDS


class Query:

    def __init__(
        self,
        registered=False, remove=False, oob=None, xdata=None,
        **kwargs
        ):

        for i in list(kwargs.keys()):
            if not i in REGISTRATION_INPUT_FIELDS:
                raise TypeError(
                    "'{}' is an invalid keyword "
                    "argument for this function".format(
                        i
                        )
                    )

        self.set_oob(oob)
        self.set_xdata(xdata)
        self.set_registered(registered)
        self.set_remove(remove)

        for i in list(kwargs.keys()):
            fun = getattr(self, 'set_{}'.format(i))
            fun(kwargs[i])

        self._input_fields = list()

        return

    def check_oob(self, value):
        if value is not None and not isinstance(
            value, org.wayround.xmpp.oob.X
            ):
            raise ValueError(
                "`oob' must be None or org.wayround.xmpp.oob.X"
                )

    def check_xdata(self, value):
        if value is not None and not isinstance(
            value, org.wayround.xmpp.xdata.XData
            ):
            raise ValueError(
                "`xdata' must be None or org.wayround.xmpp.xdata.XData"
                )

    def check_registered(self, value):
        if not isinstance(value, bool):
            raise ValueError("`registered' must be bool")

    def check_remove(self, value):
        if not isinstance(value, bool):
            raise ValueError("`remove' must be bool")

    def check_instructions(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`instructions' must be None or str")

    for i in REGISTRATION_INPUT_FIELDS:
        exec("""\
def check_{i}(self, value):
    if value is not None and not isinstance(value, str):
        raise ValueError("`{i}' must be None or str")
""".format(i=i)
            )

    @classmethod
    def new_from_element(cls, element):

        tag = org.wayround.utils.lxml.parse_element_tag(
            element, 'query', ['jabber:iq:register']
            )[0]

        if tag == None:
            raise ValueError("invalid element")

        ins = cls()

        el = element.find('{jabber:iq:register}registered')
        if el != None:
            ins.set_registered(True)

        el = element.find('{jabber:iq:register}remove')
        if el != None:
            ins.set_remove(True)

        input_fields_value = {}

        for i in REGISTRATION_INPUT_FIELDS:
            el = element.find('{{jabber:iq:register}}{}'.format(i))
            if el != None:
                input_fields_value[i] = el.text

        ins.set_input_fields(input_fields_value)

        org.wayround.utils.lxml.subelems_to_object_props(
            element, ins,
            [
             ('{jabber:x:data}x', org.wayround.xmpp.xdata.XData, 'xdata'),
             ('{jabber:x:oob}x', org.wayround.xmpp.oob.X, 'oob')
             ]
            )

        ins.check()

        return ins

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('query')
        el.set('xmlns', 'jabber:iq:register')

        if self.get_registered():
            e = lxml.etree.Element('registered')
            el.append(e)

        if self.get_remove():
            e = lxml.etree.Element('remove')
            el.append(e)

        for i in REGISTRATION_INPUT_FIELDS:
            gfunc = getattr(self, 'get_{}'.format(i))
            _t = gfunc()
            if _t != None:
                e = lxml.etree.Element(i)
                e.text = _t
                el.append(e)

        org.wayround.utils.lxml.object_props_to_subelems(
            self, el,
            ['xdata', 'oob']
            )

        return el

    def get_fields(self):

        ret = collections.OrderedDict()
        for i in REGISTRATION_FIELDS:
            ret[i] = getattr(self, 'get_{}'.format(i))()

        return ret

    def set_input_fields(self, value):

        while len(self._input_fields) != 0:
            del self._input_fields[0]

        for i in REGISTRATION_INPUT_FIELDS:
            fun = getattr(self, 'set_{}'.format(i))
            fun(None)

        for i in list(value.keys()):
            self._input_fields.append(i)
            fun = getattr(self, 'set_{}'.format(i))
            fun(value[i])

    def get_input_fields(self):

        ret = collections.OrderedDict()
        for i in REGISTRATION_INPUT_FIELDS:
            if i in self._input_fields:
                ret[i] = getattr(self, 'get_{}'.format(i))()

        return ret

org.wayround.utils.factory.class_generate_attributes(
    Query,
    ['oob', 'xdata', 'instructions', 'remove', 'registered'] + \
        REGISTRATION_INPUT_FIELDS
    )
org.wayround.utils.factory.class_generate_check(
    Query,
    ['oob', 'xdata', 'instructions', 'remove', 'registered'] + \
        REGISTRATION_INPUT_FIELDS
    )


def get_query_from_element(element):

    if type(element) != lxml.etree._Element:
        raise TypeError("`element' must be lxml.etree._Element")

    ret = None

    for i in element:

        if i.tag == '{jabber:iq:register}query':
            ret = i
            break

    if ret != None:
        ret = Query.new_from_element(ret)

    return ret


def get_form(from_jid, to_jid, stanza_processor, wait=True):

    s = org.wayround.xmpp.core.Stanza('iq')
    s.set_typ('get')
    s.set_from_jid(from_jid)
    s.set_to_jid(to_jid)
    s.set_objects(
        [
         org.wayround.xmpp.registration.Query()
         ]
        )

    res = stanza_processor.send(s, wait=wait)

    if res != None:
        if not res.is_error():
            ret = get_query_from_element(res.get_element())
        else:
            ret = res

    return ret


def set_form(from_jid, to_jid, form, stanza_processor, wait=True):

    s = org.wayround.xmpp.core.Stanza('iq')
    s.set_typ('set')
    s.set_from_jid(from_jid)
    s.set_to_jid(to_jid)
    s.set_objects(
        [
         form
         ]
        )

    res = stanza_processor.send(s, wait=wait)

    if res != None:
        if not res.is_error():
            ret = get_query_from_element(res.get_element())
        else:
            ret = res

    return ret


def unregister(from_jid, to_jid, stanza_processor, wait=True):
    form = org.wayround.xmpp.registration.Query(remove=True)
    return set_form(from_jid, to_jid, form, stanza_processor, wait)
