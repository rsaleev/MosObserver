from typing import List
from datetime import datetime
import asyncio

import os
import json

from pathlib import Path

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
    async def check_single(cls, org: Organization) -> List[DocumentItem] | list:
        output = []
        docs = await Client.fetch_documents(int(org.guid))
        if items := docs.items:
            if org.checked:
                data = [
                    item
                    for item in items
                    if item.date_published
                    and item.date_published.timestamp() > org.checked.timestamp()
                ]
                
                
            else:
                output.extend(
                    [
                        item
                        for item in items
                        if item.date_published
                        and (datetime.now() - item.date_published).days <= 3
                    ]
                )
        org.checked = datetime.now()
        await org.save()
        return output
