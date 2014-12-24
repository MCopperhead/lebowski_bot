#-*- coding: utf-8 -*-

import xmpp
import re
from time import sleep

# TODO: вынести информацию об аккаунте и набор фраз в отдельный XML для каждого бота.
# TODO: сам скрипт должен быть универсальным для всех ботов.
"""
Структура фраз в XML:
<case>
    <keyword>ковёр</keyword>
    <phrase>Ковёр задавал стиль всей комнате.</phrase>
</case>
"""
xmpp_jid = 'thedude@jabber.ru'
xmpp_pwd = 'thecarpet'
conf = 'wayfaerer@conference.jabber.ru'
nick = 'The Dude'

regexes = ((re.compile(ur'\bковёр\b', re.IGNORECASE | re.U),
            u"Ковёр задавал стиль всей комнате."),
           (re.compile(ur'\bплан\b', re.IGNORECASE | re.U),
            u"Великолепный план, Уолтер. Просто охуенный, если я правильно понял."
            u" Надёжный, блядь, как швейцарские часы."))


def message_handler(session, msg):
    if nick == msg.getFrom().getResource():
        return

    msg = msg.getBody()
    for regex, phrase in regexes:
        if regex.search(msg):
            sleep(1)
            client.send(xmpp.protocol.Message(conf, phrase, "groupchat"))
            break


jid = xmpp.protocol.JID(xmpp_jid)
client = xmpp.Client(jid.getDomain(), debug=[])
client.connect()
client.RegisterHandler('message', message_handler)
client.auth(jid.getNode(), str(xmpp_pwd))
p = xmpp.Presence(conf+"/"+nick)
p.setTag('x', namespace=xmpp.NS_MUC)
p.getTag('x').addChild('history', {'maxchars': '0', 'maxstanzas': '0'})
client.send(p)
while True:
    client.Process(1)