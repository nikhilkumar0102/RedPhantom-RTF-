import subprocess
import shutil
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
║          WMI LATERAL MOVEMENT              ║
║       Remote • Command • Execution         ║
╚════════════════════════════════════════════╝
{Colors.END}
"""

# ================= HELPERS =================

def tool_exists(name):
    return shutil.which(name) is not None


def confirm_auth():
    ans = input(
        f"{Colors.RED}[!] Confirm lateral movement authorization (yes/no): {Colors.END}"
    )
    return ans.lower() == "yes"


def run_cmd(cmd):
    try:
        return subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT
        ).decode()
    except subprocess.CalledProcessError as e:
        return e.output.decode()


# ================= MAIN =================

def run(engagement):

    print(BANNER)

    if not confirm_auth():
        print(f"{Colors.YELLOW}[-] Operation cancelled{Colors.END}")
        return

    if not tool_exists("impacket-wmiexec"):
        print(f"{Colors.RED}[!] impacket-wmiexec not found{Colors.END}")
        print("Install with: pip install impacket")
        return

    target = input("Target IP: ").strip()
    domain = input("Domain (or .): ").strip()
    username = input("Username: ").strip()
    password = input("Password: ")
    command = input("Command to execute: ").strip()

    print(f"\n{Colors.YELLOW}[*] Executing remote command via WMI...{Colors.END}")

    cmd = (
        f"impacket-wmiexec {domain}/{username}:'{password}'@{target} "
        f"\"{command}\""
    )

    output = run_cmd(cmd)

    # ---------- Logging ----------
    log_event(
        engagement,
        f"WMI lateral movement → {target} → cmd: {command}"
    )

    # ---------- Save Result ----------
    report = (
        f"WMI LATERAL MOVEMENT EXECUTION\n"
        f"{'='*50}\n"
        f"Target   : {target}\n"
        f"User     : {domain}\\{username}\n"
        f"Command  : {command}\n\n"
        f"OUTPUT:\n{output}\n"
    )

    path = save_text_result(
        engagement,
        phase="lateral_movement",
        category="wmi",
        tool="wmiexec",
        content=report
    )

    print(f"\n{Colors.GREEN}[✓] Command executed{Colors.END}")
    print(f"{Colors.BLUE}[+] Output saved to:{Colors.END} {path}")
