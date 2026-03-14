import re
import logging
import requests
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
from services.hemis_service import (
    get_hemis_captcha,
    hemis_login,
    create_session,
    DASHBOARD_URL,
    fetch_schedule,
)
from services.schedule_service import get_current_week, update_cached_week_id
from bs4 import BeautifulSoup

router = Router()
logger = logging.getLogger(__name__)


# =========================================================
# PROFIL MENYU
# =========================================================

@router.callback_query(F.data == "menu_profile")
async def show_profile_menu(callback: types.CallbackQuery):
    await callback.answer()

    user = await User.get_or_none(
        telegram_id=callback.from_user.id
    ).prefetch_related("group")

    language = user.language if user else LanguageEnum.UZ

    group_name = user.group.name if user and user.group else "—"
    hemis_status = "✅" if user and user.hemis_login else "❌"

    text = (
        f"<b>{get_text('btn_profile', language)}</b>\n\n"
        f"ID: <code>{callback.from_user.id}</code>\n"
        f"Guruh: {group_name}\n"
        f"HEMIS: {hemis_status}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_profile_menu_keyboard(language, user),
        parse_mode="HTML",
    )


# =========================================================
# 1-QADAM LOGIN SO'RASH
# =========================================================

@router.callback_query(F.data == "connect_hemis")
async def start_connect_hemis(callback: types.CallbackQuery, state: FSMContext):

    await callback.answer()

    user = await User.get_or_none(telegram_id=callback.from_user.id)
    language = user.language if user else LanguageEnum.UZ

    msg = await callback.message.edit_text(
        get_text("enter_hemis_login", language),
        reply_markup=get_back_to_menu_keyboard(language),
    )

    await state.update_data(
        flow_message_id=msg.message_id
    )

    await state.set_state(UserState.waiting_hemis_login)


# =========================================================
# 2-QADAM LOGIN QABUL QILISH
# =========================================================

@router.message(UserState.waiting_hemis_login)
async def process_hemis_login(message: types.Message, state: FSMContext):

    data = await state.get_data()

    login = message.text.strip()
    flow_msg = data.get("flow_message_id")

    try:
        await message.delete()
    except:
        pass

    try:
        await bot.delete_message(message.chat.id, flow_msg)
    except:
        pass

    await state.update_data(
        hemis_login=login
    )

    ask_password = await message.answer("🔐 HEMIS parolini kiriting:")

    await state.update_data(
        flow_message_id=ask_password.message_id
    )

    await state.set_state(UserState.waiting_hemis_password)


# =========================================================
# 3-QADAM PAROL QABUL QILISH
# =========================================================

@router.message(UserState.waiting_hemis_password)
async def process_hemis_password(message: types.Message, state: FSMContext):

    data = await state.get_data()

    password = message.text.strip()
    flow_msg = data.get("flow_message_id")

    try:
        await message.delete()
    except:
        pass

    try:
        await bot.delete_message(message.chat.id, flow_msg)
    except:
        pass

    await state.update_data(
        hemis_password=password
    )

    session = create_session()

    csrf, captcha_bytes, cookies = get_hemis_captcha(session)

    if not csrf or not captcha_bytes:

        await message.answer("❌ Captcha yuklanmadi")
        await state.clear()
        return

    await state.update_data(
        csrf=csrf,
        cookies=cookies
    )

    photo = types.BufferedInputFile(
        captcha_bytes,
        filename="captcha.jpg"
    )

    captcha_msg = await message.answer_photo(
        photo,
        caption="🧩 Captcha kodini kiriting:"
    )

    await state.update_data(
        captcha_message_id=captcha_msg.message_id
    )

    await state.set_state(UserState.waiting_hemis_captcha)


# =========================================================
# 4-QADAM CAPTCHA QABUL QILISH
# =========================================================

@router.message(UserState.waiting_hemis_captcha)
async def process_hemis_captcha(message: types.Message, state: FSMContext):

    user = await User.get_or_none(telegram_id=message.from_user.id)

    language = user.language if user else LanguageEnum.UZ

    data = await state.get_data()

    login = data.get("hemis_login")
    password = data.get("hemis_password")
    csrf = data.get("csrf")
    cookies = data.get("cookies")
    captcha_msg_id = data.get("captcha_message_id")

    captcha_code = message.text.strip()

    try:
        await message.delete()
    except:
        pass

    try:
        await bot.delete_message(message.chat.id, captcha_msg_id)
    except:
        pass

    wait = await message.answer("⏳ HEMIS ga ulanmoqda...")

    session = create_session()

    for k, v in cookies.items():
        session.cookies.set(k, v, domain="student.ukiu.uz")

    is_valid, error = hemis_login(
        session,
        csrf,
        login,
        password,
        captcha_code,
    )

    if not is_valid:

        await wait.edit_text("❌ Login yoki captcha xato")

        await state.clear()

        return

    session.get(DASHBOARD_URL)

    user.hemis_login = login
    user.hemis_password = password

    try:

        update_cached_week_id(session)

        resp = session.get(DASHBOARD_URL)

        soup = BeautifulSoup(resp.text, "html.parser")

        group_name = None

        user_role_span = soup.find("span", class_="user-role")

        if user_role_span:
            group_name = user_role_span.text.strip()

        if not group_name:

            for pattern in [
                r"Guruh:\s*([A-Z0-9\-]+)",
                r"Group:\s*([A-Z0-9\-]+)",
            ]:

                match = re.search(pattern, resp.text)

                if match:
                    group_name = match.group(1).strip()
                    break

        if group_name:

            group, _ = await Group.get_or_create(
                name=group_name.upper()
            )

            user.group = group

        await user.save()

        week = await get_current_week()

        schedule_data = fetch_schedule(
            session,
            str(week.week_number),
        )

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
                    "lesson_time": item.get("lesson_time"),
                },
            )

    except Exception as e:

        logger.error(f"HEMIS caching xatoligi: {e}")

    await wait.delete()

    user = await User.get_or_none(
        telegram_id=message.from_user.id
    ).prefetch_related("group")

    await message.answer(
        "✅ HEMIS muvaffaqiyatli ulandi",
        reply_markup=get_profile_menu_keyboard(language, user),
        parse_mode="HTML",
    )

    await state.clear()


# =========================================================
# HEMIS UZISH
# =========================================================

@router.callback_query(F.data == "disconnect_hemis")
async def disconnect_hemis(callback: types.CallbackQuery):

    await callback.answer()

    user = await User.get_or_none(
        telegram_id=callback.from_user.id
    )

    language = user.language if user else LanguageEnum.UZ

    await User.filter(
        telegram_id=callback.from_user.id
    ).update(
        hemis_login=None,
        hemis_password=None,
        group_id=None,
        reminder_enabled=False,
    )

    user = await User.get_or_none(
        telegram_id=callback.from_user.id
    )

    await callback.message.edit_text(
        get_text("hemis_disconnected", language),
        reply_markup=get_profile_menu_keyboard(language, user),
    )



# ---------------------------------------------------------------------------
# Orqaga
# ---------------------------------------------------------------------------

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()

    from handlers.users.start import cmd_start
    await cmd_start(callback.message)