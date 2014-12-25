#-*- coding: utf-8 -*-

import xmpp
import re
import xml.etree.ElementTree as ETree
import glob
import sys
from multiprocessing import Process, Manager
from time import sleep


class Bot(Process):
    """ Each bot launches in separate process.

        Class variables:
        _bot_names - names list of all launched bots. With it bots can distinguish themselves from
        other conference users.
    """
    _bot_names = []

    def __init__(self, xml):
        """
        Arguments:
        xml - string. Path and name of XML file with bot data.

        Instance variables:
        _replies_to_bots - number of replies in a row to another bots.
        """
        root = ETree.parse(xml).getroot()
        self.xml = xml
        self.xmpp_jid = sys.argv[1]
        self.xmpp_pwd = sys.argv[2]
        self.conf = sys.argv[3]
        self.bot_name = root.attrib['name']
        Bot._bot_names.append(self.bot_name)
        self.regexes = []
        self._load_regexes()
        self.client = None
        self._replies_to_bots = 0
        super(Bot, self).__init__(target=self.connect)

    def connect(self):
        """Connect to server and start processing conference messages."""
        jid = xmpp.protocol.JID(self.xmpp_jid)
        self.client = xmpp.Client(jid.getDomain(), debug=[])
        self.client.connect()
        self.client.RegisterHandler('message', self._message_handler)
        self.client.auth(jid.getNode(), self.xmpp_pwd)
        p = xmpp.Presence(self.conf+"/"+self.bot_name)
        p.setTag('x', namespace=xmpp.NS_MUC)
        p.getTag('x').addChild('history', {'maxchars': '0', 'maxstanzas': '0'})
        self.client.send(p)
        while True:
            self.client.Process(1)

    def _load_regexes(self):
        """Reload keywords and phrases from XML, and recompile regexes."""
        self.regexes = []
        root = ETree.parse(self.xml).getroot()
        for elem in root.findall('case'):
            keywords = elem.find('keywords').text.split(',')
            compiled = [re.compile(ur'\b{}\b'.format(kw.strip()), re.IGNORECASE | re.U) for kw in keywords]
            self.regexes.append((compiled, elem.find('phrase').text))

    def _message_handler(self, session, msg):
        """ Handle the message and response if needed.

            If _replies_to_bots > 2, set it to 0 and break the method execution. This is needed to stop long
            conversations between bots.
        """
        sender_name = msg.getFrom().getResource()
        if self.bot_name == sender_name:
            return

        if msg.getBody() == u"{}: reload".format(self.bot_name):
            self._load_regexes()
            self.client.send(xmpp.protocol.Message(self.conf, u"{}: готово.".format(sender_name), "groupchat"))
            return

        for keywords, phrase in self.regexes:
            for kw in keywords:
                if kw.search(msg.getBody()):
                    if self._replies_to_bots > 2:
                        self._replies_to_bots = 0
                        return
                    if sender_name in Bot._bot_names:
                        self._replies_to_bots += 1

                    sleep(2)
                    self.client.send(xmpp.protocol.Message(self.conf, phrase, "groupchat"))
                    break


def run():
    """ First, create all bots, so they can populate their Bot._bot_names list with names of all bots.
        After that run each bot in separate process.
        If you'll run each bot right after it's creation, then only the last bot will receive names of all bots,
        because bots receiving their copies of Bot._bot_names at moment of launch, and this copies will be independent
        and can't be modified by other processes.
    """
    bots = []
    for xml in glob.glob("*.xml"):
        bots.append(Bot(xml))

    for bot in bots:
        bot.start()
        sleep(1)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage: lebowski_bot.py jid password conference\n\n" \
              "Example:\n" \
              "lebowski_bot.py my_jid@jabber.ru my_password my_conference@conference.jabber.ru"

        sys.exit(0)

    run()