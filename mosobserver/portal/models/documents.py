from typing import Optional, Union, List
from click import IntRange
from pydantic import BaseModel
from datetime import datetime


class DocumentAttachment(BaseModel):
    name: str
    url: str


class DocumentCategory(BaseModel):
    id: int
    parent_id: Optional[int]
    sort: int
    title: str


class DocumentItem(BaseModel):
    attachments: List[DocumentAttachment]
    categories: Optional[List[DocumentCategory]]
    created_at: Optional[datetime]
    date_published: datetime
    date_sign: Optional[datetime]
    expertise_date_end: Optional[datetime]
    id: int
    institution_id: int
    number: str
    source_id: Optional[int]
    status_id: Optional[int]
    text: str
    title: str
    type_id: Optional[int]
    updated_at: Optional[datetime]


class DocumentResponse(BaseModel):
    _links: dict
    _meta: dict
    items: List[DocumentItem]
