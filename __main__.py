import datetime
import getpass
import logging
import os
import time

import coloredlogs
import requests

from chatexchange.client import Client
from chatexchange.parser import TranscriptPage


email = os.environ['ChatExchangeU']
password = os.environ['ChatExchangeP']


def main():
    coloredlogs.install(fmt="%(name)s %(levelname)s %(message)s", level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger('sqlalchemy').setLevel(logging.DEBUG)
    logging.getLogger('requests').setLevel(logging.DEBUG)

    client = Client()

    charcoal_hq = client.se().get_room(11540)
    
    print(charcoal_hq)


if __name__ == '__main__':
    main()
