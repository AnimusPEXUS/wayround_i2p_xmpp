
"""
XEP-0292 implementation

One of this module purposes is to ensure pickling possibility
"""

import re
import lxml.etree
import org.wayround.utils.factory
import org.wayround.utils.lxml
import org.wayround.utils.types


NAMESPACE = 'urn:ietf:params:xml:ns:vcard-4.0'


class ValueText:

    def check_value(self, value):
        if not isinstance(value, str):
            raise ValueError("`value' must be str")


VALUETEXTLIST_ELEMENTS = [
    ('text', ValueText, 'text', '+'),
    ]

VALUETEXTLIST_CLASS_PROPS = list(i[2] for i in VALUETEXTLIST_ELEMENTS)


class ValueTextList:
    pass


class ValueUri(ValueText):
    pass


VALUE_DATE_RE = re.compile(r'\d{8}|\d{4}-\d\d|--\d\d(\d\d)?|---\d\d')


class ValueDate(ValueText):

    def check_value(self, value):
        if not VALUE_DATE_RE.match(value):
            raise ValueError("invalid date text format")


VALUE_TIME_RE = re.compile(
    r'(\d\d(\d\d(\d\d)?)?|-\d\d(\d\d?)|--\d\d)'
    r'(Z|[+\-]\d\d(\d\d)?)?'
    )


class ValueTime(ValueText):

    def check_value(self, value):
        if not VALUE_TIME_RE.match(value):
            raise ValueError("invalid time text format")


VALUE_DATE_TIME_RE = re.compile(
    r'(\d{8}|--\d{4}|---\d\d)T\d\d(\d\d(\d\d)?)?'
    r'(Z|[+\-]\d\d(\d\d)?)?'
    )


class ValueDateTime(ValueText):

    def check_value(self, value):
        if not VALUE_DATE_TIME_RE.match(value):
            raise ValueError("invalid date-time text format")


#class ValueDateAndOrTime(ValueText):
#
#    def check_value(self, value):
#        if not VALUE_DATE_TIME_RE.match(value):
#            raise ValueError("invalid date-time text format")
#


VALUE_TIMESTAMP_RE = re.compile(
    r'\d{8}T\d{6}(Z|[+\-]\d\d(\d\d)?)?'
    )


class ValueTimestamp(ValueText):

    def check_value(self, value):
        if not VALUE_TIMESTAMP_RE.match(value):
            raise ValueError("invalid timestamp text format")


class ValueBoolean(ValueText):

    # TODO: maybe own check needed
    #
    #    def check_value(self, value):
    #        if not value in ['+', '-', 'yes', 'no', 'on', 'off', '0', '1']:
    #            raise ValueError("invalid boolean text format")
    pass


class ValueInteger(ValueText):

    # TODO: maybe own check needed
    #
    #    def check_value(self, value):
    #        int(value)
    pass


class ValueFloat(ValueText):

    # TODO: maybe own check needed
    #
    #    def check_value(self, value):
    #        float(value)
    pass


UTCOFFSET_RE = re.compile(r'[+\-]\d\d(\d\d)?')


class ValueUtcOffset(ValueText):

    def check_value(self, value):
        if not UTCOFFSET_RE.match(value):
            raise ValueError("invalid utc-offset text format")


LANGUAGETAG_RE = re.compile(
    r'([a-z]{2,3}((-[a-z]{3}){0,3})?|[a-z]{4,8})'
    r'(-[a-z]{4})?(-([a-z]{2}|\d{3}))?'
    r'(-([0-9a-z]{5,8}|\d[0-9a-z]{3}))*'
    r'(-[0-9a-wyz](-[0-9a-z]{2,8})+)*'
    r'(-x(-[0-9a-z]{1,8})+)?|x(-[0-9a-z]{1,8})+|'
    r'[a-z]{1,3}(-[0-9a-z]{2,8}){1,2}'
    )


class ValueLanguageTag(ValueText):

    def check_value(self, value):
        if not LANGUAGETAG_RE.match(value):
            raise ValueError("invalid language-tag text format")


class ParamLanguage:

    def check_value(self, value):
        if not isinstance(value, ValueLanguageTag):
            raise ValueError("language value must be ParamLanguage")


class ParamPrefValueInteger:

    def check_value(self, value):
        if value != None and not isinstance(value, int):
            raise ValueError("`value' must be None or int")

        if isinstance(value, int):
            v = int(value)

            if not (0 <= v <= 100):
                raise ValueError("not 0 <= `value' <= 100")

        return


PARAM_PREF_ELEMENTS = [
    ('integer', ParamPrefValueInteger, 'integer', '?')
    ]

PARAM_PREF_CLASS_PROPS = list(i[2] for i in PARAM_PREF_ELEMENTS)


class ParamPref:
    pass


class ParamAltID:

    def check_value(self, value):
        if value != None and not isinstance(value, ValueText):
            raise ValueError("altid must be None or ValueText")


PARAMPIDTEXT_RE = re.compile(r'\d+(\.\d+)?')


class ParamPidText:

    def check_value(self, value):
        if not PARAMPIDTEXT_RE.match(value):
            raise ValueError("pid text invalid")


PARAMPID_ELEMENTS = [
    ('text', ParamPidText, 'text', '+')
    ]

PARAMPID_CLASS_PROPS = list(i[2] for i in PARAMPID_ELEMENTS)


class ParamPid:

    def check_value(self, value):
        if value != None:
            raise ValueError("`value' must be None")


class ParamTypeText:

    def check_value(self, value):
        if not value in ['work', 'home']:
            raise ValueError("invalid ParamTypeText value")


PARAMTYPE_ELEMENTS = [
    ('text', ParamTypeText, 'text', '+')
    ]

PARAMTYPE_CLASS_PROPS = list(i[2] for i in PARAMTYPE_ELEMENTS)


class ParamType:

    def check_value(self, value):
        if value != None:
            raise ValueError("`value' must be None")


class ParamMediaType:

    def check_value(self, value):
        if value != None and not isinstance(value, ValueText):
            raise ValueError("`value' must be None or ValueText")


class ParamCalScaleText:

    def check_value(self, value):
        if value != 'gregorian':
            raise ValueError("invalid ParamCalScaleText value")


PARAMCALSCALE_ELEMENTS = [
    ('text', ParamCalScaleText, 'text', '?')
    ]

PARAMCALSCALE_CLASS_PROPS = list(i[2] for i in PARAMCALSCALE_ELEMENTS)


class ParamCalScale:

    def check_value(self, value):
        if value != None:
            raise ValueError("`value' must be None")


class ParamSortAs:

    def check_value(self, value):
        if not org.wayround.utils.types.struct_check(
            value,
            {'t': list,
             '.': {'t': ValueText},
             '<': 1, '>': None
             }
            ):
            raise TypeError(
                "ParamCalScale must be list of 1 or more ValueText"
                )


class ParamGeo:

    def check_value(self, value):
        if value != None and not isinstance(value, ValueUri):
            raise ValueError("ParamGeo value must be None or ValueUri")


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


class GenderSex:

    def check_value(self, value):
        if not value in ['', 'M', 'F', 'O', 'N', 'U']:
            raise ValueError("invalid GenderSex value")


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


PARAMTELTYPE_ELEMENTS = [
    ('text', TelTypeText, 'text', '+')
    ]

PARAMTELTYPE_CLASS_PROPS = list(i[2] for i in PARAMTELTYPE_ELEMENTS)


class ParamTelType:
    pass


TEL_ELEMENTS = [
    ('parameters', PropertyParameters, 'parameters', '?')
    ]

TEL_CLASS_PROPS = list(i[2] for i in TEL_ELEMENTS)


class Tel:

    def check_value(self, value):
        if not isinstance(value, (ValueUri, ValueText)):
            raise ValueError("`value' must be (ValueUri, ValueText)")


SKELETON = [
    # 0. Class;
    # 1. tag;
    # 2. namespace;
    # 3. elements struct;
    # 4. object properties list;
    # 5. element text parameter name
    (ValueTextList, 'text', NAMESPACE, VALUETEXTLIST_ELEMENTS,
     VALUETEXTLIST_CLASS_PROPS, 'value'),

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

    (ParamTelType, 'tel', NAMESPACE, TEL_ELEMENTS, TEL_CLASS_PROPS, None),

    (ParamPref, 'pref', NAMESPACE, PARAM_PREF_ELEMENTS, PARAM_PREF_CLASS_PROPS,
     None),

    (Tel, 'tel', NAMESPACE, TEL_ELEMENTS, TEL_CLASS_PROPS, None),

    (ParamPid, 'pid', NAMESPACE, PARAMPID_ELEMENTS, PARAMPID_CLASS_PROPS,
     None),

    (ParamType, 'type', NAMESPACE, PARAMTYPE_ELEMENTS, PARAMTYPE_CLASS_PROPS,
     None),

    (ParamCalScale, 'calscale', NAMESPACE, PARAMCALSCALE_ELEMENTS,
     PARAMCALSCALE_CLASS_PROPS, None),


    ]

CHILDLESS_BONES = [
    (ValueText, 'text', 'value'),
    (ValueUri, 'uri', 'value'),
    (ValueDate, 'date', 'value'),
    (ValueTime, 'time', 'value'),
    (ValueDateTime, 'date-time', 'value'),
    #    (ValueDateAndOrTime, 'text', 'value'),
    (ValueTimestamp, 'timestamp', 'value'),
    (ValueBoolean, 'boolean', 'value'),
    (ValueInteger, 'integer', 'value'),
    (ValueFloat, 'float', 'value'),
    (ValueUtcOffset, 'utc-offset', 'value'),
    (ValueLanguageTag, 'language-tag', 'value'),
    (ParamLanguage, 'language', 'value'),
    (ParamPrefValueInteger, 'integer', 'value'),
    (ParamAltID, 'altid', 'value'),
    (ParamPidText, 'text', 'value'),
    (ParamTypeText, 'text', 'value'),
    (GenderSex, 'sex', 'value'),
    (TelTypeText, 'text', 'value'),
    (ParamMediaType, 'mediatype', 'value'),
    (ParamCalScaleText, 'text', 'value'),
    (ParamSortAs, 'sort-as', 'value'),
    (ParamGeo, 'geo', 'value'),
    #    (111111, 'text', 'value'),
    ]

for i in CHILDLESS_BONES:
    SKELETON.append((i[0], i[1], NAMESPACE, [], [i[2]], i[2]))

del CHILDLESS_BONES


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
