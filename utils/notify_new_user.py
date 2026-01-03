"""Utility for notifying admins about new users"""

import logging
from datetime import datetime
from aiogram import Bot
from data.config import ADMINS


async def notify_admins_new_user(bot: Bot, user_data: dict):
    """
    Send notification to all admins when a new user joins
    
    Args:
        bot: Bot instance
        user_data: Dictionary with user information
            - telegram_id
            - full_name
            - username
            - phone_number (optional)
            - created_at
    """
    try:
        # Format user data beautifully
        tg_id = user_data.get('telegram_id', 'N/A')
        full_name = user_data.get('full_name', 'N/A')
        username = user_data.get('username', 'N/A')
        phone_num = user_data.get('phone_number', 'N/A')
        created_at = user_data.get('created_at', datetime.now())
        
        # Format datetime
        if isinstance(created_at, datetime):
            time_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_str = str(created_at)
        
        # Format username
        username_display = f"@{username}" if username and username != 'N/A' else "❌ Yo'q"
        
        # Format phone number
        phone_display = phone_num if phone_num and phone_num != 'N/A' else "❌ Yo'q"
        
        # Create beautiful notification message
        message = f"""
🆕 <b>YANGI FOYDALANUVCHI QO'SHILDI</b>

━━━━━━━━━━━━━━━━━━━━
👤 <b>To'liq ism:</b> {full_name}
🆔 <b>Telegram ID:</b> <code>{tg_id}</code>
📱 <b>Telefon raqam:</b> {phone_display}
👤 <b>Username:</b> {username_display}
🕐 <b>Qo'shilgan vaqt:</b> {time_str}
━━━━━━━━━━━━━━━━━━━━
"""
        
        # Send to all admins
        for admin_id in ADMINS:
            try:
                await bot.send_message(
                    chat_id=int(admin_id),
                    text=message,
                    parse_mode="HTML"
                )
            except Exception as err:
                logging.error(f"Failed to send notification to admin {admin_id}: {err}")
                
    except Exception as err:
        logging.exception(f"Error in notify_admins_new_user: {err}")

