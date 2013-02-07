
import logging
import lxml.etree
import signal
import socket
import time


import org.wayround.xmpp.core
import org.wayround.xmpp.client
import org.wayround.utils.file

logging.basicConfig(level = 'DEBUG', format = "%(levelname)s :: %(threadName)s :: %(message)s")

fdstw = org.wayround.utils.file.FDStatusWatcher(
    on_status_changed = org.wayround.utils.file.print_status_change
)

jid = org.wayround.xmpp.core.JID(
    user = 'test',
    domain = 'wayround.org'
    )

connection_info = org.wayround.xmpp.core.C2SConnectionInfo(
    host = 'wayround.org',
    port = 5222,
    jid = jid,
    password = 'Az9bblTgiCQZ9yUAK/WGp9cz4F8='
    )

sock = socket.create_connection(
    (
     connection_info.host,
     connection_info.port
     )
    )

logging.debug("Starting socket watcher")
fdstw.set_fd(sock.fileno())
fdstw.start()

client = org.wayround.xmpp.client.SampleC2SClient(
    sock,
    connection_info,
    jid
    )

client.start()

try:
    client.wait('stopped')
except:
    logging.exception("Error")



client.stop()

if client.sock_streamer.connection:
    client.sock_streamer.socket.shutdown(socket.SHUT_RDWR)
    client.sock_streamer.socket.close()
logging.debug("Reached the end. socket is {} {}".format(client.socket, client.socket._closed))

time.sleep(2)
fdstw.stop()
exit(0)
