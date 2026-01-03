from aiogram import Router
from aiogram.enums import ChatType

from filters import ChatTypeFilter


def setup_routers() -> Router:
    from .users import admin, start, help, language, menu
    from .errors import error_handler

    router = Router()

    # Agar kerak bo'lsa, o'z filteringizni o'rnating
    # Message handlerlar uchun chat type filter
    start.router.message.filter(ChatTypeFilter(chat_types=[ChatType.PRIVATE]))
    help.router.message.filter(ChatTypeFilter(chat_types=[ChatType.PRIVATE]))
    admin.router.message.filter(ChatTypeFilter(chat_types=[ChatType.PRIVATE]))
    
    # Callback query handlerlar uchun ham chat type filter
    language.router.callback_query.filter(ChatTypeFilter(chat_types=[ChatType.PRIVATE]))
    menu.router.callback_query.filter(ChatTypeFilter(chat_types=[ChatType.PRIVATE]))

    router.include_routers(admin.router, start.router, help.router, language.router, menu.router, error_handler.router)

    return router
