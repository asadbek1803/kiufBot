from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


inline_keyboard = [[
    InlineKeyboardButton(text="✅ Yes", callback_data='yes'),
    InlineKeyboardButton(text="❌ No", callback_data='no')
]]
are_you_sure_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_admin_menu_markup():
    """Admin panel menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="👥 Barcha foydalanuvchilar", callback_data='admin_allusers'),
            InlineKeyboardButton(text="📊 Statistika", callback_data='admin_stats')
        ],
        [
            InlineKeyboardButton(text="📢 Reklama yuborish", callback_data='admin_reklama'),
            InlineKeyboardButton(text="📥 Excel export", callback_data='admin_export')
        ],
        [
            InlineKeyboardButton(text="💾 Backup bazasi", callback_data='admin_backup'),
            InlineKeyboardButton(text="🗑️ Bazani tozalash", callback_data='admin_cleandb')
        ],
        [
            InlineKeyboardButton(text="👤 Adminlarni boshqarish", callback_data='admin_manage')
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_manage_markup():
    """Admin management menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="📋 Adminlar ro'yxati", callback_data='admin_list'),
        ],
        [
            InlineKeyboardButton(text="➕ Admin qo'shish", callback_data='admin_add'),
            InlineKeyboardButton(text="➖ Admin o'chirish", callback_data='admin_remove')
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data='admin_back')
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_reply_user_markup(user_id: int):
    """Get reply button for user feedback"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="📩 Javob berish",
                callback_data=f"reply_user_{user_id}"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)