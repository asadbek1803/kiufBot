"""Language selection handlers"""

from aiogram import Router, types, F
from models.user import User
from schemas.language import LanguageEnum
from utils.i18n import get_text
from keyboards.inline.menu import get_main_menu_keyboard, get_language_keyboard, get_admission_submenu_keyboard

router = Router()


@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery):
    """Set user language"""
    await callback.answer()

    # Extract language code from callback data
    lang_code = callback.data.split("_")[1]
    language_map = {
        "uz": LanguageEnum.UZ,
        "en": LanguageEnum.EN,
        "ru": LanguageEnum.RU,
    }
    
    selected_language = language_map.get(lang_code, LanguageEnum.UZ)

    # Update user language
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    if user:
        user.language = selected_language
        await user.save(update_fields=['language'])
    else:
        # Create user if not exists
        user = await User.create(
            telegram_id=callback.from_user.id,
            full_name=callback.from_user.full_name,
            username=callback.from_user.username,
            language=selected_language
        )

    # Send confirmation and main menu
    await callback.message.edit_text(
        get_text("language_changed", selected_language) + "\n\n" + 
        get_text("welcome", selected_language),
        reply_markup=get_main_menu_keyboard(selected_language)
    )


@router.callback_query(F.data == "select_language")
async def show_language_menu(callback: types.CallbackQuery):
    """Show language selection menu"""
    await callback.answer()
    await callback.message.edit_text(
        get_text("select_language", LanguageEnum.UZ),
        reply_markup=get_language_keyboard()
    )


@router.callback_query(F.data == "back_to_admission_menu")
async def back_to_admission_menu(callback: types.CallbackQuery):
    """Return to admission submenu"""
    await callback.message.delete()
    await callback.answer()
    await callback.message.edit_text(
        get_text("admission_menu_title", LanguageEnum.UZ),
        reply_markup=get_admission_submenu_keyboard(LanguageEnum.UZ)
    )

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    """Return to main menu"""
    await callback.answer()

    user = await User.get_or_none(telegram_id=callback.from_user.id)
    language = user.language if user else LanguageEnum.UZ

    # Try to delete the current message (photo/image message)
    try:
        await callback.message.delete()
    except Exception:
        pass  # If delete fails (e.g., message is too old or already deleted), continue

    # Send new main menu message
    await callback.message.answer(
        get_text("welcome", language),
        reply_markup=get_main_menu_keyboard(language)
    )

