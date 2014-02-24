
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

    def check_value(self, value):
        int(value)


class ValueFloat(ValueText):

    def check_value(self, value):
        float(value)


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


SOURCE_PROPERTY_PARAMETERS_ELEMENTS = [
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('mediatype', ParamMediaType, 'mediatype', '?')
    ]

SOURCE_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in SOURCE_PROPERTY_PARAMETERS_ELEMENTS)


class SourcePropertyParameters:
    pass


SOURCE_ELEMENTS = [
    ('parameters', SourcePropertyParameters, 'parameters', '?'),
    ('text', ValueText, 'text')
    ]

SOURCE_CLASS_PROPS = list(i[2] for i in SOURCE_ELEMENTS)


class Source:
    pass


class Kind:
    pass


PROPERTY_PARAMETERS_ELEMENTS = [
    ('language', ParamLanguage, 'language', '?'),
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?')
    ]

PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in PROPERTY_PARAMETERS_ELEMENTS)


class FnPropertyParameters:
    pass


FN_ELEMENTS = [
    ('parameters', FnPropertyParameters, 'parameters', '?'),
    ('text', ValueText, 'text')
    ]

FN_CLASS_PROPS = list(i[2] for i in FN_ELEMENTS)


class Fn:
    pass


N_PROPERTY_PARAMETERS_ELEMENTS = [
    ('language', ParamLanguage, 'language', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('sort-as', ParamSortAs, 'sort_as', '?')
    ]

N_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in N_PROPERTY_PARAMETERS_ELEMENTS)


class NPropertyParameters:
    pass


class NSurname:

    def check_value(self, value):
        if not isinstance(value, str):
            raise ValueError(
                "{} value must be str".format(self.__class__.__name__)
                )


class NGiven(NSurname):
    pass


class NAdditional(NSurname):
    pass


class NPrefix(NSurname):
    pass


class NSuffix(NSurname):
    pass


N_ELEMENTS = [
    ('parameters', NPropertyParameters, 'parameters', '?'),
    ('surname', NSurname, 'surname', '+'),
    ('given', NGiven, 'given', '+'),
    ('additional', NAdditional, 'additional', '+'),
    ('prefix', NPrefix, 'prefix', '+'),
    ('suffix', NSuffix, 'suffix', '+')
    ]

N_CLASS_PROPS = list(i[2] for i in N_ELEMENTS)


class N:

    def check_value(self, value):
        if value != None:
            raise ValueError("`value' must be None")


NICKNAME_PROPERTY_PARAMETERS_ELEMENTS = [
    ('language', ParamLanguage, 'language', '?'),
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?')
    ]

NICKNAME_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in NICKNAME_PROPERTY_PARAMETERS_ELEMENTS)


class NicknamePropertyParameters:
    pass


NICKNAME_ELEMENTS = [
    ('parameters', NicknamePropertyParameters, 'parameters', '?'),
    ('text', ValueText, 'text', '+')
    ]

NICKNAME_CLASS_PROPS = list(i[2] for i in NICKNAME_ELEMENTS)


class Nickname:
    pass


PHOTO_PROPERTY_PARAMETERS_ELEMENTS = [
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?'),
    ('mediatype', ParamMediaType, 'mediatype', '?')
    ]

PHOTO_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in PHOTO_PROPERTY_PARAMETERS_ELEMENTS)


class PhotoPropertyParameters:
    pass


PHOTO_ELEMENTS = [
    ('parameters', PhotoPropertyParameters, 'parameters', '?'),
    ('uri', ValueUri, 'uri', '')
    ]

PHOTO_CLASS_PROPS = list(i[2] for i in PHOTO_ELEMENTS)


class Photo:
    pass


BDAY_PROPERTY_PARAMETERS_ELEMENTS = [
    ('altid', ParamAltID, 'altid', '?'),
    ('calscale', ParamCalScale, 'calscale', '?')
    ]

BDAY_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in BDAY_PROPERTY_PARAMETERS_ELEMENTS)


class BDayPropertyParameters:
    pass


BDAY_ELEMENTS = [
    ('properties', BDayPropertyParameters, 'properties', '?'),
    ('text', ValueText, 'text', '?'),
    ('date', ValueDate, 'date', '?'),
    ('date-time', ValueDateTime, 'date_time', '?'),
    ('time', ValueTime, 'time', '?')
    ]

BDAY_CLASS_PROPS = list(i[2] for i in BDAY_ELEMENTS)


class BDay:
    pass


ANNIVERSARY_PROPERTY_PARAMETERS_ELEMENTS = [
    ('altid', ParamAltID, 'altid', '?'),
    ('calscale', ParamCalScale, 'calscale', '?')
    ]

ANNIVERSARY_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in ANNIVERSARY_PROPERTY_PARAMETERS_ELEMENTS)


class AnniversaryPropertyParameters:
    pass


ANNIVERSARY_ELEMENTS = [
    ('properties', AnniversaryPropertyParameters, 'properties', '?'),
    ('text', ValueText, 'text', '?'),
    ('date', ValueDate, 'date', '?'),
    ('date-time', ValueDateTime, 'date_time', '?'),
    ('time', ValueTime, 'time', '?')
    ]

ANNIVERSARY_CLASS_PROPS = list(i[2] for i in ANNIVERSARY_ELEMENTS)


class Anniversary:
    pass


class GenderSex:

    def check_value(self, value):
        if not value in ['', 'M', 'F', 'O', 'N', 'U']:
            raise ValueError("invalid GenderSex value")


class GenderIdentity:

    def check_value(self, value):
        if not isinstance(value, str):
            raise ValueError("GenderIdentity value must be str")


ADRPARAMLABEL_ELEMENTS = [
    ('sex', GenderSex, 'sex', ''),
    ('identity', GenderIdentity, 'identity', '?'),
    ]

ADRPARAMLABEL_CLASS_PROPS = list(i[2] for i in ADRPARAMLABEL_ELEMENTS)


class Gender:
    pass


ADRPARAMLABEL_ELEMENTS = [
    ('text', ValueText, 'text', '')
    ]

ADRPARAMLABEL_CLASS_PROPS = list(i[2] for i in ADRPARAMLABEL_ELEMENTS)


class AdrParamLabel:
    pass


ADR_PROPERTY_PARAMETERS_ELEMENTS = [
    ('language', ParamLanguage, 'language', '?'),
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?'),
    ('geo', ParamGeo, 'geo', '?'),
    ('tz', ParamTZ, 'tz', '?'),
    ('label', AdrParamLabel, 'label', '?')
    ]

ADR_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in ADR_PROPERTY_PARAMETERS_ELEMENTS)


class AdrPropertyParameters:
    pass


class AdrPobox:

    def check_value(self, value):
        if not isinstance(value, str):
            raise ValueError(
                "{} value must be str".format(self.__class__.__name__)
                )


class AdrExt(AdrPobox):
    pass


class AdrStreet(AdrPobox):
    pass


class AdrLocality(AdrPobox):
    pass


class AdrRegion(AdrPobox):
    pass


class AdrCode(AdrPobox):
    pass


class AdrCountry(AdrPobox):
    pass


ADR_ELEMENTS = [
    ('properties', AdrPropertyParameters, 'properties', '?'),
    ('pobox', AdrPobox, 'pobox', '+'),
    ('ext', AdrExt, 'ext', '+'),
    ('street', AdrStreet, 'street', '+'),
    ('locality', AdrLocality, 'locality', '+'),
    ('region', AdrRegion, 'region', '+'),
    ('code', AdrCode, 'code', '+'),
    ('country', AdrCountry, 'country', '+')
    ]

ADR_CLASS_PROPS = list(i[2] for i in ADR_ELEMENTS) + ['value']


class Adr:

    def check_value(self, value):
        if value != None:
            raise ValueError("`value' must be None")


class TelParamTypeText:

    def check_value(self, value):
        if not value in [
            'work', 'home', 'text', 'voice', 'fax', 'cell',
            'video', 'pager', 'textphone'
            ]:
            raise ValueError("invalid TelParamTypeText value")


TELPARAMTYPE_ELEMENTS = [
    ('text', TelParamTypeText, 'text', '+')
    ]

TELPARAMTYPE_CLASS_PROPS = list(i[2] for i in TELPARAMTYPE_ELEMENTS)


class TelParamType:
    pass


TEL_PROPERTY_PARAMETERS_ELEMENTS = [
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', TelParamType, 'type_', '?'),
    ('mediatype', ParamMediaType, 'mediatype', '?')
    ]

TEL_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in TEL_PROPERTY_PARAMETERS_ELEMENTS)


class TelPropertyParameters:
    pass


TEL_ELEMENTS = [
    ('parameters', TelPropertyParameters, 'parameters', '?'),
    ('uri', ValueUri, 'uri', '?'),
    ('text', ValueText, 'text', '?'),
    ]

TEL_CLASS_PROPS = list(i[2] for i in TEL_ELEMENTS)


class Tel:
    pass


EMAIL_PROPERTY_PARAMETERS_ELEMENTS = [
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?')
    ]

EMAIL_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in EMAIL_PROPERTY_PARAMETERS_ELEMENTS)


class EmailPropertyParameters:
    pass


EMAIL_ELEMENTS = [
    ('parameters', EmailPropertyParameters, 'parameters', '?'),
    ('text', ValueText, 'text', '')
    ]

EMAIL_CLASS_PROPS = list(i[2] for i in EMAIL_ELEMENTS)


class Email:
    pass


IMPP_PROPERTY_PARAMETERS_ELEMENTS = [
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?'),
    ('mediatype', ParamMediaType, 'mediatype', '?')
    ]

IMPP_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in IMPP_PROPERTY_PARAMETERS_ELEMENTS)


class ImppPropertyParameters:
    pass


IMPP_ELEMENTS = [
    ('parameters', ImppPropertyParameters, 'parameters', '?'),
    ('uri', ValueUri, 'uri', '')
    ]

IMPP_CLASS_PROPS = list(i[2] for i in IMPP_ELEMENTS) + ['value']


class Impp:
    pass


LANG_PROPERTY_PARAMETERS_ELEMENTS = [
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?')
    ]

LANG_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in LANG_PROPERTY_PARAMETERS_ELEMENTS)


class LangPropertyParameters:
    pass


LANG_ELEMENTS = [
    ('parameters', LangPropertyParameters, 'parameters', '?'),
    ('language-tag', ValueLanguageTag, 'language_tag', '')
    ]

LANG_CLASS_PROPS = list(i[2] for i in LANG_ELEMENTS)


class Lang:
    pass


TZ_PROPERTY_PARAMETERS_ELEMENTS = [
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?'),
    ('mediatype', ParamMediaType, 'mediatype', '?')
    ]

TZ_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in TZ_PROPERTY_PARAMETERS_ELEMENTS)


class TZPropertyParameters:
    pass


TZ_ELEMENTS = [
    ('parameters', TZPropertyParameters, 'parameters', '?'),
    ('uri', ValueUri, 'uri', '?'),
    ('text', ValueText, 'text', '?'),
    ('utc-offset', ValueUtcOffset, 'utc_offset', '?')
    ]

TZ_CLASS_PROPS = list(i[2] for i in TZ_ELEMENTS)


class TZ:
    pass


GEO_PROPERTY_PARAMETERS_ELEMENTS = [
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?'),
    ('mediatype', ParamMediaType, 'mediatype', '?')
    ]

GEO_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in GEO_PROPERTY_PARAMETERS_ELEMENTS)


class GeoPropertyParameters:
    pass


GEO_ELEMENTS = [
    ('parameters', GeoPropertyParameters, 'parameters', '?'),
    ('uri', ValueUri, 'uri', '')
    ]

GEO_CLASS_PROPS = list(i[2] for i in GEO_ELEMENTS)


class Geo:
    pass


TITLE_PROPERTY_PARAMETERS_ELEMENTS = [
    ('language', ParamLanguage, 'language', '?'),
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?')
    ]

TITLE_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in TITLE_PROPERTY_PARAMETERS_ELEMENTS)


class TitlePropertyParameters:
    pass


TITLE_ELEMENTS = [
    ('parameters', TitlePropertyParameters, 'parameters', '?'),
    ('text', ValueText, 'text', '')
    ]

TITLE_CLASS_PROPS = list(i[2] for i in TITLE_ELEMENTS)


class Title:
    pass


ROLE_PROPERTY_PARAMETERS_ELEMENTS = [
    ('language', ParamLanguage, 'language', '?'),
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?')
    ]

ROLE_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in ROLE_PROPERTY_PARAMETERS_ELEMENTS)


class RolePropertyParameters:
    pass


ROLE_ELEMENTS = [
    ('parameters', RolePropertyParameters, 'parameters', '?'),
    ('text', ValueText, 'text', '')
    ]

ROLE_CLASS_PROPS = list(i[2] for i in ROLE_ELEMENTS)


class Role:
    pass


LOGO_PROPERTY_PARAMETERS_ELEMENTS = [
    ('language', ParamLanguage, 'language', '?'),
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?'),
    ('mediatype', ParamMediaType, 'mediatype', '?')
    ]

LOGO_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in LOGO_PROPERTY_PARAMETERS_ELEMENTS)


class LogoPropertyParameters:
    pass


LOGO_ELEMENTS = [
    ('parameters', LogoPropertyParameters, 'parameters', '?'),
    ('uri', ValueUri, 'uri', '')
    ]

LOGO_CLASS_PROPS = list(i[2] for i in LOGO_ELEMENTS)


class Logo:
    pass


ORG_PROPERTY_PARAMETERS_ELEMENTS = [
    ('language', ParamLanguage, 'language', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('pref', ParamPref, 'pref', '?'),
    ('type', ParamType, 'type_', '?'),
    ('sort-as', ParamSortAs, 'sort_as', '?')
    ]

ORG_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in ORG_PROPERTY_PARAMETERS_ELEMENTS)


class OrgPropertyParameters:
    pass


ORG_ELEMENTS = [
    ('parameters', OrgPropertyParameters, 'parameters', '?'),
    ('text', ValueText, 'text', '+')
    ]

ORG_CLASS_PROPS = list(i[2] for i in ORG_ELEMENTS)


class Org:
    pass


MEMBER_PROPERTY_PARAMETERS_ELEMENTS = [
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('mediatype', ParamMediaType, 'mediatype', '?')
    ]

MEMBER_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in MEMBER_PROPERTY_PARAMETERS_ELEMENTS)


class MemberPropertyParameters:
    pass


MEMBER_ELEMENTS = [
    ('parameters', MemberPropertyParameters, 'parameters', '?'),
    ('uri', ValueUri, 'uri', '')
    ]

MEMBER_CLASS_PROPS = list(i[2] for i in MEMBER_ELEMENTS)


class Member:
    pass


class RelatedParamTypeText:

    def check_value(self, value):
        if not value in [
            'work', 'home', 'contact', 'acquaintance',
            'friend', 'met', 'co-worker', 'colleague', 'co-resident',
            'neighbor', 'child', 'parent', 'sibling', 'spouse',
            'kin', 'muse', 'crush', 'date', 'sweetheart', 'me',
            'agent', 'emergency'
            ]:
            raise ValueError("Invalid RelatedParamTypeText value")


RELATEDTYPE_ELEMENTS = [
    ('text', RelatedParamTypeText, 'text', '+')
    ]

RELATEDTYPE_CLASS_PROPS = list(i[2] for i in RELATEDTYPE_ELEMENTS)


class RelatedParamType:
    pass


RELATED_PROPERTY_PARAMETERS_ELEMENTS = [
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', RelatedParamType, 'type_', '?'),
    ('mediatype', ParamMediaType, 'mediatype', '?')
    ]

RELATED_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in RELATED_PROPERTY_PARAMETERS_ELEMENTS)


class RelatedPropertyParameters:
    pass


RELATED_ELEMENTS = [
    ('parameters', RelatedPropertyParameters, 'parameters', '?'),
    ]

RELATED_CLASS_PROPS = list(i[2] for i in RELATED_ELEMENTS) + ['value']


class Related:
    pass


CATEGORIES_PROPERTY_PARAMETERS_ELEMENTS = [
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?'),
    ('mediatype', ParamMediaType, 'mediatype', '?')
    ]

CATEGORIES_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in CATEGORIES_PROPERTY_PARAMETERS_ELEMENTS)


class CategoriesPropertyParameters:
    pass


CATEGORIES_ELEMENTS = [
    ('parameters', CategoriesPropertyParameters, 'parameters', '?'),
    ('text', ValueText, 'text', '+')
    ]

CATEGORIES_CLASS_PROPS = list(i[2] for i in CATEGORIES_ELEMENTS)


class Categories:
    pass


NOTE_PROPERTY_PARAMETERS_ELEMENTS = [
    ('language', ParamLanguage, 'language', '?'),
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?'),
    ('mediatype', ParamMediaType, 'mediatype', '?')
    ]

NOTE_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in NOTE_PROPERTY_PARAMETERS_ELEMENTS)


class NotePropertyParameters:
    pass

NOTE_ELEMENTS = [
    ('parameters', NotePropertyParameters, 'parameters', '?'),
    ('text', ValueText, 'text', '')
    ]

NOTE_CLASS_PROPS = list(i[2] for i in NOTE_ELEMENTS)


class Note:
    pass


PROPID_ELEMENTS = [
    ('text', ValueText, 'text', '')
    ]

PROPID_CLASS_PROPS = list(i[2] for i in PROPID_ELEMENTS)


class Propid:
    pass


REV_ELEMENTS = [
    ('timestamp', ValueTimestamp, 'timestamp', '')
    ]

REV_CLASS_PROPS = list(i[2] for i in REV_ELEMENTS)


class Rev:
    pass


SOUND_PROPERTY_PARAMETERS_ELEMENTS = [
    ('language', ParamLanguage, 'language', '?'),
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?'),
    ('mediatype', ParamMediaType, 'mediatype', '?')
    ]

SOUND_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in SOUND_PROPERTY_PARAMETERS_ELEMENTS)


class SoundPropertyParameters:
    pass


SOUND_ELEMENTS = [
    ('parameters', SoundPropertyParameters, 'parameters', '?'),
    ('uri', ValueUri, 'uri', '')
    ]

SOUND_CLASS_PROPS = list(i[2] for i in SOUND_ELEMENTS)


class Sound:

    def check_value(self, value):
        if value != None:
            raise ValueError("`value' must be None")


UID_ELEMENTS = [
    ('uri', ValueUri, 'uri', '')
    ]

UID_CLASS_PROPS = list(i[2] for i in UID_ELEMENTS)


class Uid:
    pass


class ClientpidmapSourceId:

    def check_value(self, value):
        i = int(value)
        if i < 0:
            raise ValueError("ClientpidmapSourceId must be positive")


CLIENTPIDMAP_ELEMENTS = [
    ('sourceid', ClientpidmapSourceId, 'sourceid', ''),
    ('uri', ValueUri, 'uri', '')
    ]

CLIENTPIDMAP_CLASS_PROPS = list(i[2] for i in CLIENTPIDMAP_ELEMENTS)


class Clientpidmap:
    pass


URL_PROPERTY_PARAMETERS_ELEMENTS = [
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?'),
    ('mediatype', ParamMediaType, 'mediatype', '?')
    ]

URL_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in URL_PROPERTY_PARAMETERS_ELEMENTS)


class UrlPropertyParameters:
    pass


URL_ELEMENTS = [
    ('parameters', UrlPropertyParameters, 'parameters', '?'),
    ('uri', ValueUri, 'uri', '')
    ]

URL_CLASS_PROPS = list(i[2] for i in URL_ELEMENTS)


class Url:
    pass


KEY_PROPERTY_PARAMETERS_ELEMENTS = [
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?'),
    ('mediatype', ParamMediaType, 'mediatype', '?')
    ]

KEY_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in KEY_PROPERTY_PARAMETERS_ELEMENTS)


class KeyPropertyParameters:
    pass


KEY_ELEMENTS = [
    ('parameters', KeyPropertyParameters, 'parameters', '?'),
    ('uri', ValueUri, 'value_uri', '?'),
    ('text', ValueText, 'value_text', '?')
    ]

KEY_CLASS_PROPS = list(i[2] for i in KEY_ELEMENTS)


class Key:
    pass


FBURL_PROPERTY_PARAMETERS_ELEMENTS = [
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?'),
    ('mediatype', ParamMediaType, 'mediatype', '?')
    ]

FBURL_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in FBURL_PROPERTY_PARAMETERS_ELEMENTS)


class FburlPropertyParameters:
    pass


FBURL_ELEMENTS = [
    ('properties', FburlPropertyParameters, 'properties', '?'),
    ('uri', ValueUri, 'uri', '')
    ]

FBURL_CLASS_PROPS = \
    list(i[2] for i in FBURL_ELEMENTS)


class Fburl:
    pass


CALADRURI_PROPERTY_PARAMETERS_ELEMENTS = [
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?'),
    ('mediatype', ParamMediaType, 'mediatype', '?')
    ]

CALADRURI_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in CALADRURI_PROPERTY_PARAMETERS_ELEMENTS)


class CaladruriPropertyParameters:
    pass


CALURI_ELEMENTS = [
    ('properties', CaladruriPropertyParameters, 'properties', '?'),
    ('uri', ValueUri, 'uri', '')
    ]

CALURI_CLASS_PROPS = \
    list(i[2] for i in CALURI_ELEMENTS)


class Caladruri:
    pass


CALURI_PROPERTY_PARAMETERS_ELEMENTS = [
    ('pref', ParamPref, 'pref', '?'),
    ('altid', ParamAltID, 'altid', '?'),
    ('pid', ParamPid, 'pid', '?'),
    ('type', ParamType, 'type_', '?'),
    ('mediatype', ParamMediaType, 'mediatype', '?')
    ]

CALURI_PROPERTY_PARAMETERS_CLASS_PROPS = \
    list(i[2] for i in CALURI_PROPERTY_PARAMETERS_ELEMENTS)


class CaluriPropertyParameters:
    pass


CALURI_ELEMENTS = [
    ('properties', CaluriPropertyParameters, 'properties', '?'),
    ('uri', ValueUri, 'uri', '')
    ]

CALURI_CLASS_PROPS = \
    list(i[2] for i in CALURI_ELEMENTS)


class Caluri:
    pass


SKELETON = [
    # 0. Class;
    # 1. tag;
    # 2. namespace;
    # 3. elements struct;
    # 4. object properties list;
    # 5. element text parameter name
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

    (TelParamType, 'tel', NAMESPACE, TEL_ELEMENTS, TEL_CLASS_PROPS, None),

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
    (TelParamTypeText, 'text', 'value'),
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
    ('bday', BDay, 'bday', '*'),
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
    ('rev', Rev, 'rev', '*'),
    ('role', Role, 'role', '*'),
    ('sound', Sound, 'sound', '*'),
    ('source', Source, 'source', '*'),
    ('tel', Tel, 'tel', '*'),
    ('title', Title, 'title', '*'),
    ('tz', TZ, 'tz', '*'),
    ('uid', Uid, 'uid', '*'),
    ('url', Url, 'url', '*')
    ]

VCARD_CLASS_PROPS = list(i[2] for i in VCARD_ELEMENTS)
