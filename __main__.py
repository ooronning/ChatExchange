import datetime
import getpass
import logging
import os
import time

import coloredlogs

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

    client = Client('sqlite:///./.ChatExchange.sqlite.so', auth=(email, password))

    sand_box = client.se.room(1)
    trash_can = client.se.room(1701)
    char_coal = client.se.room(11540)


if __name__ == '__main__':
    main()
