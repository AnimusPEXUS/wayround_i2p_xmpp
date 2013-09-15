
import org.wayround.xmpp.disco

def get_commands_list(jid_to, jid_from, stanza_processor=None):

    q = org.wayround.xmpp.disco.get_info(
        jid_to, jid_from, None, stanza_processor
        )

    ret = None

    if q != None:
        r = q.find(
            "{http://jabber.org/protocol/disco#info}feature[@var='http://jabber.org/protocol/commands']"
            )

        if r != None:
            q = org.wayround.xmpp.disco.get_items(
                jid_to,
                jid_from,
                'http://jabber.org/protocol/commands',
                stanza_processor
                )

            if q != None:

                items = q.findall('{http://jabber.org/protocol/disco#items}item')

                ret = {}

                for i in items:

                    ret[i.get('node')] = {
                        'jid': i.get('jid'),
                        'name': i.get('name')
                        }

    return ret
