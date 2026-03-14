import logging
import requests
from datetime import datetime
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from loader import bot
from models.user import User
from models.week import Week
from schemas.language import LanguageEnum
from utils.i18n import get_text
from keyboards.inline.menu import (
    get_schedule_menu_keyboard,
    get_back_to_menu_keyboard,
    get_week_pagination_keyboard,
)
from services.schedule_service import (
    get_current_week,
    get_or_fetch_schedule,
    format_schedule_message,
    NeedsHemisLoginError,
    format_week_date_range,
)
from services.hemis_service import get_hemis_captcha, hemis_login, create_session
from states.test import UserState

router = Router()
logger = logging.getLogger(__name__)

UZ_DAYS = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]


# ---------------------------------------------------------------------------
# Yordamchi
# ---------------------------------------------------------------------------

def _today_uz_name() -> str:
    return UZ_DAYS[datetime.today().weekday()]


async def _build_week_text(schedules, week_id: str, language: LanguageEnum) -> str:
    date_range = format_week_date_range(week_id, language)
    text = f"{get_text('week_schedule', language)}<b>{date_range}</b>\n\n"
    if not schedules:
        text += get_text("no_classes_today", language)
    else:
        text += await format_schedule_message(schedules)
    return text


async def _build_today_text(schedules, language: LanguageEnum) -> str:
    today_name = _today_uz_name()
    today_schedules = [s for s in schedules if s.day == today_name]
    text = get_text("today_schedule", language)
    if not today_schedules:
        text += get_text("no_classes_today", language)
    else:
        text += await format_schedule_message(today_schedules)
    return text


# ---------------------------------------------------------------------------
# Schedule menu
# ---------------------------------------------------------------------------

@router.callback_query(F.data == "menu_schedule")
async def show_schedule_menu(callback: types.CallbackQuery):
    await callback.answer()
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    language = user.language if user else LanguageEnum.UZ

    await callback.message.edit_text(
        "📅 <b>" + get_text("btn_schedule", language).replace("📅 ", "") + "</b>",
        reply_markup=get_schedule_menu_keyboard(language),
        parse_mode="HTML",
    )


# ---------------------------------------------------------------------------
# Bugungi jadval
# ---------------------------------------------------------------------------

@router.callback_query(F.data == "today_schedule")
async def show_today_schedule(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user = await User.get_or_none(telegram_id=callback.from_user.id).prefetch_related("group")
    language = user.language if user else LanguageEnum.UZ

    await callback.message.edit_text(get_text("schedule_loading", language), parse_mode="HTML")
    week = await get_current_week()

    try:
        schedules = await get_or_fetch_schedule(user.group, week, user=user)
    except NeedsHemisLoginError:
        await _start_captcha_flow(
            callback.message, user, state, language,
            action_type="today",
            week_id=str(week.week_number),
        )
        return

    text = await _build_today_text(schedules, language)
    await callback.message.edit_text(
        text,
        reply_markup=get_schedule_menu_keyboard(language),
        parse_mode="HTML",
    )


# ---------------------------------------------------------------------------
# Haftalik jadval (joriy hafta)
# ---------------------------------------------------------------------------

@router.callback_query(F.data == "week_schedule")
async def show_week_schedule(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user = await User.get_or_none(telegram_id=callback.from_user.id).prefetch_related("group")
    language = user.language if user else LanguageEnum.UZ

    await callback.message.edit_text(get_text("schedule_loading", language), parse_mode="HTML")
    week = await get_current_week()
    week_id = str(week.week_number)

    try:
        schedules = await get_or_fetch_schedule(user.group, week, user=user)
    except NeedsHemisLoginError:
        await _start_captcha_flow(
            callback.message, user, state, language,
            action_type="week",
            week_id=week_id,
        )
        return

    await state.update_data(selected_week_id=week_id)
    text = await _build_week_text(schedules, week_id, language)
    await callback.message.edit_text(
        text,
        reply_markup=get_week_pagination_keyboard(language, week_id),
        parse_mode="HTML",
    )


# ---------------------------------------------------------------------------
# Pagination — boshqa hafta tanlandi
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("select_week:"))
async def select_week(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user = await User.get_or_none(telegram_id=callback.from_user.id).prefetch_related("group")
    language = user.language if user else LanguageEnum.UZ

    week_id = callback.data.split(":")[1]

    await callback.message.edit_text(get_text("schedule_loading", language), parse_mode="HTML")

    week, _ = await Week.get_or_create(
        week_number=week_id,
        defaults={
            "start_date": datetime.today().date(),
            "end_date": datetime.today().date(),
        },
    )

    try:
        schedules = await get_or_fetch_schedule(user.group, week, user=user)
    except NeedsHemisLoginError:
        # ✅ FIX: week_id ni state ga saqlaymiz, captcha flow da ishlatamiz
        await _start_captcha_flow(
            callback.message, user, state, language,
            action_type="week_select",
            week_id=week_id,
        )
        return

    await state.update_data(selected_week_id=week_id)
    text = await _build_week_text(schedules, week_id, language)
    await callback.message.edit_text(
        text,
        reply_markup=get_week_pagination_keyboard(language, week_id),
        parse_mode="HTML",
    )


# ---------------------------------------------------------------------------
# Yangilash (force update)
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("update_schedule:"))
async def update_schedule(callback: types.CallbackQuery, state: FSMContext):
    week_id = callback.data.split(":")[1]
    await callback.answer()
    user = await User.get_or_none(telegram_id=callback.from_user.id).prefetch_related("group")
    language = user.language if user else LanguageEnum.UZ

    await callback.message.edit_text(get_text("schedule_loading", language), parse_mode="HTML")

    # ✅ State da selected_week_id bo'lsa o'sha haftani, bo'lmasa joriy haftani yangilaymiz
    # data = await state.get_data()

    if week_id:
        week, _ = await Week.get_or_create(
            week_number=week_id,
            defaults={
                "start_date": datetime.today().date(),
                "end_date": datetime.today().date(),
            },
        )
    else:
        week = await get_current_week()
        week_id = str(week.week_number)

    try:
        schedules = await get_or_fetch_schedule(user.group, week, force_update=True, user=user)
    except NeedsHemisLoginError:
        await _start_captcha_flow(
            callback.message, user, state, language,
            action_type="force_update",
            week_id=week_id,
        )
        return

    await state.update_data(selected_week_id=week_id)
    text = await _build_week_text(schedules, week_id, language)
    await callback.message.edit_text(
        text,
        reply_markup=get_week_pagination_keyboard(language, week_id),
        parse_mode="HTML",
    )


# ---------------------------------------------------------------------------
# Captcha flow
# ---------------------------------------------------------------------------

async def _start_captcha_flow(
    message: types.Message,
    user: User,
    state: FSMContext,
    language: LanguageEnum,
    action_type: str,
    week_id: str,          # ✅ FIX: week_id ni ham saqlaymiz
):
    """Captcha so'rab, state ga action_type va week_id ni yozadi."""
    session = create_session()
    csrf, captcha_bytes, cookies = get_hemis_captcha(session)

    if not csrf or not captcha_bytes:
        await message.edit_text(
            get_text("error_loading", language),
            reply_markup=get_back_to_menu_keyboard(language),
        )
        return

    # ✅ FIX: week_id ni state ga saqlaymiz
    await state.update_data(
        csrf=csrf,
        cookies=cookies,
        action_type=action_type,
        captcha_week_id=week_id,
    )

    try:
        await message.delete()
    except Exception:
        pass

    photo = types.BufferedInputFile(captcha_bytes, filename="captcha.jpg")
    await message.answer_photo(
        photo=photo,
        caption=get_text("enter_captcha", language),
    )
    await state.set_state(UserState.waiting_hemis_captcha_schedule)


@router.message(UserState.waiting_hemis_captcha_schedule)
async def process_schedule_captcha(message: types.Message, state: FSMContext):
    user = await User.get_or_none(telegram_id=message.from_user.id).prefetch_related("group")
    language = user.language if user else LanguageEnum.UZ

    data = await state.get_data()
    action_type = data.get("action_type", "week")
    csrf = data.get("csrf")
    cookies_dict = data.get("cookies", {})
    captcha_code = message.text.strip()

    # ✅ FIX: state dagi week_id ni olamiz
    week_id = data.get("captcha_week_id")

    wait_msg = await message.answer(get_text("loading", language))

    session = create_session()
    for k, v in cookies_dict.items():
        session.cookies.set(k, v, domain="student.ukiu.uz")

    is_valid, error_msg = hemis_login(
        session, csrf, user.hemis_login, user.hemis_password, captcha_code
    )

    if not is_valid:
        await wait_msg.delete()
        await message.answer(
            f"{error_msg}\n\nQaytadan urinib ko'ring",
            reply_markup=get_back_to_menu_keyboard(language),
        )
        await state.clear()
        return

    # ✅ FIX: week_id dan Week obyektini olamiz (joriy hafta emas!)
    if week_id:
        week, _ = await Week.get_or_create(
            week_number=week_id,
            defaults={
                "start_date": datetime.today().date(),
                "end_date": datetime.today().date(),
            },
        )
    else:
        week = await get_current_week()
        week_id = str(week.week_number)

    force_update = action_type == "force_update"

    try:
        schedules = await get_or_fetch_schedule(
            user.group, week, force_update=force_update, session=session
        )
    except Exception as e:
        logger.error(f"Captcha keyingi jadval olishda xatolik: {e}")
        await wait_msg.delete()
        await message.answer(
            get_text("error_loading", language),
            reply_markup=get_back_to_menu_keyboard(language),
        )
        await state.clear()
        return

    await wait_msg.delete()
    await state.clear()

    # ✅ FIX: action_type ga qarab to'g'ri ko'rinish
    if action_type == "today":
        text = await _build_today_text(schedules, language)
        keyboard = get_schedule_menu_keyboard(language)
    else:
        # week | week_select | force_update — barchasi haftalik ko'rinish
        text = await _build_week_text(schedules, week_id, language)
        keyboard = get_week_pagination_keyboard(language, week_id)

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")