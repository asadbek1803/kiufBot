"""Menu handlers for university information"""

import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from loader import bot
from config.models.user import User
from config.schemas.language import LanguageEnum
from config.utils.i18n import get_text
from config.utils.ukiu_scraper import scraper
from config.keyboards.inline.menu import get_main_menu_keyboard, get_back_to_menu_keyboard, get_admission_submenu_keyboard, get_back_to_admission_menu_keyboard
from config.keyboards.inline.buttons import get_reply_user_markup
from states.test import UserState
from data.config import ADMINS

router = Router()


def get_lang_code(language: LanguageEnum) -> str:
    """Convert LanguageEnum to language code"""
    if language == LanguageEnum.UZ:
        return "uz"
    elif language == LanguageEnum.EN:
        return "en"
    else:
        return "ru"


@router.callback_query(F.data == "menu_admission")
async def show_admission_menu(callback: types.CallbackQuery):
    """Show admission submenu"""
    await callback.answer()
    
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    language = user.language if user else LanguageEnum.UZ
    
    await callback.message.edit_text(
        get_text("admission_menu_title", language),
        reply_markup=get_admission_submenu_keyboard(language),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admission_directions_quotas")
async def show_directions_quotas(callback: types.CallbackQuery):
    """Show directions and quotas image"""
    await callback.answer()
    
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    language = user.language if user else LanguageEnum.UZ
    
    image_url = "https://ukiu.uz/media/qabul/photo_2025-06-13_09-58-55.jpg"
    
    await callback.message.answer_photo(
        photo=image_url,
        caption=get_text("btn_directions_quotas", language),
        reply_markup=get_back_to_admission_menu_keyboard(language)
    )


@router.callback_query(F.data == "admission_deadlines")
async def show_admission_deadlines(callback: types.CallbackQuery):
    """Show admission deadlines and criteria image"""
    await callback.answer()
    
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    language = user.language if user else LanguageEnum.UZ
    
    image_url = "https://ukiu.uz/media/qabul/photo_2025-06-13_09-58-40.jpg"
    
    await callback.message.answer_photo(
        photo=image_url,
        caption=get_text("btn_admission_deadlines", language),
        reply_markup=get_back_to_admission_menu_keyboard(language)
    )


@router.callback_query(F.data == "admission_contract_payments")
async def show_contract_payments(callback: types.CallbackQuery):
    """Show contract payments and benefits image"""
    await callback.answer()
    
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    language = user.language if user else LanguageEnum.UZ
    
    image_url = "https://ukiu.uz/media/qabul/photo_2025-06-13_13-11-49.jpg"
    
    await callback.message.answer_photo(
        photo=image_url,
        caption=get_text("btn_contract_payments", language),
        reply_markup=get_back_to_admission_menu_keyboard(language)
    )


@router.callback_query(F.data == "admission_korean_benefit")
async def show_korean_benefit(callback: types.CallbackQuery):
    """Show Korean language benefit image"""
    await callback.answer()
    
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    language = user.language if user else LanguageEnum.UZ
    
    image_url = "https://ukiu.uz/media/qabul/00222221.png"
    
    await callback.message.answer_photo(
        photo=image_url,
        caption=get_text("btn_korean_language_benefit", language),
        reply_markup=get_back_to_admission_menu_keyboard(language)
    )


@router.callback_query(F.data == "menu_university_info")
async def show_university_info(callback: types.CallbackQuery):
    """Show university information"""
    await callback.answer()
    
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    language = user.language if user else LanguageEnum.UZ
    
    # Send complete university information from i18n
    text = get_text("university_info", language)
    
    # Check if message can be edited, otherwise send new message
    if callback.message.text:
        try:
            await callback.message.edit_text(
                text,
                reply_markup=get_back_to_menu_keyboard(language),
                parse_mode="HTML"
            )
        except Exception:
            await callback.message.answer(
                text,
                reply_markup=get_back_to_menu_keyboard(language),
                parse_mode="HTML"
            )
    else:
        await callback.message.answer(
            text,
            reply_markup=get_back_to_menu_keyboard(language),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "menu_address")
async def show_address(callback: types.CallbackQuery):
    """Show university address"""
    await callback.answer()
    
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    language = user.language if user else LanguageEnum.UZ
    
    # Send complete address information from i18n
    text = get_text("address_info", language)
    
    # Check if message can be edited, otherwise send new message
    if callback.message.text:
        try:
            await callback.message.edit_text(
                text,
                reply_markup=get_back_to_menu_keyboard(language),
                parse_mode="HTML"
            )
        except Exception:
            await callback.message.answer(
                text,
                reply_markup=get_back_to_menu_keyboard(language),
                parse_mode="HTML"
            )
    else:
        await callback.message.answer(
            text,
            reply_markup=get_back_to_menu_keyboard(language),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "menu_faculties")
async def show_faculties(callback: types.CallbackQuery):
    """Show faculties list"""
    await callback.answer()
    
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    language = user.language if user else LanguageEnum.UZ
    
    # Send complete faculties information from i18n
    text = get_text("faculties_info", language)
    
    # Check if message can be edited, otherwise send new message
    if callback.message.text:
        try:
            await callback.message.edit_text(
                text,
                reply_markup=get_back_to_menu_keyboard(language),
                parse_mode="HTML"
            )
        except Exception:
            await callback.message.answer(
                text,
                reply_markup=get_back_to_menu_keyboard(language),
                parse_mode="HTML"
            )
    else:
        await callback.message.answer(
            text,
            reply_markup=get_back_to_menu_keyboard(language),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "menu_directions")
async def show_directions(callback: types.CallbackQuery):
    """Show directions/specialties list"""
    await callback.answer()
    
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    language = user.language if user else LanguageEnum.UZ
    
    # Send complete directions information from i18n
    text = get_text("directions_info", language)
    
    # Check if message can be edited, otherwise send new message
    if callback.message.text:
        try:
            await callback.message.edit_text(
                text,
                reply_markup=get_back_to_menu_keyboard(language),
                parse_mode="HTML"
            )
        except Exception:
            await callback.message.answer(
                text,
                reply_markup=get_back_to_menu_keyboard(language),
                parse_mode="HTML"
            )
    else:
        await callback.message.answer(
            text,
            reply_markup=get_back_to_menu_keyboard(language),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "menu_feedback")
async def show_feedback_menu(callback: types.CallbackQuery, state: FSMContext):
    """Show feedback menu and ask for message"""
    await callback.answer()
    
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    language = user.language if user else LanguageEnum.UZ
    
    text = get_text("feedback_menu_description", language)
    
    await callback.message.edit_text(text, reply_markup=get_back_to_menu_keyboard(language), parse_mode="HTML")
    await state.set_state(UserState.waiting_feedback)


@router.message(UserState.waiting_feedback)
async def process_feedback(message: types.Message, state: FSMContext):
    """Process user feedback and forward to admins"""
    try:
        user_id = message.from_user.id
        user = await User.get_or_none(telegram_id=user_id)
        
        # Get user info
        username = message.from_user.username
        full_name = message.from_user.full_name or "N/A"
        username_display = f"@{username}" if username else "❌ Yo'q"
        
        # Create info text
        info_text = f"""
💬 <b>YANGI TAKLIF/MUROJJAT</b>

━━━━━━━━━━━━━━━━━━━━
👤 <b>Foydalanuvchi:</b> {full_name}
🆔 <b>ID:</b> <code>{user_id}</code>
👤 <b>Username:</b> {username_display}
━━━━━━━━━━━━━━━━━━━━

<b>Xabar:</b>
"""
        
        # Send message to all admins (copy instead of forward to preserve user_id)
        for admin_id in ADMINS:
            try:
                # Send info text with user_id
                full_info_text = f"{info_text}\n\n🆔 <b>User ID:</b> <code>{user_id}</code>"
                
                # Send info text first with reply button
                info_msg = await bot.send_message(
                    chat_id=int(admin_id),
                    text=full_info_text,
                    parse_mode="HTML",
                    reply_markup=get_reply_user_markup(user_id)
                )
                
                # Copy the user's message (not forward) to preserve user_id
                if message.photo:
                    await bot.send_photo(
                        chat_id=int(admin_id),
                        photo=message.photo[-1].file_id,
                        caption=message.caption or "",
                        reply_to_message_id=info_msg.message_id
                    )
                elif message.video:
                    await bot.send_video(
                        chat_id=int(admin_id),
                        video=message.video.file_id,
                        caption=message.caption or "",
                        reply_to_message_id=info_msg.message_id
                    )
                elif message.document:
                    await bot.send_document(
                        chat_id=int(admin_id),
                        document=message.document.file_id,
                        caption=message.caption or "",
                        reply_to_message_id=info_msg.message_id
                    )
                elif message.audio:
                    await bot.send_audio(
                        chat_id=int(admin_id),
                        audio=message.audio.file_id,
                        caption=message.caption or "",
                        reply_to_message_id=info_msg.message_id
                    )
                elif message.voice:
                    await bot.send_voice(
                        chat_id=int(admin_id),
                        voice=message.voice.file_id,
                        caption=message.caption or "",
                        reply_to_message_id=info_msg.message_id
                    )
                elif message.animation:
                    await bot.send_animation(
                        chat_id=int(admin_id),
                        animation=message.animation.file_id,
                        caption=message.caption or "",
                        reply_to_message_id=info_msg.message_id
                    )
                else:
                    # Text message
                    await bot.send_message(
                        chat_id=int(admin_id),
                        text=message.text or "",
                        reply_to_message_id=info_msg.message_id
                    )
                
            except Exception as e:
                logging.error(f"Failed to send feedback to admin {admin_id}: {e}")
        
        # Confirm to user
        await message.answer(
            "✅ <b>Xabaringiz yuborildi!</b>\n\n"
            "Adminlar xabaringizni ko'rib chiqib, tez orada javob berishadi.",
            parse_mode="HTML"
        )
        
        await state.clear()
        
    except Exception as e:
        logging.exception(f"Error in process_feedback: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
        await state.clear()

