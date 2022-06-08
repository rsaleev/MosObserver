from typing import Awaitable, List

import os
import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
import aiogram.utils.markdown as fmt
from tortoise.expressions import Q, F
from dateutil import parser as dp

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
    async def start_handler(cls, msg: types.Message):
        await msg.answer(
            f"Бот запущен",
            parse_mode=types.ParseMode.HTML,
        )
        cls.chats.append(msg.chat.id)

    @classmethod
    async def help_handler(cls, msg: types.Message):
        output = "\n".join([" - ".join(cmd) for cmd in cls.commands])
        await msg.answer(f"Список команд:\n{output}")

    @classmethod
    async def orglist_handler(cls, msg: types.Message):
        orgs = await Organization.all()
        output = "\n".join([f"{org.id}.{org.title} ({org.guid})" for org in orgs])
        if len(output) >= 4096:
            shorten, leftovers = cls.shorten_msg(output)
            await msg.answer(f"{shorten}")
            await msg.answer(f"{leftovers}")
        else:
            await msg.answer(f"{output}")

    @classmethod
    async def check_handler(cls, msg: types.Message):
        await msg.answer("Начата проверка")
        output = await PortalPoller.check_all()
        for org, item in output:
            try:
                await msg.answer(
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
                await asyncio.sleep(1)
            except:
                await asyncio.sleep(1)
                continue
        await msg.answer("Проверка закончена")

    @classmethod
    async def delta_handler(cls, msg: types.Message):
        args = msg.get_args()
        if not args:
            await msg.answer(
                f"Неверная команада.Требуется ввести интервал (кол-во дней)"
            )
        else:
            delta = int(args)
            await msg.answer(f"Начата проверка за {delta} дней")

            output = await PortalPoller.check_delta(delta)
            for org, item in output:
                try:
                    await msg.answer(
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

                    await asyncio.sleep(1)
                except:
                    await asyncio.sleep(1)
                    continue

            await msg.answer("Проверка закончена")

    @classmethod
    async def date_handler(cls, msg: types.Message):
        args = msg.get_args()
        if not args:
            await msg.answer(
                f"Неверная команада.Требуется ввести интервал (кол-во дней)"
            )
        else:
            date = dp.parse(args)
            await msg.answer(f"Начата проверка c даты {date.strftime('%d.%m.%Y')}")
            output = await PortalPoller.check_date(date.date())
            for org, item in output:
                try:
                    await msg.answer(
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
                    await asyncio.sleep(1)
                except:
                    await asyncio.sleep(1)
                    continue
            await msg.answer("Проверка закончена")

    @classmethod
    async def init(cls):
        cls.disp.register_message_handler(
            cls.start_handler, commands=["start"], regexp=r"^/start$"
        )
        cls.disp.register_message_handler(
            cls.help_handler, commands=["help"], regexp=r"^/help$"
        )
        cls.disp.register_message_handler(
            cls.orglist_handler, commands=["orglist"], regexp=r"^/orglist$"
        )
        cls.disp.register_message_handler(
            cls.check_handler, commands=["check"], regexp=r"^/check$"
        )
        cls.disp.register_message_handler(
            cls.delta_handler, commands=["delta"], regexp=r"^/delta\s\d{1,2}$"
        )
        cls.disp.register_message_handler(
            cls.date_handler,
            commands=["date"],
            regexp=r"^/date\s\d{1,2}.\d{1,2}.\d{2,4}$",
        )

    @classmethod
    async def stop(cls):
        await cls.bot.close()

    @classmethod
    async def start(cls):
        await cls.init()
        await cls.disp.start_polling(relax=1)
