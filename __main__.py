import getpass
import logging
import os
import time

import coloredlogs
import requests

from chatexchange.parser import TranscriptPage


email = os.environ['ChatExchangeU']
password = os.environ['ChatExchangeP']


def main():
    coloredlogs.install(fmt="%(name)s %(levelname)s %(message)s", level=logging.DEBUG)
    logging.getLogger('sqlalchemy').setLevel(logging.DEBUG)
    logging.getLogger('requests').setLevel(logging.DEBUG)
    host = 'https://chat.stackexchange.com'

    next_url = host + '/transcript/11540/0-25'
    while next_url:
        data = TranscriptPage(requests.get(next_url))
        previous_day_url = data.previous_day_url or data.first_day_url
        if previous_day_url:
            next_url = host + previous_day_url + '/0-24'
        else:
            next_url = None

        print(data)

        time.sleep(1)


if __name__ == '__main__':
    main()
