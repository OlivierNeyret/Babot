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

# The Conversation class for Babot

from datetime import datetime, timedelta
from Event import Event
import threading
import random

class Conversation:
    def __init__(self, number, yamlData):
        self.number = number
        self.wakeupTime = None
        self.goodnightTime = None
        self.events = []
        self.__isAwake = True
        self.threads = [None, None]
        self.shutup = False
        self.comebackAnswer = yamlData['comeback']
        self.shutupAnswer = yamlData['shutup']
        self.alreadyThereAnswer = yamlData['already_there']
        self.justAwakeAnswer = yamlData['just_awake']
        self.delayToGetAsleep = yamlData['delay_asleep'][0]

    def setWakeup(self, wakeupTime):
        if(isinstance(wakeupTime, datetime)):
            self.wakeupTime = wakeupTime
            if(self.threads[0] != None):
                self.threads[0].cancel()
            delay = Event.computeNextEvent(wakeupTime)
            t = threading.Timer(delay, self.callbackWakeup)
            self.threads[0] = t
            t.start()
        else:
            print("Conversation >> WAKEUP NOT A DATETIME")

    def setGoodnight(self, goodnightTime):
        if(isinstance(goodnightTime, datetime)):
            self.goodnightTime = goodnightTime + timedelta(minutes=self.delayToGetAsleep)
            if(self.threads[1] != None):
                self.threads[1].cancel()
            delay = Event.computeNextEvent(self.goodnightTime)
            t = threading.Timer(delay, self.callbackGoodnight)
            self.threads[1] = t
            t.start()
        else:
            print("Conversation >> GOODNIGHT NOT A DATETIME")

    def callbackWakeup(self):
        print("Conversation::callbackWakeup called")
        self.__isAwake = True
        self.enableEvents()
        delay = Event.computeNextEvent(self.wakeupTime)
        t = threading.Timer(delay, self.callbackWakeup)
        self.threads[0] = t
        t.start()
    
    def callbackGoodnight(self):
        print("Conversation::callbackGoodnight called")
        self.__isAwake = False
        self.disableEvents()
        delay = Event.computeNextEvent(self.wakeupTime)
        t = threading.Timer(delay, self.callbackGoodnight)
        self.threads[1] = t
        t.start()

    def isSleeping(self):
        return not self.__isAwake

    def pause(self):
        self.shutup = True
        self.disableEvents()
        return random.choice(self.shutupAnswer)

    def wake(self):
        if(self.shutup):
            self.shutup = False
            self.enableEvents()
            return random.choice(self.comebackAnswer)
        if(self.__isAwake):
            return random.choice(self.alreadyThereAnswer)
        else:
            self.__isAwake = True
            if(self.threads[0] != None):
                self.threads[0].cancel()
            self.enableEvents()
            return random.choice(self.justAwakeAnswer)

    def enableEvents(self):
        for e in self.events:
            if(not e.name.startswith("hello") and not e.name.startswith("good_night")):
                e.enable()

    def disableEvents(self):
        for e in self.events:
            if(not(e.name.startswith("hello") or e.name.startswith("good_night"))):
                e.disable()
    
class GroupConversation(Conversation):
    def __init__(self, number, yamlData):
        super().__init__(number, yamlData)
        self.members = []

    def setMembers(self, listMember):
        self.members = listMember

    def addMember(self, member):
        self.members.append(member)