#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import requests
import re
import json
import time
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# -------- Color & Style Shortcuts --------
GREEN = Fore.GREEN
RED = Fore.RED
YELLOW = Fore.YELLOW
CYAN = Fore.CYAN
MAGENTA = Fore.MAGENTA
WHITE = Fore.WHITE
BLUE = Fore.BLUE
BOLD = Style.BRIGHT
RESET = Style.RESET_ALL

# -------- Profile Name Cache --------
cookie_name_cache = {}

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def print_animated_logo():
    clear_screen()
    
    logo_lines = [
        "╔═══════════════════════════════════════════════════════╗",
        "║                                                       ║",
        "║    ██████╗ ██████╗  ██████╗ ██╗  ██╗██╗███████╗     ║",
        "║   ██╔════╝██╔═══██╗██╔═══██╗██║ ██╔╝██║██╔════╝     ║",
        "║   ██║     ██║   ██║██║   ██║█████╔╝ ██║█████╗       ║",
        "║   ██║     ██║   ██║██║   ██║██╔═██╗ ██║██╔══╝       ║",
        "║   ╚██████╗╚██████╔╝╚██████╔╝██║  ██╗██║███████╗     ║",
        "║    ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝     ║",
        "║                                                       ║",
        "║    ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗  ║",
        "║   ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝  ║",
        "║   ██║     ███████║█████╗  ██║     █████╔╝ █████╗    ║",
        "║   ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝    ║",
        "║   ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗  ║",
        "║    ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝  ║",
        "║                                                       ║",
        "║     Facebook Cookie & Token Checker v2.0             ║",                                                                                             
        "╚═══════════════════════════════════════════════════════╝"
    ]
    
    colors = [CYAN, MAGENTA, BLUE, GREEN, YELLOW]
    
    for i, line in enumerate(logo_lines):
        color = colors[i % len(colors)]
        print(f"{color}{BOLD}{line}{RESET}")
        time.sleep(0.05)
    
    print()

def print_separator(char='=', color=CYAN):
    separator = char * 60
    for i in range(0, len(separator), 5):
        print(f"{color}{separator[:i+5]}{RESET}", end='\r')
        time.sleep(0.01)
    print()

def print_success(msg):
    print(f"{GREEN}{BOLD}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}{BOLD}❌ {msg}{RESET}")

def print_info(msg):
    print(f"{CYAN}ℹ️  {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def loading_animation(text, duration=1):
    frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        print(f"\r{CYAN}{frames[i % len(frames)]} {text}...{RESET}", end='')
        time.sleep(0.1)
        i += 1
    print(f"\r{GREEN}✓ {text} - Done!{RESET}")

def parse_cookie_string(cookie_str):
    cookies = {}
    for part in cookie_str.split(";"):
        if "=" in part:
            k, v = part.strip().split("=", 1)
            cookies[k] = v
    return cookies

def GetNew(ua=None):
    if ua is None:
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Pragma': 'akamai-x-cache-on, akamai-x-cache-remote-on, akamai-x-check-cacheable, akamai-x-get-cache-key, akamai-x-get-extracted-values, akamai-x-get-ssl-client-session-id, akamai-x-get-true-cache-key, akamai-x-serial-no, akamai-x-get-request-id,akamai-x-get-nonces,akamai-x-get-client-ip,akamai-x-feo-trace',
        'Sec-Ch-Prefers-Color-Scheme': 'light',
        'Sec-Ch-Ua': '',
        'Sec-Ch-Ua-Full-Version-List': '',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '',
        'Sec-Ch-Ua-Platform-Version': '',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': ua,
        'Viewport-Width': '924'
    }

def extract_name(cookie_string, ua=None):
    try:
        cookies = parse_cookie_string(cookie_string)
        user_id = cookies.get("c_user")
        if not user_id:
            return "❌ No c_user", None

        url = f"https://www.facebook.com/profile.php?id={user_id}"
        resp = requests.get(url, cookies=cookies, headers=GetNew(ua), timeout=15)
        html = resp.text

        profile_match = re.search(r'"CurrentUserInitialData",\[\],\{(.*?)\},', html)

        if profile_match:
            try:
                account_json = json.loads("{" + profile_match.group(1) + "}")
                name = account_json.get("NAME", "Unknown")
                return name, user_id
            except:
                return "⚠️ ParseError", user_id
        else:
            name_match = re.search(r'<title>([^<]+)</title>', html)
            if name_match:
                name = name_match.group(1).replace(' | Facebook', '').strip()
                if name and name != 'Facebook':
                    return name, user_id
            
            return "❌ Expired", None
    except:
        return "⚠️ Error", None

def extract_token_from_cookie(cookie_string):
    try:
        response = requests.get(
            'https://business.facebook.com/business_locations',
            headers={
                'Cookie': cookie_string,
                'User-Agent': 'Mozilla/5.0 (Linux; Android 11; RMX2144 Build/RKQ1.201217.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.71 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/375.1.0.28.111;]'
            },
            timeout=15
        )
        
        token_match = re.search(r'(EAAG\w+)', response.text)
        if token_match:
            return token_match.group(1)
        return None
    except:
        return None

def get_profile_name(cookie_string, ua=None):
    if cookie_string in cookie_name_cache:
        cached = cookie_name_cache[cookie_string]
        return cached["name"], cached["uid"]
    
    name, uid = extract_name(cookie_string, ua)
    
    if name not in ["❌ Expired", "⚠️ Error", "⚠️ ParseError", "❌ No c_user"]:
        cookie_name_cache[cookie_string] = {"name": name, "uid": uid}
    
    return name, uid

def check_cookie(cookie_string):
    try:
        cookies = parse_cookie_string(cookie_string)
        user_id = cookies.get("c_user")
        
        if not user_id:
            return {
                "status": "death",
                "user_id": None,
                "name": None,
                "token": None,
                "message": "Invalid cookie format"
            }

        token = extract_token_from_cookie(cookie_string)
        
        if token:
            name = None
            
            try:
                graph_url = f"https://graph.facebook.com/me?access_token={token}"
                graph_response = requests.get(graph_url, timeout=10)
                
                if graph_response.status_code == 200:
                    user_info = graph_response.json()
                    name = user_info.get('name')
                    user_id = user_info.get('id', user_id)
            except:
                pass
            
            # Method 2: If Graph API failed, try profile extraction
            if not name or name == "Unknown":
                extracted_name, extracted_uid = get_profile_name(cookie_string)
                if extracted_name not in ["❌ Expired", "⚠️ Error", "⚠️ ParseError", "❌ No c_user", "Unknown"]:
                    name = extracted_name
                    if extracted_uid:
                        user_id = extracted_uid
            
            # If still no name, set to Unknown
            if not name:
                name = "Unknown"
            
            return {
                "status": "live",
                "user_id": user_id,
                "name": name,
                "token": token,
                "message": "Cookie is valid"
            }
        else:
            # Token extraction failed - cookie is DEATH
            return {
                "status": "death",
                "user_id": None,
                "name": None,
                "token": None,
                "message": "Cookie expired"
            }
            
    except Exception:
        return {
            "status": "death",
            "user_id": None,
            "name": None,
            "token": None,
            "message": "Invalid cookie"
        }

def validate_token(access_token):
    url = f"https://graph.facebook.com/me?access_token={access_token}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            user_info = response.json()
            return {
                "status": "live",
                "name": user_info.get('name', 'Unknown'),
                "user_id": user_info.get('id', 'Unknown'),
                "token": access_token,
                "message": "Token is valid"
            }
        else:
            return {
                "status": "death",
                "name": None,
                "user_id": None,
                "token": None,
                "message": "Token expired or invalid"
            }
    except requests.exceptions.RequestException:
        return {
            "status": "death",
            "name": None,
            "user_id": None,
            "token": None,
            "message": "Network error"
        }

def display_cookie_result(index, result, total):
    print(f"\n{MAGENTA}{'━' * 60}{RESET}")
    print(f"{CYAN}{BOLD}┃ Cookie #{index}/{total}{RESET}")
    print(f"{MAGENTA}{'━' * 60}{RESET}")
    
    if result["status"] == "live":
        print(f"{GREEN}{BOLD}┃ Status     : ✅ LIVE{RESET}")
        print(f"{CYAN}┃ User ID    : {WHITE}{result['user_id']}{RESET}")
        print(f"{CYAN}┃ Name       : {WHITE}{result['name']}{RESET}")
        # Don't show token in output for security
    else:
        print(f"{RED}{BOLD}┃ Status     : ❌ DEATH{RESET}")
    
    print(f"{MAGENTA}{'━' * 60}{RESET}")

def display_token_result(index, result, total):
    print(f"\n{MAGENTA}{'━' * 60}{RESET}")
    print(f"{CYAN}{BOLD}┃ Token #{index}/{total}{RESET}")
    print(f"{MAGENTA}{'━' * 60}{RESET}")
    
    if result["status"] == "live":
        print(f"{GREEN}{BOLD}┃ Status     : ✅ LIVE{RESET}")
        print(f"{CYAN}┃ User ID    : {WHITE}{result['user_id']}{RESET}")
        print(f"{CYAN}┃ Name       : {WHITE}{result['name']}{RESET}")
    else:
        print(f"{RED}{BOLD}┃ Status     : ❌ DEATH{RESET}")
    
    print(f"{MAGENTA}{'━' * 60}{RESET}")

def save_live_items(live_items, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for item in live_items:
                f.write(item + '\n')
        return True
    except Exception as e:
        print_error(f"Failed to save: {str(e)}")
        return False

def show_summary(results, live_file=None, check_type="Cookie"):
    """Display summary of all checks"""
    total = len(results)
    live = sum(1 for r in results if r["status"] == "live")
    death = total - live
    
    print(f"\n{MAGENTA}{BOLD}{'═' * 60}{RESET}")
    print(f"{CYAN}{BOLD}           📊 {check_type.upper()} CHECK SUMMARY 📊{RESET}")
    print(f"{MAGENTA}{BOLD}{'═' * 60}{RESET}\n")
    
    print(f"{CYAN}┃ Total {check_type}s Checked : {WHITE}{BOLD}{total}{RESET}")
    print(f"{GREEN}┃ ✅ Live {check_type}s      : {WHITE}{BOLD}{live}{RESET}")
    print(f"{RED}┃ ❌ Death {check_type}s     : {WHITE}{BOLD}{death}{RESET}")
    
    if live > 0:
        success_rate = (live / total) * 100
        print(f"\n{GREEN}┃ Success Rate          : {WHITE}{BOLD}{success_rate:.1f}%{RESET}")
        
        if live_file:
            print(f"\n{GREEN}✅ Live {check_type.lower()}s saved to: {WHITE}{BOLD}{live_file}{RESET}")
    
    print(f"\n{MAGENTA}{BOLD}{'═' * 60}{RESET}\n")

def check_cookies_mode():
    print_separator('─', BLUE)
    print(f"\n{YELLOW}{BOLD}SELECT COOKIE INPUT METHOD:{RESET}\n")
    print(f"{CYAN}[1]{RESET} {WHITE}Single Cookie (Manual Entry){RESET}")
    print(f"{CYAN}[2]{RESET} {WHITE}Multiple Cookies (File Input){RESET}")
    print_separator('─', BLUE)
    
    choice = input(f"\n{CYAN}➤ Enter your choice (1 or 2): {RESET}").strip()
    
    cookies_list = []
    save_live_option = False
    
    if choice == "1":
        # Single cookie input
        print_separator('─', GREEN)
        print(f"\n{YELLOW}📝 MANUAL COOKIE ENTRY{RESET}\n")
        cookie = input(f"{CYAN}➤ Paste your Facebook cookie: {RESET}").strip()
        
        if not cookie:
            print_error("No cookie entered!")
            return
        
        cookies_list.append(cookie)
    
    elif choice == "2":
        # File input
        print_separator('─', GREEN)
        print(f"\n{YELLOW}📁 COOKIE FILE INPUT{RESET}\n")
        filepath = input(f"{CYAN}➤ Enter cookie file path: {RESET}").strip()
        
        if not os.path.exists(filepath):
            print_error(f"File not found: {filepath}")
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                cookies_list = [line.strip() for line in f if line.strip()]
            
            if not cookies_list:
                print_error("No cookies found in file!")
                return
            
            loading_animation("Loading cookies", 1)
            print_success(f"Loaded {len(cookies_list)} cookies from file")
            
            # Ask if user wants to save live cookies
            print(f"\n{YELLOW}Save live cookies to file?{RESET}")
            save_choice = input(f"{CYAN}➤ Enter filename (or press Enter to skip): {RESET}").strip()
            
            if save_choice:
                save_live_option = save_choice
            
        except Exception as e:
            print_error(f"Error reading file: {str(e)}")
            return
    
    else:
        print_error("Invalid choice!")
        return
    
    print(f"\n{GREEN}{BOLD}🚀 STARTING COOKIE VALIDATION...{RESET}\n")
    print(f"{CYAN}🔎 Checking cookies... please wait while cookies are being verified 🔄{RESET}\n")
    time.sleep(1)
    
    results = []
    live_cookies = []
    
    for i, cookie in enumerate(cookies_list, 1):
        loading_animation(f"Checking cookie {i}/{len(cookies_list)}", 0.5)
        
        result = check_cookie(cookie)
        results.append(result)
        
        display_cookie_result(i, result, len(cookies_list))
        
        if result["status"] == "live":
            live_cookies.append(cookie)
        
        if i < len(cookies_list):
            time.sleep(2)
    
    if save_live_option and live_cookies:
        if save_live_items(live_cookies, save_live_option):
            show_summary(results, save_live_option, "Cookie")
        else:
            show_summary(results, None, "Cookie")
    else:
        show_summary(results, None, "Cookie")

def check_tokens_mode():
    print_separator('─', BLUE)
    print(f"\n{YELLOW}{BOLD}SELECT TOKEN INPUT METHOD:{RESET}\n")
    print(f"{CYAN}[1]{RESET} {WHITE}Single Token (Manual Entry){RESET}")
    print(f"{CYAN}[2]{RESET} {WHITE}Multiple Tokens (File Input){RESET}")
    print_separator('─', BLUE)
    
    choice = input(f"\n{CYAN}➤ Enter your choice (1 or 2): {RESET}").strip()
    
    tokens_list = []
    save_live_option = False
    
    if choice == "1":
        # Single token input
        print_separator('─', GREEN)
        print(f"\n{YELLOW}📝 MANUAL TOKEN ENTRY{RESET}\n")
        token = input(f"{CYAN}➤ Paste your Facebook access token: {RESET}").strip()
        
        if not token:
            print_error("No token entered!")
            return
        
        tokens_list.append(token)
    
    elif choice == "2":
        # File input
        print_separator('─', GREEN)
        print(f"\n{YELLOW}📁 TOKEN FILE INPUT{RESET}\n")
        filepath = input(f"{CYAN}➤ Enter token file path: {RESET}").strip()
        
        if not os.path.exists(filepath):
            print_error(f"File not found: {filepath}")
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tokens_list = [line.strip() for line in f if line.strip()]
            
            if not tokens_list:
                print_error("No tokens found in file!")
                return
            
            loading_animation("Loading tokens", 1)
            print_success(f"Loaded {len(tokens_list)} tokens from file")
            
            # Ask if user wants to save live tokens
            print(f"\n{YELLOW}Save live tokens to file?{RESET}")
            save_choice = input(f"{CYAN}➤ Enter filename (or press Enter to skip): {RESET}").strip()
            
            if save_choice:
                save_live_option = save_choice
            
        except Exception as e:
            print_error(f"Error reading file: {str(e)}")
            return
    
    else:
        print_error("Invalid choice!")
        return
    
    print(f"\n{GREEN}{BOLD}🚀 STARTING TOKEN VALIDATION...{RESET}\n")
    time.sleep(1)
    
    results = []
    live_tokens = []
    
    for i, token in enumerate(tokens_list, 1):
        loading_animation(f"Checking token {i}/{len(tokens_list)}", 0.5)
        
        result = validate_token(token)
        results.append(result)
        
        display_token_result(i, result, len(tokens_list))
        
        if result["status"] == "live":
            live_tokens.append(token)
        
        if i < len(tokens_list):
            time.sleep(2)
    
    if save_live_option and live_tokens:
        if save_live_items(live_tokens, save_live_option):
            show_summary(results, save_live_option, "Token")
        else:
            show_summary(results, None, "Token")
    else:
        show_summary(results, None, "Token")

def main():
    print_animated_logo()
    print_separator('═', MAGENTA)
    
    print(f"\n{YELLOW}{BOLD}SELECT CHECK MODE:{RESET}\n")
    print(f"{CYAN}[1]{RESET} {WHITE}Cookie Checker{RESET}")
    print(f"{CYAN}[2]{RESET} {WHITE}Token Checker{RESET}")
    print_separator('═', MAGENTA)
    
    mode = input(f"\n{CYAN}➤ Enter your choice (1 or 2): {RESET}").strip()
    
    if mode == "1":
        check_cookies_mode()
    elif mode == "2":
        check_tokens_mode()
    else:
        print_error("Invalid choice!")
        return
    
    print(f"\n{GREEN}{BOLD}✅ Validation completed!{RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{RED}❌ Process interrupted by user!{RESET}\n")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")