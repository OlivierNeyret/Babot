# Babot - a Signal Messenger bot
Babot is a chatbot for Signal Messenger, designed to be interfaced with [signal-cli](https://github.com/AsamK/signal-cli/ "signal-cli's github") and inspired by [python-signal-cli](https://github.com/mh-g/python-signal-cli "python-signal-cli's github").

## Dependencies
### signal-cli
Signal-cli must be installed, configured and started as a system D-Bus service (see [signal-cli wiki](https://github.com/AsamK/signal-cli/wiki "signal-cli wiki")).

### Python
Python 3 is needed, with the following packages:
- GLib
- pydbus
- yaml
- emoji

### Data
Babot must be use with [Babot-data](https://github.com/OlivierNeyret/Babot-data "Babot data"). It contains every configuration files (in yaml) and images/sounds.

Babot-data directory must be indicated in *config.yml*, in *data_directory*.

## Usage
Simply launch it:
```
python3 babot.py
```
and that's it! Send a message to it and you will have an answer a few seconds later!

Warning: Babot does not answer to a message sent from the same phone number as its own.

# Behavior
## Message analyzing
Babot is notified via D-Bus when a new message arrives: msgRcv function is called. Then the message is analyzed.

Babot has two different ways of analyzing a message. The first one is *command mode*, which expects a correctly formatted message. The other one is *word mode*, which parse the message to find a keyword.

### Command mode
This mode is triggered when a message starts with a '!'. Commands are added gradually, the most important is *!help* which gives a list of available commands with a short description.

### Word mode
Word mode is the default mode. First, the message is "cleaned": every characters are lowered, diacritics are converted (at least the French ones), punctuation symbols are removed and emojis are converted to plain text. Then, each word is parsed until one is find in the word/answer database (i.e. in the file *db.yml*). If a word is find Babot sends the corresponding answer. If multiple answers are available, one is picked randomly. If no word are find, Babot sends nothing.

## Events
Events can be programmed to occur once or many times a day. At given time a message or an attachment is send to registered recipients.

### Hello and goodnight events
There is two special events: hello and goodnight. Not only Babot is supposed to say "Hello!" and "Goodnight!", but it also make it sleep, as if you used *!pause* and *!comeback* commands.

# Project organization
## 2 different repositories
The Babot project is divided in two different repositories:
- This one for general behavior and basic functionalities
- [Babot-data](https://github.com/OlivierNeyret/Babot-data "Babot data") for examples of words to react to, events to triggered, jokes to tell....

This separation is intended to ease the use of Babot by others: you can clone this repository and pull when new features are available and fork Babot-data to add your own word's reactions, events... 

Typically this repository is clone on your Babot's hosting server and your Babot-data's fork is clone both on your local machine and on server. This way it is easy to add your customization to your Babot-data, and to keep Babot *kernel* up-to-date.

## Contributions
Feel free to open an issue or to submit your pull request if you are interested by the project. 


# License
Copyright (C) 2019 Olivier Neyret

Babot program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

Babot program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You can find a copy of the GNU General Public License in the LICENSE file. If not, see http://www.gnu.org/licenses/.

Babot is supposed to be interfaced with [signal-cli](https://github.com/AsamK/signal-cli/ "signal-cli's github"), which is also licensed under the GPLv3.

Babot is inspired by [python-signal-cli](https://github.com/mh-g/python-signal-cli "python-signal-cli's github"), which is under [MIT license](https://github.com/mh-g/python-signal-cli/blob/master/LICENSE "MIT's license")
