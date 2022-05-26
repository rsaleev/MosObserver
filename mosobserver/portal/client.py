from pydoc import doc
from typing import List
import aiohttp
from mosobserver.portal.models.documents import DocumentResponse
import json


class Client:
    ROOT_URL = "https://mos.ru"

    DOCUMENTS_URL = f"{ROOT_URL}/api/documents/v2/frontend/json/ru/documents?"

    @classmethod
    async def fetch_documents(cls, institution_id: int) -> DocumentResponse:
        filter = {"institution_id": institution_id}
        query = {
            "filter": json.dumps(filter),
            "per-page": 15,
            "sort": "-date_published",
            "expand": "attachments,categories",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                cls.DOCUMENTS_URL, params=query, allow_redirects=True
            ) as response:
                documents = DocumentResponse(**await response.json())
                for item in documents.items:
                    for attachment in item.attachments:
                        attachment.url = f"{cls.ROOT_URL}{attachment.url}"
                return documents
