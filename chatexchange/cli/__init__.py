import importlib


async def main(subcommand, *a):
    command_module = importlib.import_module(subcommand, '.')
    return await command_module.main()
