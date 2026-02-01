#!/usr/bin/env python3

import os
import sys

# -------- PATH FIX (same as exploitation_main) --------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# -------- IMPORT MODULES --------

from modules.persistence import (
    cron_persistence,
    systemd_persistence,
    bashrc_persistence,
    sshkey_persistence
)

# -------- COLORS --------

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

# -------- BANNER --------

BANNER = f"""
{Colors.BLUE}{Colors.BOLD}
╔════════════════════════════════════════════╗
║             PERSISTENCE PHASE              ║
║     Cron • Systemd • Shell • SSH Keys      ║
╚════════════════════════════════════════════╝
{Colors.END}
"""

# -------- MENU --------

def main_menu():
    print(BANNER)
    print(f"""
{Colors.WHITE}[1] Cron Persistence Check{Colors.END}
{Colors.WHITE}[2] Systemd Persistence Check{Colors.END}
{Colors.WHITE}[3] Bashrc Persistence Check{Colors.END}
{Colors.WHITE}[4] SSH Key Persistence Check{Colors.END}
{Colors.YELLOW}[5] Run All Persistence Modules{Colors.END}
{Colors.RED}[6] Back to Main Menu{Colors.END}
""")
    return input("Select option: ").strip()


# -------- SAFE RUN (same pattern as exploitation) --------

def safe_run(module, engagement, name):
    print(f"{Colors.GREEN}[+] Running {name} module{Colors.END}")

    if hasattr(module, "run"):
        try:
            module.run(engagement)
        except Exception as e:
            print(f"{Colors.RED}[!] {name} failed: {e}{Colors.END}")
    else:
        print(f"{Colors.YELLOW}[!] {name} missing run(){Colors.END}")


# -------- PHASE ENTRY --------

def run(engagement):

    while True:
        choice = main_menu()

        if choice == "1":
            safe_run(cron_persistence, engagement, "cron_persistence")

        elif choice == "2":
            safe_run(systemd_persistence, engagement, "systemd_persistence")

        elif choice == "3":
            safe_run(bashrc_persistence, engagement, "bashrc_persistence")

        elif choice == "4":
            safe_run(sshkey_persistence, engagement, "sshkey_persistence")

        elif choice == "5":
            print(f"{Colors.YELLOW}[*] Running full persistence workflow...{Colors.END}")

            safe_run(cron_persistence, engagement, "cron_persistence")
            safe_run(systemd_persistence, engagement, "systemd_persistence")
            safe_run(bashrc_persistence, engagement, "bashrc_persistence")
            safe_run(sshkey_persistence, engagement, "sshkey_persistence")

        elif choice == "6":
            break

        else:
            print(f"{Colors.RED}[!] Invalid option{Colors.END}")
