
import lxml.etree

import wayround_org.utils.types
import wayround_org.utils.factory
import wayround_org.utils.lxml

import wayround_org.xmpp.xdata_media_element


class InvalidForm(Exception):
    pass


class XData:

    def __init__(
        self,
        typ='form', title=None, instructions=None, fields=None,
        reported_fields=None, reported_items=None
        ):

        if instructions == None:
            instructions = []

        if fields == None:
            fields = []

        if reported_fields == None:
            reported_fields = []

        if reported_items == None:
            reported_items = []

        self.set_typ(typ)
        self.set_title(title)
        self.set_instructions(instructions)
        self.set_fields(fields)
        self.set_reported_fields(reported_fields)
        self.set_reported_items(reported_items)

    def check_typ(self, value):
        if not value in ['cancel', 'form', 'result', 'submit']:
            raise ValueError(
                "Invalid form element type ({})".format(value)
                )

        return

    def check_title(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("title must be str or None")

    def check_instructions(self, value):
        if not wayround_org.utils.types.struct_check(
            value, {'t': list, '.': {'t': str}}
            ):
            raise ValueError("instructions must be list of str")

    def check_fields(self, value):
        if not wayround_org.utils.types.struct_check(
            value,
            {'t': list, '.': {'t': XDataField}}
            ):
            raise ValueError(
                "fields and reported must be lists of XDataField"
                )
        return

    check_reported_fields = check_fields

    def check_reported_items(self, value):
        if not wayround_org.utils.types.struct_check(
            value,
            {'t': list, '.':
             {'t': list, '.':
              {'t': XDataField
               }
              }
             }
            ):
            raise ValueError(
                "Invalid list of lists of fields"
                )
        return

    @classmethod
    def new_from_element(cls, element):

        if not wayround_org.utils.lxml.is_lxml_tag_element(element):
            raise TypeError("`element' must be lxml.etree.Element")

        tag = wayround_org.utils.lxml.parse_element_tag(
            element, 'x', ['jabber:x:data']
            )[0]

        if tag is None:
            raise ValueError("Invalid element")

        ret = cls()

        ft = element.get('type')
        if ft == None:
            ft = 'form'
        ret.set_typ(ft)

        t = element.find('{jabber:x:data}title')
        if t != None:
            ret.set_title(t.text)

        ins = ret.get_instructions()
        for i in element.findall('{jabber:x:data}instruction'):
            t = i.text
            if t != None:
                ins.append(t)

        fields = ret.get_fields()
        for i in element.findall('{jabber:x:data}field'):
            fields.append(XDataField.new_from_element(i))

        repor = ret.get_reported_fields()
        for i in element.findall('{jabber:x:data}reported'):
            if len(i) == 0:
                raise InvalidForm("Invalid `reported' children count")
            else:
                for j in i:
                    repor.append(XDataField.new_from_element(j))

        repo_items = ret.get_reported_items()
        for i in element.findall('{jabber:x:data}item'):
            items = []
            for j in i:
                if len(j) != len(repor):
                    raise InvalidForm(
    "Reported item field count does not corresponds to reported header"
                        )
                items.append(XDataField.new_from_element(j))

            repo_items.append(items)

        ret.check()
        return ret

    def gen_element(self):

        self.check()

        e = lxml.etree.Element('x')
        e.set('xmlns', 'jabber:x:data')

        t = self.get_typ()
        if t:
            e.set('type', t)

        ti = self.get_title()

        if ti:
            t = lxml.etree.Element('title')
            t.text = ti
            e.append(t)

        ins = self.get_instructions()
        if len(ins) != 0:
            for i in ins:
                t = lxml.etree.Element('instruction')
                t.text = i
                e.append(t)

        fields = self.get_fields()
        if len(fields) != 0:
            for i in fields:
                e.append(i.gen_element())

        rfields = self.get_reported_fields()
        if len(rfields) != 0:

            t = lxml.etree.Element('reported')
            for i in rfields:
                t.append(i.gen_element())

            e.append(t)

        ritems = self.get_reported_items()

        if len(ritems) != 0:

            for i in ritems:

                if len(i) != len(rfields):
                    raise InvalidForm(
    "Reported item field count does not corresponds to reported header"
                    )

                t = lxml.etree.Element('item')

                for j in i:
                    t.append(j.gen_element())

                e.append(t)

        return e

    def gen_info_text(self):

        text = ''

        title = self.get_title()

        if title:
            text += "Title:\n{}".format(title)

        insts = self.get_instructions()

        for i in insts:
            text += "[i]: {}\n".format(i)

        fields = self.get_fields()
        for i in fields:
            typ = i.get_type()
            values = i.get_values()
            values_l = len(values)

            if values_l == 0:
                text += "{} ({})\n".format(i.get_label(), typ)

            else:
                text += "{} ({}):\n".format(
                    i.get_label(), typ
                    )

                for j in values:
                    lines = j.get_value().splitlines()
                    for k in lines:
                        text += '    {}\n'.format(k)

        return text

wayround_org.utils.factory.class_generate_attributes(
    XData,
    ['typ', 'title', 'instructions', 'fields', 'reported_fields',
     'reported_items']
    )
wayround_org.utils.factory.class_generate_check(
    XData,
    ['typ', 'title', 'instructions', 'fields', 'reported_fields',
     'reported_items']
    )


class XDataField:

    def __init__(
        self,
        var=None, label=None, typ='fixed', desc=None,
        required=False, values=None, options=None, media=None
        ):

        if options == None:
            options = []

        if values == None:
            values = []

        self.set_var(var)
        self.set_label(label)
        self.set_type(typ)
        self.set_desc(desc)
        self.set_required(required)
        self.set_values(values)
        self.set_options(options)
        self.set_media(media)

        return

    def check_options(self, value):
        if not wayround_org.utils.types.struct_check(
            value, {'t': list, '.': {'t': XDataOption}}
            ):
            raise ValueError("`options' must be list of XDataOption")

    def check_values(self, value):
        if not wayround_org.utils.types.struct_check(
            value, {'t': list, '.': {'t': XDataValue}}
            ):
            raise ValueError("`values' must be list of XDataValue")

    def check_required(self, value):
        if not isinstance(value, bool):
            raise TypeError("`required' must be bool")

    def check_desc(self, value):
        if value != None and not isinstance(value, str):
            raise TypeError("`desc' must be None or str")

    def check_type(self, value):
        if not value in [
            'boolean', 'fixed', 'hidden', 'jid-multi',
            'jid-single', 'list-multi', 'list-single',
            'text-multi', 'text-private', 'text-single'
            ]:
            raise InvalidForm("Invalid field `type' value")

    def check_var(self, value):
        if value != None and not isinstance(value, str):
            raise TypeError("`var' must be None or str")

    def check_label(self, value):
        if value != None and not isinstance(value, str):
            raise TypeError("`label' must be None or str")

    def check_media(self, value):
        if (value != None
            and
            not isinstance(
                value, wayround_org.xmpp.xdata_media_element.Media)
            ):
            raise TypeError("`media' must be None or str")

    @classmethod
    def new_from_element(cls, element):

        if not wayround_org.utils.lxml.is_lxml_tag_element(element):
            raise TypeError("`element' must be lxml.etree.Element")

        if element.tag != '{jabber:x:data}field':
            raise Exception("Invalid element")

        ret = cls()

        ret.set_var(element.get('var'))
        ret.set_label(element.get('label'))

        v = element.findall('{jabber:x:data}value')
        cv = ret.get_values()
        for j in v:
            cv.append(XDataValue.new_from_element(j))

        d = element.find('{jabber:x:data}desc')
        if d != None:
            ret.set_desc(d.text)

        d = element.find('{urn:xmpp:media-element}media')
        if d != None:
            ret.set_media(
                wayround_org.xmpp.xdata_media_element.Media.new_from_element(d)
                )

        ret.set_required(element.find('{jabber:x:data}required') != None)

        o = element.findall('{jabber:x:data}option')
        co = ret.get_options()
        for j in o:
            co.append(XDataOption.new_from_element(j))

        t = element.get('type')
        if t == None:
            t = 'text-single'

        ret.set_type(t)

        ret.check()

        return ret

    def gen_element(self):

        self.check()

        e = lxml.etree.Element('field')

        t = self.get_var()
        if t:
            e.set('var', t)

        t = self.get_label()
        if t:
            e.set('label', t)

        t = self.get_type()
        if self.get_type():
            e.set('type', t)

        values = self.get_values()
        if len(values) != 0:
            for i in values:
                e.append(i.gen_element())

        desc = self.get_desc()
        if desc:
            _t = lxml.etree.Element('desc')
            _t.text = desc
            e.append(_t)

        required = self.get_required()
        if required:
            _t = lxml.etree.Element('required')
            e.append(_t)

        options = self.get_options()
        if len(options) != 0:

            for i in options:
                e.append(i.gen_element())

        media = self.get_media()
        if media:
            e.append(media.gen_element())

        return e

wayround_org.utils.factory.class_generate_attributes(
    XDataField,
    ['var', 'label', 'type', 'desc', 'required', 'values', 'options', 'media']
    )
wayround_org.utils.factory.class_generate_check(
    XDataField,
    ['var', 'label', 'type', 'desc', 'required', 'values', 'options', 'media']
    )


class XDataOption:

    def __init__(self, label=None, value=None):

        self.set_label(label)
        self.set_value(value)

    @classmethod
    def new_from_element(cls, element):

        if not wayround_org.utils.lxml.is_lxml_tag_element(element):
            raise TypeError("`element' must be lxml.etree.Element")

        if element.tag != '{jabber:x:data}option':
            raise Exception("Invalid element")

        ret = cls()
        ret.set_label(element.get('label'))
        v = element.find('{jabber:x:data}value')
        if v != None:
            ret.set_value(XDataValue.new_from_element(v))
        else:
            raise InvalidForm("Option without value")

        ret.check()

        return ret

    def check_label(self, value):
        if value != None and not isinstance(value, str):
            raise TypeError("`value' must be None or str")

    def check_value(self, value):
        if value != None and not isinstance(value, XDataValue):
            raise TypeError("`value' must be None or XDataValue")

    def gen_element(self):

        self.check()

        o = lxml.etree.Element('option')
        l = self.get_label()
        if l:
            o.set('label', l)

        value = self.get_value()
        if not isinstance(value, XDataValue):
            raise InvalidForm("option must have value")
        o.append(value.gen_element())

        return o

wayround_org.utils.factory.class_generate_attributes(
    XDataOption,
    ['label', 'value']
    )
wayround_org.utils.factory.class_generate_check(
    XDataOption,
    ['label', 'value']
    )


class XDataValue:

    def __init__(self, value):

        self.set_value(value)

    def check_value(self, value):
        if not isinstance(value, str):
            raise ValueError("`value' must be str, not {}".format(type(value)))

    @classmethod
    def new_from_element(cls, element):

        if not wayround_org.utils.lxml.is_lxml_tag_element(element):
            raise TypeError("`element' must be lxml.etree.Element")

        if element.tag != '{jabber:x:data}value':
            raise Exception("Invalid element")

        t = element.text
        if t == None:
            t = ''

        ret = cls(t)

        return ret

    def gen_element(self):
        self.check()
        e = lxml.etree.Element('value')
        e.text = self._value
        return e

wayround_org.utils.factory.class_generate_attributes(
    XDataValue,
    ['value']
    )
wayround_org.utils.factory.class_generate_check(
    XDataValue,
    ['value']
    )


def get_x_data_elements(element):

    """
    Search for jabber:x:data elements in supplied element
    """

    if not wayround_org.utils.lxml.is_lxml_tag_element(element):
        raise TypeError("`element' must be lxml.etree.Element")

    return element.findall('{jabber:x:data}x')


def get_x_data_element(element):

    ret = get_x_data_elements(element)

    if ret:
        ret = ret[0]
    else:
        ret = None

    return ret
