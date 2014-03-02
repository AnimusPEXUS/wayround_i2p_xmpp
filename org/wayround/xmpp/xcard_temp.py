
"""
XEP-0054 implementation

The main programmer interface to this module should be and XCardTemp class
"""

import lxml.etree

import org.wayround.utils.lxml
import org.wayround.utils.types
import org.wayround.utils.factory

NAMESPACE = 'vcard-temp'
LXML_NAMESPACE = '{{{}}}'.format(NAMESPACE)


class PCData:

    def __init__(self, tag, text):

        """
        tag - tag name without namespace
        """

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
    (LXML_NAMESPACE + 'FAMILY', PCData, 'family', '?'),
    (LXML_NAMESPACE + 'GIVEN', PCData, 'given', '?'),
    (LXML_NAMESPACE + 'MIDDLE', PCData, 'middle', '?'),
    (LXML_NAMESPACE + 'PREFIX', PCData, 'prefix', '?'),
    (LXML_NAMESPACE + 'SUFFIX', PCData, 'suffix', '?')
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
    (LXML_NAMESPACE + 'TYPE', PCData, 'type', '?'),
    (LXML_NAMESPACE + 'BINVAL', PCData, 'binval', '?'),
    (LXML_NAMESPACE + 'EXTVAL', PCData, 'extval', '?')
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
    (LXML_NAMESPACE + 'HOME', Empty, 'home', '?'),
    (LXML_NAMESPACE + 'WORK', Empty, 'work', '?'),
    (LXML_NAMESPACE + 'POSTAL', Empty, 'postal', '?'),
    (LXML_NAMESPACE + 'PARCEL', Empty, 'parcel', '?'),
    (LXML_NAMESPACE + 'DOM', Empty, 'dom', '?'),
    (LXML_NAMESPACE + 'INTL', Empty, 'intl', '?'),
    (LXML_NAMESPACE + 'PREF', Empty, 'pref', '?'),
    (LXML_NAMESPACE + 'POBOX', PCData, 'pobox', '?'),
    (LXML_NAMESPACE + 'EXTADD', PCData, 'extadd', '?'),
    (LXML_NAMESPACE + 'STREET', PCData, 'street', '?'),
    (LXML_NAMESPACE + 'LOCALITY', PCData, 'locality', '?'),
    (LXML_NAMESPACE + 'REGION', PCData, 'region', '?'),
    (LXML_NAMESPACE + 'PCODE', PCData, 'pcode', '?'),
    (LXML_NAMESPACE + 'CTRY', PCData, 'ctry', '?')
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
    (LXML_NAMESPACE + 'HOME', Empty, 'home', '?'),
    (LXML_NAMESPACE + 'WORK', Empty, 'work', '?'),
    (LXML_NAMESPACE + 'POSTAL', Empty, 'postal', '?'),
    (LXML_NAMESPACE + 'PARCEL', Empty, 'parcel', '?'),
    (LXML_NAMESPACE + 'DOM', Empty, 'dom', '?'),
    (LXML_NAMESPACE + 'INTL', Empty, 'intl', '?'),
    (LXML_NAMESPACE + 'PREF', Empty, 'pref', '?'),
    (LXML_NAMESPACE + 'LINE', PCData, 'line', '+')
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
    (LXML_NAMESPACE + 'HOME', Empty, 'home', '?'),
    (LXML_NAMESPACE + 'WORK', Empty, 'work', '?'),
    (LXML_NAMESPACE + 'VOICE', Empty, 'voice', '?'),
    (LXML_NAMESPACE + 'FAX', Empty, 'fax', '?'),
    (LXML_NAMESPACE + 'PAGER', Empty, 'pager', '?'),
    (LXML_NAMESPACE + 'MSG', Empty, 'msg', '?'),
    (LXML_NAMESPACE + 'CELL', Empty, 'cell', '?'),
    (LXML_NAMESPACE + 'VIDEO', Empty, 'video', '?'),
    (LXML_NAMESPACE + 'BBS', Empty, 'bbs', '?'),
    (LXML_NAMESPACE + 'MODEM', Empty, 'modem', '?'),
    (LXML_NAMESPACE + 'ISDN', Empty, 'isdn', '?'),
    (LXML_NAMESPACE + 'PCS', Empty, 'pcs', '?'),
    (LXML_NAMESPACE + 'PREF', Empty, 'pref', '?'),
    (LXML_NAMESPACE + 'NUMBER', PCData, 'number', '')
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
    (LXML_NAMESPACE + 'HOME', Empty, 'home', '?'),
    (LXML_NAMESPACE + 'WORK', Empty, 'work', '?'),
    (LXML_NAMESPACE + 'INTERNET', Empty, 'internet', '?'),
    (LXML_NAMESPACE + 'PREF', Empty, 'pref', '?'),
    (LXML_NAMESPACE + 'X400', Empty, 'x400', '?'),
    (LXML_NAMESPACE + 'USERID', PCData, 'userid', '')
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
    (LXML_NAMESPACE + 'LAT', PCData, 'lat', ''),
    (LXML_NAMESPACE + 'LON', PCData, 'lon', '')
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
    (LXML_NAMESPACE + 'TYPE', PCData, 'type', '?'),
    (LXML_NAMESPACE + 'BINVAL', PCData, 'binval', '?'),
    (LXML_NAMESPACE + 'EXTVAL', PCData, 'extval', '?')
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
    (LXML_NAMESPACE + 'ORGNAME', PCData, 'orgname', ''),
    (LXML_NAMESPACE + 'ORGUNIT', PCData, 'orgunit', '*')
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
    (LXML_NAMESPACE + 'PHONETIC', PCData, 'phonetic', '?'),
    (LXML_NAMESPACE + 'BINVAL', PCData, 'binval', '?'),
    (LXML_NAMESPACE + 'EXTVAL', PCData, 'extval', '?')
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
    (LXML_NAMESPACE + 'PUBLIC', Empty, 'public', '?'),
    (LXML_NAMESPACE + 'PRIVATE', Empty, 'private', '?'),
    (LXML_NAMESPACE + 'CONFIDENTIAL', Empty, 'confidential', '?')
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
    (LXML_NAMESPACE + 'TYPE', Empty, 'type_', '?'),
    (LXML_NAMESPACE + 'CRED', PCData, 'cred', '')
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
    (LXML_NAMESPACE + 'FN', PCData, 'fn', ''),
    (LXML_NAMESPACE + 'N', N, 'n', ''),
    (LXML_NAMESPACE + 'NICKNAME', PCData, 'nickname', '*'),
    (LXML_NAMESPACE + 'PHOTO', Photo, 'photo', '*'),
    (LXML_NAMESPACE + 'BDAY', PCData, 'bday', '*'),
    (LXML_NAMESPACE + 'ADR', Adr, 'adr', '*'),
    (LXML_NAMESPACE + 'LABEL', Label, 'label', '*'),
    (LXML_NAMESPACE + 'TEL', Tel, 'tel', '*'),
    (LXML_NAMESPACE + 'EMAIL', Email, 'email', '*'),
    (LXML_NAMESPACE + 'JABBERID', PCData, 'jabberid', '*'),
    (LXML_NAMESPACE + 'MAILER', PCData, 'mailer', '*'),
    (LXML_NAMESPACE + 'TZ', PCData, 'tz', '*'),
    (LXML_NAMESPACE + 'GEO', Geo, 'geo', '*'),
    (LXML_NAMESPACE + 'TITLE', PCData, 'title', '*'),
    (LXML_NAMESPACE + 'ROLE', PCData, 'role', '*'),
    (LXML_NAMESPACE + 'LOGO', Logo, 'logo', '*'),
    (LXML_NAMESPACE + 'AGENT', XCardTemp, 'agent', '*'),
    (LXML_NAMESPACE + 'ORG', Org, 'org', '*'),
    (LXML_NAMESPACE + 'CATEGORIES', 'categories', Categories, '*'),
    (LXML_NAMESPACE + 'NOTE', PCData, 'note', '*'),
    (LXML_NAMESPACE + 'PRODID', PCData, 'prodid', '*'),
    (LXML_NAMESPACE + 'REV', PCData, 'rev', '*'),
    (LXML_NAMESPACE + 'SORT-STRING', PCData, 'sort_string', '*'),
    (LXML_NAMESPACE + 'SOUND', Sound, 'sound', '*'),
    (LXML_NAMESPACE + 'UID', PCData, 'uid', '*'),
    (LXML_NAMESPACE + 'URL', PCData, 'url', '*'),
    (LXML_NAMESPACE + 'CLASS', Class, 'class', '*'),
    (LXML_NAMESPACE + 'KEY', Key, 'key', '*'),
    (LXML_NAMESPACE + 'DESC', PCData, 'desc', '*')
    ]

VCARD_CLASS_PROPS = list(i[2] for i in VCARD_ELEMENTS)


def is_xcard(element):

    ret = False

    tag = org.wayround.utils.lxml.parse_element_tag(
        element,
        'vCard',
        [NAMESPACE]
        )[0]

    if tag != None:
        ret = True

    return ret
