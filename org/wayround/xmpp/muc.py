
import lxml.etree

import org.wayround.xmpp.core

class Server:

    def __init__(self):
        pass

    def connect_stanza_processor(self, stanza_processor):
        pass

    def disconnect_stanza_processor(self):
        pass


# TODO: do i really need this class?
class Client:

    def __init__(self, client, client_jid):

        self._stanza_processor = None
        self._client_jid = client_jid
        self._client = client

    def connect_stanza_processor(self, stanza_processor):

        self._stanza_processor = stanza_processor

    def disconnect_stanza_processor(self):
        pass



def request_room_configuration(room_bare_jid, from_full_jid, stanza_processor):

    stanza = org.wayround.xmpp.core.Stanza('iq')

    stanza.jid_from = from_full_jid
    stanza.jid_to = room_bare_jid
    stanza.typ = 'get'

    query = lxml.etree.Element('query')
    query.set('xmlns', 'http://jabber.org/protocol/muc#owner')

    stanza.body.append(query)

    ret = stanza_processor.send(stanza, wait=None)
    return ret

def submit_room_configuration(
        room_bare_jid, from_full_jid, stanza_processor, form_element
        ):

    if type(form_element) != lxml.etree._Element:
        raise TypeError("`form_element' must be lxml.etree._Element")

    if (form_element.tag != '{jabber:x:data}x'
        and (form_element.tag != 'x' or form_element.get('xmlns') != 'jabber:x:data')):
        raise ValueError("invalid form element: {}".format(form_element.tag))

    stanza = org.wayround.xmpp.core.Stanza('iq')

    stanza.jid_from = from_full_jid
    stanza.jid_to = room_bare_jid
    stanza.typ = 'set'

    query = lxml.etree.Element('query')
    query.set('xmlns', 'http://jabber.org/protocol/muc#owner')

    query.append(form_element)

    stanza.body.append(query)

    ret = stanza_processor.send(stanza, wait=None)
    return ret

def destroy_room(
    room_bare_jid, from_full_jid, stanza_processor,
    reason=None, alternate_venue_jid=None
    ):

    destroy_e = lxml.etree.Element('destroy')
    if alternate_venue_jid:
        destroy_e.set('jid', alternate_venue_jid)

    if reason:
        reason_e = lxml.etree.Element('reason')
        reason_e.text = reason
        destroy_e.append(reason_e)

    query = lxml.etree.Element('query')
    query.set('xmlns', 'http://jabber.org/protocol/muc#owner')
    query.append(destroy_e)

    stanza = org.wayround.xmpp.core.Stanza('iq')

    stanza.jid_from = from_full_jid
    stanza.jid_to = room_bare_jid
    stanza.typ = 'set'

    stanza.body.append(query)

    ret = stanza_processor.send(stanza, wait=None)
    return ret
