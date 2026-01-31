import os
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

BANNER = f"""
{Colors.BLUE}{Colors.BOLD}
╔════════════════════════════════════════════╗
║          CREDENTIAL STORE MANAGER          ║
║          Add • View • Deduplicate          ║
╚════════════════════════════════════════════╝
{Colors.END}
"""

# ================= PATH =================
def cred_file(engagement):
    base = os.path.join(engagement["base"], "credentials")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "creds.txt")


# ================= CORE =================
def add_credential(engagement):
    print(BANNER)

    user = input("Username: ").strip()
    pwd = input("Password/Hash: ").strip()
    source = input("Source (smb/share/manual/etc): ").strip()
    host = input("Host found on: ").strip()

    line = f"{user}|{pwd}|{source}|{host}"

    path = cred_file(engagement)

    existing = []
    if os.path.exists(path):
        with open(path) as f:
            existing = [x.strip() for x in f.readlines()]

    if line in existing:
        print(f"{Colors.YELLOW}[!] Credential already stored{Colors.END}")
        return

    with open(path, "a") as f:
        f.write(line + "\n")

    print(f"{Colors.GREEN}[+] Credential stored successfully{Colors.END}")


def view_credentials(engagement):
    print(BANNER)
    path = cred_file(engagement)

    if not os.path.exists(path):
        print(f"{Colors.RED}[!] No credentials stored yet{Colors.END}")
        return

    print(f"{Colors.WHITE}Stored Credentials:{Colors.END}\n")

    with open(path) as f:
        for i, line in enumerate(f, 1):
            u, p, s, h = line.strip().split("|")
            print(f"{i}. {u} : {p}  ({s} @ {h})")


# ================= MENU =================
def run(engagement):
    while True:
        print(f"""
{Colors.WHITE}[1] Add Credential{Colors.END}
{Colors.WHITE}[2] View Stored Credentials{Colors.END}
{Colors.RED}[3] Back{Colors.END}
""")

        c = input("Select option: ").strip()

        if c == "1":
            add_credential(engagement)
        elif c == "2":
            view_credentials(engagement)
        elif c == "3":
            break
