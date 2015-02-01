
"""
XEP-0054 implementation

The main programmer interface to this module should be and XCardTemp class
"""

import lxml.etree

import wayround_org.utils.lxml
import wayround_org.utils.types
import wayround_org.utils.factory

NAMESPACE = 'vcard-temp'
LXML_NAMESPACE = '{{{}}}'.format(NAMESPACE)


class PCData:

    def __init__(self, tag, text):

        """
        tag - tag name without namespace
        """

        self._text = ''

        self.set_tag(tag)
        self.set_text(text)

    def corresponding_tag(self):
        return self.get_tag()

    def check_tag(self, value):
        if not isinstance(value, str):
            raise ValueError("`tag' must be str")

    def check_text(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`text' must be str")

    def set_text(self, value):
        self.check_text(value)
        if value == None:
            value = ''
        self._text = value
        return

    def get_text(self):
        return self._text

    @classmethod
    def new_empty(cls):
        return cls('', '')

    @classmethod
    def new_from_element(cls, element):

        tag = wayround_org.utils.lxml.parse_element_tag(
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

wayround_org.utils.factory.class_generate_attributes_and_check(
    PCData,
    ['tag']
    )


class Empty:

    def __init__(self, tag):

        self.set_tag(tag)

    def check_tag(self, value):
        if not isinstance(value, str):
            raise ValueError("`tag' must be str")

    @classmethod
    def new_from_element(cls, element):
        tag = wayround_org.utils.lxml.parse_element_tag(
            element,
            None,
            [NAMESPACE]
            )[0]

        cl = cls(tag)

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element(self.get_tag())

        return el

wayround_org.utils.factory.class_generate_attributes_and_check(Empty, ['tag'])


N_ELEMENTS = [
    (LXML_NAMESPACE + 'PREFIX', PCData, 'prefix', '?', 'Prefix'),
    (LXML_NAMESPACE + 'GIVEN', PCData, 'given', '?', 'Given'),
    (LXML_NAMESPACE + 'MIDDLE', PCData, 'middle', '?', 'Middle'),
    (LXML_NAMESPACE + 'FAMILY', PCData, 'family', '?', 'Family'),
    (LXML_NAMESPACE + 'SUFFIX', PCData, 'suffix', '?', 'Suffix')
    ]

wayround_org.utils.lxml.check_tagname_class_attrnames(N_ELEMENTS)

N_CLASS_PROPS = list(i[2] for i in N_ELEMENTS)


class N:
    pass

wayround_org.utils.lxml.simple_exchange_class_factory(
    N,
    'N',
    NAMESPACE,
    N_ELEMENTS,
    N_CLASS_PROPS
    )

wayround_org.utils.lxml.checker_factory(
    N,
    N_ELEMENTS
    )

wayround_org.utils.factory.class_generate_attributes_and_check(
    N,
    N_CLASS_PROPS
    )


PHOTO_ELEMENTS = [
    (LXML_NAMESPACE + 'TYPE', PCData, 'type_', '?', 'Type'),
    (LXML_NAMESPACE + 'BINVAL', PCData, 'binval', '?', 'Binary Value'),
    (LXML_NAMESPACE + 'EXTVAL', PCData, 'extval', '?', 'External Value')
    ]

wayround_org.utils.lxml.check_tagname_class_attrnames(PHOTO_ELEMENTS)

PHOTO_CLASS_PROPS = list(i[2] for i in PHOTO_ELEMENTS)


class Photo:
    pass

wayround_org.utils.lxml.simple_exchange_class_factory(
    Photo,
    'PHOTO',
    NAMESPACE,
    PHOTO_ELEMENTS,
    PHOTO_CLASS_PROPS
    )

wayround_org.utils.factory.class_generate_attributes_and_check(
    Photo,
    PHOTO_CLASS_PROPS
    )

wayround_org.utils.lxml.checker_factory(
    Photo,
    PHOTO_ELEMENTS
    )


ADR_ELEMENTS = [
    (LXML_NAMESPACE + 'PREF', Empty, 'pref', '?', 'Preferred'),
    (LXML_NAMESPACE + 'HOME', Empty, 'home', '?', 'Home'),
    (LXML_NAMESPACE + 'WORK', Empty, 'work', '?', 'Work'),
    (LXML_NAMESPACE + 'POSTAL', Empty, 'postal', '?', 'Postal'),
    (LXML_NAMESPACE + 'PARCEL', Empty, 'parcel', '?', 'PARCEL?'),
    (LXML_NAMESPACE + 'DOM', Empty, 'dom', '?', 'DOM?'),
    (LXML_NAMESPACE + 'INTL', Empty, 'intl', '?', 'INTL?'),
    (LXML_NAMESPACE + 'CTRY', PCData, 'ctry', '?', 'Country'),
    (LXML_NAMESPACE + 'REGION', PCData, 'region', '?', 'Region (State)'),
    (LXML_NAMESPACE + 'LOCALITY', PCData, 'locality', '?', 'Locality (City)'),
    (LXML_NAMESPACE + 'STREET', PCData, 'street', '?', 'Street'),
    (LXML_NAMESPACE + 'EXTADD', PCData, 'extadd', '?', 'EXTADD?'),
    (LXML_NAMESPACE + 'POBOX', PCData, 'pobox', '?', 'POBOX?'),
    (LXML_NAMESPACE + 'PCODE', PCData, 'pcode', '?', 'PCODE?')
    ]

wayround_org.utils.lxml.check_tagname_class_attrnames(ADR_ELEMENTS)

ADR_CLASS_PROPS = list(i[2] for i in ADR_ELEMENTS)


class Adr:
    pass

wayround_org.utils.lxml.simple_exchange_class_factory(
    Adr,
    'ADR',
    NAMESPACE,
    ADR_ELEMENTS,
    ADR_CLASS_PROPS
    )

wayround_org.utils.factory.class_generate_attributes_and_check(
    Adr,
    ADR_CLASS_PROPS
    )

wayround_org.utils.lxml.checker_factory(
    Adr,
    ADR_ELEMENTS
    )


LABEL_ELEMENTS = [
    (LXML_NAMESPACE + 'PREF', Empty, 'pref', '?', 'Preferred'),
    (LXML_NAMESPACE + 'HOME', Empty, 'home', '?', 'Home'),
    (LXML_NAMESPACE + 'WORK', Empty, 'work', '?', 'Work'),
    (LXML_NAMESPACE + 'POSTAL', Empty, 'postal', '?', 'Postal'),
    (LXML_NAMESPACE + 'PARCEL', Empty, 'parcel', '?', 'PARCEL?'),
    (LXML_NAMESPACE + 'DOM', Empty, 'dom', '?', 'DOM?'),
    (LXML_NAMESPACE + 'INTL', Empty, 'intl', '?', 'INTL?'),
    (LXML_NAMESPACE + 'LINE', PCData, 'line', '+', 'Line')
    ]

wayround_org.utils.lxml.check_tagname_class_attrnames(LABEL_ELEMENTS)

LABEL_CLASS_PROPS = list(i[2] for i in LABEL_ELEMENTS)


class Label:
    pass

wayround_org.utils.lxml.simple_exchange_class_factory(
    Label,
    'LABEL',
    NAMESPACE,
    LABEL_ELEMENTS,
    LABEL_CLASS_PROPS
    )

wayround_org.utils.factory.class_generate_attributes_and_check(
    Label,
    LABEL_CLASS_PROPS
    )

wayround_org.utils.lxml.checker_factory(
    Label,
    LABEL_ELEMENTS
    )


TEL_ELEMENTS = [
    (LXML_NAMESPACE + 'PREF', Empty, 'pref', '?', 'Preferred'),
    (LXML_NAMESPACE + 'HOME', Empty, 'home', '?', 'Home'),
    (LXML_NAMESPACE + 'WORK', Empty, 'work', '?', 'Work'),
    (LXML_NAMESPACE + 'VOICE', Empty, 'voice', '?', 'Voice'),
    (LXML_NAMESPACE + 'FAX', Empty, 'fax', '?', 'Fax'),
    (LXML_NAMESPACE + 'PAGER', Empty, 'pager', '?', 'Pager'),
    (LXML_NAMESPACE + 'MSG', Empty, 'msg', '?', 'Msg'),
    (LXML_NAMESPACE + 'CELL', Empty, 'cell', '?', 'Cell'),
    (LXML_NAMESPACE + 'VIDEO', Empty, 'video', '?', 'Video'),
    (LXML_NAMESPACE + 'BBS', Empty, 'bbs', '?', 'BBS'),
    (LXML_NAMESPACE + 'MODEM', Empty, 'modem', '?', 'Modem'),
    (LXML_NAMESPACE + 'ISDN', Empty, 'isdn', '?', 'ISDN'),
    (LXML_NAMESPACE + 'PCS', Empty, 'pcs', '?', 'PCS'),
    (LXML_NAMESPACE + 'NUMBER', PCData, 'number',
     '',
     'Number')
    ]

wayround_org.utils.lxml.check_tagname_class_attrnames(TEL_ELEMENTS)

TEL_CLASS_PROPS = list(i[2] for i in TEL_ELEMENTS)


class Tel:
    pass

wayround_org.utils.lxml.simple_exchange_class_factory(
    Tel,
    'TEL',
    NAMESPACE,
    TEL_ELEMENTS,
    TEL_CLASS_PROPS
    )

wayround_org.utils.factory.class_generate_attributes_and_check(
    Tel,
    TEL_CLASS_PROPS
    )

wayround_org.utils.lxml.checker_factory(
    Tel,
    TEL_ELEMENTS
    )


EMAIL_ELEMENTS = [
    (LXML_NAMESPACE + 'PREF', Empty, 'pref', '?', 'Preferred'),
    (LXML_NAMESPACE + 'HOME', Empty, 'home', '?', 'Home'),
    (LXML_NAMESPACE + 'WORK', Empty, 'work', '?', 'Work'),
    (LXML_NAMESPACE + 'INTERNET', Empty, 'internet', '?', 'Internet'),
    (LXML_NAMESPACE + 'X400', Empty, 'x400', '?', 'X400'),
    (LXML_NAMESPACE + 'USERID', PCData, 'userid',
     '',
     'UserID',
     'example: example@example.com')
    ]

wayround_org.utils.lxml.check_tagname_class_attrnames(EMAIL_ELEMENTS)

EMAIL_CLASS_PROPS = list(i[2] for i in EMAIL_ELEMENTS)


class Email:
    pass

wayround_org.utils.lxml.simple_exchange_class_factory(
    Email,
    'EMAIL',
    NAMESPACE,
    EMAIL_ELEMENTS,
    EMAIL_CLASS_PROPS
    )

wayround_org.utils.factory.class_generate_attributes_and_check(
    Email,
    EMAIL_CLASS_PROPS
    )

wayround_org.utils.lxml.checker_factory(
    Email,
    EMAIL_ELEMENTS
    )


GEO_ELEMENTS = [
    (LXML_NAMESPACE + 'LAT', PCData, 'lat', '', 'Latitude'),
    (LXML_NAMESPACE + 'LON', PCData, 'lon', '', 'Longitude')
    ]

wayround_org.utils.lxml.check_tagname_class_attrnames(GEO_ELEMENTS)

GEO_CLASS_PROPS = list(i[2] for i in GEO_ELEMENTS)


class Geo:
    pass

wayround_org.utils.lxml.simple_exchange_class_factory(
    Geo,
    'GEO',
    NAMESPACE,
    GEO_ELEMENTS,
    GEO_CLASS_PROPS
    )

wayround_org.utils.factory.class_generate_attributes_and_check(
    Geo,
    GEO_CLASS_PROPS
    )

wayround_org.utils.lxml.checker_factory(
    Geo,
    GEO_ELEMENTS
    )


LOGO_ELEMENTS = [
    (LXML_NAMESPACE + 'TYPE', PCData, 'type_', '?', 'Type'),
    (LXML_NAMESPACE + 'BINVAL', PCData, 'binval', '?', 'Binary Value'),
    (LXML_NAMESPACE + 'EXTVAL', PCData, 'extval', '?', 'External Value')
    ]

wayround_org.utils.lxml.check_tagname_class_attrnames(LOGO_ELEMENTS)

LOGO_CLASS_PROPS = list(i[2] for i in LOGO_ELEMENTS)


class Logo:
    pass

wayround_org.utils.lxml.simple_exchange_class_factory(
    Logo,
    'LOGO',
    NAMESPACE,
    LOGO_ELEMENTS,
    LOGO_CLASS_PROPS
    )

wayround_org.utils.factory.class_generate_attributes_and_check(
    Logo,
    LOGO_CLASS_PROPS
    )

wayround_org.utils.lxml.checker_factory(
    Logo,
    LOGO_ELEMENTS
    )


ORG_ELEMENTS = [
    (LXML_NAMESPACE + 'ORGNAME', PCData, 'orgname', '', 'Organization Name'),
    (LXML_NAMESPACE + 'ORGUNIT', PCData, 'orgunit', '*', 'Organization Unit')
    ]

wayround_org.utils.lxml.check_tagname_class_attrnames(ORG_ELEMENTS)

ORG_CLASS_PROPS = list(i[2] for i in ORG_ELEMENTS)


class Org:
    pass

wayround_org.utils.lxml.simple_exchange_class_factory(
    Org,
    'ORG',
    NAMESPACE,
    ORG_ELEMENTS,
    ORG_CLASS_PROPS
    )

wayround_org.utils.factory.class_generate_attributes_and_check(
    Org,
    ORG_CLASS_PROPS
    )

wayround_org.utils.lxml.checker_factory(
    Org,
    ORG_ELEMENTS
    )


CATEGORIES_ELEMENTS = [
    ('KEYWORD', PCData, 'keyword', '+')
    ]

wayround_org.utils.lxml.check_tagname_class_attrnames(CATEGORIES_ELEMENTS)

CATEGORIES_CLASS_PROPS = list(i[2] for i in CATEGORIES_ELEMENTS)


class Categories:
    pass

wayround_org.utils.lxml.simple_exchange_class_factory(
    Categories,
    'CATEGORIES',
    NAMESPACE,
    CATEGORIES_ELEMENTS,
    CATEGORIES_CLASS_PROPS
    )

wayround_org.utils.factory.class_generate_attributes_and_check(
    Categories,
    CATEGORIES_CLASS_PROPS
    )

wayround_org.utils.lxml.checker_factory(
    Categories,
    CATEGORIES_ELEMENTS
    )


SOUND_ELEMENTS = [
    (LXML_NAMESPACE + 'PHONETIC', PCData, 'phonetic', '?', 'Phonetic'),
    (LXML_NAMESPACE + 'BINVAL', PCData, 'binval', '?', 'Binary Value'),
    (LXML_NAMESPACE + 'EXTVAL', PCData, 'extval', '?', 'External Value')
    ]

wayround_org.utils.lxml.check_tagname_class_attrnames(SOUND_ELEMENTS)

SOUND_CLASS_PROPS = list(i[2] for i in SOUND_ELEMENTS)


class Sound:
    pass

wayround_org.utils.lxml.simple_exchange_class_factory(
    Sound,
    'SOUND',
    NAMESPACE,
    SOUND_ELEMENTS,
    SOUND_CLASS_PROPS
    )

wayround_org.utils.factory.class_generate_attributes_and_check(
    Sound,
    SOUND_CLASS_PROPS
    )

wayround_org.utils.lxml.checker_factory(
    Sound,
    SOUND_ELEMENTS
    )


CLASS_ELEMENTS = [
    (LXML_NAMESPACE + 'PUBLIC', Empty, 'public', '?', 'Public'),
    (LXML_NAMESPACE + 'PRIVATE', Empty, 'private', '?', 'Private'),
    (LXML_NAMESPACE + 'CONFIDENTIAL', Empty, 'confidential', '?',
     'Confidential')
    ]

wayround_org.utils.lxml.check_tagname_class_attrnames(CLASS_ELEMENTS)

CLASS_CLASS_PROPS = list(i[2] for i in CLASS_ELEMENTS)


class Class:
    pass

wayround_org.utils.lxml.simple_exchange_class_factory(
    Class,
    'CLASS',
    NAMESPACE,
    CLASS_ELEMENTS,
    CLASS_CLASS_PROPS
    )

wayround_org.utils.factory.class_generate_attributes_and_check(
    Class,
    CLASS_CLASS_PROPS
    )

wayround_org.utils.lxml.checker_factory(
    Class,
    CLASS_ELEMENTS
    )

KEY_ELEMENTS = [
    (LXML_NAMESPACE + 'TYPE', PCData, 'type_', '?', 'Type'),
    (LXML_NAMESPACE + 'CRED', PCData, 'cred', '', 'CRED?')
    ]

wayround_org.utils.lxml.check_tagname_class_attrnames(KEY_ELEMENTS)

KEY_CLASS_PROPS = list(i[2] for i in KEY_ELEMENTS)


class Key:
    pass

wayround_org.utils.lxml.simple_exchange_class_factory(
    Key,
    'KEY',
    NAMESPACE,
    KEY_ELEMENTS,
    KEY_CLASS_PROPS
    )

wayround_org.utils.factory.class_generate_attributes_and_check(
    Key,
    KEY_CLASS_PROPS
    )

wayround_org.utils.lxml.checker_factory(
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
        if not wayround_org.utils.types.struct_check(
            value,
            {'t': list, '.':
             {'t': tuple, '<': 3, '>': 3}
             }
            ):
            raise TypeError("`order' must be list of triple tuples")

    @classmethod
    def new_from_element(cls, element):

        tag = wayround_org.utils.lxml.parse_element_tag(
            element,
            'vCard',
            [NAMESPACE]
            )[0]

        if tag == None:
            raise ValueError("invalid element")

        cl = cls()

        order = []

        wayround_org.utils.lxml.subelems_to_order(
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

        wayround_org.utils.lxml.order_to_subelems(
            self.get_order(), el
            )

        return el

wayround_org.utils.factory.class_generate_attributes_and_check(
    XCardTemp,
    ['order']
    )

VCARD_ELEMENTS = [
    # 0. tag
    # 1. class
    # 2. corresponding class property
    # 3. mask
    # 4. title
    # 5. description
    (LXML_NAMESPACE + 'FN', PCData, 'fn', '', 'FN (Full Name)'),
    (LXML_NAMESPACE + 'N', N, 'n', '', 'N (Name)'),
    (LXML_NAMESPACE + 'NICKNAME', PCData, 'nickname', '*', 'NICKNAME'),
    (LXML_NAMESPACE + 'PHOTO', Photo, 'photo', '*', 'PHOTO'),
    (LXML_NAMESPACE + 'BDAY', PCData, 'bday', '*', 'BDAY'),
    (LXML_NAMESPACE + 'ADR', Adr, 'adr', '*', 'ADR'),
    (LXML_NAMESPACE + 'LABEL', Label, 'label', '*', 'LABEL'),
    (LXML_NAMESPACE + 'TEL', Tel, 'tel', '*', 'TEL'),
    (LXML_NAMESPACE + 'EMAIL', Email, 'email', '*', 'EMAIL'),
    (LXML_NAMESPACE + 'JABBERID', PCData, 'jabberid', '*', 'JABBERID'),
    (LXML_NAMESPACE + 'MAILER', PCData, 'mailer', '*', 'MAILER'),
    (LXML_NAMESPACE + 'TZ', PCData, 'tz', '*', 'TZ (TimeZone)'),
    (LXML_NAMESPACE + 'GEO', Geo, 'geo', '*', 'GEO'),
    (LXML_NAMESPACE + 'TITLE', PCData, 'title', '*', 'TITLE (Organization)'),
    (LXML_NAMESPACE + 'ROLE', PCData, 'role', '*', 'ROLE (Organization)'),
    (LXML_NAMESPACE + 'LOGO', Logo, 'logo', '*', 'LOGO (Organization)'),
    (LXML_NAMESPACE + 'AGENT', XCardTemp, 'agent', '*', 'AGENT'),
    (LXML_NAMESPACE + 'ORG', Org, 'org', '*', 'ORG'),
    (LXML_NAMESPACE + 'CATEGORIES', Categories, 'categories', '*',
     'CATEGORIES'),
    (LXML_NAMESPACE + 'NOTE', PCData, 'note', '*', 'NOTE'),
    (LXML_NAMESPACE + 'PRODID', PCData, 'prodid', '*', 'PRODID'),
    (LXML_NAMESPACE + 'REV', PCData, 'rev', '*', 'REV'),
    (LXML_NAMESPACE + 'SORT-STRING', PCData, 'sort_string', '*',
     'SORT-STRING'),
    (LXML_NAMESPACE + 'SOUND', Sound, 'sound', '*', 'SOUND'),
    (LXML_NAMESPACE + 'UID', PCData, 'uid', '*', 'UID (UserID)'),
    (LXML_NAMESPACE + 'URL', PCData, 'url', '*', 'URL'),
    (LXML_NAMESPACE + 'CLASS', Class, 'class', '*', 'CLASS'),
    (LXML_NAMESPACE + 'KEY', Key, 'key', '*', 'KEY (PGP)'),
    (LXML_NAMESPACE + 'DESC', PCData, 'desc', '*', 'DESC')
    ]

wayround_org.utils.lxml.check_tagname_class_attrnames(VCARD_ELEMENTS)

VCARD_CLASS_PROPS = list(i[2] for i in VCARD_ELEMENTS)


def is_xcard(element):

    ret = False

    tag = wayround_org.utils.lxml.parse_element_tag(
        element,
        'vCard',
        [NAMESPACE]
        )[0]

    if tag != None:
        ret = True

    return ret
