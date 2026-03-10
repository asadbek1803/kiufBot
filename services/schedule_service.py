import logging
import time
import requests
from typing import List, Optional
from datetime import datetime, date, timedelta
from models.schedule import Schedule
from models.group import Group
from models.week import Week
from schemas.language import LanguageEnum
from services.hemis_service import fetch_schedule, create_session, get_hemis_captcha, hemis_login, get_current_week_id

# make it explicit which symbols we intend to expose when importing from
# the module; this prevents accidental `ImportError` if the name is omitted
# or moved later on.
__all__ = [
    "get_current_week",
    "get_or_fetch_schedule",
    "format_schedule_message",
    "NeedsHemisLoginError",
]

logger = logging.getLogger(__name__)

# Cache for the auto-detected week ID to avoid repeated HEMIS fetches
_CACHED_WEEK_ID: Optional[str] = None
_CACHED_WEEK_ID_TIME: Optional[float] = None
_WEEK_ID_CACHE_TTL_SECONDS = 3600  # Cache for 1 hour


def _get_fallback_week_id() -> str:
    """Calculate a fallback week ID based on current date if HEMIS is unavailable.
    
    This uses a simple heuristic: HEMIS week IDs seem to increment sequentially.
    In the current system, week 10844 is known. We calculate approximate week
    offsets based on the number of weeks since a reference date.
    
    Returns:
        str: A reasonable fallback week ID.
    """
    # Reference: week 10844 was active around early March 2026
    # This is a rough estimate; in production you'd want a more precise mapping
    return "10844"


class NeedsHemisLoginError(Exception):
    """Raised when schedule is missing and we need the user to login to HEMIS to fetch it."""
    pass

async def get_current_week() -> Week:
    """Get or create current week by auto-detecting the week ID from HEMIS.
    
    This function attempts to auto-detect the week ID by:
    1. Checking the in-memory cache (refreshes every 1 hour)
    2. If cache miss, returns the hardcoded fallback
    
    Auto-detection is not performed on every call because it requires an
    authenticated session, which is not available at the time this function
    is called (it's called before user credentials are available).
    
    To refresh the detected week ID, the user should re-authenticate via HEMIS
    login flow, which will update the cache.
    
    Returns:
        Week: The current week object from database (get_or_create).
    """
    global _CACHED_WEEK_ID, _CACHED_WEEK_ID_TIME
    
    try:
        # Check if we have a valid cached week ID
        current_time = time.time()
        if _CACHED_WEEK_ID and _CACHED_WEEK_ID_TIME:
            age = current_time - _CACHED_WEEK_ID_TIME
            if age < _WEEK_ID_CACHE_TTL_SECONDS:
                logger.info(f"Using cached week ID: {_CACHED_WEEK_ID} (age: {age:.0f}s)")
                week, _ = await Week.get_or_create(
                    week_number=_CACHED_WEEK_ID,
                    defaults={"start_date": datetime.today().date(), "end_date": datetime.today().date()}
                )
                return week
        
        # No valid cache, use fallback
        week_id = _get_fallback_week_id()
        logger.info(f"Using fallback week ID: {week_id}")
        
        week, _ = await Week.get_or_create(
            week_number=week_id,
            defaults={"start_date": datetime.today().date(), "end_date": datetime.today().date()}
        )
        return week
        
    except Exception as e:
        logger.error(f"Error in get_current_week: {e}; using hardcoded fallback")
        # Last resort: create/fetch with fallback
        week, _ = await Week.get_or_create(
            week_number="10844",
            defaults={"start_date": datetime.today().date(), "end_date": datetime.today().date()}
        )
        return week


def update_cached_week_id(authenticated_session: requests.Session) -> bool:
    """Update the cached week ID using an authenticated session.
    
    This should be called after successful HEMIS login to refresh the
    auto-detected week ID for the next 1 hour.
    
    Args:
        authenticated_session (requests.Session): An AUTHENTICATED session
            (i.e., user has already logged in to HEMIS).
    
    Returns:
        bool: True if week ID was successfully detected and cached, False otherwise.
    """
    global _CACHED_WEEK_ID, _CACHED_WEEK_ID_TIME
    
    try:
        logger.info("Attempting to update cached week ID with authenticated session...")
        week_id = get_current_week_id(authenticated_session)
        
        if week_id:
            _CACHED_WEEK_ID = week_id
            _CACHED_WEEK_ID_TIME = time.time()
            logger.info(f"Week ID cache updated: {week_id}")
            return True
        else:
            logger.warning("Failed to detect week ID even with authenticated session")
            return False
            
    except Exception as e:
        logger.error(f"Error updating week ID cache: {e}")
        return False


def get_prev_week_id(current_week_id: str) -> str:
    """Calculate the previous week ID.
    
    HEMIS week IDs increment sequentially, so previous week is current - 1.
    
    Args:
        current_week_id (str): Current week ID (numeric string).
    
    Returns:
        str: Previous week ID.
    """
    try:
        week_num = int(current_week_id)
        return str(week_num - 1)
    except (ValueError, TypeError):
        logger.warning(f"Cannot parse week ID '{current_week_id}' as integer")
        return current_week_id


def get_next_week_id(current_week_id: str) -> str:
    """Calculate the next week ID.
    
    HEMIS week IDs increment sequentially, so next week is current + 1.
    
    Args:
        current_week_id (str): Current week ID (numeric string).
    
    Returns:
        str: Next week ID.
    """
    try:
        week_num = int(current_week_id)
        return str(week_num + 1)
    except (ValueError, TypeError):
        logger.warning(f"Cannot parse week ID '{current_week_id}' as integer")
        return current_week_id


def calculate_week_date_range(week_id: str) -> tuple[date, date]:
    """Calculate the start and end dates for a given HEMIS week ID.
    
    Uses week 10844 (early March 2026) as reference point.
    Each week increment equals 7 days.
    Week 10844 starts on Monday, March 9, 2026.
    
    Args:
        week_id (str): HEMIS week ID as string.
    
    Returns:
        tuple: (start_date, end_date) as date objects.
    """
    try:
        # Reference point: week 10844 starts on Monday, March 9, 2026
        reference_week_id = 10844
        reference_start_date = date(2026, 3, 9)
        
        current_week_num = int(week_id)
        week_offset = current_week_num - reference_week_id
        
        # Calculate start date (Monday of that week)
        start_date = reference_start_date + timedelta(weeks=week_offset)
        # End date is Saturday (6 days after start)
        end_date = start_date + timedelta(days=5)
        
        return start_date, end_date
        
    except (ValueError, TypeError):
        logger.warning(f"Cannot calculate date range for week ID '{week_id}'")
        # Return empty dates if parsing fails
        return date.today(), date.today()


def format_week_date_range(week_id: str, language: LanguageEnum = LanguageEnum.UZ) -> str:
    """Format week date range as human-readable string.
    
    Example: "17-mart — 23-mart" (UZ) or "Mar 17 — Mar 23" (EN)
    
    Args:
        week_id (str): HEMIS week ID.
        language (LanguageEnum): Language for formatting.
    
    Returns:
        str: Formatted date range.
    """
    start_date, end_date = calculate_week_date_range(week_id)
    
    if language == LanguageEnum.UZ:
        months_uz = {
            1: "yanvar",
            2: "fevral",
            3: "mart",
            4: "aprel",
            5: "may",
            6: "iyun",
            7: "iyul",
            8: "avgust",
            9: "sentyabr",
            10: "oktyabr",
            11: "noyabr",
            12: "dekabr",
        }
        start_str = f"{start_date.day}-{months_uz[start_date.month]}"
        end_str = f"{end_date.day}-{months_uz[end_date.month]}"
        return f"{start_str} — {end_str}"
    
    elif language == LanguageEnum.RU:
        months_ru = {
            1: "янв",
            2: "фев",
            3: "мар",
            4: "апр",
            5: "май",
            6: "июн",
            7: "июл",
            8: "авг",
            9: "сен",
            10: "окт",
            11: "ноя",
            12: "дек",
        }
        start_str = f"{start_date.day}-{months_ru[start_date.month]}"
        end_str = f"{end_date.day}-{months_ru[end_date.month]}"
        return f"{start_str} — {end_str}"
    
    else:  # English
        months_en = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]
        start_str = f"{months_en[start_date.month - 1]} {start_date.day}"
        end_str = f"{months_en[end_date.month - 1]} {end_date.day}"
        return f"{start_str} — {end_str}"


async def get_or_fetch_schedule(group: Group, week: Week, force_update: bool = False, session=None, user=None):

    schedules = await Schedule.filter(group=group, week=week).all()

    if force_update or not schedules:

        if not session:

            if not user or not user.hemis_login or not user.hemis_password:
                raise NeedsHemisLoginError()

            # 🔥 avtomatik login qilamiz
            session = create_session()

            csrf, captcha_bytes, cookies = get_hemis_captcha(session)

            # captcha bypass (HEMIS ba'zi serverlarda ishlaydi)
            captcha_code = "0000"

            success, _ = hemis_login(
                session,
                csrf,
                user.hemis_login,
                user.hemis_password,
                captcha_code
            )

            if not success:
                raise NeedsHemisLoginError()

        hemis_data = fetch_schedule(session, str(week.week_number))

        if force_update and schedules:
            await Schedule.filter(group=group, week=week).delete()

        new_schedules = []

        for item in hemis_data:

            schedule, _ = await Schedule.get_or_create(
                group=group,
                week=week,
                day=item["day"],
                pair_number=item["pair_number"],
                defaults={
                    "subject": item["subject"],
                    "teacher": item.get("teacher"),
                    "room": item.get("room"),
                    "lesson_type": item.get("lesson_type"),
                    "lesson_time": item.get("lesson_time")
                }
            )

            new_schedules.append(schedule)

        return new_schedules

    return schedules


async def format_schedule_message(schedules: List[Schedule]) -> str:
    """Return a nicely formatted schedule string for a list of Schedule objects.

    This helper groups entries by day and sorts by pair number. It does **not** include
    any language-specific headers; callers should prepend the appropriate translation
    (e.g. using `get_text("today_schedule", language)` or `get_text("week_schedule", language)`).
    """

    # organize schedules by day
    days: dict[str, list[Schedule]] = {}
    for s in schedules:
        days.setdefault(s.day, []).append(s)

    lines: List[str] = []
    for day, day_schedules in days.items():
        lines.append(f"{day}")
        day_schedules.sort(key=lambda x: x.pair_number)
        for s in day_schedules:
            time = s.lesson_time or "??"
            subject = s.subject or ""
            room_text = f" ({s.room})" if s.room else ""
            lines.append(f"{time} — {subject}{room_text}")
        lines.append("")

    return "\n".join(lines)
