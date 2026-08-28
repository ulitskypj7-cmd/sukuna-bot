#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 SUNRAKU — ADVANCED FILE RUNNER BOT 🔥
- User file upload karega
- Bot automatically BOT_TOKEN + CHAT_ID replace karega
- Approval system (owner approve karega)
- Run/Stop/Logs/Status/Speed controls
- LIVE STATUS + SPEED FIXED
- Default file (fast hits) bhi available
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

# ============================================================
# 🔥 USER SESSION MANAGER (Fully Fixed)
# ============================================================
class UserSession:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.file_path = None
        self.process = None
        self.is_running = False
        self.is_approved = False
        self.logs = []
        self.start_time = None
        self.end_time = None
        self.speed = 0
        self.total_checks = 0
        self.user_bot_token = ""
        self.user_chat_id = ""
        self.installed_packages = []
        self.lock = threading.Lock()
    
    def add_log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {msg}")
        if len(self.logs) > 200:
            self.logs.pop(0)
    
    def get_logs(self, lines=25):
        return "\n".join(self.logs[-lines:]) if self.logs else "No logs yet."
    
    def get_runtime(self):
        if self.start_time:
            end_time = self.end_time or datetime.now()
            diff = end_time - self.start_time
            return str(diff).split('.')[0]
        return "N/A"
    
    def get_speed(self):
        if self.start_time:
            end_time = self.end_time or datetime.now()
            runtime_seconds = max((end_time - self.start_time).total_seconds(), 1)
            speed = int((self.total_checks / runtime_seconds) * 60)
            self.speed = speed
            return speed
        return self.speed or 0

# ============================================================
# 🔥 DEFAULT FILE
# ============================================================
DEFAULT_FILE_TEMPLATE = '''#!/usr/bin/env python3
import requests
import random
import time
import sys

BOT_TOKEN = "{BOT_TOKEN}"
CHAT_ID = "{CHAT_ID}"

def fast_scanner():
    print(f"🚀 Scanner started!")
    print(f"🤖 Bot Token: {BOT_TOKEN[:10]}...")
    print(f"📌 Chat ID: {CHAT_ID}")
    counter = 0
    while True:
        try:
            user_id = random.randint(2500000000, 21254029834)
            counter += 1
            print(f"[{counter}] 🔍 Scanning: {user_id}")
            sys.stdout.flush()
            time.sleep(0.1)
        except KeyboardInterrupt:
            print("\\n⏹ Scanner stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    fast_scanner()
'''

# ============================================================
# 🔥 VARIABLE REPLACEMENT SYSTEM
# ============================================================
def replace_variables_in_file(file_path, bot_token, chat_id):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 🔥 Replace variables
        content = content.replace('"{BOT_TOKEN}"', f'"{bot_token}"')
        content = content.replace('"{CHAT_ID}"', f'"{chat_id}"')
        content = content.replace('{BOT_TOKEN}', bot_token)
        content = content.replace('{CHAT_ID}', chat_id)
        
        content = re.sub(r'BOT_TOKEN\s*=\s*"[^"]*"', f'BOT_TOKEN = "{bot_token}"', content)
        content = re.sub(r"BOT_TOKEN\s*=\s*'[^']*'", f"BOT_TOKEN = '{bot_token}'", content)
        content = re.sub(r'CHAT_ID\s*=\s*"[^"]*"', f'CHAT_ID = "{chat_id}"', content)
        content = re.sub(r"CHAT_ID\s*=\s*'[^']*'", f"CHAT_ID = '{chat_id}'", content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Variable replace error: {e}")
        return False

# ============================================================
# 🔥 APPROVAL SYSTEM
# ============================================================
def send_approval_request(user_chat_id, file_name, file_path, bot_token="", chat_id=""):
    token_info = f"🤖 Bot Token: `{bot_token[:10]}...`" if bot_token else "⏳ Pending..."
    chat_info = f"📌 Chat ID: `{chat_id}`" if chat_id else "⏳ Pending..."
    
    msg = f"""
🔔 **NEW FILE UPLOADED - APPROVAL NEEDED**

👤 User ID: `{user_chat_id}`
📁 File: `{file_name}`
📂 Path: `{file_path}`

{token_info}
{chat_info}

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
    data = call.data.split("_")
    user_chat_id = int(data[1])
    file_path = "_".join(data[2:])
    
    with lock:
        if user_chat_id not in user_sessions:
            bot.answer_callback_query(call.id, "❌ User session not found!")
            return
        session = user_sessions[user_chat_id]
        session.is_approved = True
        session.add_log("✅ File approved by owner")
    
    if session.user_bot_token and session.user_chat_id:
        replace_variables_in_file(file_path, session.user_bot_token, session.user_chat_id)
        session.add_log("✅ Variables replaced in file")
    
    bot.edit_message_text(
        f"✅ **File Approved!**\n👤 User: `{user_chat_id}`\n📁 File: `{os.path.basename(file_path)}`\n\nUser can now run the file.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown'
    )
    
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
    
    # Telegram does not support custom button colors, so colored emoji
    # markers are used to make every button visually distinct.
    btn1 = KeyboardButton("🟦 📤 𝑼𝑷𝑳𝑶𝑨𝑫 𝑭𝑰𝑳𝑬")
    btn2 = KeyboardButton("🟢 🚀 𝑹𝑼𝑵 𝑭𝑰𝑳𝑬")
    btn3 = KeyboardButton("🔴 ⏹ 𝑺𝑻𝑶𝑷 𝑭𝑰𝑳𝑬")
    btn4 = KeyboardButton("🟡 📋 𝑽𝑰𝑬𝑾 𝑳𝑶𝑮𝑺")
    btn5 = KeyboardButton("🟣 📊 𝑳𝑰𝑽𝑬 𝑺𝑻𝑨𝑻𝑼𝑺")
    btn6 = KeyboardButton("🟠 ⚡ 𝑺𝑷𝑬𝑬𝑫")
    btn7 = KeyboardButton("🟤 🔥 𝑫𝑬𝑭𝑨𝑼𝑳𝑻 𝑭𝑰𝑳𝑬")
    btn8 = KeyboardButton("📦 INSTALL PIP")
    btn9 = KeyboardButton("⚫ 👑 𝑫𝑬𝑽")
    
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9)
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

🟦 𝑼𝒑𝒍𝒐𝒂𝒅 𝒚𝒐𝒖𝒓 .𝒑𝒚 𝒇𝒊𝒍𝒆
🟢 𝑹𝒖𝒏 𝒂𝒑𝒑𝒓𝒐𝒗𝒆𝒅 𝒇𝒊𝒍𝒆
🟡 𝑽𝒊𝒆𝒘 𝒍𝒊𝒗𝒆 𝒍𝒐𝒈𝒔
🟣 𝑳𝒊𝒗𝒆 𝑺𝒕𝒂𝒕𝒖𝒔
🟠 𝑺𝒑𝒆𝒆𝒅
🟤 𝑹𝒖𝒏 𝒅𝒆𝒇𝒂𝒖𝒍𝒕 𝒇𝒂𝒔𝒕 𝒔𝒄𝒂𝒏𝒏𝒆𝒓
📦 𝑰𝒏𝒔𝒕𝒂𝒍𝒍 𝒑𝒊𝒑 𝒑𝒂𝒄𝒌𝒂𝒈𝒆𝒔 𝒇𝒐𝒓 𝒚𝒐𝒖𝒓 𝒇𝒊𝒍𝒆 (𝒐𝒓 𝒖𝒔𝒆 /pip)

👑 𝑫𝒆𝒗: @𝑺𝒖𝒏𝒓𝒂𝒌𝒖𝑽2
📢 𝑪𝒉𝒂𝒏𝒏𝒆𝒍: @𝑨𝒏𝒊𝒔𝒉𝒑𝒚 | @𝑽𝑶𝑼𝑪𝑯_𝑹
"""
    bot.reply_to(message, welcome_msg, reply_markup=main_menu())

# ============================================================
# 📤 UPLOAD FILE
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "🟦 📤 𝑼𝑷𝑳𝑶𝑨𝑫 𝑭𝑰𝑳𝑬")
def upload_file(message):
    msg1 = bot.reply_to(message, "📤 **Send your .py file** (max 5MB)\n\n📌 File will be sent for approval.", parse_mode='Markdown')
    bot.register_next_step_handler(msg1, get_variables)

def get_variables(message):
    chat_id = message.chat.id
    
    with lock:
        if chat_id not in user_sessions:
            user_sessions[chat_id] = UserSession(chat_id)
        session = user_sessions[chat_id]
    
    msg2 = bot.reply_to(message, "🤖 **Enter your BOT TOKEN:**\n\n📌 This will be automatically added to your file.", parse_mode='Markdown')
    bot.register_next_step_handler(msg2, lambda m: get_chat_id(m, session))

def get_chat_id(message, session):
    session.user_bot_token = message.text.strip()
    
    msg3 = bot.reply_to(message, "📌 **Enter your CHAT ID:**\n\n📌 This will be automatically added to your file.", parse_mode='Markdown')
    bot.register_next_step_handler(msg3, lambda m: handle_file_upload_with_vars(m, session))

def handle_file_upload_with_vars(message, session):
    chat_id = message.chat.id
    session.user_chat_id = message.text.strip()
    
    bot.reply_to(message, "✅ **Variables saved!**\n\n📤 Now send your .py file.", parse_mode='Markdown')

# ============================================================
# 📦 INSTALL PIP PACKAGE FOR USER FILE
# ============================================================
PACKAGE_SPEC_RE = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]*(?:\[[A-Za-z0-9_,.-]+\])?"
    r"(?:(?:==|!=|~=|>=|<=|>|<)[A-Za-z0-9.*+!_-]+)?$"
)

@bot.message_handler(commands=['pip'])
@bot.message_handler(func=lambda msg: msg.text in ["📦 INSTALL PIP", "🔷 📦 𝑰𝑵𝑺𝑻𝑨𝑳𝑳 𝑷𝑰𝑷"])
def install_pip_button(message):
    chat_id = message.chat.id
    with lock:
        if chat_id not in user_sessions:
            user_sessions[chat_id] = UserSession(chat_id)
        session = user_sessions[chat_id]

    if not session.file_path or not os.path.exists(session.file_path):
        bot.reply_to(
            message,
            "📁 **Pehle apni .py file upload ya select karo.**\n\n"
            "Uske baad is button se us file ki requirements install kar sakte ho.",
            parse_mode='Markdown'
        )
        return

    prompt = bot.reply_to(
        message,
        f"📦 **Packages for:** `{os.path.basename(session.file_path)}`\n\n"
        "Package names space se separate karke bhejo.\n\n"
        "Example:\n`requests pyTelegramBotAPI`\n"
        "or:\n`requests==2.32.3`\n\n"
        "Type `/cancel` to cancel.",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(prompt, install_pip_packages)

def install_pip_packages(message):
    chat_id = message.chat.id
    with lock:
        if chat_id not in user_sessions:
            user_sessions[chat_id] = UserSession(chat_id)
        session = user_sessions[chat_id]

    if not session.file_path or not os.path.exists(session.file_path):
        bot.reply_to(message, "📁 **File not found. Upload/select your file first.**", parse_mode='Markdown')
        return

    package_text = (message.text or "").strip()
    if package_text.lower() == "/cancel":
        bot.reply_to(message, "❎ **Pip installation cancelled.**", parse_mode='Markdown')
        return

    packages = package_text.split()
    if not packages:
        bot.reply_to(message, "❌ **No package name received.**", parse_mode='Markdown')
        return

    if len(packages) > 20 or any(not PACKAGE_SPEC_RE.fullmatch(pkg) for pkg in packages):
        bot.reply_to(
            message,
            "❌ **Invalid package list.**\n\n"
            "Use normal PyPI names only, for example:\n"
            "`requests flask==3.0.3`",
            parse_mode='Markdown'
        )
        return

    package_list = " ".join(packages)
    bot.reply_to(
        message,
        f"⏳ **Installing:** `{package_list}`\n\nPlease wait...",
        parse_mode='Markdown'
    )

    def pip_worker():
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--disable-pip-version-check",
                    *packages
                ],
                capture_output=True,
                text=True,
                timeout=180
            )
            output = (result.stdout or "") + (result.stderr or "")
            output = output.strip() or "No output returned."
            if len(output) > 3500:
                output = output[-3500:]

            if result.returncode == 0:
                title = "✅ Pip installation completed."
                session.installed_packages.extend(packages)
                session.add_log(f"📦 Packages installed: {package_list}")
            else:
                title = f"❌ Pip installation failed (exit code {result.returncode})."
                session.add_log(f"❌ Pip installation failed: {package_list}")

            bot.send_message(message.chat.id, f"{title}\n\n{output}")
        except subprocess.TimeoutExpired:
            bot.send_message(message.chat.id, "⏱️ Pip installation timed out after 180 seconds.")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Pip error: {e}")

    threading.Thread(target=pip_worker, daemon=True).start()

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
        session.is_approved = False
    
    try:
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_path = os.path.join(UPLOAD_DIR, f"{chat_id}_{message.document.file_name}")
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        
        session.file_path = file_path
        session.add_log(f"📤 File uploaded: {message.document.file_name}")
        
        if session.user_bot_token and session.user_chat_id:
            replace_variables_in_file(file_path, session.user_bot_token, session.user_chat_id)
            session.add_log("✅ Variables replaced in file")
        
        success = send_approval_request(
            chat_id, 
            message.document.file_name, 
            file_path,
            session.user_bot_token,
            session.user_chat_id
        )
        
        if success:
            bot.reply_to(message, f"✅ **File uploaded successfully!**\n📁 `{message.document.file_name}`\n\n⏳ **Waiting for owner approval...**\nYou will be notified when approved.", parse_mode='Markdown')
        else:
            bot.reply_to(message, f"⚠️ **File uploaded but approval failed!**\nPlease contact @SunrakuV2 manually.", parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"❌ **Upload failed:** {str(e)}", parse_mode='Markdown')

# ============================================================
# 🔥 DEFAULT FILE (Fixed)
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "🟤 🔥 𝑫𝑬𝑭𝑨𝑼𝑳𝑻 𝑭𝑰𝑳𝑬")
def set_default_file(message):
    chat_id = message.chat.id
    
    with lock:
        if chat_id not in user_sessions:
            user_sessions[chat_id] = UserSession(chat_id)
        session = user_sessions[chat_id]
    
    msg1 = bot.reply_to(message, "🤖 **Enter your BOT TOKEN for default file:**", parse_mode='Markdown')
    bot.register_next_step_handler(msg1, lambda m: get_default_vars(m, session))

def get_default_vars(message, session):
    session.user_bot_token = message.text.strip()
    
    msg2 = bot.reply_to(message, "📌 **Enter your CHAT ID:**", parse_mode='Markdown')
    bot.register_next_step_handler(msg2, lambda m: set_default_with_vars(m, session))

def set_default_with_vars(message, session):
    chat_id = message.chat.id
    session.user_chat_id = message.text.strip()
    
    default_path = os.path.join(UPLOAD_DIR, f"default_scanner_{chat_id}.py")
    
    # 🔥 Default file with user's variables
    default_content = DEFAULT_FILE_TEMPLATE.format(
        BOT_TOKEN=session.user_bot_token,
        CHAT_ID=session.user_chat_id
    )
    
    with open(default_path, 'w', encoding='utf-8') as f:
        f.write(default_content)
    
    session.file_path = default_path
    session.is_approved = False
    session.add_log("🔥 Default file selected - pending approval")
    
    success = send_approval_request(
        chat_id, 
        "default_scanner.py", 
        default_path,
        session.user_bot_token,
        session.user_chat_id
    )
    
    if success:
        bot.reply_to(message, "✅ **Default scanner selected!**\n\n⏳ **Waiting for owner approval...**\nYou will be notified when approved.", parse_mode='Markdown')
    else:
        bot.reply_to(message, "⚠️ **Default file selected but approval failed!**\nPlease contact @SunrakuV2.", parse_mode='Markdown')

# ============================================================
# 🚀 RUN FILE
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "🟢 🚀 𝑹𝑼𝑵 𝑭𝑰𝑳𝑬")
def run_file(message):
    chat_id = message.chat.id
    
    with lock:
        if chat_id not in user_sessions:
            user_sessions[chat_id] = UserSession(chat_id)
        session = user_sessions[chat_id]
    
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
        session.process = subprocess.Popen(
            # -u makes Python child scripts flush output immediately.
            [sys.executable, "-u", session.file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        session.is_running = True
        session.start_time = datetime.now()
        session.end_time = None
        session.total_checks = 0
        session.speed = 0
        session.add_log(f"🚀 File started: {os.path.basename(session.file_path)}")
        
        def read_logs():
            # Keep reading until the process really exits. The old loop
            # depended on is_running and could leave status stuck at RUNNING.
            while True:
                try:
                    output = session.process.stdout.readline()
                    if output:
                        session.add_log(output.strip())
                        session.total_checks += 1
                        continue

                    if session.process.poll() is not None:
                        break
                    time.sleep(0.05)
                except Exception as e:
                    session.add_log(f"⚠️ Log reader error: {e}")
                    break
            
            return_code = session.process.poll()
            session.is_running = False
            session.end_time = datetime.now()
            if return_code == 0:
                session.add_log("✅ File finished")
            elif return_code is not None:
                session.add_log(f"⚠️ File exited with code {return_code}")
        
        threading.Thread(target=read_logs, daemon=True).start()
        
        bot.reply_to(message, f"✅ **File started!**\n📁 `{os.path.basename(session.file_path)}`\n\n📋 Click **VIEW LOGS** to see output.\n📊 Click **LIVE STATUS** to check progress.", parse_mode='Markdown')
        
    except Exception as e:
        session.is_running = False
        session.add_log(f"❌ Run error: {str(e)}")
        bot.reply_to(message, f"❌ **Error:** {str(e)}", parse_mode='Markdown')

# ============================================================
# ⏹ STOP FILE
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "🔴 ⏹ 𝑺𝑻𝑶𝑷 𝑭𝑰𝑳𝑬")
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
        # Set this before terminate so the status changes immediately.
        session.is_running = False
        session.process.terminate()
        time.sleep(1)
        if session.process.poll() is None:
            session.process.kill()
        
        session.end_time = datetime.now()
        session.add_log("⏹ File stopped")
        
        bot.reply_to(message, "⏹ **File stopped successfully!**", parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"❌ **Stop error:** {str(e)}", parse_mode='Markdown')

# ============================================================
# 📋 VIEW LOGS
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "🟡 📋 𝑽𝑰𝑬𝑾 𝑳𝑶𝑮𝑺")
def view_logs(message):
    chat_id = message.chat.id
    
    with lock:
        if chat_id not in user_sessions:
            bot.reply_to(message, "❌ No session found!", parse_mode='Markdown')
            return
        session = user_sessions[chat_id]
    
    logs = session.get_logs(25)
    if not logs:
        bot.reply_to(message, "📋 **No logs yet.**\n\nRun a file to see output.", parse_mode='Markdown')
        return
    
    bot.reply_to(message, f"📋 **Recent Logs:**\n```\n{logs}\n```", parse_mode='Markdown')

# ============================================================
# 📊 LIVE STATUS (Fixed — Proper Working)
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "🟣 📊 𝑳𝑰𝑽𝑬 𝑺𝑻𝑨𝑻𝑼𝑺")
def show_live_status(message):
    chat_id = message.chat.id
    
    with lock:
        if chat_id not in user_sessions:
            bot.reply_to(message, "❌ **No session found!**\n\n📌 Please /start first.", parse_mode='Markdown')
            return
        session = user_sessions[chat_id]

    # Catch a child process that ended between two status button presses.
    if session.process and session.process.poll() is not None and session.is_running:
        session.is_running = False
        session.end_time = session.end_time or datetime.now()
    
    status_icon = "🟢" if session.is_running else "🔴"
    status_text = "RUNNING" if session.is_running else "STOPPED"
    approved_text = "✅ Approved" if session.is_approved else "⏳ Pending Approval"
    file_name = os.path.basename(session.file_path) if session.file_path else "None"
    runtime = session.get_runtime()
    speed = session.get_speed()
    
    status_msg = f"""
📊 **LIVE STATUS**

📁 **File:** `{file_name}`
{status_icon} **Status:** `{status_text}`
✅ **Approval:** `{approved_text}`
⏱ **Runtime:** `{runtime}`
📊 **Checks:** `{session.total_checks}`
📈 **Speed:** `{speed}` checks/min
📋 **Logs:** `{len(session.logs)}` lines

━━━━━━━━━━━━━━━━━━━━━━━━━
👑 @SunrakuV2 | 📢 @Anishpy | @VOUCH_R
"""
    bot.reply_to(message, status_msg, parse_mode='Markdown')

# ============================================================
# ⚡ SPEED (Fixed — Proper Working)
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "🟠 ⚡ 𝑺𝑷𝑬𝑬𝑫")
def show_speed(message):
    chat_id = message.chat.id
    
    with lock:
        if chat_id not in user_sessions:
            bot.reply_to(message, "❌ **No session found!**\n\n📌 Please /start first.", parse_mode='Markdown')
            return
        session = user_sessions[chat_id]
    
    if not session.start_time:
        bot.reply_to(message, "⚠️ **No file has been run yet!**\n\n📌 Start a file first using **RUN FILE**.", parse_mode='Markdown')
        return
    
    if session.process and session.process.poll() is not None and session.is_running:
        session.is_running = False
        session.end_time = session.end_time or datetime.now()

    runtime = session.get_runtime()
    speed = session.get_speed()
    run_state = "🟢 Running" if session.is_running else "🔴 Stopped/Finished"
    
    speed_msg = f"""
⚡ **SPEED REPORT**

📌 **State:** `{run_state}`
📊 **Total Checks:** `{session.total_checks}`
⏱ **Runtime:** `{runtime}`
⚡ **Speed:** `{speed}` checks/min

📈 **Performance:** {'🚀 Fast' if speed > 100 else '🐢 Slow' if speed < 30 else '⚡ Average'}

━━━━━━━━━━━━━━━━━━━━━━━━━
👑 @SunrakuV2 | 📢 @Anishpy | @VOUCH_R
"""
    bot.reply_to(message, speed_msg, parse_mode='Markdown')

# ============================================================
# 👑 DEV
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "⚫ 👑 𝑫𝑬𝑽")
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
