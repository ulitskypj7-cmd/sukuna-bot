#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 SUNRAKU — FAST SCANNER BOT 🔥
- Har user apna bot token + chat ID daalega
- Hits sirf usi user ke bot mein jaayengi
- 30 threads — fast scanning
- Total Hits + View All Hits (Main Bot mein)
- Dev: @SunrakuV2 | Channel: @Anishpy
"""

import sys
import os
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

# ============================================================
# 📸 CLEAN UI
# ============================================================
os.system('cls' if os.name == 'nt' else 'clear')

print(f"""
{DARK_PURPLE}╔═══════════════════════════════════════════════════════════╗
{DARK_PURPLE}║                                                           ║
{DARK_PURPLE}║               {NEON_PINK}✦  𝑺𝑼𝑵𝑹𝑨𝑲𝑼  ✦  {NEON_BLUE}𝑩𝑶𝑻                   ║
{DARK_PURPLE}║               {WHITE}𝑭𝑨𝑺𝑻 𝑺𝑪𝑨𝑵𝑵𝑬𝑹                           ║
{DARK_PURPLE}║                                                           ║
{DARK_PURPLE}║               {GOLD}🎉  𝟓𝟎𝟎 𝑺𝑼𝑩𝑺 𝑪𝑬𝑳𝑬𝑩𝑹𝑨𝑻𝑰𝑶𝑵  🎉               ║
{DARK_PURPLE}║                                                           ║
{DARK_PURPLE}║               {WHITE}◈  𝑬𝑵𝑻𝑬𝑹 𝑩𝑶𝑻 𝑻𝑶𝑲𝑬𝑵                          ║
{DARK_PURPLE}║                                                           ║
{DARK_PURPLE}╚═══════════════════════════════════════════════════════════╝
{RESET}
""")

print(f"{NEON_PINK}┌─────────────────────────────────────────────────────────┐")
MAIN_BOT_TOKEN = input(f"{NEON_PINK}│  ✦ 𝑩𝑶𝑻 𝑻𝑶𝑲𝑬𝑵 (Main Bot) ➜ {WHITE}").strip()
print(f"{NEON_PINK}└─────────────────────────────────────────────────────────┘{RESET}")

if not MAIN_BOT_TOKEN:
    print(f"{RED}❌ Bot Token required!{RESET}")
    sys.exit()

# ============================================================
# 🔥 INIT MAIN BOT
# ============================================================
main_bot = TeleBot(MAIN_BOT_TOKEN)

# ============================================================
# 📊 GLOBALS
# ============================================================
# 🔥 Har user ki alag list
user_sessions = {}  # {chat_id: {hits: 0, good: 0, bad: 0, total: 0, hits_list: [], is_running: False, stop_flag: False, threads: []}}
lock = threading.Lock()
THREADS = 30

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
# 🔥 CHECK JOIN
# ============================================================
def check_join(chat_id):
    joined = []
    not_joined = []

    for channel in CHANNELS:
        cid = int(channel["id"])
        username = channel["username"]

        try:
            if not chat_id:
                not_joined.append(username)
                continue

            member = checker_bot.get_chat_member(cid, int(chat_id))
            status = member.status

            if status in ["member", "administrator", "creator"]:
                joined.append(username)
            else:
                not_joined.append(username)

        except:
            not_joined.append(username)

    return len(not_joined) == 0, not_joined

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
# 🚀 FAST SCANNER — Har User Ki Alag Session
# ============================================================
def scanner_for_user(chat_id, user_bot_token):
    """Har user ke liye alag scanner"""
    global user_sessions
    
    # User ka bot initialize
    user_bot = TeleBot(user_bot_token)
    insta = InstagramChecker()
    
    # User session data
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
                
                # 🔥 Hit user ke bot mein bhejo
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
# 📊 LIVE STATUS — User Ke Bot Mein
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
# 🔥 BOT COMMANDS & BUTTONS (Main Bot)
# ============================================================

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("🚀 Run File")
    btn2 = KeyboardButton("⏹ Stop")
    btn3 = KeyboardButton("📊 Total Hits")
    btn4 = KeyboardButton("📋 View All Hits")
    btn5 = KeyboardButton("📢 Channel")
    btn6 = KeyboardButton("👑 Dev")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup

@main_bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = f"""
☠️ SUNRAKU 500 BOT ☠️

🔥 Click buttons below to control.

📌 Enter your CHAT ID and BOT TOKEN
   Hits will be sent to YOUR bot only.
   Your hits are separate from others.

👑 Dev: @SunrakuV2
📢 Channel: @Anishpy
🎉 500 SUBS SPECIAL EDITION
"""
    main_bot.reply_to(message, welcome_msg, reply_markup=main_menu())

@main_bot.message_handler(func=lambda msg: msg.text == "🚀 Run File")
def run_file(message):
    # Ask for Chat ID
    msg1 = main_bot.reply_to(message, "✏️ Enter your CHAT ID (where hits should go):")
    main_bot.register_next_step_handler(msg1, get_chat_id)

def get_chat_id(message):
    global user_sessions
    user_chat_id = message.text.strip()
    
    # Ask for Bot Token
    msg2 = main_bot.reply_to(message, "✏️ Now enter your BOT TOKEN (jisme hits aani chahiye):")
    main_bot.register_next_step_handler(msg2, lambda m: get_bot_token(m, user_chat_id))

def get_bot_token(message, user_chat_id):
    global user_sessions
    user_bot_token = message.text.strip()
    
    if not user_chat_id or not user_bot_token:
        main_bot.reply_to(message, "❌ Invalid input! Try again.", reply_markup=main_menu())
        return
    
    # Verify user's bot token
    try:
        test_bot = TeleBot(user_bot_token)
        test_bot.get_me()
    except:
        main_bot.reply_to(message, "❌ Invalid Bot Token! Try again.", reply_markup=main_menu())
        return
    
    # Check if already running for this user
    with lock:
        if user_chat_id in user_sessions and user_sessions[user_chat_id].get('is_running', False):
            main_bot.reply_to(message, "⚠️ Scanner already running for this Chat ID! Click Stop first.", reply_markup=main_menu())
            return
        
        # Create session
        user_sessions[user_chat_id] = {
            'hits': 0, 'good': 0, 'bad': 0, 'total': 0,
            'hits_list': [], 'current_email': 'Waiting...',
            'is_running': True, 'stop_flag': False
        }
    
    main_bot.reply_to(message, f"""✅ Scanner started!
📤 Hits will be sent to YOUR bot.
📌 Chat ID: {user_chat_id}
🤖 Bot: @{test_bot.get_me().username}

⏹ Click Stop to end.""", reply_markup=main_menu())
    
    # 🔥 30 threads start for this user
    for _ in range(THREADS):
        threading.Thread(target=scanner_for_user, args=(user_chat_id, user_bot_token), daemon=True).start()
    
    # Status updater for this user
    def status_updater():
        while True:
            with lock:
                if user_chat_id not in user_sessions or not user_sessions[user_chat_id].get('is_running', False):
                    break
            send_status_to_user(user_chat_id, user_bot_token)
            time.sleep(5)
    
    threading.Thread(target=status_updater, daemon=True).start()

@main_bot.message_handler(func=lambda msg: msg.text == "⏹ Stop")
def stop_scanner(message):
    global user_sessions
    
    msg1 = main_bot.reply_to(message, "✏️ Enter your CHAT ID to stop:")
    main_bot.register_next_step_handler(msg1, stop_scanner_by_chat)

def stop_scanner_by_chat(message):
    global user_sessions
    user_chat_id = message.text.strip()
    
    with lock:
        if user_chat_id not in user_sessions:
            main_bot.reply_to(message, "❌ No scanner found for this Chat ID!", reply_markup=main_menu())
            return
        
        if not user_sessions[user_chat_id].get('is_running', False):
            main_bot.reply_to(message, "⚠️ Scanner not running for this Chat ID!", reply_markup=main_menu())
            return
        
        user_sessions[user_chat_id]['stop_flag'] = True
        user_sessions[user_chat_id]['is_running'] = False
    
    main_bot.reply_to(message, f"⏹ Scanner stopped for Chat ID: {user_chat_id}", reply_markup=main_menu())

@main_bot.message_handler(func=lambda msg: msg.text == "📊 Total Hits")
def total_hits(message):
    global user_sessions
    
    msg1 = main_bot.reply_to(message, "✏️ Enter your CHAT ID to see stats:")
    main_bot.register_next_step_handler(msg1, show_total_hits)

def show_total_hits(message):
    global user_sessions
    user_chat_id = message.text.strip()
    
    with lock:
        if user_chat_id not in user_sessions:
            main_bot.reply_to(message, "❌ No scanner found for this Chat ID!", reply_markup=main_menu())
            return
        
        session = user_sessions[user_chat_id]
    
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
    main_bot.reply_to(message, status_msg, reply_markup=main_menu())

@main_bot.message_handler(func=lambda msg: msg.text == "📋 View All Hits")
def view_all_hits(message):
    global user_sessions
    
    msg1 = main_bot.reply_to(message, "✏️ Enter your CHAT ID to see all hits:")
    main_bot.register_next_step_handler(msg1, show_all_hits)

def show_all_hits(message):
    global user_sessions
    user_chat_id = message.text.strip()
    
    with lock:
        if user_chat_id not in user_sessions:
            main_bot.reply_to(message, "❌ No scanner found for this Chat ID!", reply_markup=main_menu())
            return
        
        hits_list = user_sessions[user_chat_id].get('hits_list', [])
    
    if not hits_list:
        main_bot.reply_to(message, "📋 No hits found yet for this Chat ID!", reply_markup=main_menu())
        return
    
    hit_list = "📋 ALL HITS LIST\n━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    for i, hit in enumerate(hits_list, 1):
        hit_list += f"{i}. @{hit['username']} | {hit['email']} | {hit['followers']} followers\n"
        if len(hit_list) > 3800:
            hit_list += "\n... and more!"
            break
    
    hit_list += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━\n📊 Total: {len(hits_list)} hits"
    hit_list += "\n👑 @SunrakuV2 | 📢 @Anishpy"
    
    main_bot.reply_to(message, hit_list, reply_markup=main_menu())

@main_bot.message_handler(func=lambda msg: msg.text == "📢 Channel")
def send_channel(message):
    markup = InlineKeyboardMarkup()
    for channel in CHANNELS:
        btn = InlineKeyboardButton(text=channel["username"], url=f"https://t.me/{channel['username'].replace('@', '')}")
        markup.add(btn)
    main_bot.reply_to(message, "📢 Join our channels:", reply_markup=markup)

@main_bot.message_handler(func=lambda msg: msg.text == "👑 Dev")
def send_dev(message):
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(text="👑 @SunrakuV2", url="https://t.me/SunrakuV2")
    markup.add(btn)
    main_bot.reply_to(message, "👑 Developer:", reply_markup=markup)

@main_bot.message_handler(func=lambda msg: True)
def echo_all(message):
    main_bot.reply_to(message, "❌ Use buttons below 👇", reply_markup=main_menu())

# ============================================================
# 🚀 START MAIN BOT
# ============================================================
print("✅ Main Bot is running...")
print("📌 Bot Username: @" + main_bot.get_me().username)
print("🎉 500 SUBS SPECIAL EDITION")
print("📌 Users will enter their Chat ID + Bot Token")
print("📤 Hits will go to USER'S bot (sirf usi ko)")
print("📊 Each user's hits are separate")
print("Press Ctrl+C to stop")

try:
    main_bot.infinity_polling()
except KeyboardInterrupt:
    print("\n❌ Bot stopped.")
