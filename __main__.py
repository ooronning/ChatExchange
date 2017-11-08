import getpass
import logging
import os
import time

import coloredlogs
import requests

from chatexchange.parser import *


email = os.environ['ChatExchangeU']
password = os.environ['ChatExchangeP']


def main():
    coloredlogs.install(fmt="%(name)s %(levelname)s %(message)s", level=logging.DEBUG)
    logging.getLogger('sqlalchemy').setLevel(logging.DEBUG)
    logging.getLogger('requests').setLevel(logging.DEBUG)
    print(TranscriptPage(requests.get('https://chat.stackexchange.com/transcript/11540/0-24')))



if __name__ == '__main__':
    main()
