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
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)
    logging.getLogger('chatexchange').setLevel(logging.DEBUG)
    logging.getLogger('aiohttp.client').setLevel(logging.DEBUG)

    with AsyncClient('sqlite:///./.ChatExchange.sqlite.so', auth=(email, password)) as chat:
        
        sand_box, char_coal, py_thon, java_script = await asyncio.gather(
            chat.se.room(1), chat.se.room(11540), chat.so.room(6), chat.so.room(17))

        logger.debug("char_coal == %r", char_coal)
        logger.debug("py_thon == %r", py_thon)
        logger.debug("java_script == %r", java_script)
        logger.debug("sand_box == %r", sand_box)

        async for message in char_coal.old_messages():
            logger.info("%s: %s" % (message.owner.name, message.content_text))

        async for message in py_thon.old_messages():
            logger.info("%s: %s" % (message.owner.name, message.content_text))

        async for message in java_script.old_messages():
            logger.info("%s: %s" % (message.owner.name, message.content_text))

        async for message in sand_box.old_messages():
            logger.info("%s: %s" % (message.owner.name, message.content_text))


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
