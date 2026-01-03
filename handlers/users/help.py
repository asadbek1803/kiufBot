from aiogram import Router, types
from aiogram.filters.command import Command
from config.models.user import User
from config.schemas.language import LanguageEnum
from config.utils.i18n import get_text

router = Router()


@router.message(Command('help'))
async def bot_help(message: types.Message):
    # Get user language
    user = await User.get_or_none(telegram_id=message.from_user.id)
    language = user.language if user else LanguageEnum.UZ
    
    # Help texts in different languages
    help_texts = {
        LanguageEnum.UZ: "Buyruqlar:\n/start - Botni ishga tushirish\n/help - Yordam",
        LanguageEnum.EN: "Commands:\n/start - Start the bot\n/help - Help",
        LanguageEnum.RU: "Команды:\n/start - Запустить бота\n/help - Помощь",
    }
    
    await message.answer(text=help_texts.get(language, help_texts[LanguageEnum.EN]))
