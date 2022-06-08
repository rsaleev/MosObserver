from typing import List
import os
from pathlib import Path
import json
from datetime import datetime
import asyncio
import uvloop

from mosobserver.portal.poller import PortalPoller
from mosobserver.notifier.telegram.client import TelegramBotNotifier
from mosobserver.database.connector import DBConnector


uvloop.install()


class Application:
    @classmethod
    async def run(cls):
        await DBConnector.connect()
        await PortalPoller.init()
        await TelegramBotNotifier.start()

    @classmethod
    async def shutdown(cls):
        await DBConnector.disconnect()
        await TelegramBotNotifier.stop()


if __name__ == "__main__":
    asyncio.run(Application.run())
