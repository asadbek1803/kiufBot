import logging
import asyncio
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from loader import bot
from keyboards.inline.buttons import are_you_sure_markup, get_admin_menu_markup, get_admin_manage_markup
from states.test import AdminState
from filters.admin import IsBotAdminFilter
from data.config import ADMINS
from config.utils.pgtoexcel import export_to_excel
from config.models.user import User

router = Router()


@router.message(Command('admin'), IsBotAdminFilter(ADMINS))
async def admin_panel(message: types.Message):
    """Admin panel main menu"""
    text = """
🔐 <b>ADMIN PANEL</b>

Quyidagi buyruqlardan birini tanlang yoki menyudan foydalaning:

• /allusers - Barcha foydalanuvchilar ro'yxati
• /stats - Statistika
• /reklama - Reklama yuborish
• /backup - Bazani backup qilish
• /cleandb - Bazani tozalash
• /admins - Adminlarni boshqarish
"""
    await message.answer(text, reply_markup=get_admin_menu_markup(), parse_mode="HTML")


@router.callback_query(F.data == 'admin_allusers')
async def admin_allusers_callback(call: types.CallbackQuery):
    """Get all users via callback"""
    await call.answer()
    await get_all_users_handler(call.message)


async def get_all_users_handler(message: types.Message):
    """Get all users handler"""
    try:
        users = await User.all()
        total = len(users)
        
        if total == 0:
            await message.answer("❌ Bazada foydalanuvchilar topilmadi.")
            return
        
        # Format users list
        text = f"👥 <b>BARCHA FOYDALANUVCHILAR</b>\n\n"
        text += f"📊 <b>Jami:</b> {total} ta foydalanuvchi\n\n"
        
        # Show first 20 users
        for idx, user in enumerate(users[:20], 1):
            username = f"@{user.username}" if user.username else "❌ Yo'q"
            phone = user.phone_number if user.phone_number else "❌ Yo'q"
            created = user.created_at.strftime("%d.%m.%Y %H:%M") if user.created_at else "N/A"
            
            text += f"{idx}. <b>{user.full_name or 'N/A'}</b>\n"
            text += f"   🆔 ID: <code>{user.telegram_id}</code>\n"
            text += f"   👤 Username: {username}\n"
            text += f"   📱 Tel: {phone}\n"
            text += f"   🕐 {created}\n\n"
        
        if total > 20:
            text += f"\n... va yana {total - 20} ta foydalanuvchi"
        
        await message.answer(text, parse_mode="HTML")
        
    except Exception as e:
        logging.exception(f"Error in get_all_users: {e}")
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")


@router.message(Command('allusers'), IsBotAdminFilter(ADMINS))
async def get_all_users(message: types.Message):
    await get_all_users_handler(message)


@router.callback_query(F.data == 'admin_stats')
async def admin_stats_callback(call: types.CallbackQuery):
    """Get statistics via callback"""
    await call.answer()
    await stats_handler(call.message)


@router.message(Command('stats'), IsBotAdminFilter(ADMINS))
async def stats(message: types.Message):
    await stats_handler(message)


async def stats_handler(message: types.Message):
    """Statistics handler"""
    try:
        # Get all users
        all_users = await User.all()
        total_users = len(all_users)
        
        if total_users == 0:
            await message.answer("❌ Bazada ma'lumotlar yo'q.")
            return
        
        # Calculate statistics
        # Use naive datetime to avoid timezone comparison issues
        now = datetime.now().replace(tzinfo=None)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Helper function to make datetime naive if needed
        def make_naive(dt):
            """Convert datetime to naive if it's timezone-aware"""
            if dt is None:
                return None
            if dt.tzinfo is not None:
                return dt.replace(tzinfo=None)
            return dt
        
        today_users = sum(1 for u in all_users if u.created_at and make_naive(u.created_at) >= today)
        week_users = sum(1 for u in all_users if u.created_at and make_naive(u.created_at) >= week_ago)
        month_users = sum(1 for u in all_users if u.created_at and make_naive(u.created_at) >= month_ago)
        
        # Users with phone numbers
        users_with_phone = sum(1 for u in all_users if u.phone_number)
        users_with_username = sum(1 for u in all_users if u.username)
        
        # Format statistics
        text = f"""
📊 <b>BOT STATISTIKASI</b>

━━━━━━━━━━━━━━━━━━━━
👥 <b>Jami foydalanuvchilar:</b> {total_users}
━━━━━━━━━━━━━━━━━━━━

📅 <b>Vaqt bo'yicha:</b>
• Bugun: {today_users} ta
• Oxirgi 7 kun: {week_users} ta
• Oxirgi 30 kun: {month_users} ta

📱 <b>Ma'lumotlar:</b>
• Telefon raqami bor: {users_with_phone} ta
• Username bor: {users_with_username} ta

🕐 <b>Oxirgi yangilanish:</b> {now.strftime("%d.%m.%Y %H:%M:%S")}
"""
        
        await message.answer(text, parse_mode="HTML")
        
    except Exception as e:
        logging.exception(f"Error in stats: {e}")
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")


@router.callback_query(F.data == 'admin_reklama')
async def admin_reklama_callback(call: types.CallbackQuery, state: FSMContext):
    """Start advertisement via callback"""
    await call.answer()
    await call.message.answer("📢 Reklama uchun post yuboring (matn, rasm, video yoki boshqa media)")
    await state.set_state(AdminState.ask_ad_content)


@router.message(Command('reklama'), IsBotAdminFilter(ADMINS))
async def ask_ad_content(message: types.Message, state: FSMContext):
    await message.answer("📢 Reklama uchun post yuboring (matn, rasm, video yoki boshqa media)")
    await state.set_state(AdminState.ask_ad_content)


@router.message(AdminState.ask_ad_content, IsBotAdminFilter(ADMINS))
async def send_ad_to_users(message: types.Message, state: FSMContext):
    """Send advertisement to all users"""
    try:
        await message.answer("⏳ Reklama yuborilmoqda...")
        
        # Get all users
        users = await User.all()
        total = len(users)
        
        if total == 0:
            await message.answer("❌ Bazada foydalanuvchilar topilmadi.")
            await state.clear()
            return
        
        # Counters
        success = 0
        failed = 0
        
        # Send message to all users
        for user in users:
            try:
                # Copy message based on content type
                if message.photo:
                    await bot.send_photo(
                        chat_id=user.telegram_id,
                        photo=message.photo[-1].file_id,
                        caption=message.caption or "",
                        caption_entities=message.caption_entities
                    )
                elif message.video:
                    await bot.send_video(
                        chat_id=user.telegram_id,
                        video=message.video.file_id,
                        caption=message.caption or "",
                        caption_entities=message.caption_entities
                    )
                elif message.document:
                    await bot.send_document(
                        chat_id=user.telegram_id,
                        document=message.document.file_id,
                        caption=message.caption or "",
                        caption_entities=message.caption_entities
                    )
                elif message.animation:
                    await bot.send_animation(
                        chat_id=user.telegram_id,
                        animation=message.animation.file_id,
                        caption=message.caption or "",
                        caption_entities=message.caption_entities
                    )
                else:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=message.text or message.caption or "",
                        entities=message.entities or message.caption_entities
                    )
                
                success += 1
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.05)
                
            except Exception as e:
                failed += 1
                logging.error(f"Failed to send ad to user {user.telegram_id}: {e}")
                continue
        
        # Send result
        result_text = f"""
✅ <b>REKLAMA YUBORILDI</b>

━━━━━━━━━━━━━━━━━━━━
✅ Muvaffaqiyatli: {success} ta
❌ Xatolik: {failed} ta
📊 Jami: {total} ta
━━━━━━━━━━━━━━━━━━━━
"""
        await message.answer(result_text, parse_mode="HTML")
        await state.clear()
        
    except Exception as e:
        logging.exception(f"Error in send_ad_to_users: {e}")
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
        await state.clear()


@router.callback_query(F.data == 'admin_export')
async def admin_export_callback(call: types.CallbackQuery):
    """Export to Excel via callback"""
    await call.answer("⏳ Excel fayl tayyorlanmoqda...")
    await export_to_excel_handler(call.message)


@router.callback_query(F.data == 'admin_backup')
async def admin_backup_callback(call: types.CallbackQuery):
    """Backup database via callback"""
    await call.answer("⏳ Backup tayyorlanmoqda...")
    await backup_database_handler(call.message)


@router.message(Command('backup'), IsBotAdminFilter(ADMINS))
async def backup_database(message: types.Message):
    """Backup database command"""
    await backup_database_handler(message)


async def export_to_excel_handler(message: types.Message):
    """Export users to Excel"""
    try:
        users = await User.all()
        
        if not users:
            await message.answer("❌ Bazada foydalanuvchilar topilmadi.")
            return
        
        # Prepare data
        headings = ["ID", "Telegram ID", "To'liq ism", "Username", "Telefon raqam", "Qo'shilgan vaqt"]
        data = []
        
        for user in users:
            data.append([
                user.id,
                user.telegram_id,
                user.full_name or "N/A",
                user.username or "N/A",
                user.phone_number or "N/A",
                user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "N/A"
            ])
        
        # Create file path
        filepath = "users_export.xlsx"
        
        # Export to Excel
        await export_to_excel(data, headings, filepath)
        
        # Send file
        if os.path.exists(filepath):
            file = FSInputFile(filepath)
            await message.answer_document(
                document=file,
                caption=f"📥 <b>Excel fayl</b>\n\nJami: {len(users)} ta foydalanuvchi",
                parse_mode="HTML"
            )
            # Delete file after sending
            os.remove(filepath)
        else:
            await message.answer("❌ Fayl yaratishda xatolik yuz berdi.")
            
    except Exception as e:
        logging.exception(f"Error in export_to_excel: {e}")
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")


async def backup_database_handler(message: types.Message):
    """Backup SQLite database and send to admin"""
    try:
        # Get database path (same logic as in tortoise.py)
        # From handlers/users/admin.py -> config/utils/kiuf_bot.db
        # Path(__file__) = handlers/users/admin.py
        # parent.parent.parent = config/ (root directory)
        db_path = Path(__file__).parent.parent.parent / "utils" / "kiuf_bot.db"
        
        # Alternative paths if above doesn't work
        if not db_path.exists():
            # Try relative to config directory
            db_path = Path(__file__).parent.parent / "utils" / "kiuf_bot.db"
        
        if not db_path.exists():
            # Try in utils directory from current working directory
            db_path = Path("utils") / "kiuf_bot.db"
        
        if not db_path.exists():
            # Try absolute path from config root
            config_root = Path(__file__).parent.parent.parent
            db_path = config_root / "utils" / "kiuf_bot.db"
        
        if not db_path.exists():
            await message.answer("❌ Baza fayli topilmadi. Iltimos, baza fayl yo'lini tekshiring.")
            logging.error(f"Database file not found. Searched paths: {db_path}")
            return
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"kiuf_bot_backup_{timestamp}.db"
        backup_path = Path(backup_filename)
        
        # Copy database file
        shutil.copy2(db_path, backup_path)
        
        # Get file size
        file_size = backup_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        # Send backup file
        if backup_path.exists():
            file = FSInputFile(backup_path)
            await message.answer_document(
                document=file,
                caption=f"""
💾 <b>BAZA BACKUP</b>

━━━━━━━━━━━━━━━━━━━━
📁 <b>Fayl nomi:</b> {backup_filename}
📊 <b>Hajmi:</b> {file_size_mb:.2f} MB
🕐 <b>Vaqt:</b> {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}
━━━━━━━━━━━━━━━━━━━━

✅ Backup muvaffaqiyatli yaratildi!
""",
                parse_mode="HTML"
            )
            # Delete backup file after sending
            backup_path.unlink()
        else:
            await message.answer("❌ Backup fayl yaratishda xatolik yuz berdi.")
            
    except Exception as e:
        logging.exception(f"Error in backup_database: {e}")
        await message.answer(f"❌ Backup yaratishda xatolik yuz berdi: {str(e)}")


@router.callback_query(F.data == 'admin_cleandb')
async def admin_cleandb_callback(call: types.CallbackQuery, state: FSMContext):
    """Clean database via callback"""
    await call.answer()
    msg = await call.message.answer(
        "⚠️ <b>EHTIYOT!</b>\n\nHaqiqatdan ham bazani tozalab yubormoqchimisiz?\n\nBu amalni qaytarib bo'lmaydi!",
        reply_markup=are_you_sure_markup,
        parse_mode="HTML"
    )
    await state.update_data(msg_id=msg.message_id)
    await state.set_state(AdminState.are_you_sure)


@router.message(Command('cleandb'), IsBotAdminFilter(ADMINS))
async def ask_are_you_sure(message: types.Message, state: FSMContext):
    msg = await message.reply(
        "⚠️ <b>EHTIYOT!</b>\n\nHaqiqatdan ham bazani tozalab yubormoqchimisiz?\n\nBu amalni qaytarib bo'lmaydi!",
        reply_markup=are_you_sure_markup,
        parse_mode="HTML"
    )
    await state.update_data(msg_id=msg.message_id)
    await state.set_state(AdminState.are_you_sure)


@router.callback_query(AdminState.are_you_sure, IsBotAdminFilter(ADMINS))
async def clean_db(call: types.CallbackQuery, state: FSMContext):
    """Clean database handler"""
    await call.answer()
    
    if call.data == 'yes':
        try:
            # Get count before deletion
            count = await User.all().count()
            
            # Delete all users
            await User.all().delete()
            
            await call.message.edit_text(
                f"✅ Bazani tozalash muvaffaqiyatli yakunlandi.\n\n"
                f"🗑️ O'chirilgan: {count} ta foydalanuvchi"
            )
            
        except Exception as e:
            logging.exception(f"Error in clean_db: {e}")
            await call.message.edit_text(f"❌ Xatolik yuz berdi: {str(e)}")
    else:
        await call.message.edit_text("❌ Amal bekor qilindi.")
    
    await state.clear()


# ==================== ADMIN MANAGEMENT ====================

def get_env_file_path():
    """Get .env file path"""
    # Try to find .env file in parent directories
    current_path = Path(__file__).parent.parent.parent
    env_path = current_path / ".env"
    
    if not env_path.exists():
        # Try in config directory
        env_path = Path(__file__).parent.parent / ".env"
    
    if not env_path.exists():
        # Try in current working directory
        env_path = Path(".env")
    
    return env_path


def read_env_file():
    """Read .env file and return as dictionary"""
    env_path = get_env_file_path()
    
    if not env_path.exists():
        return {}
    
    env_dict = {}
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_dict[key.strip()] = value.strip()
    
    return env_dict


def write_env_file(env_dict):
    """Write dictionary to .env file"""
    env_path = get_env_file_path()
    
    # Read existing file to preserve comments and formatting
    lines = []
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    
    # Update or add ADMINS line
    updated = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('ADMINS=') or stripped.startswith('ADMINS ='):
            # Replace ADMINS line
            admins_list = env_dict.get('ADMINS', ADMINS)
            if isinstance(admins_list, list):
                admins_str = ','.join(str(a) for a in admins_list)
            else:
                admins_str = str(admins_list)
            new_lines.append(f"ADMINS={admins_str}\n")
            updated = True
        else:
            new_lines.append(line)
    
    # If ADMINS not found, add it
    if not updated:
        admins_list = env_dict.get('ADMINS', ADMINS)
        if isinstance(admins_list, list):
            admins_str = ','.join(str(a) for a in admins_list)
        else:
            admins_str = str(admins_list)
        new_lines.append(f"ADMINS={admins_str}\n")
    
    # Write back to file
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)


@router.callback_query(F.data == 'admin_manage')
async def admin_manage_menu(call: types.CallbackQuery):
    """Admin management menu"""
    await call.answer()
    text = """
👤 <b>ADMINLARNI BOSHQARISH</b>

Quyidagi amallardan birini tanlang:

• Adminlar ro'yxatini ko'rish
• Yangi admin qo'shish
• Adminni o'chirish
"""
    await call.message.edit_text(text, reply_markup=get_admin_manage_markup(), parse_mode="HTML")


@router.callback_query(F.data == 'admin_back')
async def admin_back_to_menu(call: types.CallbackQuery):
    """Back to admin panel"""
    await call.answer()
    text = """
🔐 <b>ADMIN PANEL</b>

Quyidagi buyruqlardan birini tanlang yoki menyudan foydalaning:

• /allusers - Barcha foydalanuvchilar ro'yxati
• /stats - Statistika
• /reklama - Reklama yuborish
• /backup - Bazani backup qilish
• /cleandb - Bazani tozalash
• /admins - Adminlarni boshqarish
"""
    await call.message.edit_text(text, reply_markup=get_admin_menu_markup(), parse_mode="HTML")


@router.callback_query(F.data == 'admin_list')
async def admin_list(call: types.CallbackQuery):
    """Show list of admins"""
    await call.answer()
    
    try:
        admins_list = ADMINS
        total = len(admins_list)
        
        if total == 0:
            text = "❌ Adminlar ro'yxati bo'sh."
        else:
            text = f"👤 <b>ADMINLAR RO'YXATI</b>\n\n"
            text += f"📊 <b>Jami:</b> {total} ta admin\n\n"
            
            for idx, admin_id in enumerate(admins_list, 1):
                try:
                    # Try to get user info from bot
                    user = await bot.get_chat(int(admin_id))
                    username = f"@{user.username}" if user.username else "❌ Yo'q"
                    full_name = user.full_name or "N/A"
                    text += f"{idx}. <b>{full_name}</b>\n"
                    text += f"   🆔 ID: <code>{admin_id}</code>\n"
                    text += f"   👤 Username: {username}\n\n"
                except Exception as e:
                    text += f"{idx}. 🆔 ID: <code>{admin_id}</code>\n"
                    text += f"   ⚠️ Ma'lumot olishda xatolik\n\n"
        
        text += "\n🔙 Orqaga qaytish uchun tugmani bosing."
        await call.message.edit_text(text, reply_markup=get_admin_manage_markup(), parse_mode="HTML")
        
    except Exception as e:
        logging.exception(f"Error in admin_list: {e}")
        await call.message.edit_text(f"❌ Xatolik yuz berdi: {str(e)}")


@router.callback_query(F.data == 'admin_add')
async def admin_add_start(call: types.CallbackQuery, state: FSMContext):
    """Start adding admin"""
    await call.answer()
    await call.message.edit_text(
        "➕ <b>YANGI ADMIN QO'SHISH</b>\n\n"
        "Yangi adminning Telegram ID raqamini yuboring:\n\n"
        "💡 <i>Telegram ID ni olish uchun @userinfobot ga yuboring</i>",
        parse_mode="HTML"
    )
    await state.set_state(AdminState.add_admin)


@router.message(AdminState.add_admin, IsBotAdminFilter(ADMINS))
async def admin_add_process(message: types.Message, state: FSMContext):
    """Process adding admin"""
    try:
        admin_id = message.text.strip()
        
        # Validate admin ID
        try:
            admin_id_int = int(admin_id)
        except ValueError:
            await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting.")
            return
        
        # Check if admin already exists
        if admin_id in ADMINS:
            await message.answer(f"⚠️ Bu admin allaqachon ro'yxatda: <code>{admin_id}</code>", parse_mode="HTML")
            await state.clear()
            return
        
        # Read current .env file
        env_dict = read_env_file()
        
        # Add new admin
        current_admins = list(ADMINS)
        current_admins.append(admin_id)
        env_dict['ADMINS'] = current_admins
        
        # Write back to .env file
        write_env_file(env_dict)
        
        # Try to get user info
        try:
            user = await bot.get_chat(admin_id_int)
            username = f"@{user.username}" if user.username else "❌ Yo'q"
            full_name = user.full_name or "N/A"
            info_text = f"<b>{full_name}</b>\n👤 Username: {username}"
        except:
            info_text = "Ma'lumot olishda xatolik"
        
        await message.answer(
            f"✅ <b>Admin muvaffaqiyatli qo'shildi!</b>\n\n"
            f"🆔 ID: <code>{admin_id}</code>\n"
            f"👤 {info_text}\n\n"
            f"⚠️ <i>O'zgarishlar kuchga kirishi uchun botni qayta ishga tushiring!</i>",
            parse_mode="HTML"
        )
        await state.clear()
        
    except Exception as e:
        logging.exception(f"Error in admin_add_process: {e}")
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
        await state.clear()


@router.callback_query(F.data == 'admin_remove')
async def admin_remove_start(call: types.CallbackQuery, state: FSMContext):
    """Start removing admin"""
    await call.answer()
    
    # Show current admins
    admins_list = ADMINS
    if len(admins_list) <= 1:
        await call.message.edit_text(
            "⚠️ <b>EHTIYOT!</b>\n\n"
            "Kamida bitta admin bo'lishi kerak!\n"
            "Barcha adminlarni o'chirib bo'lmaydi.",
            reply_markup=get_admin_manage_markup(),
            parse_mode="HTML"
        )
        return
    
    text = "➖ <b>ADMINNI O'CHIRISH</b>\n\n"
    text += "O'chirish kerak bo'lgan adminning Telegram ID raqamini yuboring:\n\n"
    text += "<b>Joriy adminlar:</b>\n"
    
    for idx, admin_id in enumerate(admins_list, 1):
        text += f"{idx}. <code>{admin_id}</code>\n"
    
    await call.message.edit_text(text, parse_mode="HTML")
    await state.set_state(AdminState.remove_admin)


@router.message(AdminState.remove_admin, IsBotAdminFilter(ADMINS))
async def admin_remove_process(message: types.Message, state: FSMContext):
    """Process removing admin"""
    try:
        admin_id = message.text.strip()
        
        # Validate admin ID
        try:
            admin_id_int = int(admin_id)
        except ValueError:
            await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting.")
            return
        
        # Check if admin exists
        if admin_id not in ADMINS:
            await message.answer(f"⚠️ Bu admin ro'yxatda topilmadi: <code>{admin_id}</code>", parse_mode="HTML")
            await state.clear()
            return
        
        # Check if trying to remove the last admin
        if len(ADMINS) <= 1:
            await message.answer("⚠️ Kamida bitta admin bo'lishi kerak!")
            await state.clear()
            return
        
        # Read current .env file
        env_dict = read_env_file()
        
        # Remove admin
        current_admins = list(ADMINS)
        current_admins.remove(admin_id)
        env_dict['ADMINS'] = current_admins
        
        # Write back to .env file
        write_env_file(env_dict)
        
        await message.answer(
            f"✅ <b>Admin muvaffaqiyatli o'chirildi!</b>\n\n"
            f"🆔 ID: <code>{admin_id}</code>\n\n"
            f"⚠️ <i>O'zgarishlar kuchga kirishi uchun botni qayta ishga tushiring!</i>",
            parse_mode="HTML"
        )
        await state.clear()
        
    except Exception as e:
        logging.exception(f"Error in admin_remove_process: {e}")
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
        await state.clear()


@router.message(Command('admins'), IsBotAdminFilter(ADMINS))
async def admins_command(message: types.Message):
    """Admins command handler"""
    text = """
👤 <b>ADMINLARNI BOSHQARISH</b>

Quyidagi amallardan birini tanlang:

• Adminlar ro'yxatini ko'rish
• Yangi admin qo'shish
• Adminni o'chirish
"""
    await message.answer(text, reply_markup=get_admin_manage_markup(), parse_mode="HTML")


# ==================== FEEDBACK REPLY HANDLER ====================

@router.callback_query(F.data.startswith("reply_user_"), IsBotAdminFilter(ADMINS))
async def start_reply_to_user(call: types.CallbackQuery, state: FSMContext):
    """Start replying to user via inline button"""
    await call.answer()
    
    try:
        # Extract user_id from callback_data
        user_id = int(call.data.split("_")[-1])
        
        # Check if user exists
        user = await User.get_or_none(telegram_id=user_id)
        if not user:
            await call.message.answer("❌ Foydalanuvchi topilmadi.")
            return
        
        # Get user info
        username = user.username
        full_name = user.full_name or "N/A"
        username_display = f"@{username}" if username else "❌ Yo'q"
        
        # Save user_id to state
        await state.update_data(reply_user_id=user_id)
        await state.set_state(AdminState.reply_user)
        
        # Ask admin to write reply
        await call.message.answer(
            f"📩 <b>Javob yozish</b>\n\n"
            f"👤 <b>Foydalanuvchi:</b> {full_name}\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
            f"👤 <b>Username:</b> {username_display}\n\n"
            f"📝 Javobingizni yozing:",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logging.exception(f"Error in start_reply_to_user: {e}")
        await call.message.answer(f"❌ Xatolik: {str(e)}")


@router.message(AdminState.reply_user, IsBotAdminFilter(ADMINS))
async def send_reply_to_user(message: types.Message, state: FSMContext):
    """Send admin reply to user"""
    try:
        # Get user_id from state
        data = await state.get_data()
        user_id = data.get('reply_user_id')
        
        if not user_id:
            await message.answer("❌ Foydalanuvchi ID topilmadi.")
            await state.clear()
            return
        
        # Check if user exists
        user = await User.get_or_none(telegram_id=user_id)
        if not user:
            await message.answer("❌ Foydalanuvchi topilmadi.")
            await state.clear()
            return
        
        # Get admin info
        admin_name = message.from_user.full_name or "Admin"
        
        # Prepare reply message
        reply_text = f"""
📩 <b>Admin javobi</b>

━━━━━━━━━━━━━━━━━━━━
👤 <b>Admin:</b> {admin_name}
━━━━━━━━━━━━━━━━━━━━

{message.text or message.caption or ''}
"""
        
        # Send reply to user
        try:
            # If message has media, send it
            if message.photo:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=message.photo[-1].file_id,
                    caption=reply_text,
                    parse_mode="HTML"
                )
            elif message.video:
                await bot.send_video(
                    chat_id=user_id,
                    video=message.video.file_id,
                    caption=reply_text,
                    parse_mode="HTML"
                )
            elif message.document:
                await bot.send_document(
                    chat_id=user_id,
                    document=message.document.file_id,
                    caption=reply_text,
                    parse_mode="HTML"
                )
            elif message.audio:
                await bot.send_audio(
                    chat_id=user_id,
                    audio=message.audio.file_id,
                    caption=reply_text,
                    parse_mode="HTML"
                )
            elif message.voice:
                await bot.send_voice(
                    chat_id=user_id,
                    voice=message.voice.file_id,
                    caption=reply_text,
                    parse_mode="HTML"
                )
            elif message.animation:
                await bot.send_animation(
                    chat_id=user_id,
                    animation=message.animation.file_id,
                    caption=reply_text,
                    parse_mode="HTML"
                )
            else:
                # Text message
                await bot.send_message(
                    chat_id=user_id,
                    text=reply_text,
                    parse_mode="HTML"
                )
            
            # Confirm to admin
            await message.answer("✅ <b>Javob foydalanuvchiga yuborildi!</b>", parse_mode="HTML")
            await state.clear()
            
        except Exception as e:
            logging.error(f"Failed to send reply to user {user_id}: {e}")
            await message.answer(f"❌ Xatolik: Foydalanuvchiga javob yuborib bo'lmadi.\n\n{str(e)}")
            await state.clear()
            
    except Exception as e:
        logging.exception(f"Error in send_reply_to_user: {e}")
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
        await state.clear()


@router.message(F.reply_to_message, IsBotAdminFilter(ADMINS))
async def handle_admin_reply(message: types.Message):
    """Handle admin reply to feedback message"""
    try:
        import re
        
        # Check if the replied message exists
        replied_msg = message.reply_to_message
        
        if not replied_msg:
            return  # Not a reply, ignore
        
        # Try to get user_id from different sources
        original_user_id = None
        
        # Method 1: Check if replied message is forwarded
        if replied_msg.forward_from:
            original_user_id = replied_msg.forward_from.id
        
        # Method 2: Check if replied message contains user_id in text (info message)
        # Try multiple patterns: "User ID:", "🆔 ID:", "ID:"
        if replied_msg.text:
            # Pattern 1: "🆔 User ID: <code>123</code>" (most specific, at the end)
            match = re.search(r'🆔\s*User\s+ID:</b>\s*<code>(\d+)</code>', replied_msg.text, re.IGNORECASE)
            if not match:
                # Pattern 2: "User ID: <code>123</code>" (without emoji)
                match = re.search(r'User\s+ID:</b>\s*<code>(\d+)</code>', replied_msg.text, re.IGNORECASE)
            if not match:
                # Pattern 3: "🆔 ID: <code>123</code>" (with emoji, without "User")
                # But only if it's in the user info section (not the first ID)
                # Look for the last occurrence which should be "User ID"
                matches = list(re.finditer(r'🆔\s*ID:</b>\s*<code>(\d+)</code>', replied_msg.text))
                if matches:
                    # Take the last match (should be "User ID")
                    match = matches[-1]
                else:
                    match = None
            if not match:
                # Pattern 4: "ID: <code>123</code>" (most flexible, but must be in user info section)
                # Look for ID that appears after "━━━━━━━━━━━━━━━━━━━━" or "Foydalanuvchi"
                if "━━━━━━━━━━━━━━━━━━━━" in replied_msg.text or "Foydalanuvchi" in replied_msg.text:
                    # Get all ID matches and take the last one (should be User ID)
                    matches = list(re.finditer(r'ID:</b>\s*<code>(\d+)</code>', replied_msg.text))
                    if matches:
                        match = matches[-1]
                    else:
                        match = None
            if match:
                original_user_id = int(match.group(1))
                logging.debug(f"Found user_id from text: {original_user_id}")
        
        # Method 3: Check if replied message has caption with user_id
        if not original_user_id and replied_msg.caption:
            # Pattern 1: "User ID: <code>123</code>"
            match = re.search(r'User ID:</b>\s*<code>(\d+)</code>', replied_msg.caption)
            if not match:
                # Pattern 2: "🆔 ID: <code>123</code>"
                match = re.search(r'🆔\s*ID:</b>\s*<code>(\d+)</code>', replied_msg.caption)
            if not match:
                # Pattern 3: "ID: <code>123</code>"
                match = re.search(r'ID:</b>\s*<code>(\d+)</code>', replied_msg.caption)
            if match:
                original_user_id = int(match.group(1))
        
        # Method 4: Check if replied message is a reply to info message
        # If user's message was sent as reply to info message, check the parent
        if not original_user_id and replied_msg.reply_to_message:
            parent_msg = replied_msg.reply_to_message
            if parent_msg.text:
                # Try multiple patterns
                match = re.search(r'User ID:</b>\s*<code>(\d+)</code>', parent_msg.text)
                if not match:
                    match = re.search(r'🆔\s*ID:</b>\s*<code>(\d+)</code>', parent_msg.text)
                if not match:
                    match = re.search(r'ID:</b>\s*<code>(\d+)</code>', parent_msg.text)
                if match:
                    original_user_id = int(match.group(1))
        
        # If still no user_id found, show error with instructions
        if not original_user_id:
            await message.reply(
                "❌ <b>Xatolik!</b>\n\n"
                "Foydalanuvchi ID ni aniqlab bo'lmadi.\n\n"
                "💡 <b>Qanday javob berish kerak:</b>\n"
                "1. Foydalanuvchi ma'lumotlari ko'rsatilgan <b>info xabarga</b> reply qiling\n"
                "2. Yoki foydalanuvchi xabariga reply qiling (agar u info xabarga reply qilingan bo'lsa)\n\n"
                "📝 <i>Info xabar quyidagicha ko'rinadi:</i>\n"
                "<code>💬 YANGI TAKLIF/MUROJJAT\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "👤 Foydalanuvchi: ...\n"
                "🆔 ID: 123456789</code>",
                parse_mode="HTML"
            )
            return
        
        # Get the original user who sent the feedback
        
        # Check if user exists
        user = await User.get_or_none(telegram_id=original_user_id)
        if not user:
            await message.answer("❌ Foydalanuvchi topilmadi.")
            return
        
        # Get admin info
        admin_name = message.from_user.full_name or "Admin"
        
        # Prepare reply message
        reply_text = f"""
📩 <b>Admin javobi</b>

━━━━━━━━━━━━━━━━━━━━
👤 <b>Admin:</b> {admin_name}
━━━━━━━━━━━━━━━━━━━━

{message.text or message.caption or ''}
"""
        
        # Send reply to user
        try:
            # If message has media, send it
            if message.photo:
                await bot.send_photo(
                    chat_id=original_user_id,
                    photo=message.photo[-1].file_id,
                    caption=reply_text,
                    parse_mode="HTML"
                )
            elif message.video:
                await bot.send_video(
                    chat_id=original_user_id,
                    video=message.video.file_id,
                    caption=reply_text,
                    parse_mode="HTML"
                )
            elif message.document:
                await bot.send_document(
                    chat_id=original_user_id,
                    document=message.document.file_id,
                    caption=reply_text,
                    parse_mode="HTML"
                )
            elif message.audio:
                await bot.send_audio(
                    chat_id=original_user_id,
                    audio=message.audio.file_id,
                    caption=reply_text,
                    parse_mode="HTML"
                )
            elif message.voice:
                await bot.send_voice(
                    chat_id=original_user_id,
                    voice=message.voice.file_id,
                    caption=reply_text,
                    parse_mode="HTML"
                )
            elif message.animation:
                await bot.send_animation(
                    chat_id=original_user_id,
                    animation=message.animation.file_id,
                    caption=reply_text,
                    parse_mode="HTML"
                )
            else:
                # Text message
                await bot.send_message(
                    chat_id=original_user_id,
                    text=reply_text,
                    parse_mode="HTML"
                )
            
            # Confirm to admin
            await message.reply("✅ <b>Javob foydalanuvchiga yuborildi!</b>", parse_mode="HTML")
            
        except Exception as e:
            logging.error(f"Failed to send reply to user {original_user_id}: {e}")
            await message.reply(f"❌ Xatolik: Foydalanuvchiga javob yuborib bo'lmadi.\n\n{str(e)}")
            
    except Exception as e:
        logging.exception(f"Error in handle_admin_reply: {e}")
        await message.reply(f"❌ Xatolik yuz berdi: {str(e)}")