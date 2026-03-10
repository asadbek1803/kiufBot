from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.client.session.middlewares.request_logging import logger
from loader import bot
from models.user import User
from schemas.language import LanguageEnum
from utils.i18n import get_text
from keyboards.inline.menu import get_main_menu_keyboard, get_language_keyboard
from utils.notify_new_user import notify_admins_new_user

router = Router()


@router.message(CommandStart())
async def do_start(message: types.Message):
    """Start command handler with language support and user registration"""
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    phone_number = None
    
    # Try to get phone number from contact if available
    if message.contact:
        phone_number = message.contact.phone_number

    # Get or create user
    user, created = await User.get_or_create(
        telegram_id=telegram_id,
        defaults={
            "full_name": full_name,
            "username": username,
            "phone_number": phone_number,
            "language": LanguageEnum.UZ
        }
    )

    # Update user info if changed
    if not created:
        update_fields = []
        if user.full_name != full_name:
            user.full_name = full_name
            update_fields.append('full_name')
        if user.username != username:
            user.username = username
            update_fields.append('username')
        if phone_number and user.phone_number != phone_number:
            user.phone_number = phone_number
            update_fields.append('phone_number')
        if update_fields:
            await user.save(update_fields=update_fields)
    else:
        # New user - send notification to admins
        try:
            await notify_admins_new_user(bot, {
                'telegram_id': user.telegram_id,
                'full_name': user.full_name,
                'username': user.username,
                'phone_number': user.phone_number,
                'created_at': user.created_at
            })
        except Exception as e:
            logger.error(f"Failed to notify admins about new user: {e}")

    # Get user language
    language = user.language or LanguageEnum.UZ

    # Send welcome message with main menu
    await message.answer(
        get_text("welcome", language),
        reply_markup=get_main_menu_keyboard(language)
    )
