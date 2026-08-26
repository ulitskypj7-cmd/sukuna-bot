#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 SUNRAKU — HI2 FAST RUNNER BOT 🔥
- hi2 fast.py bot se run hoga
- User Chat ID + Token input lega
- Hits user ke bot mein jaayengi
- Main bot sirf Live Status
- Fast scanning
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
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from user_agent import generate_user_agent
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

init(autoreset=True)

# ============================================================
# 🔥 ENVIRONMENT VARIABLE (Railway)
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
THREADS = 3

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
# 🚀 HI2 FAST ENGINE (Integrated)
# ============================================================
class Hi2FastEngine:
    def __init__(self, target_chat_id, target_bot_token):
        self.target_chat_id = target_chat_id
        self.target_bot_token = target_bot_token
        self.user_bot = TeleBot(target_bot_token)
        self.hit = 0
        self.badmail = 0
        self.badinsta = 0
        self.goodinsta = 0
        self.bad = 0
        self.good = 0
        self.taken = 0
        self.limit = 0
        self.used_usernames = set()
        self.lock = threading.Lock()
        self.running = True
        
        # Hi2 specific
        self.token = target_bot_token
        self.ID = target_chat_id
        
        # About sessions
        self._about_session_index = 0
        self._about_session_lock = threading.Lock()
        self.ABOUT_SESSION_ID = ""
        self.ABOUT_CSRF_TOKEN = ""
        self.ABOUT_DS_USER_ID = ""
        self.ABOUT_COOKIE_STR = ""
        self.ABOUT_WEB_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 OPR/128.0.0.0"
        self.about_tokens = {"fb_dtsg": None, "lsd": None, "rev": "1035271382", "bkv": "61fc9465e13b77eaa110f317859102ba7fb93a0a2bcc08c46473da6713640739"}
        self.about_token_lock = threading.Lock()
        
        # ID Ranges
        self.ID_RANGES = [
            (17750001, 279760000, 2012),
            (279760001, 900990000, 2013),
            (900990001, 1629010000, 2014),
            (1629010001, 2369359761, 2015),
            (2369359762, 27238602160, 2016),
            (27238602160, 46464475395, 2020),
            (46464475395, 50289297647, 2021),
            (50289297647, 57464707082, 2022),
            (57464707082, 63313426938, 2023),
            (63313426938, 70134323896, 2024),
            (70313426938, 78313496938, 2025),
        ]
        
        # Hardcoded sessions
        self.HARDCODED_SESSIONS = [
            {"csrftoken": "SA7WOqODWLd9lq8tepS9lO5hEyQiiAjf", "mid": "acXucwABAAEpLL9LTj_zE5mdFUm4", "ig_did": "68B3C797-5435-4284-91DF-36BB57ACE8EC", "sessionid": "37980233613%3AzkmZM0x4USstRi%3A13%3AAYgWd5cwudKpm1w0dyEb0AD6LFdG2zY5HVncDeFJfA", "ds_user_id": "37980233613"},
            {"csrftoken": "tPvqXDZm6bD62k-_0a2rRl", "mid": "acVQKgABAAHxWQ3ymupl3SPVKxqV", "ig_did": "02AD7E3A-B843-43E2-B5BD-520BA7392ACA", "sessionid": "74090320231%3ACtvz4lnFouLKGZ%3A25%3AAYg8Be6H6r7-c9Vz5Jhewf-KhM-nvusIhXYYRBqZUw", "ds_user_id": "74090320231"}
        ]
        
        # Initialize about sessions
        self._next_about_session()
        self.about_refresh_tokens(self.ABOUT_COOKIE_STR)
        threading.Thread(target=self.about_token_refresher, daemon=True).start()

    def _build_cookie_str(self, s):
        return f"csrftoken={s['csrftoken']}; ig_did={s['ig_did']}; mid={s['mid']}; ds_user_id={s['ds_user_id']}; sessionid={s['sessionid']}"

    def _next_about_session(self):
        with self._about_session_lock:
            s = self.HARDCODED_SESSIONS[self._about_session_index % len(self.HARDCODED_SESSIONS)]
            self._about_session_index += 1
        self.ABOUT_SESSION_ID = s["sessionid"]
        self.ABOUT_CSRF_TOKEN = s["csrftoken"]
        self.ABOUT_DS_USER_ID = s["ds_user_id"]
        self.ABOUT_COOKIE_STR = self._build_cookie_str(s)
        return s

    def _random_about_session(self):
        s = random.choice(self.HARDCODED_SESSIONS)
        cookie_str = self._build_cookie_str(s)
        return s["sessionid"], s["csrftoken"], s["ds_user_id"], cookie_str

    def about_refresh_tokens(self, cookie_str=None, username="instagram"):
        if not self.ABOUT_SESSION_ID:
            return False
        _cookie = cookie_str or self.ABOUT_COOKIE_STR
        try:
            resp = requests.get(
                f"https://www.instagram.com/{username}/",
                headers={
                    "User-Agent": self.ABOUT_WEB_UA,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Accept-Encoding": "gzip, deflate",
                    "Cookie": _cookie,
                    "Referer": "https://www.instagram.com/",
                }
            )
            html = resp.text
            m = re.search(r'"f":"([^"]+)"', html)
            m2 = re.search(r'"LSD"[^}]*"token":"([^"]+)"', html)
            m3 = re.search(r'"server_revision":(\d+)', html)
            m4 = re.search(r'__bkv=([a-f0-9]{40,})', html)
            m5 = re.search(r'"hsi":"([^"]+)"', html)
            dyn_m = re.search(r'"__dyn":"([^"]+)"', html)
            csr_m = re.search(r'"__csr":"([^"]+)"', html)
            with self.about_token_lock:
                if m: self.about_tokens["fb_dtsg"] = m.group(1)
                if m2: self.about_tokens["lsd"] = m2.group(1)
                if m3: self.about_tokens["rev"] = m3.group(1)
                if m4: self.about_tokens["bkv"] = m4.group(1)
                if m5: self.about_tokens["hsi"] = m5.group(1)
                if dyn_m: self.about_tokens["dyn"] = dyn_m.group(1)
                if csr_m: self.about_tokens["csr"] = csr_m.group(1)
            return self.about_tokens["fb_dtsg"] is not None
        except:
            return False

    def about_token_refresher(self):
        while self.running:
            try:
                if not self.about_tokens.get("fb_dtsg"):
                    self._next_about_session()
                    self.about_refresh_tokens(self.ABOUT_COOKIE_STR)
                else:
                    self.about_refresh_tokens(self.ABOUT_COOKIE_STR)
            except:
                pass
            time.sleep(60)

    def generate_android_ua(self):
        devices = [
            {"brand": "samsung", "model": "SM-G973F", "device": "beyond1", "board": "exynos9820"},
            {"brand": "samsung", "model": "SM-A536B", "device": "a53x", "board": "s5e8825"},
            {"brand": "Google", "model": "Pixel 6", "device": "raven", "board": "raven"},
            {"brand": "Google", "model": "Pixel 7", "device": "panther", "board": "panther"},
            {"brand": "Xiaomi", "model": "M2102J20SG", "device": "ares", "board": "mt6893"},
            {"brand": "OnePlus", "model": "ONEPLUS A6003", "device": "OnePlus6", "board": "sdm845"},
        ]
        device = random.choice(devices)
        android_version = random.choice(["11", "12", "13", "14"])
        api_level = {"11": "30", "12": "31", "13": "33", "14": "34"}[android_version]
        dpi = random.choice(["420", "440", "450"])
        width = random.choice(["1080", "1440"])
        height = random.choice(["2280", "2400", "2560"])
        instagram_ver = f"{random.randint(320, 370)}.0.0.{random.randint(10, 99)}"
        locale = random.choice(["en_US", "en_GB"])
        return (f"Instagram {instagram_ver} Android ({api_level}/{android_version}; "
                f"{dpi}dpi; {width}x{height}; {device['brand']}; {device['model']}; "
                f"{device['device']}; {device['board']}; {locale}; {random.randint(300000000, 500000000)})")

    def gen_session_id(self):
        part1 = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=5))
        part2 = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=5))
        return f"{part1}:{part2}:{random.randint(100,999)}"

    def solve_recaptcha_hi2(self):
        try:
            anchor_url = "https://www.google.com/recaptcha/api2/anchor?ar=1&k=6LfEUPkgAAAAAKTgbMoewQkWBEQhO2VPL4QviKct&co=aHR0cHM6Ly9oaTIuaW46NDQz&hl=en&v=XrIDux0s7SoNe6_IHkjGC92W&size=invisible"
            params = anchor_url.split('?')[1]
            r = requests.get(f'https://www.google.com/recaptcha/enterprise/anchor?{params}', timeout=10)
            recaptcha_token = r.text.split('recaptcha-token" value="')[1].split('"')[0]
            payload = f"v={params.split('v=')[1].split('&')[0]}&reason=q&c={recaptcha_token}&k=6LfEUPkgAAAAAKTgbMoewQkWBEQhO2VPL4QviKct&co=aHR0cHM6Ly9oaTIuaW46NDQz&hl=en&size=invisible"
            headers = {"User-Agent": "Mozilla/5.0", "Referer": f"https://www.google.com/recaptcha/enterprise/anchor?{params}", "Content-Type": "application/x-www-form-urlencoded"}
            resp = requests.post('https://www.google.com/recaptcha/enterprise/reload', data=payload, headers=headers)
            return resp.text.split('resp","')[1].split('"')[0]
        except:
            return None

    def check_hi2_registration(self, email):
        if "@" in email:
            domain = email.split("@")[1]
            prefix = email.split("@")[0]
        else:
            return None
        solve = self.solve_recaptcha_hi2()
        if not solve:
            return None
        data = {'domain': domain, 'prefix': prefix, 'recaptcha': solve}
        headers = {'User-Agent': "Mozilla/5.0", 'Accept': "application/json, text/plain, */*", 'authorization': "Basic bnVsbA=="}
        try:
            response = requests.post("https://hi2.in/api/custom", data=data, headers=headers, timeout=15)
            res = response.json()
            if "already taken" in str(res):
                return True
            return False
        except:
            return None

    def get_masked_email(self, query):
        url = "https://www.instagram.com/api/graphql"
        payload = {
            'av': "0", '__d': "www", '__user': "0", '__a': "1", '__req': "f",
            'lsd': "AdRhedp9xNI2uNuFwNJXmbUAOw8", 'jazoest': "22394",
            '__spin_r': "1037676804", '__spin_b': "trunk", '__spin_t': str(int(time.time())),
            'fb_api_caller_class': "RelayModern",
            'fb_api_req_friendly_name': "CAAIGAccountSearchViewQuery",
            'server_timestamps': "true",
            'variables': json.dumps({"params": {"event_request_id": str(uuid.uuid4()), "next_uri": "", "search_query": query, "waterfall_id": str(uuid.uuid4())}}),
            'doc_id': "26178667145161478"
        }
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            'x-ig-app-id': "936619743392459",
            'x-fb-friendly-name': "CAAIGAccountSearchViewQuery",
            'x-fb-lsd': "AdRhedp9xNI2uNuFwNJXmbUAOw8",
            'x-csrftoken': "o_6jxh33ZvsQ2eFMyRaM_q",
            'origin': "https://www.instagram.com",
            'referer': "https://www.instagram.com/accounts/password/reset/",
            'Cookie': "csrftoken=o_6jxh33ZvsQ2eFMyRaM_q; ig_did=2046A480-DF50-4660-A5CD-DC58F57C7A1C; mid=aeXJYAABAAGoDWzGwrGALDqzE3Np"
        }
        try:
            response = requests.post(url, data=payload, headers=headers, timeout=20)
            data = response.json()
            for cp in data.get("data", {}).get("caa_ar_ig_account_search", {}).get("contact_points", []):
                if cp.get("type") == "EMAIL":
                    return cp.get("contact_point")
            return None
        except:
            return None

    def lookup_bloks_v2(self, email):
        url = "https://i.instagram.com/api/v1/bloks/async_action/com.bloks.www.caa.ar.search.async/"
        device = str(uuid.uuid4())
        family = str(uuid.uuid4())
        android = "android-" + secrets.token_hex(8)
        payload = {
            'params': "{\"client_input_params\":{\"aac\":\"{\\\"aac_init_timestamp\\\":" + str(int(time.time())) + ",\\\"aacjid\\\":\\\"" + str(uuid.uuid4()) + "\\\",\\\"aaccs\\\":\\\"" + secrets.token_urlsafe(32) + "\\\"}\",\"flash_call_permissions_status\":{\"READ_PHONE_STATE\":\"PERMANENTLY_DENIED\",\"READ_CALL_LOG\":\"DENIED\",\"ANSWER_PHONE_CALLS\":\"DENIED\"},\"was_headers_prefill_available\":0,\"network_bssid\":null,\"sfdid\":\"\",\"fetched_email_token_list\":{},\"search_query\":\"" + email + "\",\"auth_secure_device_id\":\"\",\"ig_oauth_token\":[],\"cloud_trust_token\":null,\"was_headers_prefill_used\":0,\"sso_accounts_auth_data\":[],\"encrypted_msisdn\":\"\",\"device_network_info\":null,\"text_input_id\":\"akyuf0:61\",\"zero_balance_state\":null,\"android_build_type\":\"release\",\"accounts_list\":[],\"is_oauth_without_permission\":0,\"ig_android_qe_device_id\":\"" + device + "\",\"gms_incoming_call_retriever_eligibility\":\"client_not_supported\",\"search_screen_type\":\"email_or_username\",\"is_whatsapp_installed\":1,\"lois_settings\":{\"lois_token\":\"\"},\"ig_vetted_device_nonce\":null,\"headers_infra_flow_id\":\"\",\"fetched_email_list\":[]},\"server_params\":{\"event_request_id\":\"" + str(uuid.uuid4()) + "\",\"is_from_logged_out\":0,\"layered_homepage_experiment_group\":null,\"device_id\":\"" + android + "\",\"login_surface\":\"login_home\",\"waterfall_id\":\"" + str(uuid.uuid4()) + "\",\"INTERNAL__latency_qpl_instance_id\":6.3987980400102E13,\"is_platform_login\":0,\"context_data\":\"\",\"login_entry_point\":\"logged_out\",\"INTERNAL__latency_qpl_marker_id\":36707139,\"family_device_id\":\"" + family + "\",\"offline_experiment_group\":\"caa_iteration_v3_perf_ig_4\",\"access_flow_version\":\"pre_mt_behavior\",\"is_from_logged_in_switcher\":0,\"qe_device_id\":\"" + device + "\"}}",
            'bk_client_context': '{"bloks_version":"5e47baf35c5a270b44c8906c8b99063564b30ef69779f3dee0b828bee2e4ef5b","styles_id":"instagram"}',
            'bloks_versioning_id': "5e47baf35c5a270b44c8906c8b99063564b30ef69779f3dee0b828bee2e4ef5b"
        }
        headers = {
            'User-Agent': "Instagram 370.1.0.43.96 Android (34/14; 450dpi; 1080x2207; samsung; SM-A235F; a23; qcom; en_IN; 704872281)",
            'accept-language': "en-IN, en-US",
            'x-bloks-version-id': "5e47baf35c5a270b44c8906c8b99063564b30ef69779f3dee0b828bee2e4ef5b",
            'x-fb-friendly-name': "IgApi: bloks/async_action/com.bloks.www.caa.ar.search.async/",
            'x-ig-android-id': android,
            'x-ig-app-id': "567067343352427",
            'x-ig-app-locale': "en_IN",
            'x-ig-client-endpoint': "com.bloks.www.caa.ar.search",
            'x-ig-device-id': device,
            'x-ig-family-device-id': family,
            'x-ig-timezone-offset': str(datetime.now().astimezone().utcoffset().total_seconds()),
            'x-mid': base64.urlsafe_b64encode(secrets.token_bytes(18)).decode().rstrip('='),
            'x-pigeon-rawclienttime': str(time.time()),
            'x-pigeon-session-id': f"UFS-{uuid.uuid4()}-0",
        }
        try:
            response = requests.post(url, data=payload, headers=headers, timeout=20)
            if f"{email}" in response.text:
                return True
            return False
        except:
            return False

    def rest(self, email):
        try:
            android_ua = self.generate_android_ua()
            url = "https://i.instagram.com/api/v1/users/check_email/"
            response = httpx.Client(http2=True).post(
                url,
                data=f"email={email}",
                headers={
                    'User-Agent': "Instagram 166.0.0.30.120 Android (30/11; 1440dpi; 2560x1440; samsung; SM-G973F; x86_64; tablet; en_US; kirin)",
                    'content-type': "application/x-www-form-urlencoded; charset=UTF-8"
                }
            )
            if 'email_is_taken' in response.text:
                registered = self.check_hi2_registration(email)
                status = "✅ ALREADY REGISTERED" if registered else "❌ NOT REGISTERED"
                masked_email = self.get_masked_email(email) or "None"
                self.hit += 1
                self.good += 1
                self.goodinsta += 1
                dom = email.split("@")[1]
                msg = f"""
<b>✨ HIT FOUND ✨</b>

<b>DOMAIN</b> ➜ <i>{dom}</i>
<b>EMAIL</b> ➜ <i>{email}</i>
<b>STATUS</b> ➜ <i>{status}</i>
<b>MASKED</b> ➜ <i>{masked_email}</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>DEV</b> ➜ @SunrakuV2
<b>CHANNEL</b> ➜ @Anishpy
"""
                self.send_hit(msg)
                return
            else:
                bloks_result = self.lookup_bloks_v2(email)
                if bloks_result is True:
                    self.hit += 1
                    self.good += 1
                    self.goodinsta += 1
                    dom = email.split("@")[1]
                    masked_email = self.get_masked_email(email) or "None"
                    msg = f"""
<b>✨ HIT FOUND (BLOKS) ✨</b>

<b>DOMAIN</b> ➜ <i>{dom}</i>
<b>EMAIL</b> ➜ <i>{email}</i>
<b>STATUS</b> ➜ <i>✅ FOUND VIA BLOKS</i>
<b>MASKED</b> ➜ <i>{masked_email}</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>DEV</b> ➜ @SunrakuV2
<b>CHANNEL</b> ➜ @Anishpy
"""
                    self.send_hit(msg)
                    return
                else:
                    self.bad += 1
                    self.badinsta += 1
        except:
            self.bad += 1

    def send_hit(self, msg):
        try:
            self.user_bot.send_message(self.target_chat_id, msg, parse_mode='HTML')
        except:
            pass

    def pookie_alex(self):
        while self.running:
            user1 = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6))
            user2 = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6))
            chosen_user = random.choice([user1, user2])
            with self.lock:
                if chosen_user in self.used_usernames:
                    continue
                self.used_usernames.add(chosen_user)
            chos = random.choice(["@hi2.in", "@telegmail.com"])
            email = chosen_user + chos
            try:
                self.rest(email)
            except:
                pass

    def start(self, threads=5):
        for _ in range(threads):
            threading.Thread(target=self.pookie_alex, daemon=True).start()

    def stop(self):
        self.running = False

# ============================================================
# 🔥 MAIN BOT COMMANDS
# ============================================================

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("🚀 Run hi2")
    btn2 = KeyboardButton("⏹ Stop")
    btn3 = KeyboardButton("📊 Live Status")
    btn4 = KeyboardButton("📢 Channel")
    btn5 = KeyboardButton("👑 Dev")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = f"""
☠️ SUNRAKU — HI2 FAST RUNNER ☠️

🔥 Click buttons below to control.
📌 Enter CHAT ID + BOT TOKEN
📤 Hits will go to YOUR bot.
⚡ Fast scanning (hi2.in + Bloks)

👑 Dev: @SunrakuV2
📢 Channel: @Anishpy
"""
    bot.reply_to(message, welcome_msg, reply_markup=main_menu())

@bot.message_handler(func=lambda msg: msg.text == "🚀 Run hi2")
def run_hi2(message):
    msg1 = bot.reply_to(message, "✏️ Enter your CHAT ID:")
    bot.register_next_step_handler(msg1, get_chat_id)

def get_chat_id(message):
    user_chat_id = message.text.strip()
    msg2 = bot.reply_to(message, "✏️ Enter your BOT TOKEN:")
    bot.register_next_step_handler(msg2, lambda m: get_bot_token(m, user_chat_id))

def get_bot_token(message, user_chat_id):
    user_bot_token = message.text.strip()
    
    if not user_chat_id or not user_bot_token:
        bot.reply_to(message, "❌ Invalid input!", reply_markup=main_menu())
        return
    
    try:
        test_bot = TeleBot(user_bot_token)
        test_bot.get_me()
    except:
        bot.reply_to(message, "❌ Invalid Bot Token!", reply_markup=main_menu())
        return
    
    with lock:
        user_sessions[user_chat_id] = {
            'engine': None,
            'is_running': True
        }
    
    # 🔥 Start hi2 engine
    engine = Hi2FastEngine(user_chat_id, user_bot_token)
    engine.start(threads=5)
    
    with lock:
        user_sessions[user_chat_id]['engine'] = engine
    
    bot.reply_to(message, f"""✅ hi2 started!
📤 Hits will be sent to YOUR bot.
🤖 Bot: @{test_bot.get_me().username}

📊 Click 'Live Status' to see stats.
⏹ Click 'Stop' to end.""", reply_markup=main_menu())

@bot.message_handler(func=lambda msg: msg.text == "⏹ Stop")
def stop_scanner(message):
    global user_sessions
    
    msg1 = bot.reply_to(message, "✏️ Enter your CHAT ID to stop:")
    bot.register_next_step_handler(msg1, stop_by_chat)

def stop_by_chat(message):
    global user_sessions
    user_chat_id = message.text.strip()
    
    with lock:
        if user_chat_id not in user_sessions:
            bot.reply_to(message, "❌ No scanner found!", reply_markup=main_menu())
            return
        if user_sessions[user_chat_id].get('engine'):
            user_sessions[user_chat_id]['engine'].stop()
        user_sessions[user_chat_id]['is_running'] = False
    
    bot.reply_to(message, f"⏹ hi2 stopped for Chat ID: {user_chat_id}", reply_markup=main_menu())

@bot.message_handler(func=lambda msg: msg.text == "📊 Live Status")
def live_status(message):
    global user_sessions
    
    msg1 = bot.reply_to(message, "✏️ Enter your CHAT ID:")
    bot.register_next_step_handler(msg1, show_live_status)

def show_live_status(message):
    global user_sessions
    user_chat_id = message.text.strip()
    
    with lock:
        if user_chat_id not in user_sessions:
            bot.reply_to(message, "❌ No scanner found!", reply_markup=main_menu())
            return
        engine = user_sessions[user_chat_id].get('engine')
        is_running = user_sessions[user_chat_id].get('is_running', False)
    
    if engine:
        status_msg = f"""
┌─────────────────────────────────────────┐
│  ✦ SUNRAKU — HI2 LIVE STATUS ✦         │
├─────────────────────────────────────────┤
│  🔥 HITS  : {engine.hit}                 │
│  ✅ GOOD  : {engine.good}                │
│  ❌ BAD   : {engine.bad}                │
│  📧 BADMAIL : {engine.badmail}           │
│  🟢 STATUS : {'RUNNING' if is_running else 'STOPPED'} │
├─────────────────────────────────────────┤
│  ◈ @SunrakuV2  ●  @Anishpy             │
└─────────────────────────────────────────┘
"""
    else:
        status_msg = "❌ No engine found!"
    
    bot.reply_to(message, status_msg, reply_markup=main_menu())

@bot.message_handler(func=lambda msg: msg.text == "📢 Channel")
def send_channel(message):
    markup = InlineKeyboardMarkup()
    for channel in CHANNELS:
        btn = InlineKeyboardButton(text=channel["username"], url=f"https://t.me/{channel['username'].replace('@', '')}")
        markup.add(btn)
    bot.reply_to(message, "📢 Join our channels:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "👑 Dev")
def send_dev(message):
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(text="👑 @SunrakuV2", url="https://t.me/SunrakuV2")
    markup.add(btn)
    bot.reply_to(message, "👑 Developer:", reply_markup=markup)

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, "❌ Use buttons below 👇", reply_markup=main_menu())

# ============================================================
# 🚀 START BOT
# ============================================================
print("✅ Bot is running on Railway...")
print("📌 Bot Username: @" + bot.get_me().username)
print("⚡ hi2 fast mode active")

try:
    bot.infinity_polling()
except Exception as e:
    print(f"❌ Error: {e}")
