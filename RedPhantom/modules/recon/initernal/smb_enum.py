#!/usr/bin/env python3
import os
import subprocess
import socket
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
║        SMB ENUMERATION (INTERNAL)           ║
║        Shares • Versions • Access           ║
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

    filename = f"smb_enum_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(base, filename)

    with open(path, "w") as f:
        f.write(content)

    return path


def is_port_open(host, port=445):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


# ================= MAIN LOGIC =================
def run(engagement):
    print(BANNER)

    output = []
    output.append("SMB ENUMERATION RESULTS")
    output.append("=" * 45)

    # ---------- Target ----------
    target = input(f"{Colors.YELLOW}[*] Enter target IP/Hostname: {Colors.END}").strip()
    output.append(f"\nTarget: {target}")

    # ---------- SMB Reachability ----------
    print(f"\n{Colors.YELLOW}[*] Checking SMB (445/tcp) reachability...{Colors.END}")
    if not is_port_open(target):
        print(f"{Colors.RED}[!] SMB service not reachable on {target}{Colors.END}")
        output.append("SMB Status: Not reachable")
        path = save_result(engagement, "\n".join(output))
        print(f"{Colors.BLUE}[+] Results saved to: {path}{Colors.END}")
        return

    print(f"{Colors.GREEN}[+] SMB service is reachable{Colors.END}")
    output.append("SMB Status: Reachable")

    # ---------- SMB Version Detection ----------
    print(f"\n{Colors.YELLOW}[*] Detecting SMB version...{Colors.END}")
    smb_version = run_cmd(f"smbclient -L //{target} -N")
    if smb_version:
        output.append("\nSMB Version / Server Info:")
        output.append(smb_version)
        print(f"{Colors.GREEN}[+] SMB version information retrieved{Colors.END}")
    else:
        output.append("\nSMB Version: Unable to detect")
        print(f"{Colors.RED}[!] Could not detect SMB version{Colors.END}")

    # ---------- Null Session Share Enumeration ----------
    print(f"\n{Colors.YELLOW}[*] Enumerating SMB shares (null session)...{Colors.END}")
    shares = run_cmd(f"smbclient -L //{target} -N 2>/dev/null")

    if shares:
        output.append("\nDiscovered SMB Shares (Anonymous):")
        output.append(shares)
        print(f"{Colors.GREEN}[+] SMB shares discovered (anonymous){Colors.END}")
    else:
        output.append("\nNo SMB shares accessible anonymously")
        print(f"{Colors.YELLOW}[-] No anonymous SMB shares found{Colors.END}")

    # ---------- OS & Domain Info ----------
    print(f"\n{Colors.YELLOW}[*] Extracting OS / Domain information...{Colors.END}")
    os_info = run_cmd(f"nmap --script smb-os-discovery -p 445 {target}")

    if os_info:
        output.append("\nSMB OS Discovery:")
        output.append(os_info)
        print(f"{Colors.GREEN}[+] OS / Domain info collected{Colors.END}")
    else:
        output.append("\nOS / Domain info: Not available")
        print(f"{Colors.YELLOW}[-] OS discovery returned no data{Colors.END}")

    # ---------- Save Results ----------
    path = save_result(engagement, "\n".join(output))

    print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] SMB Enumeration completed{Colors.END}")
    print(f"{Colors.BLUE}[+] Results saved to:{Colors.END} {path}")
