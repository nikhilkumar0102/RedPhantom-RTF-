import os
import subprocess
from datetime import datetime

# ================= COLORS =================
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

BANNER = f"""
{Colors.BLUE}{Colors.BOLD}
╔════════════════════════════════════════════╗
║        CREDENTIAL REUSE ANALYSIS           ║
║        Multi-Host Validation               ║
╚════════════════════════════════════════════╝
{Colors.END}
"""

# ================= HELPERS =================
def cred_file(engagement):
    return os.path.join(engagement["base"], "credentials", "creds.txt")


def save_results(engagement, content):
    base = os.path.join(engagement["base"], "credentials")
    os.makedirs(base, exist_ok=True)

    name = f"cred_reuse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(base, name)

    with open(path, "w") as f:
        f.write(content)

    return path


def run_cmd(cmd):
    try:
        return subprocess.check_output(
            cmd, shell=True, stderr=subprocess.DEVNULL
        ).decode()
    except:
        return ""


# ================= MAIN =================
def run(engagement):
    print(BANNER)

    path = cred_file(engagement)
    if not os.path.exists(path):
        print(f"{Colors.RED}[!] No stored credentials found{Colors.END}")
        return

    targets = input(
        "Target hosts (comma separated): "
    ).split(",")

    with open(path) as f:
        creds = [line.strip().split("|") for line in f.readlines()]

    report = []
    report.append("CREDENTIAL REUSE RESULTS")
    report.append("=" * 50)

    for host in targets:
        host = host.strip()
        print(f"\n{Colors.YELLOW}[*] Testing host {host}{Colors.END}")
        report.append(f"\nHost: {host}")

        for user, pwd, src, found_host in creds:

            smb = run_cmd(
                f"smbclient -L //{host} -U '{user}%{pwd}'"
            )

            if smb:
                print(f"{Colors.GREEN}[+] VALID → {user}@{host}{Colors.END}")
                report.append(f"VALID SMB → {user} : {pwd}")

                if "ADMIN$" in smb or "C$" in smb:
                    print(f"{Colors.RED}[!] ADMIN ACCESS{Colors.END}")
                    report.append("  Privilege: ADMIN")
            else:
                print(f"{Colors.YELLOW}[-] invalid → {user}{Colors.END}")

    outpath = save_results(engagement, "\n".join(report))

    print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] Credential reuse scan completed{Colors.END}")
    print(f"{Colors.BLUE}[+] Results saved to:{Colors.END} {outpath}")
