import asyncio
import datetime
import getpass
import logging
import os
import time

import coloredlogs

import chatexchange
from chatexchange.client import AsyncClient



logger = logging.getLogger(__name__)

email = os.environ['ChatExchangeU']
password = os.environ['ChatExchangeP']


async def main():
    coloredlogs.install(fmt="%(name)s %(levelname)s %(message)s", level=logging.DEBUG)
    logging.getLogger().setLevel(logging.WARN)
    logger.setLevel(logging.DEBUG)
    logging.getLogger('sqlalchemy').setLevel(logging.WARN)
    logging.getLogger('chatexchange').setLevel(logging.DEBUG)
    logging.getLogger('aiohttp.client').setLevel(logging.DEBUG)

    with AsyncClient('sqlite:///./.ChatExchange.sqlite.so', auth=(email, password)) as chat:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO) # enable here to skip logging seed data

        sand_box, char_coal = await asyncio.gather(chat.se.room(1), chat.se.room(11540))

        logger.debug("sand_box == %r", sand_box)
        logger.debug("char_coal == %r", char_coal)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
