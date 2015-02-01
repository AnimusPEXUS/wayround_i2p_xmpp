
import base64
import re
import hashlib
import logging
import lxml.etree

import wayround_org.utils.factory
import wayround_org.utils.lxml
import wayround_org.utils.checksum


CID_RE = re.compile(r'^(cid\:)?(?P<method>\w+)\+(?P<value>\w+)\@bob\.xmpp\.org$')


def parse_cid(value):

    ret = None

    res = CID_RE.match(value)

    if res != None:

        method = res.group('method')
        method = method.lower()

        value = res.group('value')
        value = value.lower()

        ret = {
            'method': method,
            'value': value
            }

    return ret


def format_cid(method, value):
    method = method.lower()
    value = value.lower()
    return 'cid:{method}+{value}@bob.xmpp.org'.format(
        method=method,
        value=value
        )


def generate_cid_for_data(method, data):

    if not method.isidentifier() or not hasattr(hashlib, method):
        raise ValueError("hashlib doesn't have `{}'".format(method))

    ret = None

    try:
        hash_method_name = eval("hashlib.{}()".format(method))
    except:
        logging.exception(
            "Error calling for hashlib method `{}'".format(method)
            )
        ret = None
    else:
        hash_method_name.update(data)
        dig = hash_method_name.hexdigest()
        dig = dig.lower()
        ret = format_cid(method, dig)

    return ret


class Data:

    def __init__(self, cid, max_age=None, type_=None, data=None):

        self.set_cid(cid)
        self.set_max_age(max_age)
        self.set_type_(type_)
        self.set_data(data)

        return

    def check_cid(self, value):

        if not isinstance(value, str):
            raise ValueError("`cid' must be str")

        if parse_cid(value) == None:
            raise ValueError("Can't parse as `cid' value: '{}'".format(value))

    def check_max_age(self, value):
        if value != None:
            v = 0
            try:
                v = int(value)
            except:
                raise ValueError(
                    "Invalid value for max_age: {}({})".format(
                        value, type(value)
                        )
                    )
            else:
                if v < 0:
                    raise ValueError(
                    "Invalid value for max_age: {}({})".format(
                        value, type(value)
                        )
                    )
        return

    def check_type_(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`type_' must be None or str")

    def check_data(self, value):
        if value is not None and not isinstance(value, bytes):
            raise ValueError("`data' must be None or bytes")

    @classmethod
    def new_from_element(cls, element):

        tag = wayround_org.utils.lxml.parse_element_tag(
            element,
            ['data'],
            ['urn:xmpp:bob']
            )[0]

        if tag == None:
            raise ValueError("invalid element")

        cl = cls(element.get('cid'))

        wayround_org.utils.lxml.elem_props_to_object_props(
            element, cl,
            [
             ('max-age', 'max_age'),
             ('type', 'type_')
             ]
            )

        if element.text != None:
            cl.set_data(base64.b64decode(bytes(element.text, 'utf-8')))

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        el = lxml.etree.Element('data')
        el.set('xmlns', 'urn:xmpp:bob')

        el.set('cid', self.get_cid())

        wayround_org.utils.lxml.object_props_to_elem_props(
            self, el,
            [
             ('max_age', 'max-age'),
             ('type_', 'type')
             ]
            )

        data = self.get_data()

        if data != None:
            el.text = str(base64.b64encode(data), 'utf-8')

        return el

    def is_data_error(self):

        ret = True

        data = self.get_data()

        if data != None:
            data = str(base64.b64encode(data), 'utf-8')

            cid_parsed = parse_cid(self.get_cid())

            if cid_parsed != None:
                res = wayround_org.utils.checksum.is_data_error(
                    cid_parsed['method'],
                    cid_parsed['value'],
                    data
                    )

                ret = res

        return ret


wayround_org.utils.factory.class_generate_attributes(
    Data,
    ['cid', 'max_age', 'type_', 'data']
    )
wayround_org.utils.factory.class_generate_check(
    Data,
    ['cid', 'max_age', 'type_', 'data']
    )
