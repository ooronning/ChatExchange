import datetime

from . import models



epoch = datetime.datetime.fromtimestamp(1217514151)


def data():
    # All Chat Servers:

    se = models.Server(
        meta_id=1,
        name="Stack Exchange",
        url='https://chat.stackexchange.com',
        slug='se')
    yield se

    so = models.Server(
        meta_id=2,
        name="Stack Overflow",
        url='https://chat.stackoverflow.com',
        slug='so')
    yield so

    mse = models.Server(
        meta_id=3,
        name="Meta Stack Exchange",
        url='https://chat.meta.stackexchange.com',
        slug='mse')
    yield mse

    # Some Users:

    se_jeremy = models.User(
        meta_id=1,
        meta_updated=epoch,
        server_id=se.meta_id,
        id=1251,
        name="Jeremy Banks")
    yield se_jeremy
    so_jeremy = models.User(
        meta_id=2,
        meta_updated=epoch,
        server_id=so.meta_id,
        id=1114,
        name="Jeremy Banks")
    yield so_jeremy
    mse_jeremy = models.User(
        meta_id=3,
        meta_updated=epoch,
        server_id=mse.meta_id,
        id=134300,
        name="Jeremy Banks")
    yield mse_jeremy

    se_balpha = models.User(
        meta_id=4,
        meta_updated=epoch,
        server_id=se.meta_id,
        id=4,
        name="balpha",
        is_moderator=True)
    yield se_balpha
    so_balpha = models.User(
        meta_id=5,
        meta_updated=epoch,
        server_id=so.meta_id,
        id=115866,
        name="balpha",
        is_moderator=True)
    yield so_balpha
    mse_balpha = models.User(
        meta_id=6,
        meta_updated=epoch,
        server_id=mse.meta_id,
        id=115866,
        name="balpha",
        is_moderator=True)
    yield mse_balpha

    se_community = models.User(
        meta_id=7,
        meta_updated=epoch,
        server_id=se.meta_id,
        id=-1,
        name="Community",
        is_moderator=True)
    yield se_community
    so_community = models.User(
        meta_id=8,
        meta_updated=epoch,
        server_id=so.meta_id,
        id=-1,
        name="Community",
        is_moderator=True)
    yield so_community
    mse_community = models.User(
        meta_id=9,
        meta_updated=epoch,
        server_id=mse.meta_id,
        id=-1,
        name="Community",
        is_moderator=True)
    yield mse_community

    se_manish = models.User(
        meta_id=10,
        meta_updated=epoch,
        server_id=se.meta_id,
        id=31768,
        name="Manishearth")
    yield se_manish
    so_manish = models.User(
        meta_id=11,
        meta_updated=epoch,
        server_id=so.meta_id,
        id=1198729,
        name="Manishearth")
    yield so_manish
    mse_manish = models.User(
        meta_id=12,
        meta_updated=epoch,
        server_id=mse.meta_id,
        id=178438,
        name="Manishearth")
    yield mse_manish

    se_jeff = models.User(
        meta_id=13,
        meta_updated=epoch,
        server_id=se.meta_id,
        id=6,
        name="Jeff Atwood")
    yield se_jeff
    so_jeff = models.User(
        meta_id=14,
        meta_updated=epoch,
        server_id=so.meta_id,
        id=1,
        name="Jeff Atwood")
    yield so_jeff
    mse_jeff = models.User(
        meta_id=15,
        meta_updated=epoch,
        server_id=mse.meta_id,
        id=1,
        name="Jeff Atwood")
    yield mse_jeff

    # Some Rooms:

    se_sandbox = models.Room(
        meta_id=1,
        meta_updated=epoch,
        server_id=se.meta_id,
        id=1,
        name="Sandbox")
    yield se_sandbox
    so_sandbox = models.Room(
        meta_id=2,
        meta_updated=epoch,
        server_id=so.meta_id,
        id=1,
        name="Sandbox")
    yield so_sandbox
    mse_tavern = models.Room(
        meta_id=3,
        meta_updated=epoch,
        server_id=mse.meta_id,
        id=89,
        name="Tavern on the Meta")
    yield mse_tavern
    mse_sandbox = models.Room(
        meta_id=4,
        meta_updated=epoch,
        server_id=mse.meta_id,
        id=134300,
        name="\u202EShadow's Sandbox")
    yield mse_sandbox

    # Some Messages:
    return
    se_hello = models.Message(
        meta_id=1,
        meta_updated=epoch,
        room_id=se_sandbox.id,
        owner_user_id=se_jeremy.id,
        id=40990576,
        content="hello, world")
    yield se_hello
    so_hello = models.Message(
        meta_id=2,
        meta_updated=epoch,
        room_id=so_sandbox.id,
        owner_user_id=so_jeremy.id,
        id=39911857,
        content="hello, world")
    yield so_hello
    mse_tavern_hello = models.Message(
        meta_id=3,
        meta_updated=epoch,
        room_id=mse_sandbox.id,
        owner_user_id=mse_jeremy.id,
        id=6472666,
        content="hello, world")
    yield mse_tavern_hello
    mse_sandbox_hello = models.Message(
        meta_id=4,
        meta_updated=epoch,
        room_id=mse_sandbox.id,
        owner_user_id=mse_jeremy.id,
        id=6472649,
        content="hello, world")
    yield mse_sandbox_hello
