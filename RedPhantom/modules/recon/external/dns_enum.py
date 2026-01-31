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
║             DNS ENUMERATION                ║
║   Records • NameServers • Misconfigs       ║
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


def save_results(engagement, content):
    base = os.path.join(engagement["base"], "recon", "external")
    os.makedirs(base, exist_ok=True)

    filename = f"dns_enum_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(base, filename)

    with open(path, "w") as f:
        f.write(content)

    return path


# ================= MAIN =================
def run(engagement):
    print(BANNER)

    domain = input(f"{Colors.YELLOW}[*] Target domain: {Colors.END}").strip()

    report = []
    report.append("DNS ENUMERATION RESULTS")
    report.append("=" * 50)
    report.append(f"Target Domain: {domain}\n")

    record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]
    counts = {}

    print(f"{Colors.YELLOW}[*] Enumerating DNS records...{Colors.END}")
    for rtype in record_types:
        result = run_cmd(f"dig {rtype} {domain} +short")
        if result:
            report.append(f"\n{rtype} Records:")
            report.append(result)
            counts[rtype] = len(result.splitlines())
            print(f"{Colors.GREEN}[+] {rtype} records found{Colors.END}")
        else:
            counts[rtype] = 0
            print(f"{Colors.YELLOW}[-] No {rtype} records{Colors.END}")

    print(f"\n{Colors.YELLOW}[*] Checking zone transfer...{Colors.END}")
    ns_records = run_cmd(f"dig NS {domain} +short")
    zone_transfer = False

    if ns_records:
        for ns in ns_records.splitlines():
            zt = run_cmd(f"dig AXFR {domain} @{ns}")
            if zt and "Transfer failed" not in zt:
                zone_transfer = True
                report.append(f"\n[!] ZONE TRANSFER ALLOWED on {ns}")
                report.append(zt)
                print(f"{Colors.RED}[!] Zone transfer allowed on {ns}{Colors.END}")
                break

    if not zone_transfer:
        report.append("\nZone Transfer: Not Allowed")
        print(f"{Colors.GREEN}[+] Zone transfer not allowed{Colors.END}")

    report.append("\nSUMMARY:")
    for r, c in counts.items():
        report.append(f"{r} Records : {c}")
    report.append(f"Zone Transfer Allowed : {'YES' if zone_transfer else 'NO'}")

    path = save_results(engagement, "\n".join(report))

    print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] DNS enumeration completed{Colors.END}")
    print(f"{Colors.BLUE}[+] Results saved to:{Colors.END} {path}")
                                                                    