from tortoise.models import Model
from tortoise import fields
from config.schemas.language import LanguageEnum


class User(Model):
    """User model for Tortoise ORM"""
    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(unique=True, index=True)
    username = fields.CharField(max_length=255, null=True)
    full_name = fields.CharField(max_length=255, null=True)
    phone_number = fields.CharField(max_length=20, null=True)
    language = fields.CharEnumField(LanguageEnum, default=LanguageEnum.UZ)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"

    def __str__(self):
        return f"User {self.telegram_id} ({self.full_name})"

