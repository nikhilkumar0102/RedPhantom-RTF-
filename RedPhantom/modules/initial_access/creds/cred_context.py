#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime

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
{Colors.BLUE}{Colors.BOLD}
╔════════════════════════════════════════════╗
║     CREDENTIAL CONTEXT DISCOVERY            ║
║     Identity • Privileges • Access          ║
╚════════════════════════════════════════════╝
{Colors.END}
"""

# ================= HELPERS =================
def run_cmd(cmd):
    try:
        return subprocess.check_output(
            cmd, shell=True, stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return ""


def save_result(engagement, content):
    base = os.path.join(engagement["base"], "credentials")
    os.makedirs(base, exist_ok=True)

    filename = f"cred_context_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(base, filename)

    with open(path, "w") as f:
        f.write(content)

    return path


# ================= MAIN =================
def run(engagement):
    print(BANNER)

    target = input(f"{Colors.YELLOW}[*] Target IP/Hostname: {Colors.END}").strip()
    username = input(f"{Colors.YELLOW}[*] Username: {Colors.END}").strip()
    password = input(f"{Colors.YELLOW}[*] Password: {Colors.END}")

    report = []
    report.append("CREDENTIAL CONTEXT DISCOVERY")
    report.append("=" * 50)
    report.append(f"Target   : {target}")
    report.append(f"Username : {username}\n")

    # ---------- Identity ----------
    print(f"{Colors.YELLOW}[*] Identifying user context...{Colors.END}")
    whoami = run_cmd(
        f"rpcclient -U '{username}%{password}' {target} -c 'getusername'"
    )
    if whoami:
        report.append("User Identity:")
        report.append(whoami)
        print(f"{Colors.GREEN}[+] User identity retrieved{Colors.END}")
    else:
        report.append("User Identity: Unable to retrieve")
        print(f"{Colors.RED}[!] Could not retrieve identity{Colors.END}")

    # ---------- Group Membership ----------
    print(f"{Colors.YELLOW}[*] Enumerating group memberships...{Colors.END}")
    groups = run_cmd(
        f"rpcclient -U '{username}%{password}' {target} -c 'enumdomgroups'"
    )
    if groups:
        report.append("\nGroup Memberships:")
        report.append(groups)
        print(f"{Colors.GREEN}[+] Group membership data collected{Colors.END}")
    else:
        report.append("\nGroup Memberships: Not accessible")
        print(f"{Colors.YELLOW}[-] Group info not accessible{Colors.END}")

    # ---------- Admin Privilege Check ----------
    print(f"{Colors.YELLOW}[*] Checking administrative privileges...{Colors.END}")
    admin_check = run_cmd(
        f"smbclient //{target}/C$ -U '{username}%{password}' -c 'dir'"
    )
    if admin_check:
        report.append("\nAdministrative Access: YES (C$ accessible)")
        print(f"{Colors.GREEN}[+] Administrative privileges detected{Colors.END}")
    else:
        report.append("\nAdministrative Access: NO")
        print(f"{Colors.YELLOW}[-] No admin access detected{Colors.END}")

    # ---------- Save ----------
    path = save_result(engagement, "\n".join(report))

    print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] Credential context discovery completed{Colors.END}")
    print(f"{Colors.BLUE}[+] Results saved to:{Colors.END} {path}")
