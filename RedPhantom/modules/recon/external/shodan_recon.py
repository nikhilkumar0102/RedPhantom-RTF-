#!/usr/bin/env python3
import os
import json
import requests
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
║            SHODAN RECONNAISSANCE            ║
║        External Exposure & Attack Surface  ║
╚════════════════════════════════════════════╝
{Colors.END}
"""

# ================= CONFIG =================
SHODAN_API_URL = "https://api.shodan.io"
API_KEY_FILE = os.path.expanduser("~/.shodan_api")

# ================= HELPERS =================
def load_api_key():
    if not os.path.exists(API_KEY_FILE):
        print(f"{Colors.RED}[!] Shodan API key not found{Colors.END}")
        print(f"{Colors.YELLOW}[*] Create file ~/.shodan_api and paste your API key{Colors.END}")
        return None

    with open(API_KEY_FILE) as f:
        return f.read().strip()


def save_result(engagement, content):
    base = os.path.join(engagement["base"], "recon", "external")
    os.makedirs(base, exist_ok=True)

    filename = f"shodan_recon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(base, filename)

    with open(path, "w") as f:
        f.write(content)

    return path


def shodan_host_lookup(api_key, target):
    url = f"{SHODAN_API_URL}/shodan/host/{target}?key={api_key}"
    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        return None

    return response.json()


# ================= MAIN LOGIC =================
def run(engagement):
    print(BANNER)

    api_key = load_api_key()
    if not api_key:
        return

    target = input(f"{Colors.YELLOW}[*] Enter target IP / Hostname: {Colors.END}").strip()

    print(f"\n{Colors.YELLOW}[*] Querying Shodan for target exposure...{Colors.END}")
    data = shodan_host_lookup(api_key, target)

    output = []
    output.append("SHODAN RECONNAISSANCE REPORT")
    output.append("=" * 55)
    output.append(f"Target: {target}")
    output.append(f"Scan Time: {datetime.now()}")

    if not data:
        print(f"{Colors.RED}[!] No Shodan data found for target{Colors.END}")
        output.append("\nNo data returned from Shodan.")
        path = save_result(engagement, "\n".join(output))
        print(f"{Colors.BLUE}[+] Results saved to: {path}{Colors.END}")
        return

    # ---------- General Info ----------
    print(f"{Colors.GREEN}[+] Target found in Shodan{Colors.END}")
    output.append("\n--- General Information ---")
    output.append(f"IP Address : {data.get('ip_str')}")
    output.append(f"Organization : {data.get('org')}")
    output.append(f"ISP : {data.get('isp')}")
    output.append(f"ASN : {data.get('asn')}")
    output.append(f"Country : {data.get('country_name')}")

    # ---------- Open Ports ----------
    ports = data.get("ports", [])
    output.append("\n--- Open Ports ---")
    if ports:
        for p in ports:
            output.append(f"- Port {p}")
            print(f"{Colors.GREEN}[+] Open Port: {p}{Colors.END}")
    else:
        output.append("No open ports identified")

    # ---------- Services & Technologies ----------
    output.append("\n--- Services & Technologies ---")
    for service in data.get("data", []):
        port = service.get("port")
        product = service.get("product", "Unknown")
        version = service.get("version", "")
        tech = f"{product} {version}".strip()

        output.append(f"Port {port}: {tech}")

    # ---------- Vulnerabilities ----------
    vulns = data.get("vulns", {})
    output.append("\n--- Known Vulnerabilities (CVE) ---")
    if vulns:
        for cve in vulns:
            output.append(f"- {cve}")
            print(f"{Colors.RED}[!] CVE Detected: {cve}{Colors.END}")
    else:
        output.append("No known CVEs reported by Shodan")

    # ---------- Tags ----------
    tags = data.get("tags", [])
    if tags:
        output.append("\n--- Tags ---")
        for tag in tags:
            output.append(f"- {tag}")

    # ---------- Save Results ----------
    path = save_result(engagement, "\n".join(output))

    print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] Shodan reconnaissance completed{Colors.END}")
    print(f"{Colors.BLUE}[+] Results saved to:{Colors.END} {path}")
                                                                    