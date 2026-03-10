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
from keyboards.inline.menu import get_schedule_menu_keyboard, get_back_to_menu_keyboard, get_week_pagination_keyboard
from services.schedule_service import get_current_week, get_or_fetch_schedule, format_schedule_message, NeedsHemisLoginError, format_week_date_range
from services.hemis_service import get_hemis_captcha, hemis_login, create_session
from states.test import UserState

router = Router()

@router.callback_query(F.data == "menu_schedule")
async def show_schedule_menu(callback: types.CallbackQuery):
    """Show schedule menu"""
    await callback.answer()
    
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    language = user.language if user else LanguageEnum.UZ
    
    await callback.message.edit_text(
        "📅 <b>" + get_text("btn_schedule", language).replace("📅 ", "") + "</b>",
        reply_markup=get_schedule_menu_keyboard(language),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "today_schedule")
async def show_today_schedule(callback: types.CallbackQuery, state: FSMContext):
    """Show today's schedule"""
    await callback.answer()
    user = await User.get_or_none(telegram_id=callback.from_user.id).prefetch_related("group")
    language = user.language if user else LanguageEnum.UZ
    
    # Prompt user to connect HEMIS if they don't have a group
    await callback.message.edit_text(get_text("schedule_loading", language), parse_mode="HTML")
    week = await get_current_week()
    
    try:
        schedules = await get_or_fetch_schedule(user.group, week, user=user)
    except NeedsHemisLoginError:
        await start_captcha_flow(callback.message, user, state, language, "today")
        return
    
    # Filter for today
    weekday = datetime.today().weekday()
    uz_days = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
    today_name = uz_days[weekday]
    
    today_schedules = [s for s in schedules if s.day == today_name]
    
    if not today_schedules:
        text = get_text("no_classes_today", language)
    else:
        # prepend localized header for today's schedule
        text = get_text("today_schedule", language)
        text += await format_schedule_message(today_schedules)
        
    await callback.message.edit_text(
        text,
        reply_markup=get_schedule_menu_keyboard(language),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "week_schedule")
async def show_week_schedule(callback: types.CallbackQuery, state: FSMContext):
    """Show week's schedule"""
    await callback.answer()
    user = await User.get_or_none(telegram_id=callback.from_user.id).prefetch_related("group")
    language = user.language if user else LanguageEnum.UZ
    
    await callback.message.edit_text(get_text("schedule_loading", language), parse_mode="HTML")
    week = await get_current_week()
    
    try:
        schedules = await get_or_fetch_schedule(user.group, week, user=user)
    except NeedsHemisLoginError:
        await start_captcha_flow(callback.message, user, state, language, "week")
        return
    
    # Store the week ID in FSM for pagination
    await state.update_data(selected_week_id=str(week.week_number))
    
    # Get date range for display
    date_range = format_week_date_range(str(week.week_number), language)
    text = f"{get_text('week_schedule', language)}<b>{date_range}</b>\n\n"
    
    if not schedules:
        text += get_text("no_classes_today", language)
    else:
        text += await format_schedule_message(schedules)
        
    await callback.message.edit_text(
        text,
        reply_markup=get_week_pagination_keyboard(language, str(week.week_number)),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("select_week:"))
async def select_week(callback: types.CallbackQuery, state: FSMContext):
    """Handle week selection from pagination buttons"""
    await callback.answer()
    user = await User.get_or_none(telegram_id=callback.from_user.id).prefetch_related("group")
    language = user.language if user else LanguageEnum.UZ
    
    # Extract week ID from callback data (format: "select_week:10839")
    week_id = callback.data.split(":")[1]
    
    await callback.message.edit_text(get_text("schedule_loading", language), parse_mode="HTML")
    
    # Get or create the week in database
    week, _ = await Week.get_or_create(
        week_number=week_id,
        defaults={"start_date": datetime.today().date(), "end_date": datetime.today().date()}
    )
    
    try:
        schedules = await get_or_fetch_schedule(user.group, week, user=user)
    except NeedsHemisLoginError:
        await start_captcha_flow(callback.message, user, state, language, "week_select")
        return
    
    # Store the selected week ID in FSM
    await state.update_data(selected_week_id=week_id)
    
    # Get date range for display
    date_range = format_week_date_range(week_id, language)
    text = f"{get_text('week_schedule', language)}<b>{date_range}</b>\n\n"
    
    if not schedules:
        text += get_text("no_classes_today", language)
    else:
        text += await format_schedule_message(schedules)
        
    await callback.message.edit_text(
        text,
        reply_markup=get_week_pagination_keyboard(language, week_id),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "update_schedule")
async def update_schedule(callback: types.CallbackQuery, state: FSMContext):
    """Update cache"""
    await callback.answer()
    user = await User.get_or_none(telegram_id=callback.from_user.id).prefetch_related("group")
    language = user.language if user else LanguageEnum.UZ
    
    await callback.message.edit_text(get_text("schedule_loading", language), parse_mode="HTML")
    week = await get_current_week()
    
    try:
        schedules = await get_or_fetch_schedule(user.group, week, force_update=True, user=user)
    except NeedsHemisLoginError:
        await start_captcha_flow(callback.message, user, state, language, "force_update")
        return
    if not schedules:
        text = get_text("no_classes_today", language)
    else:
        # when user manually updates we show weekly header as well
        text = get_text("week_schedule", language)
        text += await format_schedule_message(schedules)
        
    await callback.message.edit_text(
        text,
        reply_markup=get_schedule_menu_keyboard(language),
        parse_mode="HTML"
    )

async def start_captcha_flow(message: types.Message, user: User, state: FSMContext, language: LanguageEnum, action_type: str):
    """Initiates captcha fetch for schedule generation"""
    session = create_session()
    csrf, captcha_bytes, cookies = get_hemis_captcha(session)
    
    if not csrf or not captcha_bytes:
        await message.edit_text("Error fetching HEMIS.", reply_markup=get_back_to_menu_keyboard(language))
        return
        
    await state.update_data({
        "csrf": csrf,
        "cookies": cookies,
        "action_type": action_type
    })
    
    await message.delete()
    
    photo = types.BufferedInputFile(captcha_bytes, filename="captcha.jpg")
    await message.answer_photo(
        photo=photo,
        caption="Jadvalni yuklash uchun rasmda ko'rsatilgan kodni kiriting / Введите код с картинки:"
    )
    await state.set_state(UserState.waiting_hemis_captcha_schedule)

@router.message(UserState.waiting_hemis_captcha_schedule)
async def process_schedule_captcha(message: types.Message, state: FSMContext):
    user = await User.get_or_none(telegram_id=message.from_user.id).prefetch_related("group")
    language = user.language if user else LanguageEnum.UZ
    
    data = await state.get_data()
    action_type = data.get("action_type")
    csrf = data.get("csrf")
    cookies_dict = data.get("cookies", {})
    captcha_code = message.text
    
    wait_msg = await message.answer(get_text("loading", language))
    
    session = create_session()
    
    for k, v in cookies_dict.items():
        session.cookies.set(k, v, domain="student.ukiu.uz")
    
    is_valid, error_msg = hemis_login(session, csrf, user.hemis_login, user.hemis_password, captcha_code)
    
    if not is_valid:
        await wait_msg.delete()
        await message.answer(
            f"{error_msg}\n\nQaytadan urinib ko'ring", 
            reply_markup=get_back_to_menu_keyboard(language)
        )
        # We need to restart the captcha flow if it fails
        await state.clear()
        return
        
    week = await get_current_week()
    force_update = True if action_type == "force_update" else False
    
    try:
        schedules = await get_or_fetch_schedule(user.group, week, force_update=force_update, user=user, session=session)
    except Exception as e:
        logging.error(f"Error fetching schedule post-login: {e}")
        await wait_msg.delete()
        await message.answer(
            "Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.",
            reply_markup=get_back_to_menu_keyboard(language)
        )
        await state.clear()
        return
        
    await wait_msg.delete()
    await state.clear()
    
    text = ""
    if action_type == "today":
        weekday = datetime.today().weekday()
        uz_days = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
        today_name = uz_days[weekday]
        today_schedules = [s for s in schedules if s.day == today_name]
        
        text = get_text("today_schedule", language)
        if not today_schedules:
            text += get_text("no_classes_today", language)
        else:
            text += await format_schedule_message(today_schedules)
            
    else: # week or force_update
        text = get_text("week_schedule", language)
        if not schedules:
            text += get_text("no_classes_today", language)
        else:
            text += await format_schedule_message(schedules)
            
    await message.answer(
        text,
        reply_markup=get_schedule_menu_keyboard(language),
        parse_mode="HTML"
    )
