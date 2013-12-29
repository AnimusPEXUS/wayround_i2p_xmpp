
import logging
import threading

import org.wayround.utils.signal
import org.wayround.xmpp.above.client
import org.wayround.xmpp.core
import org.wayround.xmpp.muc


#class Item(org.wayround.utils.signal.Signal):
class Item:

    def __init__(
        self,
        nick,
        affiliation=None, role=None,
        available=None, show=None, status=None
        ):

#        super().__init__(['changed'])

        self.set_nick(nick)
        self.set_affiliation(affiliation)
        self.set_role(role)
        self.set_available(available)
        self.set_show(show)
        self.set_status(status)

    check_nick = org.wayround.xmpp.muc.Item.check_nick
    check_affiliation = org.wayround.xmpp.muc.Item.check_affiliation
    check_role = org.wayround.xmpp.muc.Item.check_role

    def check_available(self, value):
        if value is not None and not isinstance(value, bool):
            raise TypeError("`available' must be None or bool")

    def check_show(self, value):
        if value is not None:
            org.wayround.xmpp.core.PresenceShow.check_text(self, value)

    def check_status(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`status' must be None or str")

org.wayround.utils.factory.class_generate_attributes(
    Item,
    ['nick', 'affiliation', 'role', 'available', 'show', 'status']
    )

#org.wayround.utils.factory.class_generate_attributes(
#    Item,
#    [('nick', 'changed'),
#     ('affiliation', 'changed'),
#     ('role', 'changed'),
#     ('available', 'changed'),
#     ('show', 'changed'),
#     ('status', 'changed')
#     ]
#    )


class Storage(org.wayround.utils.signal.Signal):

    def __init__(self, room_jid, presence_client):

        if not isinstance(presence_client, org.wayround.xmpp.above.client.Presence):
            raise TypeError(
                "`presence_client' must be org.wayround.xmpp.above.client.Presence"
                )

        if not isinstance(room_jid, org.wayround.xmpp.core.JID):
            raise TypeError(
                "`room_jid' must be org.wayround.xmpp.core.JID"
                )

        self._room_jid = room_jid
        self._presence_client = presence_client

        self._lock = threading.Lock()

        self._items = []

        super().__init__(['add', 'remove', 'set'])

        presence_client.connect_signal(
            ['presence'], self._on_presence
            )

        return

    def _on_presence(self, event, presence_obj, from_jid, to_jid, stanza):

        if event == 'presence':

            fj = org.wayround.xmpp.core.JID.new_from_str(from_jid)

            if fj.bare() == self._room_jid.bare():

                show = stanza.get_show()
                show_val = None
                if show:
                    show_val = show.get_text()
                else:
                    show_val = 'available'
                    if stanza.get_typ() == 'unavailable':
                        show_val = 'unavailable'

                status = stanza.get_status()
                status_val = None
                if len(status) != 0:
                    status_val = status[0].get_text()
                else:
                    status_val = ''

                available_val = stanza.get_typ() != 'unavailable'

                self.set(
                    nick=from_jid.resource,
                    show=show_val,
                    status=status_val,
                    available=available_val
                    )

                muc_elem_list = org.wayround.xmpp.muc.get_muc_elements(
                    stanza.get_element()
                    )

                if len(muc_elem_list) == 1:

                    e = muc_elem_list[1]

                    if e.tag == \
                        '{http://jabber.org/protocol/muc#user}x':

                        muc_obj = org.wayround.xmpp.muc.X.new_from_element(e)

                        item = muc_obj.get_item()

                        self.set(
                            nick=from_jid.resource,
                            affiliation=item.get_affiliation(),
                            role=item.get_role(),
                            new_nick=item.get_nick()
                            )

                else:
                    logging.error(
                        "Not supported more then one muc element in stanza"
                        )

        return

    def set(
        self,
        nick,
        affiliation=None, role=None, new_nick=None,
        available=None, show=None, status=None
        ):

        d = None

        for i in self._items:
            if i.nick == nick:
                d = i

        if d == None:
            d = Item(nick)
            self._items.append(d)
            self.emit_signal('add', self, nick, d)

        for i in [
            'affiliation',
            'role',
            'available',
            'show',
            'status'
            ]:
            val = eval(i)
            if val != None:
                setter = getattr(d, 'set_{}'.format(i))
                setter(val)

        if new_nick != None:
            d.set_nick(new_nick)

        self.emit_signal('set', self, nick, d)

        return
