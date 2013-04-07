
import xml.sax.saxutils

import org.wayround.xmpp.core

class Body(org.wayround.xmpp.core.StanzaElement):

    def __init__(self, text='', xmllang=None):
        self.text = text
        self.xmllang = xmllang

    def __str__(self):
        return self.to_str()

    def to_str(self):
        xmllang_t = ''
        if self.xmllang:
            xmllang_t = ' xml:lang="{}"'.format(xml.sax.saxutils.escape(self.xmllang))
        return '<body{xmllang}>{text}</body>'.format(
            xmllang=xmllang_t,
            text=xml.sax.saxutils.escape(self.text)
            )

class Subject(org.wayround.xmpp.core.StanzaElement):

    def __init__(self, text='', xmllang=None):
        self.text = text
        self.xmllang = xmllang

    def __str__(self):
        return self.to_str()

    def to_str(self):
        xmllang_t = ''
        if self.xmllang:
            xmllang_t = ' xml:lang="{}"'.format(xml.sax.saxutils.escape(self.xmllang))
        return '<subject{xmllang}>{text}</subject>'.format(
            xmllang=xmllang_t,
            text=xml.sax.saxutils.escape(self.text)
            )

class Thread(org.wayround.xmpp.core.StanzaElement):

    def __init__(self, value='', parent=None):
        self.value = value
        self.parent = parent

    def __str__(self):
        return self.to_str()

    def to_str(self):
        parent_t = ''
        if self.parent:
            parent_t = ' parent="{}"'.format(xml.sax.saxutils.escape(self.parent))
        return '<thread{parent}>{value}</thread>'.format(
            parent=parent_t,
            value=xml.sax.saxutils.escape(self.value)
            )
