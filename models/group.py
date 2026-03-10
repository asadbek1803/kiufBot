from tortoise.models import Model
from tortoise import fields


class Group(Model):
    """Student group"""

    id = fields.IntField(pk=True)

    name = fields.CharField(max_length=50, unique=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "groups"

    def __str__(self):
        return self.name