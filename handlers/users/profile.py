import re
import requests
import logging
import io
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from loader import bot
from models.user import User
from models.group import Group
from models.schedule import Schedule
from schemas.language import LanguageEnum
from utils.i18n import get_text
from keyboards.inline.menu import get_profile_menu_keyboard, get_back_to_menu_keyboard
from states.test import UserState
from services.hemis_service import get_hemis_captcha, hemis_login, create_session, get_student_group, DASHBOARD_URL, fetch_schedule
from services.schedule_service import get_or_fetch_schedule, get_current_week, update_cached_week_id
from bs4 import BeautifulSoup


router = Router()

@router.callback_query(F.data == "menu_profile")
async def show_profile_menu(callback: types.CallbackQuery):
    """Show profile menu"""
    await callback.answer()
    
    user = await User.get_or_none(telegram_id=callback.from_user.id).prefetch_related("group")
    language = user.language if user else LanguageEnum.UZ
    
    group_name = user.group.name if user and user.group else "—"
    hemis_status = "✅" if user and user.hemis_login else "❌"
    
    # Strip emojis roughly if needed, otherwise just append
    profile_text = get_text('btn_profile', language)
    
    text = f"<b>{profile_text}</b>\n\n"
    text += f"ID: <code>{callback.from_user.id}</code>\n"
    text += f"Group: {group_name}\n"
    text += f"HEMIS: {hemis_status}"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_profile_menu_keyboard(language, user),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "connect_hemis")
async def start_connect_hemis(callback: types.CallbackQuery, state: FSMContext):
    """Start HEMIS connection process"""
    await callback.answer()
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    language = user.language if user else LanguageEnum.UZ
    
    await callback.message.edit_text(
        get_text("enter_hemis_login", language),
        reply_markup=get_back_to_menu_keyboard(language)
    )
    await state.set_state(UserState.waiting_hemis_login)


@router.message(UserState.waiting_hemis_login)
async def process_hemis_login(message: types.Message, state: FSMContext):

    user = await User.get_or_none(telegram_id=message.from_user.id)
    language = user.language if user else LanguageEnum.UZ

    await state.update_data(hemis_login=message.text.strip())

    await message.answer(
        get_text("enter_hemis_password", language),
        reply_markup=get_back_to_menu_keyboard(language)
    )

    await state.set_state(UserState.waiting_hemis_password)
@router.message(UserState.waiting_hemis_password)
async def process_hemis_password(message: types.Message, state: FSMContext):

    user = await User.get_or_none(telegram_id=message.from_user.id)
    language = user.language if user else LanguageEnum.UZ

    await state.update_data(hemis_password=message.text.strip())

    wait_msg = await message.answer(get_text("loading", language))

    session = create_session()

    csrf, captcha_bytes, cookies = get_hemis_captcha(session)

    if not csrf or not captcha_bytes:
        await wait_msg.delete()

        # user has not yet been mutated; pass it along so the menu
        # reflects the correct HEMIS state (usually ``None`` at this point).
        await message.answer(
            get_text("error_loading", language),
            reply_markup=get_profile_menu_keyboard(language, user)
        )

        await state.clear()
        return

    await wait_msg.delete()

    # ⚠️ MUHIM: loginni qayta yozmaymiz
    await state.update_data(
        csrf=csrf,
        cookies=cookies
    )

    photo = types.BufferedInputFile(captcha_bytes, filename="captcha.jpg")

    await message.answer_photo(
        photo=photo,
        caption="Rasmda ko'rsatilgan kodni kiriting\n\n⚠️ 20 soniya ichida kiriting"
    )

    await state.set_state(UserState.waiting_hemis_captcha)

@router.message(UserState.waiting_hemis_captcha)
async def process_hemis_captcha(message: types.Message, state: FSMContext):

    user = await User.get_or_none(telegram_id=message.from_user.id)
    language = user.language if user else LanguageEnum.UZ

    data = await state.get_data()

    login = data.get("hemis_login")
    password = data.get("hemis_password")
    csrf = data.get("csrf")
    cookies_dict = data.get("cookies", {})

    captcha_code = message.text.strip()

    wait_msg = await message.answer(get_text("loading", language))

    session = create_session()

    # Cookie qayta tiklash to the correct domain
    for k, v in cookies_dict.items():
        session.cookies.set(k, v, domain="student.ukiu.uz")

    # HEMIS LOGIN
    is_valid, error_message = hemis_login(
        session,
        csrf,
        login,
        password,
        captcha_code
    )

    if not is_valid:
        await wait_msg.delete()

        error_text = error_message or get_text("hemis_login_error", language)

        await message.answer(
            f"{error_text}\n\nQaytadan urinib ko'ring",
            reply_markup=get_back_to_menu_keyboard(language)
        )

        await state.set_state(UserState.waiting_hemis_captcha)
        return

    # 🔥 MUHIM: DASHBOARDNI OCHIB SESSIONNI AKTIV QILAMIZ
    session.get(DASHBOARD_URL)

    # LOGIN SUCCESS
    user.hemis_login = login
    user.hemis_password = password

    try:
        # 0️⃣ UPDATE CACHED WEEK ID (now that session is authenticated)
        logging.info("Updating cached week ID with authenticated session...")
        update_cached_week_id(session)

        # 1️⃣ GURUHNI OLISH
        resp = session.get(DASHBOARD_URL)

        soup = BeautifulSoup(resp.text, "html.parser")

        group_name = None

        user_role_span = soup.find("span", class_="user-role")

        if user_role_span:
            group_name = user_role_span.text.strip()

        if not group_name:

            patterns = [
                r'Guruh:\s*([A-Z0-9\-]+)',
                r'Group:\s*([A-Z0-9\-]+)'
            ]

            for pattern in patterns:
                match = re.search(pattern, resp.text)
                if match:
                    group_name = match.group(1).strip()
                    break

        # 2️⃣ GROUP DB GA YOZISH
        if group_name:

            group, _ = await Group.get_or_create(
                name=group_name.upper()
            )

            user.group = group

        await user.save()

        # 3️⃣ JADVALNI OLISH
        week = await get_current_week()

        schedule_data = fetch_schedule(
            session,
            str(week.week_number)
        )

        # 4️⃣ DB GA YOZISH
        for item in schedule_data:

            await Schedule.get_or_create(
                group=user.group,
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

    except Exception as e:
        logging.error(f"HEMIS caching error: {e}")

    await wait_msg.delete()

    await message.answer(
        get_text("hemis_connected", language),
        reply_markup=get_profile_menu_keyboard(language, user)
    )

    await state.clear()


@router.callback_query(F.data == "disconnect_hemis")
async def disconnect_hemis(callback: types.CallbackQuery):
    """Disconnect HEMIS account"""
    await callback.answer()
    
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    language = user.language if user else LanguageEnum.UZ
    
    if user:
        user.hemis_login = None
        user.hemis_password = None
        await user.save(update_fields=["hemis_login", "hemis_password"])
    
    # user object has been cleared of credentials, pass ``user`` so
    # the keyboard renders the "connect" button again (it's allowed to be
    # ``None``).
    await callback.message.edit_text(
        get_text("hemis_disconnected", language),
        reply_markup=get_profile_menu_keyboard(language, user)
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    """Go back to main menu"""
    await callback.answer()
    await state.clear()
    
    from handlers.users.start import cmd_start
    await cmd_start(callback.message)