import logging
from datetime import date, timedelta

from loader import bot
from models.user import User
from models.week import Week
from models.schedule import Schedule
from schemas.language import LanguageEnum
from services.schedule_service import get_current_week, format_schedule_message
from utils.i18n import get_text

logger = logging.getLogger(__name__)

# Kunlar tartibi (HEMIS dan keladigan o'zbek nomlari asosida)
WEEKDAY_ORDER = [
    "Dushanba",
    "Seshanba",
    "Chorshanba",
    "Payshanba",
    "Juma"
]

# Python date.weekday() → HEMIS kun nomi
WEEKDAY_MAP = {
    0: "Dushanba",
    1: "Seshanba",
    2: "Chorshanba",
    3: "Payshanba",
    4: "Juma",
    5: None, # Shanba kuni dam olish kuni
    6: None,  # Yakshanba — dam olish kuni
}


def _get_tomorrow_day_name() -> str | None:
    """Ertangi kun nomini qaytaradi. Yakshanba bo'lsa None."""
    tomorrow = date.today() + timedelta(days=1)
    return WEEKDAY_MAP.get(tomorrow.weekday())


async def send_daily_reminders() -> None:
    """reminder_enabled=True bo'lgan barcha foydalanuvchilarga
    ertangi dars jadvalini yuboradi.

    Har kuni soat 20:00 da chaqirilishi kerak.
    """
    tomorrow_name = _get_tomorrow_day_name()

    if tomorrow_name is None:
        logger.info("Ertaga dam olish kuni — eslatma yuborilmaydi.")
        return

    try:
        week = await get_current_week()
    except Exception as e:
        logger.error(f"Haftani olishda xatolik: {e}")
        return

    users = await User.filter(
        reminder_enabled=True
    ).prefetch_related("group").all()

    if not users:
        logger.info("Eslatma yoqilgan foydalanuvchi topilmadi.")
        return

    sent = 0
    failed = 0

    for user in users:
        try:
            await _send_reminder_to_user(user, week, tomorrow_name)
            sent += 1
        except Exception as e:
            logger.warning(
                f"Foydalanuvchi {user.telegram_id} ga eslatma yuborishda xatolik: {e}"
            )
            failed += 1

    logger.info(f"Eslatmalar yuborildi: {sent} ta. Xatolik: {failed} ta.")


async def _send_reminder_to_user(user, week, tomorrow_name: str) -> None:
    """Bitta foydalanuvchiga ertangi dars jadvalini yuboradi."""
    language = getattr(user, "language", LanguageEnum.UZ)

    if not user.group:
        return

    schedules = await Schedule.filter(
        group=user.group,
        week=week,
        day=tomorrow_name
    ).order_by("pair_number").all()

    if not schedules:
        # Ertaga dars yo'q — xabar yubormaslik yoki yuborish?
        # Hozircha yubormaymiz (spam bo'lmasligi uchun)
        return

    schedule_text = await format_schedule_message(schedules)

    text = (
        f"🔔 <b>{get_text('reminder_title', language)}</b>\n\n"
        f"📅 <b>{tomorrow_name}</b>\n\n"
        f"{schedule_text}"
    )

    await bot.send_message(
        chat_id=user.telegram_id,
        text=text,
        parse_mode="HTML"
    )