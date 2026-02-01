import subprocess
from utils.result_saver import save_text_result
from core.logger import log_event

# ================= COLORS =================
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

# ================= BANNER =================
BANNER = f"""
{Colors.BLUE}{Colors.BOLD}
╔════════════════════════════════════════════╗
║          SSH LATERAL MOVEMENT              ║
║        Pivot • Verify • Enumerate          ║
╚════════════════════════════════════════════╝
{Colors.END}
"""


# ================= HELPERS =================

def run_cmd(cmd):
    try:
        return subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.DEVNULL,
            timeout=20
        ).decode()
    except Exception:
        return ""


def sshpass_exists():
    return subprocess.call(
        "which sshpass",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ) == 0


# ================= MAIN =================

def run(engagement):

    print(BANNER)

    # ---------- Authorization ----------
    confirm = input(
        f"{Colors.YELLOW}[!] Confirm lateral movement authorization (yes/no): {Colors.END}"
    ).lower()

    if confirm != "yes":
        print(f"{Colors.RED}[!] Aborted by operator{Colors.END}")
        return

    # ---------- Inputs ----------
    target = input("Target host: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ")

    if not sshpass_exists():
        print(f"{Colors.RED}[!] sshpass not installed — required for password auth{Colors.END}")
        print("Install with: sudo apt install sshpass")
        return

    print(f"\n{Colors.YELLOW}[*] Testing SSH authentication...{Colors.END}")

    test_cmd = (
        f"sshpass -p '{password}' "
        f"ssh -o StrictHostKeyChecking=no "
        f"-o ConnectTimeout=5 "
        f"{username}@{target} whoami"
    )

    whoami = run_cmd(test_cmd)

    if not whoami:
        print(f"{Colors.RED}[-] SSH authentication failed{Colors.END}")
        log_event(engagement, f"SSH lateral FAILED → {target} ({username})")
        return

    print(f"{Colors.GREEN}[+] SSH access confirmed as {whoami.strip()}{Colors.END}")
    log_event(engagement, f"SSH lateral SUCCESS → {target} ({username})")

    # ---------- Controlled Recon ----------
    print(f"{Colors.YELLOW}[*] Gathering pivot host context...{Colors.END}")

    commands = {
        "whoami": "whoami",
        "hostname": "hostname",
        "id": "id",
        "sudo": "sudo -l"
    }

    results = {}

    for label, cmd in commands.items():
        full = (
            f"sshpass -p '{password}' "
            f"ssh -o StrictHostKeyChecking=no "
            f"{username}@{target} \"{cmd}\""
        )
        results[label] = run_cmd(full)

    # ---------- Build Report ----------
    report = []
    report.append("SSH LATERAL MOVEMENT RESULT")
    report.append("=" * 50)
    report.append(f"Target   : {target}")
    report.append(f"User     : {username}")
    report.append(f"Identity : {whoami.strip()}\n")

    for k, v in results.items():
        report.append(f"\n[{k.upper()}]")
        report.append(v.strip() if v else "N/A")

    # ---------- Save ----------
    path = save_text_result(
        engagement,
        phase="lateral_movement",
        category="ssh",
        tool="ssh_lateral",
        content="\n".join(report)
    )

    print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] SSH lateral movement completed{Colors.END}")
    print(f"{Colors.BLUE}Saved results →{Colors.END} {path}")
