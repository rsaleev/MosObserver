from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware


from mosobserver.notifier.telegram import CONFIG


class NotAllowedUser(Exception):
    pass


class AuthMiddleware(BaseMiddleware):
    def __init__(self):
        self._users = CONFIG["telegram"]["allowed_users"]

    async def on_pre_process_message(self, msg: types.Message):
        if msg.from_user.username not in self._users:
            await msg.reply("Доступ запрещен")
