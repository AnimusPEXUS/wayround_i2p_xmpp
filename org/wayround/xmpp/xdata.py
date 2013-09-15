
import lxml.etree

def get_x_data_elements(element):

    """
    Search for jabber:x:data elements in supplied element
    """

    if type(element) != lxml.etree._Element:
        raise TypeError("`element' must be lxml.etree.Element")

    return element.findall('{jabber:x:data}x')

def get_x_data_element(element):

    ret = get_x_data_elements(element)

    if ret:
        ret = ret[0]
    else:
        ret = None

    return ret

class InvalidForm(Exception): pass

def element_to_data(element):

    if type(element) != lxml.etree._Element:
        raise TypeError("`element' must be lxml.etree.Element")

    if element.tag != '{jabber:x:data}x':
        raise Exception("Invalid element")

    data = {}

    data['form_type'] = element.get('type')

    if data['form_type'] == None:
        raise InvalidForm("Invalid form element")

    data['title'] = None
    t = element.find('{jabber:x:data}title')
    if t != None:
        data['title'] = t.text

    data['instructions'] = []

    for i in element:
        if i.tag == '{jabber:x:data}instruction':
            t = i.text
            if t == None:
                t = ''
            data['instructions'].append(t)

    data['fields'] = []

    for i in element:
        if i.tag == '{jabber:x:data}field':
            f = {
                'var': None,
                'label': None,
                'type': None,
                'label': None,
                'desc': None,
                'required': False,
                'values':[],
                'options':[]
                }
            f['var'] = i.get('var')
            f['label'] = i.get('label')
            f['type'] = i.get('type')

            if not f['type'] in [
                'boolean', 'fixed', 'hidden', 'jid-multi',
                'jid-single', 'list-multi', 'list-single',
                'text-multi', 'text-private', 'text-single'
                ]:
                raise InvalidForm("Invalid field type value")

            v = i.findall('{jabber:x:data}value')
            for j in v:
                f['value'].append(j.text)

            o = i.findall('{jabber:x:data}option')
            for j in o:
                v = j.find('{jabber:x:data}value')
                if v != None:
                    f['option'].append({'label':j.get('label'), 'value':v.text})
                else:
                    raise InvalidForm("Option without value")

    return data
