#!/usr/bin/env python3

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from modules.cleanup import (
    artifact_cleaner,
    history_review,
    workspace_cleaner
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


BANNER = f"""
{Colors.BLUE}{Colors.BOLD}
╔════════════════════════════════════════════╗
║         CLEANUP & ANTI-FORENSICS           ║
║      Artifact • History • Workspace        ║
╚════════════════════════════════════════════╝
{Colors.END}
"""


def main_menu():
    print(BANNER)
    print(f"""
{Colors.WHITE}[1] Artifact Cleaner{Colors.END}
{Colors.WHITE}[2] Command History Review{Colors.END}
{Colors.WHITE}[3] Workspace Cleaner{Colors.END}
{Colors.YELLOW}[4] Run Full Cleanup Phase{Colors.END}
{Colors.RED}[5] Back to Main Menu{Colors.END}
""")
    return input("Select option: ").strip()


def safe_run(module, engagement, name):
    print(f"{Colors.GREEN}[+] Running {name}{Colors.END}")
    if hasattr(module, "run"):
        try:
            module.run(engagement)
        except Exception as e:
            print(f"{Colors.RED}[!] {name} failed: {e}{Colors.END}")
    else:
        print(f"{Colors.YELLOW}[!] {name} missing run(){Colors.END}")


def run(engagement):

    while True:
        choice = main_menu()

        if choice == "1":
            safe_run(artifact_cleaner, engagement, "artifact_cleaner")

        elif choice == "2":
            safe_run(history_review, engagement, "history_review")

        elif choice == "3":
            safe_run(workspace_cleaner, engagement, "workspace_cleaner")

        elif choice == "4":
            safe_run(artifact_cleaner, engagement, "artifact_cleaner")
            safe_run(history_review, engagement, "history_review")
            safe_run(workspace_cleaner, engagement, "workspace_cleaner")

        elif choice == "5":
            break

        else:
            print(f"{Colors.RED}[!] Invalid option{Colors.END}")
