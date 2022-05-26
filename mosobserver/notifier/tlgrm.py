from typing import Awaitable, List

import os
import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
import aiogram.utils.markdown as fmt
from tortoise.expressions import Q, F

from mosobserver.portal.models.documents import DocumentItem
from mosobserver.database.models.portal import Organization
from mosobserver.portal.poller import PortalPoller


class TelegramBotNotifier:

    bot = Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])
    disp = Dispatcher(bot)

    chats = []

    commands = [
        ("/check", "Запуск проверки обновлений"),
        ("/orgs", "Получить список КНО"),
        ("/check <id>", "Запуск проверки обновлений по ID КНО"),
    ]

    @classmethod
    def shorten_msg(cls, output: str):
        shorten = []
        leftovers = []
        splitted = output.split(sep="\n")
        for sp in splitted:
            while len("\n".join(shorten)) < 4000:
                shorten.append(sp)
            leftovers.append(sp)
        return "\n".join(shorten), "\n".join(leftovers)

    @classmethod
    async def start_handler(cls, event: types.Message):
        await event.answer(
            f"Бот запущен",
            parse_mode=types.ParseMode.HTML,
        )
        cls.chats.append(event.chat.id)

    @classmethod
    async def help_handler(cls, event: types.Message):
        output = "\n".join([" - ".join(cmd) for cmd in cls.commands])
        await event.answer(f"Список команд:\n{output}")

    @classmethod
    async def orglist_handler(cls, event: types.Message):
        orgs = await Organization.all()
        output = "\n".join([f"{org.id}.{org.title} ({org.guid})" for org in orgs])
        if len(output) >= 4096:
            shorten, leftovers = cls.shorten_msg(output)
            await event.answer(f"{shorten}")
            await event.answer(f"{leftovers}")
        else:
            await event.answer(f"{output}")

    @classmethod
    async def check_handler(cls, event: types.Message):
        await event.answer("Начата проверка")
        organizations: List[Organization] = await Organization.all()
        for org in organizations:
            items: List[DocumentItem] = await PortalPoller.check_single(org)
            output = []
            if org.checked is None:
                output.extend(
                    [
                        item
                        for item in items
                        if item.date_published >= (datetime.now() - timedelta(days=3))
                    ]
                )
            else:
                output.extend(
                    [
                        item
                        for item in items
                        if item.date_published.day >= org.checked.day
                    ]
                )
            for item in output:
                await event.answer(
                    fmt.text(
                        fmt.text(fmt.bold("Организация: "), org.title),
                        fmt.text(
                            fmt.italic("Дата публикации: "),
                            item.date_published.strftime("%d-%m-%Y %H:%M:%S"),
                        ),
                        fmt.text("Название документа: ", item.title),
                        fmt.text(
                            "Ссылки на скачивание: ",
                            *[
                                fmt.link(title="Скачать", url=attachment.url)
                                for attachment in item.attachments
                                if attachment and attachment != ""
                            ],
                            sep="\n",
                        ),
                        sep="\n\n",
                    ),
                    parse_mode=types.ParseMode.MARKDOWN,
                )
        await event.answer("Проверка закончена")

    @classmethod
    async def init(cls):
        cls.disp.register_message_handler(cls.start_handler, commands={"start"})
        cls.disp.register_message_handler(cls.help_handler, commands={"help"})
        cls.disp.register_message_handler(cls.orglist_handler, commands={"orglist"})
        cls.disp.register_message_handler(cls.check_handler, commands={"check"})

    @classmethod
    async def stop(cls):
        await cls.bot.close()

    @classmethod
    async def start(cls):
        await cls.init()
        await cls.disp.start_polling(relax=2)
