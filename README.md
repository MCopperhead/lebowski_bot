### Requirements: ###
- python 2
- xmpppy module (python-xmpp package in deb distros)

### Usage: ###
lebowski_bot.py jid password conference

Example:
lebowski_bot.py my_jid@jabber.ru my_password my_conference@conference.jabber.ru


### Description: ###
Bot for jabber conferences. React on keywords in messages and responding with "Big Lebowski" movie quotations.
Creates a separate python process for each XML file in directory.
XML file describes the bot name and list of it's phrases and keywords to react on.