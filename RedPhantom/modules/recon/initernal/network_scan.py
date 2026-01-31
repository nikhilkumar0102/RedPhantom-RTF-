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
╔══════════════════════════════════════════╗
║        INTERNAL NETWORK RECON             ║
║        Host • Subnet • Services           ║
╚══════════════════════════════════════════╝
{Colors.END}
"""

# ================= HELPERS =================
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Unknown"


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

    filename = f"network_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(base, filename)

    with open(path, "w") as f:
        f.write(content)

    return path


# ================= MAIN LOGIC =================
def run(engagement):
    print(BANNER)

    output = []
    output.append("INTERNAL NETWORK RECONNAISSANCE")
    output.append("=" * 40)

    print(f"{Colors.YELLOW}[*] Gathering local host information...{Colors.END}")
    hostname = socket.gethostname()
    local_ip = get_local_ip()

    output.append(f"\nHost Information:")
    output.append(f"Hostname : {hostname}")
    output.append(f"Local IP : {local_ip}")

    print(f"{Colors.GREEN}[+] Hostname : {hostname}{Colors.END}")
    print(f"{Colors.GREEN}[+] Local IP : {local_ip}{Colors.END}")

    # ---------- Interface & Route Info ----------
    print(f"\n{Colors.YELLOW}[*] Detecting network configuration...{Colors.END}")
    ip_addr = run_cmd("ip addr")
    ip_route = run_cmd("ip route")

    output.append("\nNetwork Interfaces:")
    output.append(ip_addr if ip_addr else "N/A")

    output.append("\nRouting Table:")
    output.append(ip_route if ip_route else "N/A")

    # ---------- Live Host Discovery ----------
    print(f"\n{Colors.YELLOW}[*] Performing ARP-based host discovery...{Colors.END}")
    arp_scan = run_cmd("arp -a")

    if arp_scan:
        output.append("\nDiscovered Hosts (ARP):")
        output.append(arp_scan)
        print(f"{Colors.GREEN}[+] Hosts discovered via ARP{Colors.END}")
    else:
        output.append("\nDiscovered Hosts (ARP): None")
        print(f"{Colors.RED}[!] No ARP results found{Colors.END}")

    # ---------- Basic Service Discovery ----------
    print(f"\n{Colors.YELLOW}[*] Performing lightweight service discovery (top ports)...{Colors.END}")
    ports = [22, 80, 443, 445, 3389]
    open_ports = []

    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((local_ip, port))
        if result == 0:
            open_ports.append(port)
        sock.close()

    output.append("\nLocal Host Open Ports:")
    if open_ports:
        for p in open_ports:
            output.append(f"- Port {p} open")
            print(f"{Colors.GREEN}[+] Port {p} open{Colors.END}")
    else:
        output.append("No common ports open")
        print(f"{Colors.YELLOW}[-] No common ports detected{Colors.END}")

    # ---------- Save Results ----------
    path = save_result(engagement, "\n".join(output))

    print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] Network scan completed{Colors.END}")
    print(f"{Colors.BLUE}[+] Results saved to:{Colors.END} {path}")
