
import lxml.etree

import org.wayround.utils.factory
import org.wayround.utils.lxml
import org.wayround.utils.types


class Media:

    def __init__(self, width=None, height=None, uri=None):

        if uri == None:
            uri = []

        self.set_uri(uri)
        self.set_width(width)
        self.set_height(height)

    def check_uri(self, value):
        if not org.wayround.utils.types.struct_check(
            value,
            {'t': list, '.': {'t': URI}}
            ):
            raise ValueError("`uri' must be list of URI")

    def check_width(self, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("`width' must be None or int")

    def check_height(self, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("`height' must be None or int")

    @classmethod
    def new_from_element(cls, element):

        tag = org.wayround.utils.lxml.parse_element_tag(
            element,
            ['media'],
            ['urn:xmpp:media-element']
            )[0]

        if tag == None:
            raise ValueError("invalid element")

        cl = cls()

        org.wayround.utils.lxml.elem_props_to_object_props(
            element, cl,
            [
             ('width', 'width'),
             ('height', 'height')
             ]
            )

        org.wayround.utils.lxml.subelemsm_to_object_propsm(
            element, cl,
            [
             ('{urn:xmpp:media-element}uri', URI, 'uri')
             ]
            )

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('media')
        el.set('xmlns', 'urn:xmpp:media-element')

        org.wayround.utils.lxml.object_props_to_elem_props(
            self, el,
            [
             ('width', 'width'),
             ('height', 'height')
             ]
            )

        org.wayround.utils.lxml.object_propsm_to_subelemsm(
            self, el,
            ['uri']
            )

        return el

org.wayround.utils.factory.class_generate_attributes(
    Media,
    ['width', 'height', 'uri']
    )
org.wayround.utils.factory.class_generate_check(
    Media,
    ['width', 'height', 'uri']
    )


class URI:

    def __init__(self, type_, text):

        self.set_type_(type_)
        self.set_text(text)

    def check_type_(self, value):
        if not isinstance(value, str):
            raise ValueError("`type_' must be str")

    def check_text(self, value):
        if not isinstance(value, str):
            raise ValueError("`text' must be str")

    @classmethod
    def new_from_element(cls, element):

        tag = org.wayround.utils.lxml.parse_element_tag(
            element,
            ['uri'],
            ['urn:xmpp:media-element']
            )[0]

        if tag == None:
            raise ValueError("invalid element")

        cl = cls(element.get('type'), element.text)

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('uri')

        el.set('type', self.get_type_())
        el.text = self.get_text()

        return el

org.wayround.utils.factory.class_generate_attributes(
    URI,
    ['type_', 'text']
    )
org.wayround.utils.factory.class_generate_check(
    URI,
    ['type_', 'text']
    )
