
"""
XEP-0292 implementation

One of this module purposes is to ensure pickling possibility
"""

import lxml.etree
import org.wayround.utils.factory
import org.wayround.utils.lxml
import org.wayround.utils.types


NAMESPACE = 'urn:ietf:params:xml:ns:vcard-4.0'


class ValueUri:
    pass


class ValueText:

    def check_value(self, value):
        if not isinstance(value, str):
            raise ValueError("`value' must be str")

org.wayround.utils.lxml.simple_exchange_class_factory(
    ValueText,
    'text',
    NAMESPACE,
    [],
    ['value'],
    value_name='value'
    )

org.wayround.utils.factory.class_generate_attributes_and_check(
    ValueText,
    ['value']
    )

org.wayround.utils.lxml.checker_factory(
    ValueText,
    []
    )


VALUETEXTLIST_ELEMENTS = [
    ('text', ValueText, 'text', '+'),
    ]

VALUETEXTLIST_CLASS_PROPS = list(i[2] for i in VALUETEXTLIST_ELEMENTS)


class ValueTextList:
    pass


class Sex:

    def check_value(self, value):
        if not value in ['', 'M', 'F', 'O', 'N', 'U']:
            raise ValueError("invalid Sex value")

org.wayround.utils.lxml.simple_exchange_class_factory(
    Sex,
    'sex',
    NAMESPACE,
    [],
    ['value'],
    value_name='value'
    )

org.wayround.utils.factory.class_generate_attributes_and_check(
    Sex,
    ['value']
    )


class LanguageTag:

    def __init__(self, text=None):

        self.set_text(text)

        return

    def check_text(self, value):
        if value != None and not isinstance(value, str):
            raise ValueError("`text' must be None or str")

    @classmethod
    def new_from_element(cls, element):

        tag = org.wayround.utils.lxml.parse_element_tag(
            element,
            'language-tag',
            NAMESPACE
            )[0]

        if tag is None:
            raise ValueError("invalid element tag or namespace")

        cl = cls(element.text)

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('language-tag')
        el.text = self.get_text()

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(
    LanguageTag,
    ['text']
    )


class ParamPrefInteger:

    def check_value(self, value):
        if value != None and not isinstance(value, int):
            raise ValueError("`value' must be None or int")

        if isinstance(value, int):
            v = int(value)

            if not (0 <= v <= 100):
                raise ValueError("not 0 <= `value' <= 100")

        return

org.wayround.utils.lxml.simple_exchange_class_factory(
    ParamPrefInteger,
    'integer',
    NAMESPACE,
    [],
    ['value']
    )


org.wayround.utils.factory.class_generate_attributes_and_check(
    ParamPrefInteger,
    ['value']
    )


PARAM_PREF_ELEMENTS = [
    ('integer', ParamPrefInteger, 'integer', '?')
    ]


class ParamPref:

    def __init__(self, **kwargs):

        for i in PROPERTY_PARAMETERS_CLASS_PROPS:
            set_func = getattr(self, 'set_{}'.format(i))
            set_func(kwargs.get(i))

        return

PARAM_LANGUAGE_ELEMENTS = [
    ('language-tag', LanguageTag, 'language_tag', '?')
    ]

PARAM_LANGUAGE_CLASS_PROPS = list(i[2] for i in PARAM_LANGUAGE_ELEMENTS)


class ParamLanguage:
    pass


class ParamAltID:
    pass


class ParamPid:
    pass


class ParamType:
    pass


class ParamMediaType:
    pass


class ParamCalScale:
    pass


class ParamSortAs:
    pass


class ParamGeo:
    pass


class ParamTZ:
    pass


class ParamLabel:
    pass


PROPERTY_PARAMETERS_ELEMENTS = [
    ('language', ParamLanguage, 'language', '?'),
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?'),
    ('mediatype', ParamMediaType, 'mediatype', '?'),
    ('calscale', ParamCalScale, 'calscale', '?'),
    ('sort-as', ParamSortAs, 'sort_as', '?'),
    ('geo?', ParamGeo, 'geo', '?'),
    ('tz', ParamTZ, 'tz', '?'),
    ('label', ParamLabel, 'label', '?')
    ]

PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in PROPERTY_PARAMETERS_ELEMENTS) + ['value']


class PropertyParameters:

    def check_value(self, value):
        if value != None:
            raise ValueError("`value' must be None")


ADR_ELEMENTS = [
    ('properties', PropertyParameters, 'properties', '?'),
    ('pobox', ValueText, 'pobox', '?'),
    ('extadd', ValueText, 'extadd', '?'),
    ('street', ValueText, 'street', '?'),
    ('locality', ValueText, 'locality', '?'),
    ('region', ValueText, 'region', '?'),
    ('pcode', ValueText, 'pcode', '?'),
    ('ctry', ValueText, 'ctry', '?')
    ]

ADR_CLASS_PROPS = list(i[2] for i in ADR_ELEMENTS) + ['value']


class Adr:

    def check_value(self, value):
        if value != None:
            raise ValueError("`value' must be None")


CATEGORIES_ELEMENTS = [
    ('KEYWORD', ValueText, 'keyword', '*')
    ]

CATEGORIES_CLASS_PROPS = list(i[2] for i in CATEGORIES_ELEMENTS) + ['value']


class Categories:

    def check_value(self, value):
        if value != None:
            raise ValueError("`value' must be None")


EMAIL_ELEMENTS = [
    ('parameters', PropertyParameters, 'parameters', '?')
    ]

EMAIL_CLASS_PROPS = list(i[2] for i in EMAIL_ELEMENTS) + ['value']


class Email:

    def check_value(self, value):
        if not isinstance(value, ValueText):
            raise ValueError("`value' must be ValueText")


FN_ELEMENTS = [
    ('parameters', PropertyParameters, 'parameters', '?')
    ]

FN_CLASS_PROPS = list(i[2] for i in FN_ELEMENTS) + ['value']


class Fn:

    def check_value(self, value):
        if value != None:
            raise ValueError("`value' must be None")


GEO_ELEMENTS = [
    ('parameters', PropertyParameters, 'parameters', '?'),
    ('lat', ValueText, 'lat', ''),
    ('lon', ValueText, 'lon', '')
    ]

GEO_CLASS_PROPS = list(i[2] for i in GEO_ELEMENTS) + ['value']


class Geo:

    def check_value(self, value):
        if value != None and not isinstance(value, ValueUri):
            raise ValueError("`value' must be None or ValueUri")


KEY_ELEMENTS = [
    ('parameters', PropertyParameters, 'parameters', '?')
    ]

KEY_CLASS_PROPS = list(i[2] for i in KEY_ELEMENTS)


class Key:

    def check_value(self, value):
        if not isinstance(value, (ValueUri, ValueText)):
            raise ValueError("`value' must be (ValueUri, ValueText)")


LOGO_ELEMENTS = [
    ('TYPE', ValueText, 'type', '?'),
    ('BINVAL', ValueText, 'binval', '?'),
    ('EXTVAL', ValueText, 'extval', '?')
    ]

LOGO_CLASS_PROPS = list(i[2] for i in LOGO_ELEMENTS)


class Logo:

    def check_value(self, value):
        if value != None:
            raise ValueError("`value' must be None")


N_ELEMENTS = [
    ('FAMILY', ValueText, 'family', '?'),
    ('GIVEN', ValueText, 'given', '?'),
    ('MIDDLE', ValueText, 'middle', '?'),
    ('PREFIX', ValueText, 'prefix', '?'),
    ('SUFFIX', ValueText, 'suffix', '?')
    ]

N_CLASS_PROPS = list(i[2] for i in N_ELEMENTS)


class N:

    def check_value(self, value):
        if value != None:
            raise ValueError("`value' must be None")


ORG_ELEMENTS = [
    ('ORGNAME', ValueText, 'orgname', ''),
    ('ORGUNIT', ValueText, 'orgunit', '')
    ]

ORG_CLASS_PROPS = list(i[2] for i in ORG_ELEMENTS)


class Org:

    def check_value(self, value):
        if value != None:
            raise ValueError("`value' must be None")


PHOTO_ELEMENTS = [
    ('TYPE', ValueText, 'type', '?'),
    ('BINVAL', ValueText, 'binval', '?'),
    ('EXTVAL', ValueText, 'extval', '?')
    ]

PHOTO_CLASS_PROPS = list(i[2] for i in PHOTO_ELEMENTS)


class Photo:

    def check_value(self, value):
        if value != None:
            raise ValueError("`value' must be None")


SOUND_ELEMENTS = [
    ('PHONETIC', ValueText, 'phonetic', '?'),
    ('BINVAL', ValueText, 'binval', '?'),
    ('EXTVAL', ValueText, 'extval', '?')
    ]

SOUND_CLASS_PROPS = list(i[2] for i in SOUND_ELEMENTS)


class Sound:

    def check_value(self, value):
        if value != None:
            raise ValueError("`value' must be None")


class TelTypeText:

    def check_value(self, value):
        if not value in ['work', 'home', 'text', 'voice', 'fax', 'cell',
                         'video', 'pager', 'textphone']:
            raise ValueError("invalid TelTypeText value")

org.wayround.utils.lxml.simple_exchange_class_factory(
    TelTypeText,
    'text',
    NAMESPACE,
    [],
    ['value'],
    value_name='value'
    )

org.wayround.utils.factory.class_generate_attributes_and_check(
    TelTypeText,
    ['value']
    )


TEL_ELEMENTS = [
    ('parameters', PropertyParameters, 'parameters', '?')
    ]

TEL_CLASS_PROPS = list(i[2] for i in TEL_ELEMENTS)


class Tel:

    def check_value(self, value):
        if not isinstance(value, (ValueUri, ValueText)):
            raise ValueError("`value' must be (ValueUri, ValueText)")


SKELETON = [
    (ValueTextList, 'text', NAMESPACE, VALUETEXTLIST_ELEMENTS,
     VALUETEXTLIST_CLASS_PROPS, 'value'),
    (ParamLanguage, 'language', NAMESPACE, PARAM_LANGUAGE_ELEMENTS,
     PARAM_LANGUAGE_CLASS_PROPS, None),
    (PropertyParameters, 'parameters', NAMESPACE, PROPERTY_PARAMETERS_ELEMENTS,
     PROPERTY_PARAMETERS_CLASS_PROPS, None),
    (Adr, 'adr', NAMESPACE, ADR_ELEMENTS, ADR_CLASS_PROPS, None),
    (Categories, 'categories', NAMESPACE, CATEGORIES_ELEMENTS,
     CATEGORIES_CLASS_PROPS, None),
    (Email, 'email', NAMESPACE, EMAIL_ELEMENTS, EMAIL_CLASS_PROPS, None),
    (Fn, 'fn', NAMESPACE, FN_ELEMENTS, FN_CLASS_PROPS, None),
    (Geo, 'geo', NAMESPACE, GEO_ELEMENTS, GEO_CLASS_PROPS, None),
    (Key, 'key', NAMESPACE, KEY_ELEMENTS, KEY_CLASS_PROPS, None),
    (Logo, 'logo', NAMESPACE, LOGO_ELEMENTS, LOGO_CLASS_PROPS, None),
    (N, 'n', NAMESPACE, N_ELEMENTS, N_CLASS_PROPS, None),
    (Org, 'org', NAMESPACE, ORG_ELEMENTS, ORG_CLASS_PROPS, None),
    (Photo, 'photo', NAMESPACE, PHOTO_ELEMENTS, PHOTO_CLASS_PROPS, None),
    (Sound, 'sound', NAMESPACE, SOUND_ELEMENTS, SOUND_CLASS_PROPS, None),
    (Tel, 'tel', NAMESPACE, TEL_ELEMENTS, TEL_CLASS_PROPS, None)
    ]

for i in SKELETON:

    org.wayround.utils.lxml.simple_exchange_class_factory(
        i[0],
        i[1],
        i[2],
        i[3],
        i[4],
        i[5]
        )

    org.wayround.utils.factory.class_generate_attributes_and_check(
        i[0],
        i[4]
        )

    org.wayround.utils.lxml.checker_factory(
        i[0],
        i[3]
        )

del SKELETON


class XCard:

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
            'vcard',
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

        el = lxml.etree.Element('vcard')
        el.set('xmlns', NAMESPACE)

        org.wayround.utils.lxml.subelems_to_order(
            self.get_order(), el
            )

        return el

org.wayround.utils.factory.class_generate_attributes_and_check(
    XCard,
    ['order']
    )

VCARD_ELEMENTS = [
    ('adr', Adr, 'adr', '*'),
    ('anniversary', Anniversary, 'anniversary', '*'),
    ('bday', Bday, 'bday', '*'),
    ('caladruri', Caladruri, 'caladruri', '*'),
    ('caluri', Caluri, 'caluri', '*'),
    ('categories', 'categories', Categories, '*'),
    ('clientpidmap', Clientpidmap, 'clientpidmap', '*'),
    ('email', Email, 'email', '*'),
    ('fburl', Fburl, 'fburl', '*'),
    ('fn', Fn, 'fn', ''),
    ('gender', Gender, 'gender', '*'),
    ('geo', Geo, 'geo', '*'),
    ('impp', Impp, 'impp', '*'),
    ('key', Key, 'key', '*'),
    ('kind', Kind, 'kind', '*'),
    ('lang', Lang, 'lang', '*'),
    ('logo', Logo, 'logo', '*'),
    ('member', Member, 'member', '*'),
    ('n', N, 'n', ''),
    ('nickname', Nickname, 'nickname', '*'),
    ('note', Note, 'note', '*'),
    ('org', Org, 'org', '*'),
    ('photo', Photo, 'photo', '*'),
    ('prodid', ValueText, 'prodid', '*'),
    ('related', Related, 'related', '*'),
    ('rev', ValueText, 'rev', '*'),
    ('role', Role, 'role', '*'),
    ('sound', Sound, 'sound', '*'),
    ('source', Source, 'source', '*'),
    ('tel', Tel, 'tel', '*'),
    ('title', Title, 'title', '*'),
    ('tz', ValueText, 'tz', '*'),
    ('uid', ValueText, 'uid', '*'),
    ('url', Url, 'url', '*')
    ]

VCARD_CLASS_PROPS = list(i[2] for i in VCARD_ELEMENTS)
