from tortoise.models import Model
from tortoise import fields
from schemas.language import LanguageEnum


class User(Model):
    """Telegram user"""

    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(unique=True, index=True)

    username = fields.CharField(max_length=255, null=True)
    full_name = fields.CharField(max_length=255, null=True)
    phone_number = fields.CharField(max_length=20, null=True)

    language = fields.CharEnumField(LanguageEnum, default=LanguageEnum.UZ)
    reminder_enabled = fields.BooleanField(default=False)
    hemis_login = fields.CharField(max_length=100, null=True)
    hemis_password = fields.CharField(max_length=100, null=True)

    group: fields.ForeignKeyRelation["Group"] = fields.ForeignKeyField(
        "models.Group",
        related_name="users",
        null=True,
        source_field="group_id"
    )

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"

    def __str__(self):
        return f"{self.telegram_id} - {self.full_name}"