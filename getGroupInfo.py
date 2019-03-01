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

# This is an helper script to know what signal-cli knows about your groups
 
from pydbus import SystemBus

bus = SystemBus()
signal = bus.get('org.asamk.Signal')

groups = signal.getGroupIds()
print("Group (Id-Name-Members):")
for g in groups:
    print("  Id=" + str(g) + " Name=" + signal.getGroupName(g))
    members = signal.getGroupMembers(g)
    print("  Members:")
    for m in members:
        print("    " + m)
