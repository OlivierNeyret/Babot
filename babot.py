#!/usr/bin/python3

# Copyright (C) 2019 Olivier Neyret
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

def initEvent(event):
    recipients = eventsDB[event][0]["registered_recipient"]
    message = random.choice(eventsDB[event][1]["answers"])
    attachment = random.choice(eventsDB[event][2]["attachment"])
    whenStr = eventsDB[event][3]
    when = datetime.strptime(whenStr, "%H:%M:%S")
    delay = computeNextEvent(when)
    threading.Timer(delay, callbackEvent, args=[recipients, message, attachment, when, event]).start()

def computeNextEvent(when):
    now = datetime.now()
    addDay = 0
    if(now.hour > when.hour or (now.hour == when.hour and now.minute > when.minute) or (now.hour == when.hour and now.minute == when.minute and now.second > when.second) or (now.hour == when.hour and now.minute == when.minute and now.second == when.second and now.microsecond > when.microsecond)):
        addDay = 1
    nowAfter = now.replace(day=now.day+addDay, hour=when.hour, minute=when.minute, second=when.second, microsecond=when.microsecond)
    delay = (nowAfter - now).total_seconds()
    return delay

def callbackEvent(recipients, message, attachment, when, event):
    messageToSend = "[Babot] " + message
    messageToSend = emoji.emojize(messageToSend)
    attachmentsToSend = []
    if(attachment != ""): # attachment
        attachmentsToSend.append(DIR_DATA+'ressources/events/'+attachment)
    for recipient in recipients:
        if(recipient[0] == "+"):
            signal.sendMessage(messageToSend, attachmentsToSend, [recipient])
        else:
            signal.sendGroupMessage(messageToSend, attachmentsToSend, recipient)
    initEvent(event)

def cleanMessage(message):
    clean = message.lower()
    clean = clean.translate(str.maketrans("àâçéèêëîïôùûü"+string.punctuation, 'aaceeeeiiouuu'+' '*len(string.punctuation)))
    # clean = ''.join(' ' + char if char in emoji.UNICODE_EMOJI else char for char in clean).strip() # COMMENT BECAUSE add space before and after each emoji, useful if two (or more) emojis are written without space between them
    clean = emoji.demojize(clean)
    return clean

# Expect a command without the first '!'
def commande(message, source, groupID):
    cmd = message.split(None, 1)[0]
    if(cmd == "help"):
        return "Available commands:\n\t!joke (sends a joke)"
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
    else: # Look for stickers
        if(cmd in stickersDB):
            stick = stickersDB[cmd]
            authorized_recipient = stick[0]["authorized_recipient"]
            if(source in authorized_recipient or groupID in authorized_recipient):
                return "%stickers/"+stick[1]
    return configDB['command_unknown'][0]

def IA(message, source, groupID):
    if(message[0] == "!"):
        return commande(message[1:], source, groupID)
    message = cleanMessage(message)
    for word in message.split():
        if(word in wordDB):
            answers = wordDB[word]
            answer = random.choice(answers)
            if(answer != "" and answer[0] == '%'):
                answer = '%answers/'+answer[1:]
            return answer
    return ""

def msgRcv (timestamp, source, groupID, message, attachments):
    # print ("== MESSAGE RECEIVE ==")
    # print (message)
    if(message != ""):
        messageToSend = '['+configDB['name'][0]+'] '
        answer = IA(message, source, groupID)
        if(answer != ""):
            attachmentsToSend = []
            if(answer[0] == "%"): # attachment
                attachmentsToSend.append(DIR_DATA+'ressources/'+answer[1:])
            else:
                messageToSend += answer
                messageToSend = emoji.emojize(messageToSend)
            if(groupID == []):
                signal.sendMessage(messageToSend, attachmentsToSend, [source])
            else:
                signal.sendGroupMessage(messageToSend, attachmentsToSend, groupID)
    # Delete attachment
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
from datetime import datetime, timedelta
import threading

configFile = open("config.yml")
configDB = yaml.load(configFile)

# DIR_DATA = "/home/signal-cli/data/"
DIR_DATA = configDB["data_directory"][0]

fileWord = open(DIR_DATA+"behavior/word.yml")
wordDB = yaml.load(fileWord)
fileStickers = open(DIR_DATA+"behavior/stickers.yml")
stickersDB = yaml.load(fileStickers)
fileEvents = open(DIR_DATA+"behavior/events.yml")
eventsDB = yaml.load(fileEvents)

for event in eventsDB:
    initEvent(event)

bus = SystemBus()
loop = GLib.MainLoop()

signal = bus.get('org.asamk.Signal')

signal.onMessageReceived = msgRcv
loop.run()
