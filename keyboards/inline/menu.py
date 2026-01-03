"""Menu keyboards for the bot"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from schemas.language import LanguageEnum
from utils.i18n import get_text


def get_main_menu_keyboard(language: LanguageEnum = LanguageEnum.UZ) -> InlineKeyboardMarkup:
    """Get main menu keyboard"""
    # Determine language code for URL
    lang_code = "uz" if language == LanguageEnum.UZ else ("en" if language == LanguageEnum.EN else "ru")
    
    keyboard = [
        [
            InlineKeyboardButton(
                text=get_text("btn_360_university", language),
                web_app=WebAppInfo(url=f"https://ukiu.uz/{lang_code}/sphere/1/")
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("btn_admission", language),
                callback_data="menu_admission"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("btn_university_info", language),
                callback_data="menu_university_info"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("btn_address", language),
                callback_data="menu_address"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("btn_faculties", language),
                callback_data="menu_faculties"
            ),
            InlineKeyboardButton(
                text=get_text("btn_directions", language),
                callback_data="menu_directions"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("btn_language", language),
                callback_data="select_language"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("btn_developer", language),
                url="https://t.me/asadbek_074"
            ),
            InlineKeyboardButton(
                text=get_text("btn_feedback", language),
                callback_data="menu_feedback"
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Get language selection keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(
                text=get_text("lang_uzbek", LanguageEnum.UZ),
                callback_data="lang_uz"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("lang_english", LanguageEnum.EN),
                callback_data="lang_en"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("lang_russian", LanguageEnum.RU),
                callback_data="lang_ru"
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)



def get_back_to_admission_menu_keyboard(language: LanguageEnum = LanguageEnum.UZ) -> InlineKeyboardMarkup:
    """Get back to admission submenu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(
                text=get_text("btn_back", language),
                callback_data="back_to_admission_menu"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
    

def get_back_to_menu_keyboard(language: LanguageEnum = LanguageEnum.UZ) -> InlineKeyboardMarkup:
    """Get back to menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(
                text=get_text("btn_back", language),
                callback_data="back_to_menu"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admission_submenu_keyboard(language: LanguageEnum = LanguageEnum.UZ) -> InlineKeyboardMarkup:
    """Get admission submenu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(
                text=get_text("btn_directions_quotas", language),
                callback_data="admission_directions_quotas"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("btn_admission_deadlines", language),
                callback_data="admission_deadlines"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("btn_contract_payments", language),
                callback_data="admission_contract_payments"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("btn_korean_language_benefit", language),
                callback_data="admission_korean_benefit"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("btn_back", language),
                callback_data="back_to_menu"
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

