
import lxml.etree

import wayround_org.utils.factory
import wayround_org.utils.lxml


class X:

    def __init__(self, url, desc=None):

        self.set_url(url)
        self.set_desc(url)

    def check_url(self, value):
        if not isinstance(str, value):
            raise TypeError("`url' must be str")

    def check_desc(self, value):
        if value is not None and not isinstance(str, value):
            raise TypeError("`desc' must be str or None")

    @classmethod
    def new_from_element(cls, element):

        tag = 'x'
        ns = 'jabber:x:oob'
        if cls == Query:
            tag = 'query'
            ns = 'jabber:iq:oob'

        tag, ns = wayround_org.utils.lxml.parse_element_tag(
            element, tag, [ns]
            )

        if tag == None:
            raise ValueError("invalid element")

        url = None
        desc = None

        url_el = element.find('{{ns}}url'.format(ns=ns))
        if url_el != None:
            url = url_el.text

        desc_el = element.find('{{ns}}desc'.format(ns=ns))
        if desc_el != None:
            desc = desc_el.text

        obj = None
        if cls == X:
            obj = X(url)
        else:
            obj = Query(url)

        if cls == Query:
            obj.set_sid(element.get('sid'))

        obj.set_desc(desc)

        # FIXME: error?
        wayround_org.utils.lxml.subelems_to_object_props(
            element
            )

        obj.check()

        return obj

    def gen_element(self):

        self.check()

        tag = 'x'
        ns = 'jabber:x:oob'
        if type(self) == Query:
            tag = 'query'
            ns = 'jabber:iq:oob'

        el = lxml.etree.Element(tag)
        el.set('xmlns', ns)

        url_el = lxml.etree.Element('url')
        url_el.text = self.get_url()
        el.append(url_el)

        desc_el = lxml.etree.Element('desc')
        desc_el.text = self.get_desc()
        el.append(desc_el)

        if type(self) == Query:
            el.set('sid', self.get_sid())

        return el

wayround_org.utils.factory.class_generate_attributes(
    X,
    ['url', 'desc']
    )
wayround_org.utils.factory.class_generate_check(
    X,
    ['url', 'desc']
    )


class Query(X):

    def __init__(self, url, desc=None, sid=None):

        super().__init__(url, desc)

        self.set_sid(sid)

    def check_sid(self, value):
        if value is not None and not isinstance(str, value):
            raise TypeError("`sid' must be str or None")

wayround_org.utils.factory.class_generate_attributes(
    Query,
    ['sid']
    )
wayround_org.utils.factory.class_generate_check(
    Query,
    ['sid']
    )
