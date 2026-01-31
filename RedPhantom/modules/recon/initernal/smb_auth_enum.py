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
║     AUTHENTICATED SMB ENUMERATION           ║
║     Shares • Access • Domain Intel          ║
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
    base = os.path.join(engagement["base"], "recon", "internal")
    os.makedirs(base, exist_ok=True)

    filename = f"smb_auth_enum_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(base, filename)

    with open(path, "w") as f:
        f.write(content)

    return path


# ================= MAIN LOGIC =================
def run(engagement):
    print(BANNER)

    output = []
    output.append("AUTHENTICATED SMB ENUMERATION")
    output.append("=" * 50)

    # ---------- Target & Credentials ----------
    target = input(f"{Colors.YELLOW}[*] Target IP/Hostname: {Colors.END}").strip()
    username = input(f"{Colors.YELLOW}[*] Username: {Colors.END}").strip()
    password = input(f"{Colors.YELLOW}[*] Password: {Colors.END}")

    output.append(f"\nTarget: {target}")
    output.append(f"User  : {username}")

    auth = f"-U '{username}%{password}'"

    # ---------- Share Enumeration ----------
    print(f"\n{Colors.YELLOW}[*] Enumerating SMB shares (authenticated)...{Colors.END}")
    shares = run_cmd(f"smbclient -L //{target} {auth}")

    if shares:
        output.append("\nAccessible SMB Shares:")
        output.append(shares)
        print(f"{Colors.GREEN}[+] Shares enumerated successfully{Colors.END}")
    else:
        output.append("\nSMB Share Enumeration: Failed")
        print(f"{Colors.RED}[!] Failed to enumerate shares{Colors.END}")

    # ---------- Password Policy ----------
    print(f"\n{Colors.YELLOW}[*] Retrieving password policy...{Colors.END}")
    pass_policy = run_cmd(
        f"rpcclient -U '{username}%{password}' {target} -c 'getdompwinfo'"
    )

    if pass_policy:
        output.append("\nPassword Policy:")
        output.append(pass_policy)
        print(f"{Colors.GREEN}[+] Password policy retrieved{Colors.END}")
    else:
        output.append("\nPassword Policy: Not accessible")
        print(f"{Colors.YELLOW}[-] Password policy not accessible{Colors.END}")

    # ---------- Domain Users ----------
    print(f"\n{Colors.YELLOW}[*] Enumerating domain users...{Colors.END}")
    users = run_cmd(
        f"rpcclient -U '{username}%{password}' {target} -c 'enumdomusers'"
    )

    if users:
        output.append("\nDomain Users:")
        output.append(users)
        print(f"{Colors.GREEN}[+] Domain users enumerated{Colors.END}")
    else:
        output.append("\nDomain Users: Enumeration failed")
        print(f"{Colors.YELLOW}[-] Could not enumerate domain users{Colors.END}")

    # ---------- Domain Groups ----------
    print(f"\n{Colors.YELLOW}[*] Enumerating domain groups...{Colors.END}")
    groups = run_cmd(
        f"rpcclient -U '{username}%{password}' {target} -c 'enumdomgroups'"
    )

    if groups:
        output.append("\nDomain Groups:")
        output.append(groups)
        print(f"{Colors.GREEN}[+] Domain groups enumerated{Colors.END}")
    else:
        output.append("\nDomain Groups: Enumeration failed")
        print(f"{Colors.YELLOW}[-] Could not enumerate domain groups{Colors.END}")

    # ---------- Save Results ----------
    path = save_result(engagement, "\n".join(output))

    print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] Authenticated SMB enumeration completed{Colors.END}")
    print(f"{Colors.BLUE}[+] Results saved to:{Colors.END} {path}")
