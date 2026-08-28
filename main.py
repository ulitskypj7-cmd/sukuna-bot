#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 SUNRAKU — ADVANCED FILE RUNNER BOT 🔥
- User file upload karega
- Approval request teri chat ID pe jaayegi
- Approve ke baad hi file run ho sakti hai
- Default file bhi approval ke baad run hogi
- Dev: @SunrakuV2 | Channel: @Anishpy | @VOUCH_R
"""

import os
import sys
import time
import random
import json
import re
import requests
import threading
import subprocess
import shutil
from datetime import datetime
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ============================================================
# 🔥 ENVIRONMENT VARIABLE
# ============================================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ BOT_TOKEN environment variable not set!")
    sys.exit()

bot = TeleBot(BOT_TOKEN)

# ============================================================
# 📊 GLOBALS
# ============================================================
user_sessions = {}
lock = threading.Lock()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 🔥 Owner Chat ID (Approval ke liye)
OWNER_CHAT_ID = 8641613327

# 🔥 Pending approvals
pending_approvals = {}  # {user_chat_id: {"file_path": path, "file_name": name, "user_id": user_id}}

# ============================================================
# 🔥 DEFAULT FILE (Fast Hits Wali)
# ============================================================
DEFAULT_FILE = """
import requests
import random
import time

def fast_scanner():
    while True:
        user_id = random.randint(2500000000, 21254029834)
        print(f"Scanning: {user_id}")
        time.sleep(0.1)

if __name__ == "__main__":
    fast_scanner()
"""

# Save default file
with open(os.path.join(UPLOAD_DIR, "default_scanner.py"), "w") as f:
    f.write(DEFAULT_FILE)

# ============================================================
# 🔥 USER SESSION MANAGER
# ============================================================
class UserSession:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.file_path = None
        self.process = None
        self.is_running = False
        self.is_approved = False  # 🔥 Approval status
        self.logs = []
        self.start_time = None
        self.speed = 0
        self.total_checks = 0
        self.lock = threading.Lock()
    
    def add_log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {msg}")
        if len(self.logs) > 100:
            self.logs.pop(0)
    
    def get_logs(self, lines=20):
        return "\n".join(self.logs[-lines:]) if self.logs else "No logs yet."

# ============================================================
# 🔥 APPROVAL SYSTEM
# ============================================================
def send_approval_request(user_chat_id, file_name, file_path):
    """Owner ko approval request bhejo"""
    msg = f"""
🔔 **NEW FILE UPLOADED - APPROVAL NEEDED**

👤 User ID: `{user_chat_id}`
📁 File: `{file_name}`
📂 Path: `{file_path}`

📌 Click Approve to allow user to run this file.
"""
    markup = InlineKeyboardMarkup(row_width=2)
    btn_approve = InlineKeyboardButton(
        text="✅ APPROVE",
        callback_data=f"approve_{user_chat_id}_{file_path}"
    )
    btn_reject = InlineKeyboardButton(
        text="❌ REJECT",
        callback_data=f"reject_{user_chat_id}"
    )
    markup.add(btn_approve, btn_reject)
    
    try:
        bot.send_message(OWNER_CHAT_ID, msg, reply_markup=markup, parse_mode='Markdown')
        return True
    except Exception as e:
        print(f"Approval send error: {e}")
        return False

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve_file(call):
    """Owner ne approve kiya"""
    data = call.data.split("_")
    user_chat_id = int(data[1])
    file_path = "_".join(data[2:])  # Path mein underscores ho sakte hain
    
    with lock:
        if user_chat_id not in user_sessions:
            bot.answer_callback_query(call.id, "❌ User session not found!")
            return
        session = user_sessions[user_chat_id]
        session.is_approved = True
        session.add_log("✅ File approved by owner")
    
    bot.edit_message_text(
        f"✅ **File Approved!**\n👤 User: `{user_chat_id}`\n📁 File: `{os.path.basename(file_path)}`\n\nUser can now run the file.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown'
    )
    
    # User ko notify karo
    try:
        bot.send_message(
            user_chat_id,
            f"✅ **Your file has been approved!**\n\n📁 `{os.path.basename(file_path)}`\n🚀 Click **RUN FILE** to start.",
            parse_mode='Markdown'
        )
    except:
        pass
    
    bot.answer_callback_query(call.id, "✅ Approved!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_file(call):
    """Owner ne reject kiya"""
    user_chat_id = int(call.data.split("_")[1])
    
    with lock:
        if user_chat_id in user_sessions:
            session = user_sessions[user_chat_id]
            session.is_approved = False
            session.add_log("❌ File rejected by owner")
    
    bot.edit_message_text(
        f"❌ **File Rejected!**\n👤 User: `{user_chat_id}`\n\nFile has been rejected by owner.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown'
    )
    
    # User ko notify karo
    try:
        bot.send_message(
            user_chat_id,
            "❌ **Your file has been rejected by the owner.**\n\nPlease contact @SunrakuV2 for approval.",
            parse_mode='Markdown'
        )
    except:
        pass
    
    bot.answer_callback_query(call.id, "❌ Rejected!")

# ============================================================
# 🔥 BOT COMMANDS & BUTTONS
# ============================================================

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn1 = KeyboardButton("📤 𝑼𝑷𝑳𝑶𝑨𝑫 𝑭𝑰𝑳𝑬")
    btn2 = KeyboardButton("🚀 𝑹𝑼𝑵 𝑭𝑰𝑳𝑬")
    btn3 = KeyboardButton("⏹ 𝑺𝑻𝑶𝑷 𝑭𝑰𝑳𝑬")
    btn4 = KeyboardButton("📋 𝑽𝑰𝑬𝑾 𝑳𝑶𝑮𝑺")
    btn5 = KeyboardButton("📊 𝑺𝑻𝑨𝑻𝑼𝑺")
    btn6 = KeyboardButton("⚡ 𝑺𝑷𝑬𝑬𝑫")
    btn7 = KeyboardButton("🔥 𝑫𝑬𝑭𝑨𝑼𝑳𝑻 𝑭𝑰𝑳𝑬")
    btn8 = KeyboardButton("👑 𝑫𝑬𝑽")
    
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    with lock:
        if chat_id not in user_sessions:
            user_sessions[chat_id] = UserSession(chat_id)
    
    welcome_msg = f"""
☠️ 𝑺𝑼𝑵𝑹𝑨𝑲𝑼 — 𝑭𝑰𝑳𝑬 𝑹𝑼𝑵𝑵𝑬𝑹 ☠️

🔥 𝑪𝒍𝒊𝒄𝒌 𝒃𝒖𝒕𝒕𝒐𝒏𝒔 𝒃𝒆𝒍𝒐𝒘 𝒕𝒐 𝒄𝒐𝒏𝒕𝒓𝒐𝒍.

📌 **File Upload requires approval!**
   Owner will approve before you can run.

📤 𝑼𝒑𝒍𝒐𝒂𝒅 𝒚𝒐𝒖𝒓 .𝒑𝒚 𝒇𝒊𝒍𝒆
🚀 𝑹𝒖𝒏 𝒂𝒑𝒑𝒓𝒐𝒗𝒆𝒅 𝒇𝒊𝒍𝒆
📋 𝑽𝒊𝒆𝒘 𝒍𝒊𝒗𝒆 𝒍𝒐𝒈𝒔
📊 𝑪𝒉𝒆𝒄𝒌 𝒔𝒕𝒂𝒕𝒖𝒔 𝒂𝒏𝒅 𝒔𝒑𝒆𝒆𝒅
🔥 𝑹𝒖𝒏 𝒅𝒆𝒇𝒂𝒖𝒍𝒕 𝒇𝒂𝒔𝒕 𝒔𝒄𝒂𝒏𝒏𝒆𝒓

👑 𝑫𝒆𝒗: @𝑺𝒖𝒏𝒓𝒂𝒌𝒖𝑽2
📢 𝑪𝒉𝒂𝒏𝒏𝒆𝒍: @𝑨𝒏𝒊𝒔𝒉𝒑𝒚 | @𝑽𝑶𝑼𝑪𝑯_𝑹
"""
    bot.reply_to(message, welcome_msg, reply_markup=main_menu())

# ============================================================
# 📤 UPLOAD FILE
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "📤 𝑼𝑷𝑳𝑶𝑨𝑫 𝑭𝑰𝑳𝑬")
def upload_file(message):
    bot.reply_to(message, "📤 **Send your .py file** (max 5MB)\n\n📌 File will be sent for approval before you can run it.", parse_mode='Markdown')

@bot.message_handler(content_types=['document'])
def handle_file_upload(message):
    chat_id = message.chat.id
    file_id = message.document.file_id
    
    if not message.document.file_name.endswith('.py'):
        bot.reply_to(message, "❌ **Only .py files are allowed!**", parse_mode='Markdown')
        return
    
    if message.document.file_size > 5 * 1024 * 1024:
        bot.reply_to(message, "❌ **File too large! Max 5MB.**", parse_mode='Markdown')
        return
    
    with lock:
        if chat_id not in user_sessions:
            user_sessions[chat_id] = UserSession(chat_id)
        session = user_sessions[chat_id]
        session.is_approved = False  # 🔥 Reset approval on new upload
    
    try:
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_path = os.path.join(UPLOAD_DIR, f"{chat_id}_{message.document.file_name}")
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        
        session.file_path = file_path
        session.add_log(f"📤 File uploaded: {message.document.file_name}")
        
        # 🔥 Send approval request to owner
        success = send_approval_request(chat_id, message.document.file_name, file_path)
        
        if success:
            bot.reply_to(message, f"✅ **File uploaded successfully!**\n📁 `{message.document.file_name}`\n\n⏳ **Waiting for owner approval...**\nYou will be notified when approved.", parse_mode='Markdown')
        else:
            bot.reply_to(message, f"⚠️ **File uploaded but approval failed!**\nPlease contact @SunrakuV2 manually.", parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"❌ **Upload failed:** {str(e)}", parse_mode='Markdown')

# ============================================================
# 🔥 DEFAULT FILE
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "🔥 𝑫𝑬𝑭𝑨𝑼𝑳𝑻 𝑭𝑰𝑳𝑬")
def set_default_file(message):
    chat_id = message.chat.id
    
    with lock:
        if chat_id not in user_sessions:
            user_sessions[chat_id] = UserSession(chat_id)
        session = user_sessions[chat_id]
    
    default_path = os.path.join(UPLOAD_DIR, "default_scanner.py")
    session.file_path = default_path
    session.is_approved = False  # 🔥 Default file bhi approval require karega
    session.add_log("🔥 Default file selected - pending approval")
    
    # 🔥 Send approval request for default file
    success = send_approval_request(chat_id, "default_scanner.py", default_path)
    
    if success:
        bot.reply_to(message, "✅ **Default scanner selected!**\n\n⏳ **Waiting for owner approval...**\nYou will be notified when approved.", parse_mode='Markdown')
    else:
        bot.reply_to(message, "⚠️ **Default file selected but approval failed!**\nPlease contact @SunrakuV2.", parse_mode='Markdown')

# ============================================================
# 🚀 RUN FILE
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "🚀 𝑹𝑼𝑵 𝑭𝑰𝑳𝑬")
def run_file(message):
    chat_id = message.chat.id
    
    with lock:
        if chat_id not in user_sessions:
            user_sessions[chat_id] = UserSession(chat_id)
        session = user_sessions[chat_id]
    
    # 🔥 Check approval
    if not session.is_approved:
        bot.reply_to(message, "❌ **File not approved!**\n\n📌 Upload a file or select default file.\n⏳ Wait for owner approval.", parse_mode='Markdown')
        return
    
    if session.is_running:
        bot.reply_to(message, "⚠️ **File is already running!**\nClick **STOP FILE** first.", parse_mode='Markdown')
        return
    
    if not session.file_path or not os.path.exists(session.file_path):
        session.add_log("❌ No file found! Upload or select default.")
        bot.reply_to(message, "❌ **No file found!**\n\n📤 Upload a .py file\n🔥 Or select **DEFAULT FILE**", parse_mode='Markdown')
        return
    
    try:
        # Install requirements if present
        req_file = os.path.join(os.path.dirname(session.file_path), "requirements.txt")
        if os.path.exists(req_file):
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], capture_output=True)
            session.add_log("📦 Requirements installed")
        
        # Run file
        session.process = subprocess.Popen(
            [sys.executable, session.file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        session.is_running = True
        session.start_time = datetime.now()
        session.total_checks = 0
        session.add_log(f"🚀 File started: {os.path.basename(session.file_path)}")
        
        # Log reader thread
        def read_logs():
            while session.is_running:
                try:
                    output = session.process.stdout.readline()
                    if output:
                        session.add_log(output.strip())
                        session.total_checks += 1
                except:
                    break
            
            # Read remaining stderr
            if session.process:
                stderr = session.process.stderr.read()
                if stderr:
                    session.add_log(f"⚠️ {stderr.strip()}")
        
        threading.Thread(target=read_logs, daemon=True).start()
        
        bot.reply_to(message, f"✅ **File started!**\n📁 `{os.path.basename(session.file_path)}`\n\n📋 Click **VIEW LOGS** to see output.\n📊 Click **STATUS** to check progress.", parse_mode='Markdown')
        
    except Exception as e:
        session.is_running = False
        session.add_log(f"❌ Run error: {str(e)}")
        bot.reply_to(message, f"❌ **Error:** {str(e)}", parse_mode='Markdown')

# ============================================================
# ⏹ STOP FILE
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "⏹ 𝑺𝑻𝑶𝑷 𝑭𝑰𝑳𝑬")
def stop_file(message):
    chat_id = message.chat.id
    
    with lock:
        if chat_id not in user_sessions:
            bot.reply_to(message, "❌ No session found!", parse_mode='Markdown')
            return
        session = user_sessions[chat_id]
    
    if not session.is_running:
        bot.reply_to(message, "⚠️ **No file is running!**", parse_mode='Markdown')
        return
    
    try:
        session.process.terminate()
        time.sleep(1)
        if session.process.poll() is None:
            session.process.kill()
        
        session.is_running = False
        session.add_log("⏹ File stopped")
        
        bot.reply_to(message, "⏹ **File stopped successfully!**", parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"❌ **Stop error:** {str(e)}", parse_mode='Markdown')

# ============================================================
# 📋 VIEW LOGS
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "📋 𝑽𝑰𝑬𝑾 𝑳𝑶𝑮𝑺")
def view_logs(message):
    chat_id = message.chat.id
    
    with lock:
        if chat_id not in user_sessions:
            bot.reply_to(message, "❌ No session found!", parse_mode='Markdown')
            return
        session = user_sessions[chat_id]
    
    logs = session.get_logs(20)
    if not logs:
        bot.reply_to(message, "📋 **No logs yet.**\n\nRun a file to see output.", parse_mode='Markdown')
        return
    
    bot.reply_to(message, f"📋 **Recent Logs:**\n```\n{logs}\n```", parse_mode='Markdown')

# ============================================================
# 📊 STATUS
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "📊 𝑺𝑻𝑨𝑻𝑼𝑺")
def show_status(message):
    chat_id = message.chat.id
    
    with lock:
        if chat_id not in user_sessions:
            bot.reply_to(message, "❌ No session found!", parse_mode='Markdown')
            return
        session = user_sessions[chat_id]
    
    status = "🟢 RUNNING" if session.is_running else "🔴 STOPPED"
    approved = "✅ Approved" if session.is_approved else "⏳ Pending Approval"
    file_name = os.path.basename(session.file_path) if session.file_path else "None"
    
    runtime = "N/A"
    if session.start_time and session.is_running:
        runtime = str(datetime.now() - session.start_time).split('.')[0]
    elif session.start_time:
        runtime = str(datetime.now() - session.start_time).split('.')[0]
    
    status_msg = f"""
📊 **FILE STATUS**

📁 File: `{file_name}`
🟢 Status: {status}
✅ Approval: {approved}
⏱ Runtime: {runtime}
📊 Checks: {session.total_checks}
📈 Speed: {session.speed} checks/min
📋 Logs: {len(session.logs)} lines

━━━━━━━━━━━━━━━━━━━━━━━━━
👑 @SunrakuV2 | 📢 @Anishpy | @VOUCH_R
"""
    bot.reply_to(message, status_msg, parse_mode='Markdown')

# ============================================================
# ⚡ SPEED
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "⚡ 𝑺𝑷𝑬𝑬𝑫")
def show_speed(message):
    chat_id = message.chat.id
    
    with lock:
        if chat_id not in user_sessions:
            bot.reply_to(message, "❌ No session found!", parse_mode='Markdown')
            return
        session = user_sessions[chat_id]
    
    if not session.is_running:
        bot.reply_to(message, "⚠️ **No file is running!**", parse_mode='Markdown')
        return
    
    if session.start_time:
        runtime_seconds = (datetime.now() - session.start_time).total_seconds()
        if runtime_seconds > 0:
            speed = int((session.total_checks / runtime_seconds) * 60)
            session.speed = speed
        else:
            speed = 0
    else:
        speed = 0
    
    speed_msg = f"""
⚡ **SPEED REPORT**

📊 Total Checks: {session.total_checks}
⏱ Runtime: {str(datetime.now() - session.start_time).split('.')[0] if session.start_time else 'N/A'}
⚡ Speed: {speed} checks/min

━━━━━━━━━━━━━━━━━━━━━━━━━
👑 @SunrakuV2 | 📢 @Anishpy | @VOUCH_R
"""
    bot.reply_to(message, speed_msg, parse_mode='Markdown')

# ============================================================
# 👑 DEV
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "👑 𝑫𝑬𝑽")
def show_dev(message):
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton("👑 @SunrakuV2", url="https://t.me/SunrakuV2")
    btn2 = InlineKeyboardButton("📢 @Anishpy", url="https://t.me/Anishpy")
    btn3 = InlineKeyboardButton("📢 @VOUCH_R", url="https://t.me/VOUCH_R")
    markup.add(btn1, btn2, btn3)
    
    bot.reply_to(message, "👑 **Developer & Channels:**", reply_markup=markup, parse_mode='Markdown')

# ============================================================
# 🚀 START BOT
# ============================================================
print("✅ Bot is running...")
print("📌 Bot Username: @" + bot.get_me().username)
print("🔥 Advanced File Runner Bot Active")
print(f"👑 Owner Chat ID: {OWNER_CHAT_ID}")

while True:
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"⚠️ Polling error: {e}")
        time.sleep(5)
        continue
