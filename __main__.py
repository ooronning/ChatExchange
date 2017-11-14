import asyncio
import datetime
import getpass
import itertools
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
        record.levelled_name = '%s/%-5s' % (record.name, record.levelname)

        self.last = record.relativeCreated
        return True


async def main():
    logging.basicConfig(format="%(e)32s %(relative)6s ms%(n)s%(levelled_name)32s %(message)s", level=logging.DEBUG)

    logger.setLevel(logging.DEBUG)
    logging.getLogger().setLevel(logging.WARN)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('chatexchange').setLevel(logging.DEBUG)

    for handler in logging.getLogger().handlers:
        handler.addFilter(Filter())

    with AsyncClient('sqlite:///./.ChatExchange.sqlite.so', auth=(email, password)) as chat:
        for room in await asyncio.gather(
                chat.mse.room(89), chat.se.room(11540), chat.so.room(6)):
            async for message in room.old_messages():
                pass

            await report_most_replied(chat, room.server, room)


async def report_most_replied(chat, server, room):
    with chat.sql_session() as sql:
        most_replied_to_ids = [id for (id,) in itertools.islice(sql.execute('''
                select
                    message.parent_message_id as message_id
                from
                    Message message
                    left join Room room on message.room_meta_id = room.meta_id
                    left join Server server on message.server_meta_id = server.meta_id
                    left join Message parent on message.parent_message_id = parent.message_id and message.server_meta_id = parent.server_meta_id
                where
                    server.meta_id = :server_meta_id
                    and room.room_id = :room_id
                group by
                    message.parent_message_id
                order by
                    count(message.parent_message_id) desc
        ''', {'server_meta_id': room.server_meta_id, 'room_id': room.room_id}), 4)]

    print("Most replied-to messages in room #%s: %s:" % (room.room_id, room.name))
    for message_id in most_replied_to_ids:
        message = await server.message(message_id)
        replies = await message.replies()
        print("%s replies (%s)" % (len(replies), ", ".join("%s by %s" % (m.message_id, m.owner.name) for m in replies)))
        print("https://chat.stackoverflow.com/transcript/messages/%s" % (message.message_id))




if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
