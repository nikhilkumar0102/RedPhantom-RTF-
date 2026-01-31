# modules/initial_access/initial_access_main.py
#!/usr/bin/env python3
import os
import sys

#================== PATH FIX ===============
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

# ================= IMPORTS =================

from modules.initial_access.creds import (
    cred_context,
    cred_validate,
    cred_reuse,
    cred_store
)

from modules.initial_access.web import (
    web_discovery,
    web_vuln_scan
)

# ================= COLORS =================

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

# ================= BANNER =================

BANNER = f"""
{Colors.RED}{Colors.BOLD}
╔════════════════════════════════════════════╗
║           INITIAL ACCESS PHASE              ║
║     Foothold • Credentials • Exploits       ║
╚════════════════════════════════════════════╝
{Colors.END}
"""

# ================= MENUS =================

def main_menu():
    print(BANNER)
    print(f"""
{Colors.WHITE}[1] Web-Based Attacks{Colors.END}
{Colors.WHITE}[2] Credential-Based Access{Colors.END}
{Colors.RED}[3] Back to Main Menu{Colors.END}
""")
    return input("Select option: ").strip()


def credential_menu():
    print(f"""
{Colors.YELLOW}{Colors.BOLD}Credential-Based Access{Colors.END}

{Colors.WHITE}[1] Credential Context Review{Colors.END}
{Colors.WHITE}[2] Credential Store Manager{Colors.END}
{Colors.WHITE}[3] Credential Validation{Colors.END}
{Colors.WHITE}[4] Credential Reuse Check{Colors.END}
{Colors.RED}[5] Back{Colors.END}
""")
    return input("Select option: ").strip()


def web_menu():
    print(f"""
{Colors.YELLOW}{Colors.BOLD}Web Initial Access{Colors.END}

{Colors.WHITE}[1] Web Discovery{Colors.END}
{Colors.WHITE}[2] Web Vulnerability Scan{Colors.END}
{Colors.RED}[3] Back{Colors.END}
""")
    return input("Select option: ").strip()




# ================= SAFE RUN =================

def safe_run(module, engagement, name):
    if hasattr(module, "run"):
        module.run(engagement)
    else:
        print(f"{Colors.YELLOW}[!] {name} missing run(){Colors.END}")


# ================= PHASE ENTRY =================

def run(engagement):

    while True:
        choice = main_menu()

        # ================= WEB =================
        if choice == "1":
            while True:
                w = web_menu()

                if w == "1":
                    safe_run(web_discovery, engagement, "web_discovery")

                elif w == "2":
                    safe_run(web_vuln_scan, engagement, "web_vuln_scan")

                elif w == "3":
                    break

                else:
                    print(f"{Colors.RED}[!] Invalid option{Colors.END}")

        # ================= CREDS =================
        elif choice == "2":
            while True:
                c = credential_menu()

                if c == "1":
                    safe_run(cred_context, engagement, "cred_context")

                elif c == "2":
                    safe_run(cred_store, engagement, "cred_store")

                elif c == "3":
                    safe_run(cred_validate, engagement, "cred_validate")

                elif c == "4":
                    safe_run(cred_reuse, engagement, "cred_reuse")

                elif c == "5":
                    break

                else:
                    print(f"{Colors.RED}[!] Invalid option{Colors.END}")


        # ================= EXIT =================
        elif choice == "3":
            break

        else:
            print(f"{Colors.RED}[!] Invalid option{Colors.END}")
