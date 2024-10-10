import os
from os import system as ss
import time
import requests
from datetime import datetime
from colorama import Fore, Style, init
from fake_useragent import UserAgent

try:
    from cfonts import render
except ModuleNotFoundError:
    ss('pip install python-cfonts')
try:
    import requests
except ModuleNotFoundError:
    os.system("pip install requests")
    
init(autoreset=True)

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_tokens_and_proxies(token_file, proxy_file):
    with open(token_file, 'r') as token_f:
        tokens = [line.strip() for line in token_f if line.strip()]
    with open(proxy_file, 'r') as proxy_f:
        proxies = [line.strip() for line in proxy_f if line.strip()]
    return tokens, proxies

def get_headers(token):
    ua = UserAgent()
    return {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-ID,en-US;q=0.9,en;q=0.8,id;q=0.7',
        'content-length': '0',
        'dnt': '1',
        'origin': 'https://cf.seeddao.org',
        'priority': 'u=1, i',
        'referer': 'https://cf.seeddao.org/',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'telegram-data': token,
        'user-agent': ua.random
    }

def handle_request(method, url, headers, proxy, data=None):
    proxies = {"http": proxy, "https": proxy}
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, proxies=proxies)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, proxies=proxies)
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        print(f"{Fore.RED + Style.BRIGHT}Request timed out using proxy {proxy}.")
    except requests.ConnectionError:
        print(f"{Fore.RED + Style.BRIGHT}Connection error occurred using proxy {proxy}.")
    except requests.RequestException as e:
        if "login-bonuses" in str(e):
            print(f"{Fore.YELLOW + Style.BRIGHT}Try again in two hours ✘ using proxy {proxy}.")
        elif "seed/claim" in str(e):
            print(f"{Fore.YELLOW + Style.BRIGHT}Collection is not available now ✘ using proxy {proxy}.")
        else:
            print(f"{Fore.RED + Style.BRIGHT}Request failed using proxy {proxy}.")
    return None

def login(token, proxy):
    url_profile = "https://elb.seeddao.org/api/v1/profile2"
    url_balance = "https://elb.seeddao.org/api/v1/profile/balance"
    headers = get_headers(token)

    data = handle_request('GET', url_profile, headers, proxy)
    balance_data = handle_request('GET', url_balance, headers, proxy)
    if balance_data:
        balance = balance_data.get("data") / 1000000000
        print(f"{Fore.GREEN + Style.BRIGHT}Balance: {Fore.WHITE + Style.BRIGHT}{balance:.3f} using proxy {proxy}")

def daily_bonus(token, proxy):
    url_bonus = "https://elb.seeddao.org/api/v1/login-bonuses"
    headers = get_headers(token)

    response_data = handle_request('POST', url_bonus, headers, proxy)
    if response_data:
        reward = response_data.get("data", {}).get("amount")
        print(f"{Fore.GREEN + Style.BRIGHT}Daily Reward Claimed: {Fore.WHITE + Style.BRIGHT}{int(reward)/1000000000} using proxy {proxy}" if reward else f"{Fore.YELLOW + Style.BRIGHT}Daily Reward Already Claimed using proxy {proxy}")

def claim(token, proxy):
    url_claim = "https://elb.seeddao.org/api/v1/seed/claim"
    headers = get_headers(token)

    response_data = handle_request('POST', url_claim, headers, proxy)
    if response_data:
        amount = response_data.get("data", {}).get("amount")
        print(f"{Fore.GREEN + Style.BRIGHT}Seed Claimed: {Fore.WHITE + Style.BRIGHT}{int(amount)/1000000000} using proxy {proxy}" if amount else f"{Fore.YELLOW + Style.BRIGHT}Seed Already Claimed using proxy {proxy}")

def spin(token, proxy):
    url_ticket = "https://elb.seeddao.org/api/v1/spin-ticket"
    url_spin = "https://elb.seeddao.org/api/v1/spin-reward"
    headers = get_headers(token)

    ticket_data = handle_request('GET', url_ticket, headers, proxy)
    if ticket_data:
        tickets = ticket_data.get('data', [])
        for ticket in tickets:
            body_spin = {'ticket_id': ticket['id']}
            spin_data = handle_request('POST', url_spin, headers, proxy, data=body_spin)
            if spin_data:
                print(f"{Fore.CYAN + Style.BRIGHT}Spin Reward: {spin_data.get('data', {}).get('type')} using proxy {proxy}")

def task(token, proxy):
    url_tasks = "https://elb.seeddao.org/api/v1/tasks/progresses"
    headers = get_headers(token)

    task_data = handle_request('GET', url_tasks, headers, proxy)
    if task_data:
        tasks = task_data.get('data', [])
        for task in tasks:
            url_complete = f"https://elb.seeddao.org/api/v1/tasks/{task['id']}"
            task_complete_data = handle_request('POST', url_complete, headers, proxy)
            if task_complete_data:
                task_name = task.get('name', 'Unknown Task')
                print(f"{Fore.GREEN + Style.BRIGHT}Task »» '{task_name}' success ✓ using proxy {proxy}")
            time.sleep(5)

def countdown_timer(seconds):
    while seconds > 0:
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        print(f"{Fore.CYAN + Style.BRIGHT}Wait {hours:02}:{mins:02}:{secs:02}", end='\r')
        time.sleep(1)
        seconds -= 1
    print("Wait 00:00:00          ", end='\r')

def main():
    clear_terminal()
    
    run_task = input("Do you want to continue completing tasks ? ✓ (y/n): ").strip().lower()
    tokens, proxies = load_tokens_and_proxies('data.txt', 'proxies.txt')

    while True:
        clear_terminal()

        for i, (token, proxy) in enumerate(zip(tokens, proxies), start=1):
            print(f"{Fore.CYAN + Style.BRIGHT}Number of accounts »» {i} using proxy: {proxy}{Style.RESET_ALL}")
            login(token, proxy)
            daily_bonus(token, proxy)
            claim(token, proxy)
            spin(token, proxy)
            if run_task == 'y':
                task(token, proxy)

        countdown_timer(1 * 60 * 60)

if __name__ == "__main__":
    main()
