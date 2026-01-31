#!/usr/bin/env python3
import os
import subprocess
import shutil
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
╔══════════════════════════════════════════════════╗
║        EXTERNAL ATTACK SURFACE MAPPING            ║
║        ASN • CIDR • Tech Stack • Summary          ║
╚══════════════════════════════════════════════════╝
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


def tool_exists(tool):
    return shutil.which(tool) is not None


def save_results(engagement, content):
    base = os.path.join(engagement["base"], "recon", "external")
    os.makedirs(base, exist_ok=True)

    filename = f"attack_surface_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(base, filename)

    with open(path, "w") as f:
        f.write(content)

    return path


# ================= MAIN LOGIC =================
def run(engagement):
    print(BANNER)

    domain = input(f"{Colors.YELLOW}[*] Target domain: {Colors.END}").strip()

    output = []
    output.append("EXTERNAL ATTACK SURFACE REPORT")
    output.append("=" * 60)
    output.append(f"Target Domain: {domain}\n")

    # ---------- ASN DISCOVERY ----------
    print(f"{Colors.YELLOW}[*] Discovering ASN information...{Colors.END}")
    asn_info = run_cmd(f"whois {domain} | grep -i 'origin\\|aut-num'")

    if asn_info:
        output.append("ASN INFORMATION:")
        output.append(asn_info + "\n")
        print(f"{Colors.GREEN}[+] ASN identified{Colors.END}")
    else:
        output.append("ASN INFORMATION: Not found\n")
        print(f"{Colors.YELLOW}[-] ASN not found{Colors.END}")

    # ---------- CIDR EXPANSION ----------
    print(f"\n{Colors.YELLOW}[*] Extracting CIDR ranges...{Colors.END}")
    cidrs = run_cmd(f"whois {domain} | grep -Eo '([0-9]{{1,3}}\\.){{3}}[0-9]{{1,3}}/[0-9]{{1,2}}'")

    cidr_list = sorted(set(cidrs.splitlines())) if cidrs else []

    if cidr_list:
        output.append("CIDR RANGES:")
        for c in cidr_list:
            output.append(f"- {c}")
        print(f"{Colors.GREEN}[+] {len(cidr_list)} CIDR ranges found{Colors.END}")
    else:
        output.append("CIDR RANGES: None found")
        print(f"{Colors.YELLOW}[-] No CIDR ranges discovered{Colors.END}")

    # ---------- TECH STACK FINGERPRINTING ----------
    print(f"\n{Colors.YELLOW}[*] Fingerprinting exposed technologies...{Colors.END}")
    tech = run_cmd(f"curl -I https://{domain} | grep -i 'server\\|x-powered-by'")

    if tech:
        output.append("\nTECH STACK FINGERPRINT:")
        output.append(tech)
        print(f"{Colors.GREEN}[+] Tech stack identified{Colors.END}")
    else:
        output.append("\nTECH STACK FINGERPRINT: Not detected")
        print(f"{Colors.YELLOW}[-] Tech stack not detected{Colors.END}")

    # ---------- ATTACK SURFACE SUMMARY ----------
    output.append("\nATTACK SURFACE SUMMARY:")
    output.append(f"- Domain               : {domain}")
    output.append(f"- ASN Identified        : {'YES' if asn_info else 'NO'}")
    output.append(f"- CIDR Ranges Found     : {len(cidr_list)}")
    output.append(f"- Web Stack Identified  : {'YES' if tech else 'NO'}")

    output.append("\nRECOMMENDED NEXT STEPS:")
    output.append("- Scan exposed CIDR ranges for live hosts")
    output.append("- Focus on identified web technologies")
    output.append("- Correlate with subdomain & DNS findings")

    # ---------- SAVE ----------
    path = save_results(engagement, "\n".join(output))

    print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] External attack surface mapping completed{Colors.END}")
    print(f"{Colors.BLUE}[+] Results saved to:{Colors.END} {path}")
