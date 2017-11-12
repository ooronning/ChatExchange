import asyncio
import datetime
import getpass
import logging
import os
import random
import time

import chatexchange
from chatexchange.client import AsyncClient



logger = logging.getLogger(__name__)

email = os.environ['ChatExchangeU']
password = os.environ['ChatExchangeP']


class Filter(logging.Filter):
    last = 0

    def filter(self, record):
        # see https://stackoverflow.com/a/43052949/1114
        delta = record.relativeCreated - self.last
        record.relative = '+{0:.0f}'.format(delta)
        record.e = ''
        record.n = '\n'
        record.levelled_name = '%s/%-6s' % (record.name, record.levelname)

        self.last = record.relativeCreated
        return True


async def main():
    logging.basicConfig(format="%(e)32s %(relative)6s ms%(n)s%(levelled_name)32s %(message)s", level=logging.DEBUG)

    logger.setLevel(logging.DEBUG)
    logging.getLogger().setLevel(logging.WARN)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)
    logging.getLogger('chatexchange').setLevel(logging.DEBUG)

    for handler in logging.getLogger().handlers:
        handler.addFilter(Filter())

    with AsyncClient('sqlite:///./.ChatExchange.sqlite.so', auth=(email, password)) as chat:
        sand_box, char_coal, py_thon, java_script = await asyncio.gather(
            chat.se.room(1), chat.se.room(11540), chat.so.room(6), chat.so.room(17))

        logger.debug("char_coal == %r", char_coal)
        logger.debug("py_thon == %r", py_thon)
        logger.debug("java_script == %r", java_script)
        logger.debug("sand_box == %r", sand_box)

        async for message in py_thon.old_messages():
           pass
        async for message in char_coal.old_messages():
           pass
        async for message in sand_box.old_messages():
           pass
        async for message in java_script.old_messages():
           pass 


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
