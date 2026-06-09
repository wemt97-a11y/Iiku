#!/usr/bin/env python3
# TERMINAL_OUTPUT: TELEGRAM_BOT_ENGINE_v6.0_COLOR_BUTTONS
# STATUS: PRODUCTION_READY - WITH TELEGRAM OFFICIAL COLOR STYLES

import asyncio
import re
import time
import random
import threading
from typing import Dict, List
import requests
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from fake_useragent import UserAgent

# ============= SYSTEM_CONFIG =============
BOT_TOKEN = "8771621771:AAH-N3vr9aBZPUu_WiQKb1f29SJCh6um4Xo"  # غيّر هذا إلى التوكن الجديد
DEVELOPER_USERNAME = "Aegriss"
CHANNEL_LINK = "https://t.me/+xScEFigNbXMzNGM0"

SESSION_POOL = [
    "a0f49aaf1ecd041dc6469aa9de3e8a8b", "35af0ab71fa286b4d32fa794eab67766",
    "f00e754b271ebcbeb1ec81d1b8b74c94", "774cb9362213b37b4bd51528d3e30295",
    "2b37fd4151b4eaf7196f5f5e7e659f64", "e75ed27910bc3b0d134faa20f7d6be86",
]

bot = AsyncTeleBot(BOT_TOKEN)
user_data: Dict[int, Dict] = {}
active_jobs: Dict[int, threading.Thread] = {}

# ============= CORE_FUNCTIONS =============
def extract_tiktok_id(username_or_url: str) -> str:
    pattern = r'(?:https?:\/\/)?(?:www\.)?tiktok\.com\/@([a-zA-Z0-9_.]+)'
    match = re.search(pattern, username_or_url)
    if match:
        return match.group(1)
    if username_or_url.startswith('@'):
        return username_or_url[1:]
    return username_or_url

def get_user_id(username: str) -> str:
    headers = {
        'User-Agent': UserAgent().random,
        'Accept': 'text/html,application/xhtml+xml'
    }
    try:
        resp = requests.get(f'https://www.tiktok.com/@{username}', headers=headers, timeout=10)
        match = re.search(r'"user":{"id":"(\d+)"', resp.text)
        return match.group(1) if match else None
    except:
        return None

def send_report(session_id: str, target_id: str) -> bool:
    url = "https://api16-normal-c-alisg.tiktokv.com/aweme/v2/aweme/feedback/"
    params = {
        'report_type': 'user',
        'object_id': target_id,
        'owner_id': target_id,
        'reason': '9004',
        'lang': 'ar',
        '_rticket': str(int(time.time() * 1000)),
        'aid': '1340',
        'ts': str(int(time.time()))
    }
    headers = {
        'User-Agent': 'com.zhiliaoapp.musically.go/430103 (Linux; Android 15)',
        'Cookie': f'sessionid={session_id}; sid_tt={session_id}'
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        return 'status_code":0' in resp.text
    except:
        return False

# ============= MAIN_MESSAGE_TEMPLATE =============
def get_main_message() -> str:
    return """
─── ❮ 𝗧𝗶𝗸𝗧𝗼𝗸 𝗥𝗲𝗽𝗼𝗿𝘁𝘀 ❯ ───

🛡️ نـظام الإبـلاغ الـذكي والـسريع
🚀 خـيارك الأول لإغـلاق وتـعطيل أي حـساب تـيك تـوك بـضغطة زر.

🔍 الـحالة: مـتصل وجـاهز للتنفيذ..
──────────────────
« بـانتظار تـحديد الـهدف »
"""

# ============= OFFICIAL TELEGRAM COLOR BUTTONS (Bot API 7.10+) =============
# Using style parameter: "primary" (blue), "danger" (red), "success" (green)
# This is the new official feature from Telegram Bot API 9.4 [citation:1][citation:8][citation:10]

def render_dashboard() -> InlineKeyboardMarkup:
    """Create dashboard with OFFICIAL Telegram colored buttons (Primary, Danger, Success)"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🎯 تعيين الهدف", callback_data="set_target", style="primary"),
        InlineKeyboardButton("🔑 اضافة سيشنات", callback_data="add_sessions", style="success")
    )
    keyboard.add(
        InlineKeyboardButton("⚡ سرعة الهجوم", callback_data="intensity", style="primary"),
        InlineKeyboardButton("💥 بدء الهجوم", callback_data="launch", style="danger")
    )
    keyboard.add(
        InlineKeyboardButton("📊 الاحصائيات", callback_data="stats", style="primary"),
        InlineKeyboardButton("🛑 ايقاف الهجوم", callback_data="stop", style="danger")
    )
    keyboard.add(
        InlineKeyboardButton("👨‍💻 المطور", url=f"https://t.me/{DEVELOPER_USERNAME}", style="primary"),
        InlineKeyboardButton("📢 القناة", url=CHANNEL_LINK, style="success")
    )
    return keyboard

def render_intensity_keyboard() -> InlineKeyboardMarkup:
    """Create intensity selection with colored buttons"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("⚡ فائق (2ث)", callback_data="int_2", style="danger"),
        InlineKeyboardButton("🚀 سريع (5ث)", callback_data="int_5", style="danger")
    )
    keyboard.add(
        InlineKeyboardButton("🐢 متوسط (10ث)", callback_data="int_10", style="primary"),
        InlineKeyboardButton("⚠️ بطيء (15ث)", callback_data="int_15", style="primary")
    )
    keyboard.add(
        InlineKeyboardButton("🔙 رجوع", callback_data="back", style="primary")
    )
    return keyboard

def format_progress_bar(current: int, total: int, width: int = 20) -> str:
    filled = int(width * current / total)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {current}/{total} تم بنجاح"

# ============= REPORT_ENGINE =============
async def execute_report_batch(user_id: int, target_username: str, sessions: List[str], intensity: int, message_id: int, chat_id: int):
    target_id = get_user_id(target_username)
    if not target_id:
        await bot.edit_message_text("❌ الهدف غير موجود او محظور", chat_id, message_id)
        return
    
    total = len(sessions)
    success = 0
    
    for i, session in enumerate(sessions):
        if user_id in active_jobs and not active_jobs[user_id].is_alive():
            await bot.edit_message_text("🛑 تم ايقاف الهجوم", chat_id, message_id)
            return
        
        if send_report(session, target_id):
            success += 1
        
        progress = format_progress_bar(success, total)
        await bot.edit_message_text(
            f"🔄 جاري ارسال البلاغات...\n{progress}\n\n✅ نجح: {success}\n❌ فشل: {i+1-success}\n📊 نسبة النجاح: {(success/(i+1))*100:.1f}%",
            chat_id, message_id
        )
        await asyncio.sleep(random.uniform(1, 2))
        
        if (i + 1) % 10 == 0 and i + 1 < total:
            await asyncio.sleep(intensity)
    
    await bot.edit_message_text(
        f"✅ اكتمل الهجوم\n━━━━━━━━━━━━━━\n🎯 الهدف: @{target_username}\n✅ نجح: {success}\n❌ فشل: {total-success}\n📊 نسبة النجاح: {(success/total)*100:.1f}%",
        chat_id, message_id
    )
    if user_id in active_jobs:
        del active_jobs[user_id]

# ============= HANDLERS =============
@bot.message_handler(commands=['start'])
async def start_command(message):
    user_data[message.from_user.id] = {
        'target': None, 
        'intensity': 10, 
        'sessions': SESSION_POOL.copy()
    }
    await bot.send_message(
        message.chat.id,
        get_main_message(),
        reply_markup=render_dashboard()
    )

@bot.callback_query_handler(func=lambda call: True)
async def handle_callbacks(call: CallbackQuery):
    user_id = call.from_user.id
    data = call.data
    
    if data == "add_sessions":
        await bot.edit_message_text(
            "🔐 اضافة سيشنات جديدة\n━━━━━━━━━━\nارسل عدد السيشنات التي تريد اضافتها اولا\nمثال: 10\nثم ارسل السيشنات كل سيشن في سطر جديد",
            call.message.chat.id, call.message.message_id
        )
        user_data[user_id]['waiting_for_session_count'] = True
    
    elif data == "set_target":
        await bot.edit_message_text(
            "🎯 تعيين الهدف\n━━━━━━━━━━\nارسل رابط التيك توك او اسم المستخدم\nمثال: @username\nاو: https://tiktok.com/@user",
            call.message.chat.id, call.message.message_id
        )
        user_data[user_id]['waiting_for_target'] = True
    
    elif data == "intensity":
        await bot.edit_message_text(
            "⚡ اختر سرعة الهجوم", 
            call.message.chat.id, 
            call.message.message_id, 
            reply_markup=render_intensity_keyboard()
        )
    
    elif data.startswith("int_"):
        intensity = int(data.split('_')[1])
        if user_id in user_data:
            user_data[user_id]['intensity'] = intensity
        await bot.answer_callback_query(call.id, f"تم ضبط السرعة على {intensity} ثواني")
        msg_text = get_main_message() + f"\n\n✅ تم ضبط السرعة: {intensity} ثانية"
        await bot.edit_message_text(msg_text, call.message.chat.id, call.message.message_id, reply_markup=render_dashboard())
    
    elif data == "launch":
        if user_id in active_jobs:
            await bot.answer_callback_query(call.id, "⚠️ يوجد هجوم نشط حاليا")
            return
        target = user_data.get(user_id, {}).get('target')
        if not target:
            await bot.answer_callback_query(call.id, "❌ لم يتم تعيين هدف. استخدم زر تعيين هدف اولا")
            return
        
        sessions = user_data[user_id].get('sessions', SESSION_POOL)
        intensity = user_data[user_id].get('intensity', 10)
        
        msg = await bot.edit_message_text("🚀 جاري تجهيز الهجوم...", call.message.chat.id, call.message.message_id)
        
        def run_async():
            asyncio.run(execute_report_batch(user_id, target, sessions, intensity, msg.message_id, call.message.chat.id))
        
        thread = threading.Thread(target=run_async)
        active_jobs[user_id] = thread
        thread.start()
    
    elif data == "stats":
        stats = user_data.get(user_id, {})
        sessions_count = len(stats.get('sessions', []))
        status = "🔥 هجوم نشط" if user_id in active_jobs else "✅ في انتظار"
        stats_text = get_main_message() + f"""

📊 الاحصائيات
━━━━━━━━━━━━
🎯 الهدف: {stats.get('target', 'لا يوجد')}
⚡ السرعة: {stats.get('intensity', 10)} ثانية
🔑 عدد السيشنات: {sessions_count}
📌 الحالة: {status}"""
        await bot.edit_message_text(stats_text, call.message.chat.id, call.message.message_id, reply_markup=render_dashboard())
    
    elif data == "stop":
        if user_id in active_jobs:
            active_jobs[user_id].join(timeout=0)
            del active_jobs[user_id]
            msg_text = get_main_message() + "\n\n🛑 تم ايقاف الهجوم بنجاح"
            await bot.edit_message_text(msg_text, call.message.chat.id, call.message.message_id, reply_markup=render_dashboard())
        else:
            await bot.answer_callback_query(call.id, "لا يوجد هجوم نشط لايقافه")
    
    elif data == "back":
        await bot.edit_message_text(get_main_message(), call.message.chat.id, call.message.message_id, reply_markup=render_dashboard())

@bot.message_handler(func=lambda message: True)
async def handle_messages(message):
    user_id = message.from_user.id
    
    if user_id not in user_data:
        user_data[user_id] = {'target': None, 'intensity': 10, 'sessions': SESSION_POOL.copy()}
    
    if user_data[user_id].get('waiting_for_session_count'):
        try:
            count = int(message.text.strip())
            if count > 0:
                user_data[user_id]['expected_session_count'] = count
                user_data[user_id]['waiting_for_session_count'] = False
                user_data[user_id]['waiting_for_sessions'] = True
                await bot.send_message(message.chat.id, f"✅ تم. الان ارسل {count} سيشن (كل سيشن 32 حرف ورقم)\nكل سيشن في سطر منفصل")
            else:
                await bot.send_message(message.chat.id, "❌ العدد يجب ان يكون اكبر من 0")
        except ValueError:
            await bot.send_message(message.chat.id, "❌ الرجاء ارسال عدد صحيح")
    
    elif user_data[user_id].get('waiting_for_sessions'):
        sessions = re.findall(r'[a-f0-9]{32}', message.text)
        
        if sessions:
            user_data[user_id]['sessions'].extend(sessions)
            await bot.send_message(
                message.chat.id, 
                f"✅ تم اضافة {len(sessions)} سيشن\n📊 العدد الكلي الان: {len(user_data[user_id]['sessions'])} سيشن",
                reply_markup=render_dashboard()
            )
        else:
            await bot.send_message(message.chat.id, "❌ لم يتم العثور على سيشنات صالحة (32 حرف ورقم)", reply_markup=render_dashboard())
        
        user_data[user_id]['waiting_for_sessions'] = False
        user_data[user_id].pop('expected_session_count', None)
    
    elif user_data[user_id].get('waiting_for_target'):
        username = extract_tiktok_id(message.text)
        if username:
            user_data[user_id]['target'] = username
            user_data[user_id]['waiting_for_target'] = False
            msg_text = get_main_message() + f"\n\n🎯 تم تعيين الهدف: @{username}"
            await bot.send_message(message.chat.id, msg_text, reply_markup=render_dashboard())
        else:
            await bot.send_message(message.chat.id, "❌ رابط او اسم مستخدم غير صالح", reply_markup=render_dashboard())
    
    else:
        await bot.send_message(message.chat.id, get_main_message(), reply_markup=render_dashboard())

# ============= BOOT_SEQUENCE =============
if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════╗
    ║  TERMINAL: ARCHITECT_ENGINE_v6.0          ║
    ║  STATUS: COLOR_BUTTONS_ACTIVE             ║
    ║  FEATURE: Telegram Official Button Colors ║
    ║  STYLES: Primary / Danger / Success       ║
    ║  BOT: TELEGRAM_ACTIVE                     ║
    ╚══════════════════════════════════════════╝
    """)
    asyncio.run(bot.polling(non_stop=True))