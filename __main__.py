import asyncio
import datetime
import getpass
import logging
import os
import time

import coloredlogs

from chatexchange.client import Client



logger = logging.getLogger(__name__)

email = os.environ['ChatExchangeU']
password = os.environ['ChatExchangeP']


async def main():
    coloredlogs.install(fmt="%(name)s %(levelname)s %(message)s", level=logging.DEBUG)
    logging.getLogger().setLevel(logging.WARN)
    logger.setLevel(logging.DEBUG)
    logging.getLogger('sqlalchemy').setLevel(logging.WARN)
    logging.getLogger('chatexchange').setLevel(logging.DEBUG)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logging.getLogger('aiohttp.client').setLevel(logging.DEBUG)

    with Client('sqlite:///./.ChatExchange.sqlite.so', auth=(email, password)) as chat:
        sand_box_request = chat.se.room(1)
        char_coal_request = chat.se.room(11540)

        sand_box = await sand_box_request
        char_coal = await char_coal_request

        logger.debug(sand_box)
        logger.debug(char_coal)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
