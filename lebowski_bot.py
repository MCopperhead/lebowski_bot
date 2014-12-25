#-*- coding: utf-8 -*-

import xmpp
import re
import xml.etree.ElementTree as ETree
import glob
import sys
from multiprocessing import Process
from time import sleep


class Bot(Process):
    def __init__(self, xml):
        """
        xml - string. Path and name of XML file with bot data.
        """
        root = ETree.parse(xml).getroot()
        self.xml = xml
        self.xmpp_jid = sys.argv[1]
        self.xmpp_pwd = sys.argv[2]
        self.conf = sys.argv[3]
        self.bot_name = root.attrib['name']
        self.regexes = []
        self._load_regexes()
        self.client = None
        super(Bot, self).__init__(target=self.connect)

    def connect(self):
        """
        Connect to server and start processing conference messages.
        """
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
        """
        Reload keywords and phrases from XML, and recompile regexes.
        """
        self.regexes = []
        root = ETree.parse(self.xml).getroot()
        for elem in root.findall('case'):
            keywords = elem.find('keywords').text.split(',')
            compiled = [re.compile(ur'\b{}\b'.format(kw.strip()), re.IGNORECASE | re.U) for kw in keywords]
            self.regexes.append((compiled, elem.find('phrase').text))

    def _message_handler(self, session, msg):
        """
        Handle the message and response if needed.
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
                    sleep(1)
                    self.client.send(xmpp.protocol.Message(self.conf, phrase, "groupchat"))
                    break


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage: lebowski_bot.py jid password conference\n\n" \
              "Example:\n" \
              "lebowski_bot.py my_jid@jabber.ru my_password my_conference@conference.jabber.ru"

        sys.exit(0)

    for xml in glob.glob("*.xml"):
        bot = Bot(xml)
        bot.start()