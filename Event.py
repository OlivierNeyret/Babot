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

# The Event class for Babot

from datetime import datetime, timedelta
import threading
import random
import emoji

class Event:
    def __init__(self, event, name, signal, dir_data):
        self.name = name
        self.recipients = event[0]["registered_recipient"]
        self.messages = event[1]["answers"]
        self.attachments = event[2]["attachment"]
        self.whenDatetimes = []
        for wheStr in event[3]["when"]:
            self.whenDatetimes.append(datetime.strptime(wheStr, "%H:%M:%S"))
        self.__threads = []
        self.signal = signal
        self.dir_data = dir_data

    def enable(self):
        for when in self.whenDatetimes:
            self.__enableOne(when)

    def __enableOne(self, when):
        delay = self.computeNextEvent(when)
        t = threading.Timer(delay, self.callback, args=[when])
        self.__threads.append(t)
        t.start()

    def disable(self):
        for t in self.__threads:
            t.cancel()

    def callback(self, when):
        messageToSend = "[Babot] " + random.choice(self.messages)
        messageToSend = emoji.emojize(messageToSend, use_aliases=True)
        attachmentsToSend = []
        if(self.attachments != None and self.attachments != []): # attachment
            attachmentsToSend.append(self.dir_data+'ressources/events/'+random.choice(self.attachments))
        for recipient in self.recipients:
            if(recipient[0] == "+"):
                self.signal.sendMessage(messageToSend, attachmentsToSend, [recipient])
            else:
                self.signal.sendGroupMessage(messageToSend, attachmentsToSend, recipient)
        self.__threads.remove(threading.current_thread())
        self.__enableOne(when)

    @staticmethod
    def computeNextEvent(when):
        now = datetime.now()
        addDay = 0
        if(now.time() > when.time()):
            addDay = 1
        nowAfter = now + timedelta(days=addDay)
        nowAfter = nowAfter.replace(hour=when.hour, minute=when.minute, second=when.second, microsecond=when.microsecond)
        delay = (nowAfter - now).total_seconds()
        return delay
