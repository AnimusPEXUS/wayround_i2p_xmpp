
import lxml.etree

import org.wayround.xmpp.core

def _x(jid_to, jid_from, node=None, stanza_processor=None, mode='info'):
    """
    :param org.wayround.xmpp.core.StanzaProcessor stanza_processor:
    """

    if not mode in ['info', 'items']:
        raise ValueError("`mode' invalid")

    if not isinstance(stanza_processor, org.wayround.xmpp.core.StanzaProcessor):
        raise TypeError(
            "`stanza_processor' must be of type org.wayround.xmpp.core.StanzaProcessor"
            )

    q = lxml.etree.Element('query')
    q.set('xmlns', 'http://jabber.org/protocol/disco#{}'.format(mode))

    if node != None:
        q.set('node', node)

    stanza = org.wayround.xmpp.core.Stanza(
        tag='iq',
        jid_from=jid_from,
        jid_to=jid_to,
        typ='get',
        body=[
            q
            ]
        )

#    print("Sending disco stanza")
    ret = stanza_processor.send(stanza, wait=None)
#    print("Sending disco stanza result achived: {}".format(ret))

    return ret


def get_info(jid_to, jid_from, node=None, stanza_processor=None):

    ret = None

    res = _x(jid_to, jid_from=jid_from, node=node, stanza_processor=stanza_processor, mode='info')

    if isinstance(res, org.wayround.xmpp.core.Stanza):
        ret = res.body.find('{http://jabber.org/protocol/disco#info}query')

    return ret, res

def get_items(jid_to, jid_from, node=None, stanza_processor=None):

    ret = None

    res = _x(jid_to, jid_from=jid_from, node=node, stanza_processor=stanza_processor, mode='items')

    if isinstance(res, org.wayround.xmpp.core.Stanza):
        ret = res.body.find('{http://jabber.org/protocol/disco#items}query')

    return ret, res

def get(jid_to, jid_from, node=None, stanza_processor=None):
    return {
        'info': get_info(jid_to, jid_from=jid_from, node=node, stanza_processor=stanza_processor),
        'items': get_items(jid_to, jid_from=jid_from, node=node, stanza_processor=stanza_processor)
        }
