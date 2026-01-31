import os
import subprocess
import shutil
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
{Colors.RED}{Colors.BOLD}
╔════════════════════════════════════════════╗
║        WEB VULNERABILITY SCANNING           ║
║    Recon Summary • Controlled Nuclei       ║
╚════════════════════════════════════════════╝
{Colors.END}
"""

# ================= HELPERS =================
def tool_exists(tool):
    return shutil.which(tool) is not None


def install_nuclei():
    print(f"{Colors.YELLOW}[*] Installing nuclei...{Colors.END}")
    subprocess.run(
        "go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
        shell=True
    )
    os.environ["PATH"] += f":{os.path.expanduser('~/go/bin')}"


def run_cmd(cmd):
    try:
        return subprocess.check_output(
            cmd, shell=True, stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return ""


def resolve_ip(host):
    try:
        return socket.gethostbyname(host)
    except Exception:
        return None


def detect_protocol(host):
    for proto in ["https", "http"]:
        try:
            r = subprocess.run(
                ["curl", "-I", "-m", "4", f"{proto}://{host}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            if r.returncode == 0:
                return proto
        except Exception:
            pass
    return None


def save_results(engagement, content):
    base = os.path.join(engagement["base"], "vulnerability")
    os.makedirs(base, exist_ok=True)

    filename = f"web_vuln_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(base, filename)

    with open(path, "w") as f:
        f.write(content)

    return path

# ================= MAIN =================
def run(engagement):
    print(BANNER)

    target = input(f"{Colors.YELLOW}[*] Target domain / IP: {Colors.END}").strip()

    report = []
    report.append("WEB VULNERABILITY SCAN REPORT")
    report.append("=" * 55)
    report.append(f"Target: {target}")
    report.append(f"Timestamp: {datetime.now()}\n")

    # ---------- Recon Summary ----------
    print(f"{Colors.YELLOW}[*] Performing auto web reconnaissance...{Colors.END}")

    ip = resolve_ip(target)
    proto = detect_protocol(target)

    report.append("RECON SUMMARY")
    report.append("-" * 30)
    report.append(f"Resolved IP : {ip if ip else 'Unresolved'}")
    report.append(f"Protocol   : {proto.upper() if proto else 'Not reachable'}")

    if proto:
        headers = run_cmd(f"curl -I {proto}://{target}")
        server = "Unknown"
        for line in headers.splitlines():
            if line.lower().startswith("server:"):
                server = line.split(":", 1)[1].strip()

        report.append(f"Server     : {server}")
        print(f"{Colors.GREEN}[+] Web service reachable ({proto.upper()}){Colors.END}")
    else:
        print(f"{Colors.RED}[!] Target not reachable over HTTP/HTTPS{Colors.END}")
        path = save_results(engagement, "\n".join(report))
        print(f"{Colors.BLUE}[+] Results saved to:{Colors.END} {path}")
        return

    # ---------- Nuclei Scan ----------
    print(f"\n{Colors.YELLOW}[*] Preparing controlled nuclei scan...{Colors.END}")

    if not tool_exists("nuclei"):
        install_nuclei()

    nuclei_templates = "cves,misconfiguration,exposures"
    nuclei_cmd = (
        f"nuclei -u {proto}://{target} "
        f"-t {nuclei_templates} "
        f"-severity low,medium,high,critical "
        f"-silent"
    )

    print(f"{Colors.YELLOW}[*] Running nuclei (controlled templates)...{Colors.END}")
    nuclei_output = run_cmd(nuclei_cmd)

    report.append("\nNUCLEI FINDINGS")
    report.append("-" * 30)

    if nuclei_output:
        report.append(nuclei_output)
        print(f"{Colors.RED}[!] Vulnerabilities detected{Colors.END}")
    else:
        report.append("No findings detected using selected templates.")
        print(f"{Colors.GREEN}[+] No vulnerabilities detected{Colors.END}")

    # ---------- Save ----------
    path = save_results(engagement, "\n".join(report))

    print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] Web vulnerability scan completed{Colors.END}")
    print(f"{Colors.BLUE}[+] Results saved to:{Colors.END} {path}")
