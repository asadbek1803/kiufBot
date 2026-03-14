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
                text=get_text("btn_schedule", language),
                callback_data="menu_schedule"
            ),
            InlineKeyboardButton(
                text=get_text("btn_profile", language),
                callback_data="menu_profile"
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
                url="https://t.me/asadbek_dev"
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
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_schedule_menu_keyboard(language: LanguageEnum = LanguageEnum.UZ) -> InlineKeyboardMarkup:
    """Asosiy schedule menyu — update tugmasi yo'q"""
    keyboard = [
        [InlineKeyboardButton(
            text=get_text("btn_today_schedule", language),
            callback_data="today_schedule"
        )],
        [InlineKeyboardButton(
            text=get_text("btn_week_schedule", language),
            callback_data="week_schedule"
        )],
        [InlineKeyboardButton(
            text=get_text("btn_back", language),
            callback_data="back_to_menu"
        )],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_week_pagination_keyboard(language: LanguageEnum = LanguageEnum.UZ, week_id: str = None) -> InlineKeyboardMarkup:
    """Haftalik jadval — pagination + update tugmasi bor"""
    from services.schedule_service import get_prev_week_id, get_next_week_id, format_week_date_range

    keyboard = []

    if week_id:
        prev_week = get_prev_week_id(week_id)
        next_week = get_next_week_id(week_id)
        prev_date_range = format_week_date_range(prev_week, language)
        next_date_range = format_week_date_range(next_week, language)

        keyboard.append([
            InlineKeyboardButton(
                text=f"⬅️ {prev_date_range}",
                callback_data=f"select_week:{prev_week}"
            ),
            InlineKeyboardButton(
                text=f"{next_date_range} ➡️",
                callback_data=f"select_week:{next_week}"
            ),
        ])

        # ✅ week_id ni callback data ga qo'shamiz
        keyboard.append([
            InlineKeyboardButton(
                text=get_text("btn_update_schedule", language),
                callback_data=f"update_schedule:{week_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text=get_text("btn_back", language),
            callback_data="menu_schedule"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.i18n import get_text


def get_profile_menu_keyboard(language, user=None):
    buttons: list[list[InlineKeyboardButton]] = []

    hemis_connected = user and getattr(user, "hemis_login", None)

    # --- HEMIS tugmasi ---
    if hemis_connected:
        buttons.append([
            InlineKeyboardButton(
                text=get_text("btn_disconnect_hemis", language),
                callback_data="disconnect_hemis"
            )
        ])

        # --- Eslatma tugmasi — FAQAT HEMIS ulangan bo'lsa ko'rinadi ---
        reminder_enabled = getattr(user, "reminder_enabled", False)
        buttons.append([
            InlineKeyboardButton(
                text=get_text("btn_reminder_disable" if reminder_enabled else "btn_reminder_enable", language),
                callback_data="reminder_disable" if reminder_enabled else "reminder_enable"
            )
        ])

    else:
        buttons.append([
            InlineKeyboardButton(
                text=get_text("btn_connect_hemis", language),
                callback_data="connect_hemis"
            )
        ])

    # --- Orqaga ---
    buttons.append([
        InlineKeyboardButton(
            text=get_text("btn_back", language),
            callback_data="back_to_menu"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_to_menu_keyboard(language):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=get_text("btn_back", language),
            callback_data="back_to_menu"
        )
    ]])