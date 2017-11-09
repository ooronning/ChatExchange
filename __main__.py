import datetime
import getpass
import logging
import os
import time

import coloredlogs
import requests

from chatexchange.client import Client



email = os.environ['ChatExchangeU']
password = os.environ['ChatExchangeP']


def main():
    coloredlogs.install(fmt="%(name)s %(levelname)s %(message)s", level=logging.DEBUG)
    logging.getLogger().setLevel(logging.WARN)
    logging.getLogger('sqlalchemy').setLevel(logging.WARN)
    logging.getLogger('chatexchange').setLevel(logging.DEBUG)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logging.getLogger('requests').setLevel(logging.DEBUG)

    client = Client('sqlite:///./data.so')

    sandbox = client.se().room(1)
    charcoal_hq = client.se().room(11540)

    print("was given", charcoal_hq)


if __name__ == '__main__':
    main()
