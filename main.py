#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 SUNRAKU — FAST SCANNER BOT 🔥
- Har user apna bot token + chat ID daalega
- Hits sirf usi user ke bot mein jaayengi
- 30 threads — fast scanning
- Total Hits + View All Hits (Main Bot mein)
- ALL CAPS SERIF FONT BUTTONS
- FORCE SUBSCRIBE: @Anishpy, @VOUCH_R, Request Group
- Dev: @SunrakuV2 | Channel: @Anishpy
"""

import os
import sys
import time
import random
import json
import re
import requests
import threading
import uuid
import secrets
import base64
import httpx
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from user_agent import generate_user_agent
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ============================================================
# 🎨 TERMINAL COLORS
# ============================================================
RESET = "\033[0m"
DARK_PURPLE = "\033[38;5;54m"
NEON_PINK = "\033[38;5;213m"
NEON_BLUE = "\033[38;5;51m"
GOLD = "\033[38;5;220m"
WHITE = "\033[97m"
GREEN = "\033[38;5;46m"
RED = "\033[38;5;196m"
CYAN = "\033[38;5;51m"
ORANGE = "\033[38;5;208m"

# ============================================================
# 🔥 RAILWAY READY — ENVIRONMENT VARIABLE
# ============================================================
MAIN_BOT_TOKEN = os.getenv("BOT_TOKEN")
if not MAIN_BOT_TOKEN:
    print(f"{RED}❌ BOT_TOKEN environment variable not set!{RESET}")
    sys.exit()

main_bot = TeleBot(MAIN_BOT_TOKEN)

# ============================================================
# 📊 GLOBALS
# ============================================================
user_sessions = {}
lock = threading.Lock()
THREADS = 30

# ============================================================
# 🔥 FORCE SUBSCRIBE CHANNELS (Group ID Set)
# ============================================================
REQUIRED_CHANNELS = [
    {"id": -1004456548997, "username": "@Anishpy", "link": "https://t.me/Anishpy"},
    {"id": -1004320460507, "username": "@VOUCH_R", "link": "https://t.me/VOUCH_R"},
    {"id": -1004472230708, "username": "Request Group", "link": "https://t.me/+s5v5rCbhorpkYTEx"}  # 🔥 Group ID + Link Set
]

# ============================================================
# 🔥 CONFIG
# ============================================================
CONFIG_URL = "https://raw.githubusercontent.com/a3564119-netizen/Sunraku-Config/main/config.json"

try:
    data = requests.get(CONFIG_URL, timeout=10).json()
except:
    print("❌ Config fetch failed!")
    sys.exit()

TARGET_TOOL_NAME = "𝐒𝐮𝐧𝐫𝐚𝐤𝐮 × 𝐕𝐄𝐑𝐈𝐅𝐈𝐄𝐃"
tool = next((t for t in data["tools"] if t["tool_name"] == TARGET_TOOL_NAME), None)

if not tool:
    print("❌ Tool not found!")
    sys.exit()

FORCE_JOIN = tool["force_join"]
CHANNELS = tool["channels"]
CHECKER_BOT_TOKEN = tool["checker_bot_token"]
TRACKER_BOT_TOKEN = tool["tracker_bot_token"]
ADMIN_CHAT_IDS = tool["admins"]

checker_bot = TeleBot(CHECKER_BOT_TOKEN)
tracker_bot = TeleBot(TRACKER_BOT_TOKEN)

# ============================================================
# 🔥 CHECK JOIN (Bot Admin Hai Toh Sab Check Ho Jayega)
# ============================================================
def check_join(chat_id):
    """Check if user has joined all required channels"""
    joined = []
    not_joined = []

    for channel in REQUIRED_CHANNELS:
        cid = channel["id"]
        username = channel["username"]

        try:
            if not chat_id:
                not_joined.append(username)
                continue

            # 🔥 Bot admin hai toh koi error nahi aayega
            member = checker_bot.get_chat_member(cid, int(chat_id))
            status = member.status

            if status in ["member", "administrator", "creator"]:
                joined.append(username)
            else:
                not_joined.append(username)

        except Exception as e:
            print(f"⚠️ Error checking {username}: {e}")
            not_joined.append(username)

    return len(not_joined) == 0, not_joined

# ============================================================
# 🔥 FORCE SUBSCRIBE BUTTONS
# ============================================================
def force_subscribe_markup():
    """Buttons to join required channels"""
    markup = InlineKeyboardMarkup(row_width=1)
    
    for channel in REQUIRED_CHANNELS:
        btn = InlineKeyboardButton(
            text=f"📢 JOIN {channel['username']}",
            url=channel["link"]
        )
        markup.add(btn)
    
    # 🔥 Check again button
    btn_check = InlineKeyboardButton(
        text="✅ I HAVE JOINED",
        callback_data="check_join"
    )
    markup.add(btn_check)
    
    return markup

@main_bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join_callback(call):
    """Check if user joined after clicking button"""
    user_id = call.from_user.id
    is_joined, not_joined_list = check_join(user_id)
    
    if is_joined:
        main_bot.edit_message_text(
            "✅ **Access Granted!**\n\nYou have joined all required channels.\nClick /start to use the bot.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
    else:
        missing = "\n".join(not_joined_list)
        main_bot.edit_message_text(
            f"❌ **Still Missing:**\n{missing}\n\nPlease join all channels first.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=force_subscribe_markup(),
            parse_mode='Markdown'
        )

# ============================================================
# 🔥 INSTAGRAM CHECKER
# ============================================================
class InstagramChecker:
    def __init__(self):
        self.session = requests.Session()
        self.csrf = None
        self.lsd = None
        self.doc_id = "26672929172408668"
        self.lock = threading.Lock()

    def _ensure_tokens(self):
        with self.lock:
            if self.csrf and self.lsd:
                return True
        try:
            headers = {
                'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
                'x-ig-app-id': "936619743392459",
                'x-bloks-version-id': "f0fd53409d7667526e529854656fe20159af8b76db89f40c333e593b51a2ce10",
                'origin': "https://www.instagram.com",
                'referer': "https://www.instagram.com/",
            }
            response = self.session.get('https://www.instagram.com/', headers=headers, timeout=20)
            if response.status_code == 200:
                csrf = response.cookies.get('csrftoken', '')
                match = re.search(r'"LSD",\[\],\{"token":"([^"]+)"\}', response.text)
                lsd = match.group(1) if match else None
                if csrf and lsd:
                    with self.lock:
                        self.csrf = csrf
                        self.lsd = lsd
                    return True
        except:
            pass
        return False

    def check_email(self, email):
        url = "https://i.instagram.com/api/v1/bloks/async_action/com.bloks.www.caa.ar.search.async/"
        device = "android-" + ''.join(random.choices('abcdef0123456789', k=16))
        family = str(uuid.uuid4())
        android = "android-" + ''.join(random.choices('abcdef0123456789', k=16))
        waterfall = str(uuid.uuid4())

        payload = {
            'params': "{\"client_input_params\":{\"aac\":\"{\\\"aac_init_timestamp\\\":"+ str(int(time.time())) +",\\\"aacjid\\\":\\\""+ str(uuid.uuid4()) +"\\\",\\\"aaccs\\\":\\\""+ secrets.token_urlsafe(32) +"\\\"}\",\"flash_call_permissions_status\":{\"READ_PHONE_STATE\":\"PERMANENTLY_DENIED\",\"READ_CALL_LOG\":\"DENIED\",\"ANSWER_PHONE_CALLS\":\"DENIED\"},\"was_headers_prefill_available\":0,\"network_bssid\":null,\"sfdid\":\"\",\"fetched_email_token_list\":{},\"search_query\":\""+ email +"\",\"auth_secure_device_id\":\"\",\"ig_oauth_token\":[],\"cloud_trust_token\":null,\"was_headers_prefill_used\":0,\"sso_accounts_auth_data\":[],\"encrypted_msisdn\":\"\",\"device_network_info\":null,\"text_input_id\":\"akyuf0:61\",\"zero_balance_state\":null,\"android_build_type\":\"release\",\"accounts_list\":[],\"is_oauth_without_permission\":0,\"ig_android_qe_device_id\":\""+ device +"\",\"gms_incoming_call_retriever_eligibility\":\"client_not_supported\",\"search_screen_type\":\"email_or_username\",\"is_whatsapp_installed\":1,\"lois_settings\":{\"lois_token\":\"\"},\"ig_vetted_device_nonce\":null,\"headers_infra_flow_id\":\"\",\"fetched_email_list\":[]},\"server_params\":{\"event_request_id\":\""+ str(uuid.uuid4()) +"\",\"is_from_logged_out\":0,\"layered_homepage_experiment_group\":null,\"device_id\":\""+ android +"\",\"login_surface\":\"login_home\",\"waterfall_id\":\""+ waterfall +"\",\"INTERNAL__latency_qpl_instance_id\":6.3987980400102E13,\"is_platform_login\":0,\"context_data\":\"\",\"login_entry_point\":\"logged_out\",\"INTERNAL__latency_qpl_marker_id\":36707139,\"family_device_id\":\""+ family +"\",\"offline_experiment_group\":\"caa_iteration_v3_perf_ig_4\",\"access_flow_version\":\"pre_mt_behavior\",\"is_from_logged_in_switcher\":0,\"qe_device_id\":\""+ device +"\"}}",
            'bk_client_context': "{\"bloks_version\":\"5e47baf35c5a270b44c8906c8b99063564b30ef69779f3dee0b828bee2e4ef5b\",\"styles_id\":\"instagram\"}",
            'bloks_versioning_id': "5e47baf35c5a270b44c8906c8b99063564b30ef69779f3dee0b828bee2e4ef5b"
        }
        headers = {
            'User-Agent': "Instagram 320.0.0.34.109 Android (33/13; 420dpi; 1080x2340; samsung; SM-A546B; a54x; exynos1380; en_US; 465123678)",
            'accept-language': "en-IN, en-US",
            'x-bloks-version-id': "5e47baf35c5a270b44c8906c8b99063564b30ef69779f3dee0b828bee2e4ef5b",
            'x-fb-friendly-name': "IgApi: bloks/async_action/com.bloks.www.caa.ar.search.async/",
            'x-ig-android-id': android,
            'x-ig-app-id': "567067343352427",
            'x-ig-app-locale': "en_IN",
            'x-ig-client-endpoint': "com.bloks.www.caa.ar.search",
            'x-ig-device-id': device,
            'x-ig-family-device-id': family,
            'x-ig-timezone-offset': str(int(datetime.now().astimezone().utcoffset().total_seconds())),
            'x-mid': base64.urlsafe_b64encode(secrets.token_bytes(18)).decode().rstrip('='),
            'x-pigeon-rawclienttime': str(time.time()),
            'x-pigeon-session-id': f"UFS-{uuid.uuid4()}-0",
            'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
        }
        try:
            resp = requests.post(url, data=payload, headers=headers, timeout=10)
            if f"{email}" in resp.text:
                return True
            return False
        except:
            return False

    def get_user_data(self, user_id):
        if not self._ensure_tokens():
            return None
        url = "https://www.instagram.com/api/graphql"
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-bloks-version-id': "f0fd53409d7667526e529854656fe20159af8b76db89f40c333e593b51a2ce10",
            'x-ig-app-id': '936619743392459',
            'x-fb-lsd': self.lsd,
            'x-csrftoken': self.csrf,
            'x-fb-friendly-name': 'PolarisProfilePageContentQuery',
            'sec-ch-ua-platform': '"Android"',
            'origin': 'https://www.instagram.com',
            'sec-fetch-site': 'same-origin'
        }
        cookies = {'rur': '"HIL\\0545636887483\\0541808136332:01fe43b89fcef61b8a466bfa81acf2b1bbab08f406fc99b1da8b7d889fa68683a3364c43"'}
        variables = {
            "enable_integrity_filters": True,
            "id": str(user_id),
            "__relay_internal__pv__PolarisCannesGuardianExperienceEnabledrelayprovider": True,
            "__relay_internal__pv__PolarisCASB976ProfileEnabledrelayprovider": False,
            "__relay_internal__pv__PolarisWebSchoolsEnabledrelayprovider": False,
            "__relay_internal__pv__PolarisRepostsConsumptionEnabledrelayprovider": False,
        }
        payload = {
            'lsd': self.lsd,
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'PolarisProfilePageContentQuery',
            'variables': json.dumps(variables),
            'server_timestamps': 'true',
            'doc_id': self.doc_id,
        }
        try:
            response = self.session.post(url, headers=headers, data=payload, cookies=cookies, timeout=10)
            if response.status_code == 200:
                data = response.json()
                user = data.get('data', {}).get('user')
                if user and user.get('username'):
                    return user
        except:
            pass
        return None

# ============================================================
# 🚀 FAST SCANNER
# ============================================================
def scanner_for_user(chat_id, user_bot_token):
    global user_sessions
    
    user_bot = TeleBot(user_bot_token)
    insta = InstagramChecker()
    
    with lock:
        if chat_id not in user_sessions:
            user_sessions[chat_id] = {
                'hits': 0, 'good': 0, 'bad': 0, 'total': 0,
                'hits_list': [], 'current_email': 'Waiting...',
                'is_running': True, 'stop_flag': False
            }
    
    while True:
        with lock:
            if chat_id not in user_sessions or user_sessions[chat_id].get('stop_flag', False):
                break
            session = user_sessions[chat_id]
        
        try:
            user_id = random.randint(2500000000, 21254029834)
            user_data = insta.get_user_data(user_id)
            
            if not user_data:
                continue

            username = user_data.get('username')
            if not username:
                continue

            email = f"{username}@gmail.com"
            session['current_email'] = email
            session['total'] += 1

            if insta.check_email(email):
                session['good'] += 1
                session['hits'] += 1
                
                hit_entry = {
                    'username': username,
                    'email': email,
                    'followers': user_data.get('follower_count', 0),
                    'time': datetime.now().strftime('%H:%M:%S')
                }
                session['hits_list'].append(hit_entry)
                
                hit_msg = f"""
✅ HIT FOUND!
👤 @{username}
📧 {email}
👥 {user_data.get('follower_count', 0)} followers
━━━━━━━━━━━━━━━━━━━━━━━━━
👑 @SunrakuV2 | 📢 @Anishpy
🎉 500 SUBS SPECIAL
"""
                try:
                    user_bot.send_message(chat_id, hit_msg)
                except:
                    pass
            else:
                session['bad'] += 1

            time.sleep(random.uniform(0.05, 0.15))

        except:
            time.sleep(random.uniform(0.1, 0.2))

# ============================================================
# 📊 LIVE STATUS
# ============================================================
def send_status_to_user(chat_id, user_bot_token):
    global user_sessions
    
    with lock:
        if chat_id not in user_sessions:
            return
        session = user_sessions[chat_id]
    
    status_msg = f"""
┌─────────────────────────────────────────┐
│  ✦ SUNRAKU 500 BOT ✦                   │
├─────────────────────────────────────────┤
│  ✅ GOOD  : {session['good']}  🔥 HITS : {session['hits']}  ❌ BAD : {session['bad']} │
│  📊 TOTAL : {session['total']}           │
│  📧 {session['current_email'][:30]:<30} │
│  ◈ @SunrakuV2  ●  @Anishpy             │
└─────────────────────────────────────────┘
"""
    try:
        user_bot = TeleBot(user_bot_token)
        user_bot.send_message(chat_id, status_msg)
    except:
        pass

# ============================================================
# 🔥 BOT COMMANDS & BUTTONS
# ============================================================

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("🚀 𝑹𝑼𝑵 𝑭𝑰𝑳𝑬")
    btn2 = KeyboardButton("⏹ 𝑺𝑻𝑶𝑷")
    btn3 = KeyboardButton("📊 𝑻𝑶𝑻𝑨𝑳 𝑯𝑰𝑻𝑺")
    btn4 = KeyboardButton("📋 𝑽𝑰𝑬𝑾 𝑨𝑳𝑳")
    btn5 = KeyboardButton("📢 𝑪𝑯𝑨𝑵𝑵𝑬𝑳")
    btn6 = KeyboardButton("👑 𝑫𝑬𝑽")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup

@main_bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    is_joined, not_joined_list = check_join(user_id)
    
    if not is_joined:
        missing = "\n".join(not_joined_list)
        msg = f"""
☠️ **𝑺𝑼𝑵𝑹𝑨𝑲𝑼 𝟓𝟎𝟎 𝑩𝑶𝑻** ☠️

❌ **MUST JOIN THESE CHANNELS FIRST:**

📢 **{missing}**

🔽 **Click buttons below to join:**

After joining, click **"✅ I HAVE JOINED"** to continue.
"""
        main_bot.reply_to(
            message, 
            msg, 
            reply_markup=force_subscribe_markup(),
            parse_mode='Markdown'
        )
        return
    
    welcome_msg = f"""
☠️ 𝑺𝑼𝑵𝑹𝑨𝑲𝑼 𝟓𝟎𝟎 𝑩𝑶𝑻 ☠️

🔥 𝑪𝒍𝒊𝒄𝒌 𝒃𝒖𝒕𝒕𝒐𝒏𝒔 𝒃𝒆𝒍𝒐𝒘 𝒕𝒐 𝒄𝒐𝒏𝒕𝒓𝒐𝒍.

📌 𝑬𝒏𝒕𝒆𝒓 𝒚𝒐𝒖𝒓 𝑪𝑯𝑨𝑻 𝑰𝑫 𝒂𝒏𝒅 𝑩𝑶𝑻 𝑻𝑶𝑲𝑬𝑵
   𝑯𝒊𝒕𝒔 𝒘𝒊𝒍𝒍 𝒃𝒆 𝒔𝒆𝒏𝒕 𝒕𝒐 𝒀𝑶𝑼𝑹 𝒃𝒐𝒕 𝒐𝒏𝒍𝒚.

👑 𝑫𝒆𝒗: @𝑺𝒖𝒏𝒓𝒂𝒌𝒖𝑽2
📢 𝑪𝒉𝒂𝒏𝒏𝒆𝒍: @𝑨𝒏𝒊𝒔𝒉𝒑𝒚
🎉 𝟓𝟎𝟎 𝑺𝑼𝑩𝑺 𝑺𝑷𝑬𝑪𝑰𝑨𝑳
"""
    main_bot.reply_to(message, welcome_msg, reply_markup=main_menu())

@main_bot.message_handler(func=lambda msg: msg.text == "🚀 𝑹𝑼𝑵 𝑭𝑰𝑳𝑬")
def run_file(message):
    user_id = message.from_user.id
    is_joined, _ = check_join(user_id)
    
    if not is_joined:
        main_bot.reply_to(
            message, 
            "❌ **You must join all required channels first!**\nClick /start to see join buttons.",
            parse_mode='Markdown'
        )
        return
    
    msg1 = main_bot.reply_to(message, "✏️ 𝑬𝒏𝒕𝒆𝒓 𝒚𝒐𝒖𝒓 𝑪𝑯𝑨𝑻 𝑰𝑫:")
    main_bot.register_next_step_handler(msg1, get_chat_id)

def get_chat_id(message):
    user_chat_id = message.text.strip()
    msg2 = main_bot.reply_to(message, "✏️ 𝑬𝒏𝒕𝒆𝒓 𝒚𝒐𝒖𝒓 𝑩𝑶𝑻 𝑻𝑶𝑲𝑬𝑵:")
    main_bot.register_next_step_handler(msg2, lambda m: get_bot_token(m, user_chat_id))

def get_bot_token(message, user_chat_id):
    user_bot_token = message.text.strip()
    
    if not user_chat_id or not user_bot_token:
        main_bot.reply_to(message, "❌ 𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝒊𝒏𝒑𝒖𝒕!", reply_markup=main_menu())
        return
    
    try:
        test_bot = TeleBot(user_bot_token)
        test_bot.get_me()
    except:
        main_bot.reply_to(message, "❌ 𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝑩𝒐𝒕 𝑻𝒐𝒌𝒆𝒏!", reply_markup=main_menu())
        return
    
    with lock:
        if user_chat_id in user_sessions and user_sessions[user_chat_id].get('is_running', False):
            main_bot.reply_to(message, "⚠️ 𝑺𝒄𝒂𝒏𝒏𝒆𝒓 𝒂𝒍𝒓𝒆𝒂𝒅𝒚 𝒓𝒖𝒏𝒏𝒊𝒏𝒈!", reply_markup=main_menu())
            return
        
        user_sessions[user_chat_id] = {
            'hits': 0, 'good': 0, 'bad': 0, 'total': 0,
            'hits_list': [], 'current_email': 'Waiting...',
            'is_running': True, 'stop_flag': False
        }
    
    main_bot.reply_to(message, f"""✅ 𝑺𝒄𝒂𝒏𝒏𝒆𝒓 𝒔𝒕𝒂𝒓𝒕𝒆𝒅!
📤 𝑯𝒊𝒕𝒔 𝒘𝒊𝒍𝒍 𝒈𝒐 𝒕𝒐 𝒀𝑶𝑼𝑹 𝒃𝒐𝒕.
🤖 𝑩𝒐𝒕: @{test_bot.get_me().username}

⏹ 𝑪𝒍𝒊𝒄𝒌 𝑺𝒕𝒐𝒑 𝒕𝒐 𝒆𝒏𝒅.""", reply_markup=main_menu())
    
    for _ in range(THREADS):
        threading.Thread(target=scanner_for_user, args=(user_chat_id, user_bot_token), daemon=True).start()
    
    def status_updater():
        while True:
            with lock:
                if user_chat_id not in user_sessions or not user_sessions[user_chat_id].get('is_running', False):
                    break
            send_status_to_user(user_chat_id, user_bot_token)
            time.sleep(5)
    
    threading.Thread(target=status_updater, daemon=True).start()

@main_bot.message_handler(func=lambda msg: msg.text == "⏹ 𝑺𝑻𝑶𝑷")
def stop_scanner(message):
    global user_sessions
    msg1 = main_bot.reply_to(message, "✏️ 𝑬𝒏𝒕𝒆𝒓 𝒚𝒐𝒖𝒓 𝑪𝑯𝑨𝑻 𝑰𝑫:")
    main_bot.register_next_step_handler(msg1, stop_by_chat)

def stop_by_chat(message):
    global user_sessions
    user_chat_id = message.text.strip()
    
    with lock:
        if user_chat_id not in user_sessions:
            main_bot.reply_to(message, "❌ 𝑵𝒐 𝒔𝒄𝒂𝒏𝒏𝒆𝒓 𝒇𝒐𝒖𝒏𝒅!", reply_markup=main_menu())
            return
        
        if not user_sessions[user_chat_id].get('is_running', False):
            main_bot.reply_to(message, "⚠️ 𝑵𝒐𝒕 𝒓𝒖𝒏𝒏𝒊𝒏𝒈!", reply_markup=main_menu())
            return
        
        user_sessions[user_chat_id]['stop_flag'] = True
        user_sessions[user_chat_id]['is_running'] = False
    
    main_bot.reply_to(message, f"⏹ 𝑺𝒕𝒐𝒑𝒑𝒆𝒅!", reply_markup=main_menu())

@main_bot.message_handler(func=lambda msg: msg.text == "📊 𝑻𝑶𝑻𝑨𝑳 𝑯𝑰𝑻𝑺")
def total_hits(message):
    global user_sessions
    msg1 = main_bot.reply_to(message, "✏️ 𝑬𝒏𝒕𝒆𝒓 𝒚𝒐𝒖𝒓 𝑪𝑯𝑨𝑻 𝑰𝑫:")
    main_bot.register_next_step_handler(msg1, show_total_hits)

def show_total_hits(message):
    global user_sessions
    user_chat_id = message.text.strip()
    
    with lock:
        if user_chat_id not in user_sessions:
            main_bot.reply_to(message, "❌ 𝑵𝒐 𝒔𝒄𝒂𝒏𝒏𝒆𝒓 𝒇𝒐𝒖𝒏𝒅!", reply_markup=main_menu())
            return
        session = user_sessions[user_chat_id]
    
    status_msg = f"""
┌─────────────────────────────────────────┐
│  ✦ 𝑺𝑼𝑵𝑹𝑨𝑲𝑼 𝟓𝟎𝟎 𝑩𝑶𝑻 ✦                   │
├─────────────────────────────────────────┤
│  ✅ 𝑮𝑶𝑶𝑫  : {session['good']}  🔥 𝑯𝑰𝑻𝑺 : {session['hits']}  ❌ 𝑩𝑨𝑫 : {session['bad']} │
│  📊 𝑻𝑶𝑻𝑨𝑳 : {session['total']}           │
│  📧 {session['current_email'][:30]:<30} │
│  ◈ @𝑺𝒖𝒏𝒓𝒂𝒌𝒖𝑽2  ●  @𝑨𝒏𝒊𝒔𝒉𝒑𝒚             │
└─────────────────────────────────────────┘
"""
    main_bot.reply_to(message, status_msg, reply_markup=main_menu())

@main_bot.message_handler(func=lambda msg: msg.text == "📋 𝑽𝑰𝑬𝑾 𝑨𝑳𝑳")
def view_all_hits(message):
    global user_sessions
    msg1 = main_bot.reply_to(message, "✏️ 𝑬𝒏𝒕𝒆𝒓 𝒚𝒐𝒖𝒓 𝑪𝑯𝑨𝑻 𝑰𝑫:")
    main_bot.register_next_step_handler(msg1, show_all_hits)

def show_all_hits(message):
    global user_sessions
    user_chat_id = message.text.strip()
    
    with lock:
        if user_chat_id not in user_sessions:
            main_bot.reply_to(message, "❌ 𝑵𝒐 𝒔𝒄𝒂𝒏𝒏𝒆𝒓 𝒇𝒐𝒖𝒏𝒅!", reply_markup=main_menu())
            return
        hits_list = user_sessions[user_chat_id].get('hits_list', [])
    
    if not hits_list:
        main_bot.reply_to(message, "📋 𝑵𝒐 𝒉𝒊𝒕𝒔 𝒚𝒆𝒕!", reply_markup=main_menu())
        return
    
    hit_list = "📋 𝑨𝑳𝑳 𝑯𝑰𝑻𝑺\n━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    for i, hit in enumerate(hits_list, 1):
        hit_list += f"{i}. @{hit['username']} | {hit['email']} | {hit['followers']} followers\n"
        if len(hit_list) > 3800:
            hit_list += "\n... and more!"
            break
    
    hit_list += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━\n📊 𝑻𝒐𝒕𝒂𝒍: {len(hits_list)} hits"
    hit_list += "\n👑 @𝑺𝒖𝒏𝒓𝒂𝒌𝒖𝑽2 | 📢 @𝑨𝒏𝒊𝒔𝒉𝒑𝒚"
    
    main_bot.reply_to(message, hit_list, reply_markup=main_menu())

@main_bot.message_handler(func=lambda msg: msg.text == "📢 𝑪𝑯𝑨𝑵𝑵𝑬𝑳")
def send_channel(message):
    markup = InlineKeyboardMarkup()
    for channel in REQUIRED_CHANNELS:
        btn = InlineKeyboardButton(text=f"📢 {channel['username']}", url=channel["link"])
        markup.add(btn)
    main_bot.reply_to(message, "📢 𝑱𝒐𝒊𝒏 𝒐𝒖𝒓 𝒄𝒉𝒂𝒏𝒏𝒆𝒍𝒔:", reply_markup=markup)

@main_bot.message_handler(func=lambda msg: msg.text == "👑 𝑫𝑬𝑽")
def send_dev(message):
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(text="👑 @𝑺𝒖𝒏𝒓𝒂𝒌𝒖𝑽2", url="https://t.me/SunrakuV2")
    markup.add(btn)
    main_bot.reply_to(message, "👑 𝑫𝒆𝒗𝒆𝒍𝒐𝒑𝒆𝒓:", reply_markup=markup)

@main_bot.message_handler(func=lambda msg: True)
def echo_all(message):
    main_bot.reply_to(message, "❌ 𝑼𝒔𝒆 𝒃𝒖𝒕𝒕𝒐𝒏𝒔 👇", reply_markup=main_menu())

# ============================================================
# 🚀 START BOT
# ============================================================
print("✅ Main Bot is running...")
print("📌 Bot Username: @" + main_bot.get_me().username)
print("🎉 500 SUBS SPECIAL EDITION")
print("🔒 Force Subscribe: @Anishpy, @VOUCH_R, Request Group")

while True:
    try:
        main_bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"⚠️ Polling error: {e}")
        time.sleep(5)
        continue
