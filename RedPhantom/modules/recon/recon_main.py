#!/usr/bin/env python3
import os
import sys

# ================= PATH FIX =================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

# ========= External Recon =========
from external.shodan_recon import run as shodan_run
from external.subdomain_enum import run as subdomain_run
from external.dns_enum import run as dns_run
from external.nmap_port_vuln_scan import run as nmap_port

# ========= Internal Recon =========
from internal.network_scan import run as network_run
from internal.smb_enum import run as smb_run
from internal.smb_auth_enum import run as smb_auth_run

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
RECON_BANNER = f"""
{Colors.BLUE}{Colors.BOLD}
██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝

        RECONNAISSANCE PHASE
{Colors.END}
"""

# ================= MENUS =================
def menu():
    print(RECON_BANNER)
    print(f"""
{Colors.WHITE}[1] External Reconnaissance{Colors.END}
{Colors.WHITE}[2] Internal Reconnaissance{Colors.END}
{Colors.RED}[3] Back{Colors.END}
""")
    return input("Select option: ").strip()


def external_menu():
    print(f"""
{Colors.YELLOW}External Recon{Colors.END}
{Colors.WHITE}[1] Shodan Recon{Colors.END}
{Colors.WHITE}[2] Subdomain Enumeration{Colors.END}
{Colors.WHITE}[3] DNS Enumeration{Colors.END}
{Colors.WHITE}[4] Nmap Port & Vulnerability Discovery{Colors.END}
{Colors.RED}[5] Back{Colors.END}
""")
    return input("Select option: ").strip()


def internal_menu():
    print(f"""
{Colors.YELLOW}Internal Recon{Colors.END}
{Colors.WHITE}[1] Network Discovery{Colors.END}
{Colors.WHITE}[2] SMB Enumeration{Colors.END}
{Colors.WHITE}[3] Authenticated SMB Enumeration{Colors.END}
{Colors.RED}[4] Back{Colors.END}
""")
    return input("Select option: ").strip()


# ================= CORE LOGIC =================
def run(engagement):
    while True:
        choice = menu()

        if choice == "1":
            while True:
                ext = external_menu()
                if ext == "1":
                    shodan_run(engagement)
                elif ext == "2":
                    subdomain_run(engagement)
                elif ext == "3":
                    dns_run(engagement)
                elif ext == "4":
                    nmap_port(engagement)
                elif ext == "5":
                    break

        elif choice == "2":
            while True:
                inte = internal_menu()
                if inte == "1":
                    network_run(engagement)
                elif inte == "2":
                    smb_run(engagement)
                elif inte == "3":
                    smb_auth_run(engagement)
                elif inte == "4":
                    break

        elif choice == "3":
            break


# ================= ENTRY POINT =================
if __name__ == "__main__":
    print(f"{Colors.RED}[!] recon_main.py is not meant to be run standalone.{Colors.END}")
    print(f"{Colors.YELLOW}[*] This module is executed from main.py with an active engagement.{Colors.END}")
