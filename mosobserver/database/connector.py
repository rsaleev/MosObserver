import os
from pathlib import Path
from tortoise import Tortoise


class DBConnector:
    @staticmethod
    async def connect():
        await Tortoise.init(
            db_url=f"sqlite://{Path(os.getcwd()).absolute()}/mosobserver.db",
            modules={"observer": ["mosobserver.database.models"]},
            timezone="Europe/Moscow",
        )
        await Tortoise.generate_schemas()

    @staticmethod
    async def disconnect():
        await Tortoise.close_connections()
