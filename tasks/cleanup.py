import logging
from datetime import date
from models.schedule import Schedule
from models.week import Week
from services.schedule_service import get_current_week

logger = logging.getLogger(__name__)


async def delete_old_schedules() -> None:
    """Tugagan haftalarning jadvallarini va Week yozuvlarini o'chiradi.

    Har kuni bir marta chaqirilishi kerak (masalan, soat 03:00 da).
    Joriy haftadan oldingi barcha Week yozuvlari va ularga bog'liq
    Schedule'lar cascade tarzida o'chiriladi.

    Qoidalar:
    - Joriy hafta va undan keyingi haftalar SAQLANADI.
    - Joriy haftadan kichik week_number bo'lgan haftalar o'chiriladi.
    """
    try:
        current_week = await get_current_week()
        current_week_number = int(current_week.week_number)

        old_weeks = await Week.filter(
            week_number__lt=current_week_number
        ).all()

        if not old_weeks:
            logger.info("O'chiriladigan eski hafta topilmadi.")
            return

        deleted_schedules = 0
        deleted_weeks = 0

        for week in old_weeks:
            count = await Schedule.filter(week=week).count()
            await Schedule.filter(week=week).delete()
            deleted_schedules += count

            await week.delete()
            deleted_weeks += 1

            logger.info(
                f"Hafta {week.week_number} o'chirildi: "
                f"{count} ta jadval yozuvi."
            )

        logger.info(
            f"Cleanup tugadi: {deleted_weeks} hafta, "
            f"{deleted_schedules} jadval yozuvi o'chirildi."
        )

    except Exception as e:
        logger.error(f"Cleanup xatoligi: {e}", exc_info=True)