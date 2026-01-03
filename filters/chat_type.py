from aiogram.enums import ChatType
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from typing import Union


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_types: list[ChatType]):
        self.chat_types = chat_types

    async def __call__(self, obj: Union[Message, CallbackQuery]) -> bool:
        # Message uchun chat type ni tekshirish
        if isinstance(obj, Message):
            return obj.chat.type in self.chat_types
        # CallbackQuery uchun message orqali tekshirish
        elif isinstance(obj, CallbackQuery) and obj.message:
            return obj.message.chat.type in self.chat_types
        # Agar CallbackQuery da message yo'q bo'lsa, False qaytarish
        return False
