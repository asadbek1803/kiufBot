"""Menu handlers for university information"""

import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from loader import bot
from models.user import User
from schemas.language import LanguageEnum
from utils.i18n import get_text
from keyboards.inline.menu import (
    get_main_menu_keyboard,
    get_back_to_menu_keyboard,
    get_admission_submenu_keyboard,
    get_back_to_admission_menu_keyboard,
)
from keyboards.inline.buttons import get_reply_user_markup
from states.test import UserState
from data.config import ADMINS

router = Router()

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Yordamchi funksiyalar
# ---------------------------------------------------------------------------

async def _get_user_lang(telegram_id: int) -> LanguageEnum:
    """Foydalanuvchi tilini qaytaradi, topilmasa UZ."""
    user = await User.get_or_none(telegram_id=telegram_id)
    return user.language if user else LanguageEnum.UZ


async def _safe_delete(message: types.Message) -> None:
    """Xabarni xatosiz o'chiradi (allaqachon o'chirilgan bo'lsa e'tibor bermaydi)."""
    try:
        await message.delete()
    except Exception:
        pass


async def _edit_or_replace_text(
    message: types.Message,
    text: str,
    reply_markup,
) -> types.Message:
    """Agar xabar matn bo'lsa — edit qiladi.
    Agar rasm/media bo'lsa — uni o'chirib yangi matn xabar yuboradi.
    Qaytarilgan xabar — joriy aktiv xabar.
    """
    if message.text:
        try:
            return await message.edit_text(
                text,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )
        except Exception:
            pass

    # Media xabar yoki edit ishlamadi — eskisini o'chirib yangi yuboramiz
    await _safe_delete(message)
    return await message.answer(
        text,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


async def _replace_with_photo(
    message: types.Message,
    photo: str,
    caption: str,
    reply_markup,
) -> types.Message:
    """Joriy xabarni o'chirib rasm yuboradi."""
    await _safe_delete(message)
    return await message.answer_photo(
        photo=photo,
        caption=caption,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


# ---------------------------------------------------------------------------
# Admission submenu
# ---------------------------------------------------------------------------

@router.callback_query(F.data == "menu_admission")
async def show_admission_menu(callback: types.CallbackQuery):
    await callback.answer()
    language = await _get_user_lang(callback.from_user.id)

    await _edit_or_replace_text(
        callback.message,
        get_text("admission_menu_title", language),
        get_admission_submenu_keyboard(language),
    )


@router.callback_query(F.data == "admission_directions_quotas")
async def show_directions_quotas(callback: types.CallbackQuery):
    await callback.answer()
    language = await _get_user_lang(callback.from_user.id)

    await _replace_with_photo(
        callback.message,
        photo="https://ukiu.uz/media/qabul/photo_2025-06-13_09-58-55.jpg",
        caption=get_text("btn_directions_quotas", language),
        reply_markup=get_back_to_admission_menu_keyboard(language),
    )


@router.callback_query(F.data == "admission_deadlines")
async def show_admission_deadlines(callback: types.CallbackQuery):
    await callback.answer()
    language = await _get_user_lang(callback.from_user.id)

    await _replace_with_photo(
        callback.message,
        photo="https://ukiu.uz/media/qabul/photo_2025-06-13_09-58-40.jpg",
        caption=get_text("btn_admission_deadlines", language),
        reply_markup=get_back_to_admission_menu_keyboard(language),
    )


@router.callback_query(F.data == "admission_contract_payments")
async def show_contract_payments(callback: types.CallbackQuery):
    await callback.answer()
    language = await _get_user_lang(callback.from_user.id)

    await _replace_with_photo(
        callback.message,
        photo="https://ukiu.uz/media/qabul/photo_2025-06-13_13-11-49.jpg",
        caption=get_text("btn_contract_payments", language),
        reply_markup=get_back_to_admission_menu_keyboard(language),
    )


@router.callback_query(F.data == "admission_korean_benefit")
async def show_korean_benefit(callback: types.CallbackQuery):
    await callback.answer()
    language = await _get_user_lang(callback.from_user.id)

    await _replace_with_photo(
        callback.message,
        photo="https://ukiu.uz/media/qabul/00222221.png",
        caption=get_text("btn_korean_language_benefit", language),
        reply_markup=get_back_to_admission_menu_keyboard(language),
    )


# ---------------------------------------------------------------------------
# Oddiy matn sahifalari (edit orqali ishlaydi)
# ---------------------------------------------------------------------------

async def _show_text_page(callback: types.CallbackQuery, i18n_key: str, keyboard_fn=None):
    """Matnli sahifalar uchun umumiy yordamchi."""
    await callback.answer()
    language = await _get_user_lang(callback.from_user.id)
    markup = keyboard_fn(language) if keyboard_fn else get_back_to_menu_keyboard(language)

    await _edit_or_replace_text(
        callback.message,
        get_text(i18n_key, language),
        markup,
    )


@router.callback_query(F.data == "menu_university_info")
async def show_university_info(callback: types.CallbackQuery):
    await _show_text_page(callback, "university_info")


@router.callback_query(F.data == "menu_address")
async def show_address(callback: types.CallbackQuery):
    await _show_text_page(callback, "address_info")


@router.callback_query(F.data == "menu_faculties")
async def show_faculties(callback: types.CallbackQuery):
    await _show_text_page(callback, "faculties_info")


@router.callback_query(F.data == "menu_directions")
async def show_directions(callback: types.CallbackQuery):
    await _show_text_page(callback, "directions_info")


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------

@router.callback_query(F.data == "menu_feedback")
async def show_feedback_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    language = await _get_user_lang(callback.from_user.id)

    await _edit_or_replace_text(
        callback.message,
        get_text("feedback_menu_description", language),
        get_back_to_menu_keyboard(language),
    )
    await state.set_state(UserState.waiting_feedback)


@router.message(UserState.waiting_feedback)
async def process_feedback(message: types.Message, state: FSMContext):
    """Foydalanuvchi xabarini adminlarga yuboradi."""
    await state.clear()

    try:
        user_id = message.from_user.id
        username = message.from_user.username
        full_name = message.from_user.full_name or "N/A"
        username_display = f"@{username}" if username else "❌ Yo'q"

        info_text = (
            "💬 <b>YANGI TAKLIF/MUROJJAT</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Foydalanuvchi:</b> {full_name}\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
            f"👤 <b>Username:</b> {username_display}\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )

        # Media turini aniqlash
        _MEDIA_SENDERS = {
            "photo":     lambda m, cid, reply_id: bot.send_photo(
                             cid, m.photo[-1].file_id,
                             caption=m.caption or "", reply_to_message_id=reply_id),
            "video":     lambda m, cid, reply_id: bot.send_video(
                             cid, m.video.file_id,
                             caption=m.caption or "", reply_to_message_id=reply_id),
            "document":  lambda m, cid, reply_id: bot.send_document(
                             cid, m.document.file_id,
                             caption=m.caption or "", reply_to_message_id=reply_id),
            "audio":     lambda m, cid, reply_id: bot.send_audio(
                             cid, m.audio.file_id,
                             caption=m.caption or "", reply_to_message_id=reply_id),
            "voice":     lambda m, cid, reply_id: bot.send_voice(
                             cid, m.voice.file_id,
                             caption=m.caption or "", reply_to_message_id=reply_id),
            "animation": lambda m, cid, reply_id: bot.send_animation(
                             cid, m.animation.file_id,
                             caption=m.caption or "", reply_to_message_id=reply_id),
        }

        def _get_sender(msg: types.Message):
            for attr, sender in _MEDIA_SENDERS.items():
                if getattr(msg, attr, None):
                    return sender
            # Oddiy matn
            return lambda m, cid, reply_id: bot.send_message(
                cid, m.text or "", reply_to_message_id=reply_id)

        content_sender = _get_sender(message)

        for admin_id in ADMINS:
            try:
                info_msg = await bot.send_message(
                    chat_id=int(admin_id),
                    text=info_text,
                    parse_mode="HTML",
                    reply_markup=get_reply_user_markup(user_id),
                )
                await content_sender(message, int(admin_id), info_msg.message_id)
            except Exception as e:
                logger.error(f"Admin {admin_id} ga xabar yuborishda xatolik: {e}")

        user = await User.get_or_none(telegram_id=user_id)
        language = user.language if user else LanguageEnum.UZ

        await message.answer(
            get_text("feedback_sent", language),
            parse_mode="HTML",
        )

    except Exception as e:
        logger.exception(f"process_feedback xatoligi: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")