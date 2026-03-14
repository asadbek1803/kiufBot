"""
handlers/users/profile.py fayliga QO'SHISH kerak bo'lgan
reminder callback handlerlar.

Mavjud import qatorlariga qo'shing:
    from tasks.reminder import send_daily_reminders  # ixtiyoriy, test uchun
"""

from aiogram import Router, types, F
from models.user import User
from schemas.language import LanguageEnum
from utils.i18n import get_text
from keyboards.inline.menu import get_profile_menu_keyboard

# Bu router mavjud profile router bilan birlashtiriladi
# (alohida router sifatida ro'yxatdan o'tkazish shart emas,
#  mavjud `router` obyektiga qo'shsangiz yetarli)

router = Router()

@router.callback_query(F.data == "reminder_disable")
async def disable_reminder(callback: types.CallbackQuery):
    await callback.answer()

    user = await User.get_or_none(telegram_id=callback.from_user.id)
    language = user.language if user else LanguageEnum.UZ

    if user:
        user.reminder_enabled = False
        await user.save(update_fields=["reminder_enabled"])
        # ✅ DB dan qayta o'qiymiz — yangilangan obyekt
        user = await User.get_or_none(telegram_id=callback.from_user.id)

    await callback.message.edit_text(
        get_text("reminder_disabled_text", language),
        reply_markup=get_profile_menu_keyboard(language, user),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "reminder_enable")
async def enable_reminder(callback: types.CallbackQuery):
    await callback.answer()

    user = await User.get_or_none(telegram_id=callback.from_user.id)
    language = user.language if user else LanguageEnum.UZ

    if user:
        user.reminder_enabled = True
        await user.save(update_fields=["reminder_enabled"])
        # ✅ DB dan qayta o'qiymiz
        user = await User.get_or_none(telegram_id=callback.from_user.id)

    await callback.message.edit_text(
        get_text("reminder_enabled_text", language),
        reply_markup=get_profile_menu_keyboard(language, user),
        parse_mode="HTML"
    )