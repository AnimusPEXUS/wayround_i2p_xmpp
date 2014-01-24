
import lxml.etree

import org.wayround.utils.factory
import org.wayround.utils.lxml

import org.wayround.xmpp.xdata


class Captcha:

    def __init__(self, x):

        self.set_x(x)

    def check_x(self, value):

        if not isinstance(value, org.wayround.xmpp.xdata.XData):
            raise ValueError("`x' must be org.wayround.xmpp.xdata.XData")

    @classmethod
    def new_from_element(cls, element):

        tag = org.wayround.utils.lxml.parse_element_tag(
            element,
            ['captcha'],
            ['urn:xmpp:captcha']
            )[0]

        if tag == None:
            raise ValueError("invalid element")

        xdata = element.find('{jabber:x:data}x')

        if xdata == None:
            raise ValueError("x form not found in captcha element")

        cl = cls(org.wayround.xmpp.xdata.XData.new_from_element(xdata))

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('captcha')
        el.set('xmlns', 'urn:xmpp:captcha')

        el.append(self.get_x().gen_element())

        return el


org.wayround.utils.factory.class_generate_attributes(
    Captcha,
    ['x']
    )
org.wayround.utils.factory.class_generate_check(
    Captcha,
    ['x']
    )
