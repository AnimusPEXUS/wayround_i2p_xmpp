
"""
XEP-0054 implementation
"""

import lxml.etree

import org.wayround.utils.lxml
import org.wayround.utils.types


class PCData:

    def __init__(self, tag, text):

        self.set_tag(tag)
        self.set_text(text)

    def check_tag(self, value):
        if not isinstance(value, str):
            raise ValueError("`tag' must be str")

    def check_text(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`text' must be str")

    @classmethod
    def new_from_element(cls, element):
        tag = org.wayround.utils.lxml.parse_element_tag(
            element,
            None,
            ['vcard-temp']
            )[0]

        cl = cls(tag, element.text)

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element(self.get_tag())

        el.text = self.get_text()

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(
    PCData,
    ['tag', 'text']
    )


class Empty:

    def __init__(self, tag, text):

        self.set_tag(tag)

    def check_tag(self, value):
        if not isinstance(value, str):
            raise ValueError("`tag' must be str")

    @classmethod
    def new_from_element(cls, element):
        tag = org.wayround.utils.lxml.parse_element_tag(
            element,
            None,
            ['vcard-temp']
            )[0]

        cl = cls(tag, element.text)

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element(self.get_tag())

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(Empty, ['tag'])


N_ELEMENTS = [
    ('FAMILY?', PCData, 'family')
    ('GIVEN?', PCData, 'given')
    ('MIDDLE?', PCData, 'middle')
    ('PREFIX?', PCData, 'prefix')
    ('SUFFIX?', PCData, 'suffix')
    ]

N_CLASS_PROPS = list(i[2] for i in N_ELEMENTS)


class N:

    def __init__(self, **kwargs):

        for i in N_CLASS_PROPS:
            set_func = getattr(self, 'set_{}'.format(i))
            set_func(kwargs.get(i))

        return

    for i in N_CLASS_PROPS:
        exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, str):
        raise ValueError("`{i}' must be None or str")
        """.format(i=i))

    del i

    @classmethod
    def new_from_element(cls, element):

        cl = cls()

        org.wayround.utils.lxml.subelems_to_object_props2(
            element, cl,
            N_ELEMENTS
            )

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('N')

        org.wayround.utils.lxml.object_props_to_subelems2(
            self, el,
            N_ELEMENTS
            )

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(
    N,
    N_CLASS_PROPS
    )

PHOTO_ELEMENTS = [
    ('TYPE?', PCData, 'type'),
    ('BINVAL?', PCData, 'binval'),
    ('EXTVAL?', PCData, 'extval')
    ]

PHOTO_CLASS_PROPS = list(i[2] for i in PHOTO_ELEMENTS)


class Photo:

    def __init__(self, **kwargs):

        for i in PHOTO_CLASS_PROPS:
            set_func = getattr(self, 'set_{}'.format(i))
            set_func(kwargs.get(i))

        return

    for i in PHOTO_CLASS_PROPS:
        exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, str):
        raise ValueError("`{i}' must be None or str")
        """.format(i=i))

    del i

    @classmethod
    def new_from_element(cls, element):

        cl = cls()

        org.wayround.utils.lxml.subelems_to_object_props2(
            element, cl,
            N_ELEMENTS
            )

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('PHOTO')

        org.wayround.utils.lxml.object_props_to_subelems2(
            self, el,
            N_ELEMENTS
            )

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(
    Photo,
    PHOTO_CLASS_PROPS
    )


ADR_ELEMENTS = [
    ('HOME?', Empty, 'home'),
    ('WORK?', Empty, 'work'),
    ('POSTAL?', Empty, 'postal'),
    ('PARCEL?', Empty, 'parcel'),
    ('DOM?', Empty, 'dom'),
    ('INTL?', Empty, 'intl'),
    ('PREF?', Empty, 'pref'),
    ('POBOX?', PCData, 'pobox'),
    ('EXTADD?', PCData, 'extadd'),
    ('STREET?', PCData, 'street'),
    ('LOCALITY?', PCData, 'locality'),
    ('REGION?', PCData, 'region'),
    ('PCODE?', PCData, 'pcode'),
    ('CTRY?', PCData, 'ctry')
    ]

ADR_CLASS_PROPS = list(i[2] for i in ADR_ELEMENTS)


class Adr:

    def __init__(self, **kwargs):

        for i in ADR_CLASS_PROPS:
            set_func = getattr(self, 'set_{}'.format(i))
            set_func(kwargs.get(i))

        return

    for i in ADR_ELEMENTS:
        if i[1] == PCData:
            exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, PCData):
        raise ValueError("`{i}' must be None or PCData")
        """.format(i=i[2]))

        if i[1] == Empty:
            exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, Empty):
        raise ValueError("`{i}' must be None or Empty")
        """.format(i=i[2]))

    del i

    @classmethod
    def new_from_element(cls, element):

        cl = cls()

        org.wayround.utils.lxml.subelems_to_object_props2(
            element, cl,
            ADR_ELEMENTS
            )

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('PHOTO')

        org.wayround.utils.lxml.object_props_to_subelems2(
            self, el,
            ADR_ELEMENTS
            )

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(
    Adr,
    ADR_CLASS_PROPS
    )

LABEL_ELEMENTS = [
    ('HOME?', Empty, 'home'),
    ('WORK?', Empty, 'work'),
    ('POSTAL?', Empty, 'postal'),
    ('PARCEL?', Empty, 'parcel'),
    ('DOM?', Empty, 'dom'),
    ('INTL?', Empty, 'intl'),
    ('PREF?', Empty, 'pref'),
    ('LINE*', PCData, 'line')
    ]

LABEL_CLASS_PROPS = list(i[2] for i in LABEL_ELEMENTS)


class Label:

    def __init__(self, **kwargs):

        for i in LABEL_CLASS_PROPS:
            set_func = getattr(self, 'set_{}'.format(i))
            set_func(kwargs.get(i))

        return

    for i in LABEL_ELEMENTS:
        if i[1] == PCData:
            exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, PCData):
        raise ValueError("`{i}' must be None or PCData")
        """.format(i=i[2]))

        if i[1] == Empty:
            exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, Empty):
        raise ValueError("`{i}' must be None or Empty")
        """.format(i=i[2]))

    del i

    @classmethod
    def new_from_element(cls, element):

        cl = cls()

        org.wayround.utils.lxml.subelems_to_object_props2(
            element, cl,
            LABEL_ELEMENTS
            )

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('LABEL')

        org.wayround.utils.lxml.object_props_to_subelems2(
            self, el,
            LABEL_ELEMENTS
            )

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(
    Label,
    LABEL_CLASS_PROPS
    )


TEL_ELEMENTS = [
    ('HOME?', Empty, 'home'),
    ('WORK?', Empty, 'work'),
    ('VOICE?', Empty, 'voice'),
    ('FAX?', Empty, 'fax'),
    ('PAGER?', Empty, 'pager'),
    ('MSG?', Empty, 'msg'),
    ('CELL?', Empty, 'cell'),
    ('VIDEO?', Empty, 'video'),
    ('BBS?', Empty, 'bbs'),
    ('MODEM?', Empty, 'modem'),
    ('ISDN?', Empty, 'isdn'),
    ('PCS?', Empty, 'pcs'),
    ('PREF?', Empty, 'pref'),
    ('NUMBER', PCData, 'number')
    ]

TEL_CLASS_PROPS = list(i[2] for i in TEL_ELEMENTS)


class Tel:

    def __init__(self, **kwargs):

        for i in TEL_CLASS_PROPS:
            set_func = getattr(self, 'set_{}'.format(i))
            set_func(kwargs.get(i))

        return

    for i in TEL_ELEMENTS:
        if i[1] == PCData:
            exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, PCData):
        raise ValueError("`{i}' must be None or PCData")
        """.format(i=i[2]))

        if i[1] == Empty:
            exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, Empty):
        raise ValueError("`{i}' must be None or Empty")
        """.format(i=i[2]))

    del i

    @classmethod
    def new_from_element(cls, element):

        cl = cls()

        org.wayround.utils.lxml.subelems_to_object_props2(
            element, cl,
            TEL_ELEMENTS
            )

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('TEL')

        org.wayround.utils.lxml.object_props_to_subelems2(
            self, el,
            TEL_ELEMENTS
            )

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(
    Tel,
    TEL_CLASS_PROPS
    )


EMAIL_ELEMENTS = [
    ('HOME?', Empty, 'home'),
    ('WORK?', Empty, 'work'),
    ('INTERNET?', Empty, 'internet'),
    ('PREF?', Empty, 'pref'),
    ('X400?', Empty, 'x400'),
    ('USERID', PCData, 'msg')
    ]

EMAIL_CLASS_PROPS = list(i[2] for i in EMAIL_ELEMENTS)


class Email:

    def __init__(self, **kwargs):

        for i in EMAIL_CLASS_PROPS:
            set_func = getattr(self, 'set_{}'.format(i))
            set_func(kwargs.get(i))

        return

    for i in EMAIL_ELEMENTS:
        if i[1] == PCData:
            exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, PCData):
        raise ValueError("`{i}' must be None or PCData")
        """.format(i=i[2]))

        if i[1] == Empty:
            exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, Empty):
        raise ValueError("`{i}' must be None or Empty")
        """.format(i=i[2]))

    del i

    @classmethod
    def new_from_element(cls, element):

        cl = cls()

        org.wayround.utils.lxml.subelems_to_object_props2(
            element, cl,
            EMAIL_ELEMENTS
            )

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('EMAIL')

        org.wayround.utils.lxml.object_props_to_subelems2(
            self, el,
            EMAIL_ELEMENTS
            )

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(
    Email,
    EMAIL_CLASS_PROPS
    )


GEO_ELEMENTS = [
    ('LAT', PCData, 'lat'),
    ('LON', PCData, 'lon')
    ]

GEO_CLASS_PROPS = list(i[2] for i in GEO_ELEMENTS)


class Geo:

    def __init__(self, **kwargs):

        for i in GEO_CLASS_PROPS:
            set_func = getattr(self, 'set_{}'.format(i))
            set_func(kwargs.get(i))

        return

    for i in GEO_ELEMENTS:
        if i[1] == PCData:
            exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, PCData):
        raise ValueError("`{i}' must be None or PCData")
        """.format(i=i[2]))

        if i[1] == Empty:
            exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, Empty):
        raise ValueError("`{i}' must be None or Empty")
        """.format(i=i[2]))

    del i

    @classmethod
    def new_from_element(cls, element):

        cl = cls()

        org.wayround.utils.lxml.subelems_to_object_props2(
            element, cl,
            GEO_ELEMENTS
            )

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('GEO')

        org.wayround.utils.lxml.object_props_to_subelems2(
            self, el,
            GEO_ELEMENTS
            )

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(
    Geo,
    GEO_CLASS_PROPS
    )


LOGO_ELEMENTS = [
    ('TYPE?', PCData, 'type'),
    ('BINVAL?', PCData, 'binval'),
    ('EXTVAL?', PCData, 'extval')
    ]

LOGO_CLASS_PROPS = list(i[2] for i in LOGO_ELEMENTS)


class Logo:

    def __init__(self, **kwargs):

        for i in LOGO_CLASS_PROPS:
            set_func = getattr(self, 'set_{}'.format(i))
            set_func(kwargs.get(i))

        return

    for i in LOGO_CLASS_PROPS:
        exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, str):
        raise ValueError("`{i}' must be None or str")
        """.format(i=i))

    del i

    @classmethod
    def new_from_element(cls, element):

        cl = cls()

        org.wayround.utils.lxml.subelems_to_object_props2(
            element, cl,
            LOGO_ELEMENTS
            )

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('LOGO')

        org.wayround.utils.lxml.object_props_to_subelems2(
            self, el,
            LOGO_ELEMENTS
            )

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(
    Logo,
    LOGO_CLASS_PROPS
    )


ORG_ELEMENTS = [
    ('ORGNAME', PCData, 'orgname'),
    ('ORGUNIT', PCData, 'orgunit')
    ]

ORG_CLASS_PROPS = list(i[2] for i in ORG_ELEMENTS)


class Org:

    def __init__(self, **kwargs):

        for i in ORG_CLASS_PROPS:
            set_func = getattr(self, 'set_{}'.format(i))
            set_func(kwargs.get(i))

        return

    for i in ORG_ELEMENTS:
        if i[1] == PCData:
            exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, PCData):
        raise ValueError("`{i}' must be None or PCData")
        """.format(i=i[2]))

        if i[1] == Empty:
            exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, Empty):
        raise ValueError("`{i}' must be None or Empty")
        """.format(i=i[2]))

    del i

    @classmethod
    def new_from_element(cls, element):

        cl = cls()

        org.wayround.utils.lxml.subelems_to_object_props2(
            element, cl,
            ORG_ELEMENTS
            )

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('ORG')

        org.wayround.utils.lxml.object_props_to_subelems2(
            self, el,
            ORG_ELEMENTS
            )

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(
    Org,
    ORG_CLASS_PROPS
    )


CATEGORIES_ELEMENTS = [
    ('KEYWORD*', PCData, 'keyword')
    ]

CATEGORIES_CLASS_PROPS = list(i[2] for i in CATEGORIES_ELEMENTS)


class Categories:

    def __init__(self, **kwargs):

        for i in CATEGORIES_CLASS_PROPS:
            set_func = getattr(self, 'set_{}'.format(i))
            set_func(kwargs.get(i))

        return

    for i in CATEGORIES_ELEMENTS:
        if i[1] == PCData:
            exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, PCData):
        raise ValueError("`{i}' must be None or PCData")
        """.format(i=i[2]))

        if i[1] == Empty:
            exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, Empty):
        raise ValueError("`{i}' must be None or Empty")
        """.format(i=i[2]))

    del i

    @classmethod
    def new_from_element(cls, element):

        cl = cls()

        org.wayround.utils.lxml.subelems_to_object_props2(
            element, cl,
            CATEGORIES_ELEMENTS
            )

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('CATEGORIES')

        org.wayround.utils.lxml.object_props_to_subelems2(
            self, el,
            CATEGORIES_ELEMENTS
            )

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(
    Categories,
    CATEGORIES_CLASS_PROPS
    )


SOUND_ELEMENTS = [
    ('PHONETIC?', PCData, 'phonetic'),
    ('BINVAL?', PCData, 'binval'),
    ('EXTVAL?', PCData, 'extval')
    ]

SOUND_CLASS_PROPS = list(i[2] for i in SOUND_ELEMENTS)


class Sound:

    def __init__(self, **kwargs):

        for i in SOUND_CLASS_PROPS:
            set_func = getattr(self, 'set_{}'.format(i))
            set_func(kwargs.get(i))

        return

    for i in SOUND_CLASS_PROPS:
        exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, str):
        raise ValueError("`{i}' must be None or str")
        """.format(i=i))

    del i

    @classmethod
    def new_from_element(cls, element):

        cl = cls()

        org.wayround.utils.lxml.subelems_to_object_props2(
            element, cl,
            SOUND_ELEMENTS
            )

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('SOUND')

        org.wayround.utils.lxml.object_props_to_subelems2(
            self, el,
            SOUND_ELEMENTS
            )

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(
    Sound,
    SOUND_CLASS_PROPS
    )


CLASS_ELEMENTS = [
    ('PUBLIC', Empty, 'public'),
    ('PRIVATE', Empty, 'private'),
    ('CONFIDENTIAL', Empty, 'confidential')
    ]

CLASS_CLASS_PROPS = list(i[2] for i in CLASS_ELEMENTS)


class Class:

    def __init__(self, **kwargs):

        for i in CLASS_CLASS_PROPS:
            set_func = getattr(self, 'set_{}'.format(i))
            set_func(kwargs.get(i))

        return

    for i in CLASS_ELEMENTS:
        if i[1] == PCData:
            exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, PCData):
        raise ValueError("`{i}' must be None or PCData")
        """.format(i=i[2]))

        if i[1] == Empty:
            exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, Empty):
        raise ValueError("`{i}' must be None or Empty")
        """.format(i=i[2]))

    del i

    @classmethod
    def new_from_element(cls, element):

        cl = cls()

        org.wayround.utils.lxml.subelems_to_object_props2(
            element, cl,
            CLASS_ELEMENTS
            )

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('CLASS')

        org.wayround.utils.lxml.object_props_to_subelems2(
            self, el,
            CLASS_ELEMENTS
            )

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(
    Class,
    CLASS_CLASS_PROPS
    )


KEY_ELEMENTS = [
    ('TYPE?', Empty, 'type_'),
    ('CRED', Empty, 'cred')
    ]

KEY_CLASS_PROPS = list(i[2] for i in KEY_ELEMENTS)


class Key:

    def __init__(self, **kwargs):

        for i in KEY_CLASS_PROPS:
            set_func = getattr(self, 'set_{}'.format(i))
            set_func(kwargs.get(i))

        return

    for i in KEY_ELEMENTS:
        if i[1] == PCData:
            exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, PCData):
        raise ValueError("`{i}' must be None or PCData")
        """.format(i=i[2]))

        if i[1] == Empty:
            exec("""
def check_{i}(self, value):
    if value is not None and not isinstnace(value, Empty):
        raise ValueError("`{i}' must be None or Empty")
        """.format(i=i[2]))

    del i

    @classmethod
    def new_from_element(cls, element):

        cl = cls()

        org.wayround.utils.lxml.subelems_to_object_props2(
            element, cl,
            KEY_ELEMENTS
            )

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('KEY')

        org.wayround.utils.lxml.object_props_to_subelems2(
            self, el,
            KEY_ELEMENTS
            )

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(
    Key,
    KEY_CLASS_PROPS
    )



class XCardTemp:

    def __init__(self, order=None):

        if order == None:
            order = []

        self.set_order(order)

        return

    def check_order(self, value):
        if not org.wayround.utils.types.struct_check(
            value,
            {'t': list, '.':
             {'t': tuple, '<': 3, '>': 3}
             }
            ):
            raise TypeError("`order' must be list of triple tuples")

    @classmethod
    def new_from_element(cls, element):

        tag = org.wayround.utils.lxml.parse_element_tag(
            element,
            'vCard',
            ['vcard-temp']
            )[0]

        if tag == None:
            raise ValueError("invalid element")

        cl = cls()

        order = []

        org.wayround.utils.lxml.subelems_to_order(
            element, order,
            VCARD_ELEMENTS
            )

        cl.set_order(order)

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('vCard')
        el.set('xmlns', 'vcard-temp')

        org.wayround.utils.lxml.subelems_to_order(
            self.get_order(), el
            )

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(
    XCardTemp,
    ['order']
    )

VCARD_ELEMENTS = [
    ('FN', PCData, 'fn'),
    ('N', N, 'n'),
    ('NICKNAME*', PCData, 'nickname'),
    ('PHOTO*', Photo, 'photo'),
    ('BDAY*', PCData, 'bday'),
    ('ADR*', Adr, 'adr'),
    ('LABEL*', Label, 'label'),
    ('TEL*', Tel, 'tel'),
    ('EMAIL*', Email, 'email'),
    ('JABBERID*', PCData, 'jabberid'),
    ('MAILER*', PCData, 'mailer'),
    ('TZ*', PCData, 'tz'),
    ('GEO*', Geo, 'geo'),
    ('TITLE*', PCData, 'title'),
    ('ROLE*', PCData, 'role'),
    ('LOGO*', Logo, 'logo'),
    ('AGENT*', XCardTemp, 'agent'),
    ('ORG*', Org, 'org'),
    ('CATEGORIES*', 'categories', Categories),
    ('NOTE*', PCData, 'note'),
    ('PRODID*', PCData, 'prodid'),
    ('REV*', PCData, 'rev'),
    ('SORT-STRING*', PCData, 'sort_string'),
    ('SOUND*', Sound, 'sound'),
    ('UID*', PCData, 'uid'),
    ('URL*', PCData, 'url'),
    ('CLASS*', Class, 'class'),
    ('KEY*', Key, 'key'),
    ('DESC*', PCData, 'desc')
    ]

VCARD_CLASS_PROPS = list(i[2] for i in VCARD_ELEMENTS)
