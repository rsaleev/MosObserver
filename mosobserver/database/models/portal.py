from tortoise.models import Model
from tortoise.fields import (
    IntField,
    CharField,
    DatetimeField,
    TextField,
    ForeignKeyField,
)


class Organization(Model):

    id = IntField(pk=True)
    title = CharField(max_length=255, unique=True)
    guid = CharField(max_length=255, unique=True)
    checked = DatetimeField(default=None, null=True)

    class Meta:
        app = "observer"


class Documents(Model):

    id = IntField(pk=True)
    title = TextField()
    created = DatetimeField()
    updated = DatetimeField()
    published = DatetimeField()
    organization = ForeignKeyField("observer.Organization", related_name="documents")

    class Meta:
        app = "observer"


