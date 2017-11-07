#!/usr/bin/env python
import getpass
import logging
import os
import time

import coloredlogs

import chatexchange
from chatexchange.events import MessageEdited


coloredlogs.install(fmt="%(name)s %(levelname)s %(message)s", level=logging.DEBUG)
logging.getLogger('sqlalchemy').setLevel(logging.DEBUG)

email = os.environ['ChatExchangeU']
password = os.environ['ChatExchangeP']

client = chatexchange.Client('stackexchange.com', email, password)

me = client.get_me()
sandbox = client.get_room(1)
my_message = None

for message in sandbox.old_messages():
    print(message.owner.name, message.content)
    time.sleep(0.25)
