import os
import subprocess
import socket
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
╔════════════════════════════════════════════╗
║        SUBDOMAIN ENUMERATION                ║
║   Passive • Resolution • Liveness           ║
╚════════════════════════════════════════════╝
{Colors.END}
"""

# ================= HELPERS =================
def tool_exists(tool):
    return shutil.which(tool) is not None


def install_subfinder():
    print(f"{Colors.YELLOW}[*] Installing subfinder...{Colors.END}")
    subprocess.run(
        "go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
        shell=True
    )
    os.environ["PATH"] += f":{os.path.expanduser('~/go/bin')}"


def run_cmd(cmd):
    try:
        return subprocess.check_output(
            cmd, shell=True, stderr=subprocess.DEVNULL
        ).decode().splitlines()
    except Exception:
        return []


def resolve_domain(domain):
    try:
        return socket.gethostbyname(domain)
    except Exception:
        return None


def check_liveness(domain):
    for proto in ["https", "http"]:
        try:
            result = subprocess.run(
                ["curl", "-I", "-m", "3", f"{proto}://{domain}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if result.returncode == 0:
                return proto.upper()
        except Exception:
            pass
    return None


def save_results(engagement, content):
    base = os.path.join(engagement["base"], "recon", "external")
    os.makedirs(base, exist_ok=True)

    filename = f"subdomains_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(base, filename)

    with open(path, "w") as f:
        f.write(content)

    return path


# ================= MAIN =================
def run(engagement):
    print(BANNER)

    domain = input(f"{Colors.YELLOW}[*] Target domain: {Colors.END}").strip()

    if not tool_exists("subfinder"):
        install_subfinder()

    print(f"\n{Colors.YELLOW}[*] Enumerating subdomains (passive)...{Colors.END}")
    subdomains = run_cmd(f"subfinder -silent -d {domain}")

    if not subdomains:
        print(f"{Colors.RED}[!] No subdomains found{Colors.END}")
        return

    live, resolved, unresolved = [], [], []

    report = []
    report.append("SUBDOMAIN ENUMERATION RESULTS")
    report.append("=" * 50)
    report.append(f"Target Domain: {domain}")
    report.append(f"Total Found : {len(subdomains)}\n")

    for sub in sorted(set(subdomains)):
        ip = resolve_domain(sub)
        if not ip:
            unresolved.append(sub)
            continue

        proto = check_liveness(sub)
        if proto:
            live.append((sub, ip, proto))
            print(f"{Colors.GREEN}[LIVE]{Colors.END} {sub} → {ip} ({proto})")
        else:
            resolved.append((sub, ip))
            print(f"{Colors.YELLOW}[RESOLVED]{Colors.END} {sub} → {ip}")

    report.append("\nLIVE SUBDOMAINS:")
    for s, ip, proto in live:
        report.append(f"{s} | {ip} | {proto}")

    report.append("\nRESOLVED (NOT LIVE):")
    for s, ip in resolved:
        report.append(f"{s} | {ip}")

    report.append("\nUNRESOLVED:")
    for s in unresolved:
        report.append(s)

    report.append("\nSUMMARY:")
    report.append(f"Live       : {len(live)}")
    report.append(f"Resolved   : {len(resolved)}")
    report.append(f"Unresolved : {len(unresolved)}")

    path = save_results(engagement, "\n".join(report))

    print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] Subdomain enumeration completed{Colors.END}")
    print(f"{Colors.BLUE}[+] Results saved to:{Colors.END} {path}")
