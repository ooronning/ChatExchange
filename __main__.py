import getpass
import logging
import os
import time

import coloredlogs
import requests

import chatexchange.parser


email = os.environ['ChatExchangeU']
password = os.environ['ChatExchangeP']


def main():
    coloredlogs.install(fmt="%(name)s %(levelname)s %(message)s", level=logging.DEBUG)
    logging.getLogger('sqlalchemy').setLevel(logging.DEBUG)
    logging.getLogger('requests').setLevel(logging.DEBUG)
    html = requests.get('https://chat.stackexchange.com/transcript/11540/0-24').text
    page = chatexchange.parser.TranscriptPage(html)
    print(page)


if __name__ == '__main__':
    main()
