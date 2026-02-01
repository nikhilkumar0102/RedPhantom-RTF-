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
║        NMAP PORT & VULNERABILITY SCAN       ║
║   Ports • Services • NSE Vuln Detection    ║
╚════════════════════════════════════════════╝
{Colors.END}
"""


# ================= HELPERS =================
def nmap_exists():
    return subprocess.call(
        ["which", "nmap"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ) == 0


def run_cmd(cmd):
    try:
        return subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT
        ).decode(errors="ignore")
    except subprocess.CalledProcessError as e:
        return e.output.decode(errors="ignore")


def save_results(engagement, content):
    base = os.path.join(engagement["base"], "recon", "external")
    os.makedirs(base, exist_ok=True)

    filename = f"nmap_port_vuln_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(base, filename)

    with open(path, "w") as f:
        f.write(content)

    return path


def vuln_detected(output):
    indicators = [
        "VULNERABLE:",
        "State: VULNERABLE",
        "CVE-"
    ]
    return any(i in output for i in indicators)


# ================= MAIN =================
def run(engagement):
    print(BANNER)

    if not nmap_exists():
        print(f"{Colors.RED}[!] Nmap not installed. Aborting scan.{Colors.END}")
        return

    target = input(f"{Colors.YELLOW}[*] Target IP / Host: {Colors.END}").strip()

    print(f"\n{Colors.YELLOW}[*] Running Nmap safe port & NSE scan...{Colors.END}")

    cmd = [
        "nmap",
        "-sS",
        "-sV",
        "--script", "safe,vuln",
        "-T4",
        target
    ]

    output = run_cmd(cmd)

    report = []
    report.append("NMAP PORT & VULNERABILITY SCAN")
    report.append("=" * 55)
    report.append(f"Target : {target}")
    report.append(f"Time   : {datetime.now().isoformat()}")
    report.append("")
    report.append(output)

    # ---------- Alert Section ----------
    if vuln_detected(output):
        report.append("\n[ALERT] POTENTIAL VULNERABILITIES IDENTIFIED")
        print(f"{Colors.RED}{Colors.BOLD}[ALERT] Vulnerabilities detected!{Colors.END}")
    else:
        report.append("\n[OK] No vulnerabilities detected by NSE scripts")
        print(f"{Colors.GREEN}[✓] No NSE-reported vulnerabilities found{Colors.END}")

    path = save_results(engagement, "\n".join(report))

    print(f"{Colors.BLUE}[+] Results saved to:{Colors.END} {path}")
                                                                    