
"""
XEP-0054 implementation

The main programmer interface to this module should be and XCardTemp class
"""

import lxml.etree

import org.wayround.utils.lxml
import org.wayround.utils.types
import org.wayround.utils.factory

NAMESPACE = 'vcard-temp'


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
            [NAMESPACE]
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
            [NAMESPACE]
            )[0]

        cl = cls(tag, element.text)

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element(self.get_tag())

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(Empty, ['tag'])


N_ELEMENTS = [
    ('FAMILY', PCData, 'family', '?'),
    ('GIVEN', PCData, 'given', '?'),
    ('MIDDLE', PCData, 'middle', '?'),
    ('PREFIX', PCData, 'prefix', '?'),
    ('SUFFIX', PCData, 'suffix', '?')
    ]

N_CLASS_PROPS = list(i[2] for i in N_ELEMENTS)


class N:
    pass

org.wayround.utils.lxml.simple_exchange_class_factory(
    N,
    'N',
    NAMESPACE,
    N_ELEMENTS,
    N_CLASS_PROPS
    )

org.wayround.utils.lxml.checker_factory(
    N,
    N_ELEMENTS
    )

org.wayround.utils.factory.class_generate_attributes_and_check(
    N,
    N_CLASS_PROPS
    )


PHOTO_ELEMENTS = [
    ('TYPE', PCData, 'type', '?'),
    ('BINVAL', PCData, 'binval', '?'),
    ('EXTVAL', PCData, 'extval', '?')
    ]

PHOTO_CLASS_PROPS = list(i[2] for i in PHOTO_ELEMENTS)


class Photo:
    pass

org.wayround.utils.lxml.simple_exchange_class_factory(
    Photo,
    'PHOTO',
    NAMESPACE,
    PHOTO_ELEMENTS,
    PHOTO_CLASS_PROPS
    )

org.wayround.utils.factory.class_generate_attributes_and_check(
    Photo,
    PHOTO_CLASS_PROPS
    )

org.wayround.utils.lxml.checker_factory(
    Photo,
    PHOTO_ELEMENTS
    )


ADR_ELEMENTS = [
    ('HOME', Empty, 'home', '?'),
    ('WORK', Empty, 'work', '?'),
    ('POSTAL', Empty, 'postal', '?'),
    ('PARCEL', Empty, 'parcel', '?'),
    ('DOM', Empty, 'dom', '?'),
    ('INTL', Empty, 'intl', '?'),
    ('PREF', Empty, 'pref', '?'),
    ('POBOX', PCData, 'pobox', '?'),
    ('EXTADD', PCData, 'extadd', '?'),
    ('STREET', PCData, 'street', '?'),
    ('LOCALITY', PCData, 'locality', '?'),
    ('REGION', PCData, 'region', '?'),
    ('PCODE', PCData, 'pcode', '?'),
    ('CTRY', PCData, 'ctry', '?')
    ]

ADR_CLASS_PROPS = list(i[2] for i in ADR_ELEMENTS)


class Adr:
    pass

org.wayround.utils.lxml.simple_exchange_class_factory(
    Adr,
    'ADR',
    NAMESPACE,
    ADR_ELEMENTS,
    ADR_CLASS_PROPS
    )

org.wayround.utils.factory.class_generate_attributes_and_check(
    Adr,
    ADR_CLASS_PROPS
    )

org.wayround.utils.lxml.checker_factory(
    Adr,
    ADR_ELEMENTS
    )


LABEL_ELEMENTS = [
    ('HOME', Empty, 'home', '?'),
    ('WORK', Empty, 'work', '?'),
    ('POSTAL', Empty, 'postal', '?'),
    ('PARCEL', Empty, 'parcel', '?'),
    ('DOM', Empty, 'dom', '?'),
    ('INTL', Empty, 'intl', '?'),
    ('PREF', Empty, 'pref', '?'),
    ('LINE', PCData, 'line', '+')
    ]

LABEL_CLASS_PROPS = list(i[2] for i in LABEL_ELEMENTS)


class Label:
    pass

org.wayround.utils.lxml.simple_exchange_class_factory(
    Label,
    'LABEL',
    NAMESPACE,
    LABEL_ELEMENTS,
    LABEL_CLASS_PROPS
    )

org.wayround.utils.factory.class_generate_attributes_and_check(
    Label,
    LABEL_CLASS_PROPS
    )

org.wayround.utils.lxml.checker_factory(
    Label,
    LABEL_ELEMENTS
    )


TEL_ELEMENTS = [
    ('HOME', Empty, 'home', '?'),
    ('WORK', Empty, 'work', '?'),
    ('VOICE', Empty, 'voice', '?'),
    ('FAX', Empty, 'fax', '?'),
    ('PAGER', Empty, 'pager', '?'),
    ('MSG', Empty, 'msg', '?'),
    ('CELL', Empty, 'cell', '?'),
    ('VIDEO', Empty, 'video', '?'),
    ('BBS', Empty, 'bbs', '?'),
    ('MODEM', Empty, 'modem', '?'),
    ('ISDN', Empty, 'isdn', '?'),
    ('PCS', Empty, 'pcs', '?'),
    ('PREF', Empty, 'pref', '?'),
    ('NUMBER', PCData, 'number', '')
    ]

TEL_CLASS_PROPS = list(i[2] for i in TEL_ELEMENTS)


class Tel:
    pass

org.wayround.utils.lxml.simple_exchange_class_factory(
    Tel,
    'TEL',
    NAMESPACE,
    TEL_ELEMENTS,
    TEL_CLASS_PROPS
    )

org.wayround.utils.factory.class_generate_attributes_and_check(
    Tel,
    TEL_CLASS_PROPS
    )

org.wayround.utils.lxml.checker_factory(
    Tel,
    TEL_ELEMENTS
    )


EMAIL_ELEMENTS = [
    ('HOME', Empty, 'home', '?'),
    ('WORK', Empty, 'work', '?'),
    ('INTERNET', Empty, 'internet', '?'),
    ('PREF', Empty, 'pref', '?'),
    ('X400', Empty, 'x400', '?'),
    ('USERID', PCData, 'userid', '')
    ]

EMAIL_CLASS_PROPS = list(i[2] for i in EMAIL_ELEMENTS)


class Email:
    pass

org.wayround.utils.lxml.simple_exchange_class_factory(
    Email,
    'EMAIL',
    NAMESPACE,
    EMAIL_ELEMENTS,
    EMAIL_CLASS_PROPS
    )

org.wayround.utils.factory.class_generate_attributes_and_check(
    Email,
    EMAIL_CLASS_PROPS
    )

org.wayround.utils.lxml.checker_factory(
    Email,
    EMAIL_ELEMENTS
    )


GEO_ELEMENTS = [
    ('LAT', PCData, 'lat', ''),
    ('LON', PCData, 'lon', '')
    ]

GEO_CLASS_PROPS = list(i[2] for i in GEO_ELEMENTS)


class Geo:
    pass

org.wayround.utils.lxml.simple_exchange_class_factory(
    Geo,
    'GEO',
    NAMESPACE,
    GEO_ELEMENTS,
    GEO_CLASS_PROPS
    )

org.wayround.utils.factory.class_generate_attributes_and_check(
    Geo,
    GEO_CLASS_PROPS
    )

org.wayround.utils.lxml.checker_factory(
    Geo,
    GEO_ELEMENTS
    )


LOGO_ELEMENTS = [
    ('TYPE', PCData, 'type', '?'),
    ('BINVAL', PCData, 'binval', '?'),
    ('EXTVAL', PCData, 'extval', '?')
    ]

LOGO_CLASS_PROPS = list(i[2] for i in LOGO_ELEMENTS)


class Logo:
    pass

org.wayround.utils.lxml.simple_exchange_class_factory(
    Logo,
    'LOGO',
    NAMESPACE,
    LOGO_ELEMENTS,
    LOGO_CLASS_PROPS
    )

org.wayround.utils.factory.class_generate_attributes_and_check(
    Logo,
    LOGO_CLASS_PROPS
    )

org.wayround.utils.lxml.checker_factory(
    Logo,
    LOGO_ELEMENTS
    )


ORG_ELEMENTS = [
    ('ORGNAME', PCData, 'orgname', ''),
    ('ORGUNIT', PCData, 'orgunit', '*')
    ]

ORG_CLASS_PROPS = list(i[2] for i in ORG_ELEMENTS)


class Org:
    pass

org.wayround.utils.lxml.simple_exchange_class_factory(
    Org,
    'ORG',
    NAMESPACE,
    ORG_ELEMENTS,
    ORG_CLASS_PROPS
    )

org.wayround.utils.factory.class_generate_attributes_and_check(
    Org,
    ORG_CLASS_PROPS
    )

org.wayround.utils.lxml.checker_factory(
    Org,
    ORG_ELEMENTS
    )


CATEGORIES_ELEMENTS = [
    ('KEYWORD', PCData, 'keyword', '+')
    ]

CATEGORIES_CLASS_PROPS = list(i[2] for i in CATEGORIES_ELEMENTS)


class Categories:
    pass

org.wayround.utils.lxml.simple_exchange_class_factory(
    Categories,
    'CATEGORIES',
    NAMESPACE,
    CATEGORIES_ELEMENTS,
    CATEGORIES_CLASS_PROPS
    )

org.wayround.utils.factory.class_generate_attributes_and_check(
    Categories,
    CATEGORIES_CLASS_PROPS
    )

org.wayround.utils.lxml.checker_factory(
    Categories,
    CATEGORIES_ELEMENTS
    )


SOUND_ELEMENTS = [
    ('PHONETIC', PCData, 'phonetic', '?'),
    ('BINVAL', PCData, 'binval', '?'),
    ('EXTVAL', PCData, 'extval', '?')
    ]

SOUND_CLASS_PROPS = list(i[2] for i in SOUND_ELEMENTS)


class Sound:
    pass

org.wayround.utils.lxml.simple_exchange_class_factory(
    Sound,
    'SOUND',
    NAMESPACE,
    SOUND_ELEMENTS,
    SOUND_CLASS_PROPS
    )

org.wayround.utils.factory.class_generate_attributes_and_check(
    Sound,
    SOUND_CLASS_PROPS
    )

org.wayround.utils.lxml.checker_factory(
    Sound,
    SOUND_ELEMENTS
    )


CLASS_ELEMENTS = [
    ('PUBLIC', Empty, 'public', '?'),
    ('PRIVATE', Empty, 'private', '?'),
    ('CONFIDENTIAL', Empty, 'confidential', '?')
    ]

CLASS_CLASS_PROPS = list(i[2] for i in CLASS_ELEMENTS)


class Class:
    pass

org.wayround.utils.lxml.simple_exchange_class_factory(
    Class,
    'CLASS',
    NAMESPACE,
    CLASS_ELEMENTS,
    CLASS_CLASS_PROPS
    )

org.wayround.utils.factory.class_generate_attributes_and_check(
    Class,
    CLASS_CLASS_PROPS
    )

org.wayround.utils.lxml.checker_factory(
    Class,
    CLASS_ELEMENTS
    )

KEY_ELEMENTS = [
    ('TYPE', Empty, 'type_', '?'),
    ('CRED', PCData, 'cred', '')
    ]

KEY_CLASS_PROPS = list(i[2] for i in KEY_ELEMENTS)


class Key:
    pass

org.wayround.utils.lxml.simple_exchange_class_factory(
    Key,
    'KEY',
    NAMESPACE,
    KEY_ELEMENTS,
    KEY_CLASS_PROPS
    )

org.wayround.utils.factory.class_generate_attributes_and_check(
    Key,
    KEY_CLASS_PROPS
    )

org.wayround.utils.lxml.checker_factory(
    Key,
    KEY_ELEMENTS
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
            [NAMESPACE]
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
        el.set('xmlns', NAMESPACE)

        org.wayround.utils.lxml.subelems_to_order(
            self.get_order(), el,
            VCARD_ELEMENTS
            )

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(
    XCardTemp,
    ['order']
    )

VCARD_ELEMENTS = [
    ('FN', PCData, 'fn', ''),
    ('N', N, 'n', ''),
    ('NICKNAME*', PCData, 'nickname', '*'),
    ('PHOTO*', Photo, 'photo', '*'),
    ('BDAY*', PCData, 'bday', '*'),
    ('ADR*', Adr, 'adr', '*'),
    ('LABEL*', Label, 'label', '*'),
    ('TEL*', Tel, 'tel', '*'),
    ('EMAIL*', Email, 'email', '*'),
    ('JABBERID*', PCData, 'jabberid', '*'),
    ('MAILER*', PCData, 'mailer', '*'),
    ('TZ*', PCData, 'tz', '*'),
    ('GEO*', Geo, 'geo', '*'),
    ('TITLE*', PCData, 'title', '*'),
    ('ROLE*', PCData, 'role', '*'),
    ('LOGO*', Logo, 'logo', '*'),
    ('AGENT*', XCardTemp, 'agent', '*'),
    ('ORG*', Org, 'org', '*'),
    ('CATEGORIES*', 'categories', Categories, '*'),
    ('NOTE*', PCData, 'note', '*'),
    ('PRODID*', PCData, 'prodid', '*'),
    ('REV*', PCData, 'rev', '*'),
    ('SORT-STRING*', PCData, 'sort_string', '*'),
    ('SOUND*', Sound, 'sound', '*'),
    ('UID*', PCData, 'uid', '*'),
    ('URL*', PCData, 'url', '*'),
    ('CLASS*', Class, 'class', '*'),
    ('KEY*', Key, 'key', '*'),
    ('DESC*', PCData, 'desc', '*')
    ]

VCARD_CLASS_PROPS = list(i[2] for i in VCARD_ELEMENTS)
