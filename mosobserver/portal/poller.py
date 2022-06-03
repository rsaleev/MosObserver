from typing import List
from datetime import datetime
import asyncio

import os
import json

from pathlib import Path

from datetime import timedelta, date

from tortoise.exceptions import IntegrityError
from tortoise.expressions import Q, F

from mosobserver.database.models.portal import Organization
from mosobserver.portal.client import Client
from mosobserver.portal.models.documents import DocumentItem


class PortalPoller:
    @classmethod
    async def init(cls):
        filepath = f"{Path(os.getcwd()).absolute()}/organizations.json"
        file = open(filepath)
        data = json.loads(file.read())
        file.close()
        for org in data["organizations"]:
            try:
                await Organization.create(guid=org["id"], title=org["title"])
            except IntegrityError:
                continue

    @classmethod
    async def fetch(cls, org: Organization) -> List[DocumentItem] | list:
        output = []
        try:
            docs = await Client.fetch_documents(int(org.guid))
        except:
            return output
        else:
            if items := docs.items:
                output.extend(items)
            org.checked = datetime.now()
            await org.save()
            return output

    @classmethod
    async def check_all(cls):
        organizations: List[Organization] = await Organization.all()
        output = []
        for org in organizations:
            items: List[DocumentItem] = await cls.fetch(org)
            if org.checked is None:
                output.extend(
                    [
                        (org, item)
                        for item in items
                        if item.date_published >= (datetime.now() - timedelta(days=3))
                    ]
                )
            else:
                output.extend(
                    [
                        (org, item)
                        for item in items
                        if item.date_published.day >= org.checked.day
                    ]
                )
        return output

    @classmethod
    async def check_date(cls, date: date):
        organizations: List[Organization] = await Organization.all()
        output = []
        for org in organizations:
            items: List[DocumentItem] = await cls.fetch(org)
            output.extend(
                [(org, item) for item in items if item.date_published.date() >= date]
            )
        return output

    @classmethod
    async def check_delta(cls, delta: int):
        organizations: List[Organization] = await Organization.all()
        output = []
        for org in organizations:
            items: List[DocumentItem] = await cls.fetch(org)
            output.extend(
                [
                    (org, item)
                    for item in items
                    if item.date_published.date()
                    >= (datetime.now() - timedelta(days=delta)).date()
                ]
            )
        return output
