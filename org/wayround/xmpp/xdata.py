
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
        raise ValueError("Invalid element")

    data = {}

    data['form_type'] = element.get('type')

    if data['form_type'] == None:
        data['form_type'] = 'form'

    if not data['form_type'] in ['cancel', 'form', 'result', 'submit']:
        raise InvalidForm(
            "Invalid form element type ({})".format(data['form_type'])
            )

    data['title'] = None
    t = element.find('{jabber:x:data}title')
    if t != None:
        data['title'] = t.text

    data['instructions'] = []

    data['fields'] = []
    data['reported_fields'] = []
    data['reported_items'] = []

    for i in element.findall('{jabber:x:data}instruction'):
        t = i.text
        if t != None:
            data['instructions'].append(t)


    for i in element.findall('{jabber:x:data}field'):
        data['fields'].append(_field_to_data(i))

    for i in element.findall('{jabber:x:data}reported'):
        if len(i) == 0:
            raise InvalidForm("Invalid `reported' children count")
        else:
            for j in i:
                data['reported_fields'].append(_field_to_data(j))

    for i in element.findall('{jabber:x:data}item'):
        items = []
        for j in i:
            if len(j) != len(data['reported_fields']):
                raise InvalidForm(
"Reported item field count does not corresponds to reported header"
                    )
            items.append(_field_to_data(j))

        data['reported_items'].append(items)

    return data

def _field_to_data(element):

    if type(element) != lxml.etree._Element:
        raise TypeError("`element' must be lxml.etree.Element")

    if element.tag != '{jabber:x:data}field':
        raise Exception("Invalid element")

    f = {
        'var': element.get('var'),
        'label': element.get('label'),
        'type': element.get('type'),
        'desc': None,
        'required': False,
        'values':[],
        'options':[]
        }

    if not f['type'] in [
        'boolean', 'fixed', 'hidden', 'jid-multi',
        'jid-single', 'list-multi', 'list-single',
        'text-multi', 'text-private', 'text-single'
        ]:
        raise InvalidForm("Invalid field type value")

    v = element.findall('{jabber:x:data}value')
    for j in v:
        f['values'].append(_value_to_data(j))

    d = element.find('{jabber:x:data}desc')
    if d != None:
        f['desc'] = d.text

    f['required'] = element.find('{jabber:x:data}required') != None

    o = element.findall('{jabber:x:data}option')
    for j in o:
        v = j.find('{jabber:x:data}value')
        if v != None:
            f['options'].append({'label':j.get('label'), 'value':_value_to_data(v)})
        else:
            raise InvalidForm("Option without value")

    return f

def _value_to_data(element):

    if type(element) != lxml.etree._Element:
        raise TypeError("`element' must be lxml.etree.Element")

    if element.tag != '{jabber:x:data}value':
        raise Exception("Invalid element")

    return element.text

def _data_to_value(data):

    e = lxml.etree.Element('value')
    e.text = data

    return e

def _data_to_field(data):

    if not isinstance(data, dict):
        raise TypeError("`data' must be dict")

    e = lxml.etree.Element('field')

    for i in ['var', 'label', 'type']:
        if data[i]:
            e.set(i, data[i])

    if not data['type'] in [
        'boolean', 'fixed', 'hidden', 'jid-multi',
        'jid-single', 'list-multi', 'list-single',
        'text-multi', 'text-private', 'text-single'
        ]:
        raise InvalidForm("Invalid field type value")

    if len(data['values']) != 0:
        for i in data['values']:
            e.append(_data_to_value(i))

    if data['desc']:
        d = lxml.etree.Element('desc')
        d.text = data['desc']
        e.append(d)

    if data['required']:
        o = lxml.etree.Element('required')
        e.append(o)


    if len(data['options']) != 0:

        for i in data['options']:
            o = lxml.etree.Element('option')
            if i['label']:
                o.set('label', i['label'])
            o.append(_data_to_value(i['value']))

            e.append(o)

    return e


def data_to_element(data):

    if not isinstance(data, dict):
        raise TypeError("`data' must be dict")

    e = lxml.etree.Element('x')
    e.set('xmlns', 'jabber:x:data')

    if not data['form_type'] in ['cancel', 'form', 'result', 'submit']:
        raise InvalidForm(
            "Invalid form element type ({})".format(data['form_type'])
            )

    e.set('type', data['form_type'])

    if data['title']:
        t = lxml.etree.Element('title')
        t.text = data['title']
        e.append(t)

    if len(data['instructions']) != 0:
        for i in data['instructions']:
            t = lxml.etree.Element('instruction')
            t.text = i
            e.append(t)


    if len(data['fields']) != 0:
        for i in data['fields']:
            e.append(_data_to_field(i))


    if len(data['reported_fields']) != 0:

        t = lxml.etree.Element('reported')
        for i in data['reported_fields']:
            t.append(_data_to_field(i))

        e.append(t)

    if len(data['reported_items']) != 0:

        for i in data['reported_items']:

            if len(i) != len(data['reported_fields']):
                raise InvalidForm(
"Reported item field count does not corresponds to reported header"
                )

            t = lxml.etree.Element('item')

            for j in i:
                t.append(_data_to_field(j))

            e.append(t)

    return e

