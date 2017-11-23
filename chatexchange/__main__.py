import asyncio
import sys

from . import cli



asyncio.get_event_loop().run_until_complete(cli.main(*sys.argv[1:]))
