#!/usr/bin/python3

# Copyright (C) 2019-2021 Olivier Neyret
#
# This file is part of Babot.
#
# Babot program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# Babot program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

def cleanMessage(message):
    clean = message.lower()
    clean = clean.translate(str.maketrans("àâçéèêëîïôùûü"+string.punctuation, 'aaceeeeiiouuu'+' '*len(string.punctuation)))
    # clean = ''.join(' ' + char if char in emoji.UNICODE_EMOJI else char for char in clean).strip() # COMMENT BECAUSE add space before and after each emoji, useful if two (or more) emojis are written without space between them
    clean = emoji.demojize(clean)
    return clean

# Expect a command without the first '!'
def command(conv, message, source, groupID):
    cmd = message.split(None, 1)[0]
    if(cmd == "help"):
        return ("Available commands:"
                "\n\t!joke (sends a joke)"
                "\n\t!pause (stop Babot)"
                "\n\t!comeback (activate Babot)")
    elif(cmd == "pause"):
        if(conv != None):
            return '%conversations/'+conv.pause()[1:]
    elif(cmd == "comeback"):
        if(conv != None):
            return '%conversations/'+conv.wake()[1:]
    elif(cmd == "neworder"):
        return ""
    elif(cmd == "answerorder"):
        return ""
    elif(cmd == "closeorder"):
        return ""
    elif(cmd == "registerevent"):
        return ""
    elif(cmd == "unregisterevent"):
        return ""
    elif(cmd == "joke"):
        return "%jokes/"+random.choice(os.listdir(DIR_DATA+'ressources/'+"jokes"))
    else:
        return configDB['command_unknown'][0]

def IA(conv, source, groupID, message, attachments):
    if(conv != None and conv.isSleeping()):
        answer = conv.wake()
        if(answer != "" and answer[0] == '%'):
            answer = '%conversations/'+answer[1:]
        return answer, ""
    if(message[0] == "!"):
        return command(conv, message[1:], source, groupID), ""
    if(message.isupper()):
        return random.choice(configDB['full_capslock']), ""
    message = cleanMessage(message)
    for word in message.split():
        if(word in wordDB):
            answers = wordDB[word]
            answer = random.choice(answers)
            if(isinstance(answer, str)):
                if(answer != "" and answer[0] == '%'):
                    answer = '%answers/'+answer[1:]
                return answer, ""
            else:
                if(answer[0] != "" and answer[0][0] == '%'):
                    answer[0] = '%answers/'+answer[0][1:]
                return answer[0], answer[1]
    return "", ""

def msgRcv (timestamp, sender, groupID, message, attachments):
    # check only groupId for now, until indentites are accessible from dbus
    conv = next((x for x in conversations if x.number == groupID), None)
    if(message == '!comeback' or (conv != None and conv.shutup == False) or conv == None):
        if(message != ""):
            messageToSend = '['+emoji.emojize(configDB['name'][0], use_aliases=True)+'] '
            answer, reaction = IA(conv, sender, groupID, message, attachments)
            if(answer != ""):
                attachmentsToSend = []
                if(answer[0] == "%"): # attachment
                    attachmentsToSend.append(DIR_DATA+'ressources/'+answer[1:])
                else:
                    messageToSend += answer
                    messageToSend = emoji.emojize(messageToSend, use_aliases=True)
                if(groupID == []):
                    signal.sendMessage(messageToSend, attachmentsToSend, [sender])
                else:
                    signal.sendGroupMessage(messageToSend, attachmentsToSend, groupID)
            if reaction != "":
                if(groupID == []):
                    signal.sendMessageReaction(emoji.emojize(reaction, True), False, sender, timestamp, [sender])                
                else:
                    signal.sendGroupMessageReaction(emoji.emojize(reaction, True), False, sender, timestamp, groupID)
    # Delete attachments
    for a in attachments:
        os.remove(a)
    return

from pydbus import SystemBus
from gi.repository import GLib
import yaml
import random
import string
import emoji
import os
from Event import Event
from Conversation import Conversation, GroupConversation

configFile = open("config.yml")
configDB = yaml.load(configFile, Loader=yaml.FullLoader)

DIR_DATA = configDB["data_directory"][0]

wordDB = yaml.load(open(DIR_DATA+"behavior/word.yml"), Loader=yaml.FullLoader)
eventsDB = yaml.load(open(DIR_DATA+"behavior/events.yml"), Loader=yaml.FullLoader)
convDB = yaml.load(open(DIR_DATA+"behavior/conversation.yml"), Loader=yaml.FullLoader)

bus = SystemBus()
loop = GLib.MainLoop()

signal = bus.get('org.asamk.Signal')

# Create known Conversation instances
# (only for groups because https://github.com/AsamK/signal-cli/issues/195)
conversations = []
gs = signal.getGroupIds()
for g in gs:
    gc = GroupConversation(g, convDB)
    gc.setMembers(signal.getGroupMembers(g))
    conversations.append(gc)

if eventsDB != None:
    for event in eventsDB:
        e = Event(eventsDB[event], event, signal, DIR_DATA, configDB['name'][0])
        for recipient in eventsDB[event][0]['registered_recipient']:
            c = next((x for x in conversations if x.number == recipient), None)
            if(c != None):
                c.events.append(e)
                if(event.startswith("hello")):
                    c.setWakeup(e.whenDatetimes[0])
                    print("One hello event prepared")
                elif(event.startswith("good_night")):
                    c.setGoodnight(e.whenDatetimes[0])
                    print("One good night event prepared")
            else:
                print("Recipient not known by babot: "+str(recipient)+"\nBabot will continue to work anyway. No events will be triggered.")
        e.enable()

signal.onMessageReceived = msgRcv
loop.run()
