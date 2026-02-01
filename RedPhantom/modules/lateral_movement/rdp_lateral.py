import subprocess
import socket
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
║           RDP LATERAL MOVEMENT             ║
║       Credentialed • Controlled • Logged   ║
╚════════════════════════════════════════════╝
{Colors.END}
"""

# ================= HELPERS =================

def tool_exists(tool):
    return shutil.which(tool) is not None


def port_open(host, port=3389):
    try:
        s = socket.socket()
        s.settimeout(2)
        result = s.connect_ex((host, port))
        s.close()
        return result == 0
    except:
        return False


# ================= MAIN =================

def run(engagement):

    print(BANNER)

    # ---------- Authorization Gate ----------
    confirm = input(
        f"{Colors.RED}[!] Confirm lateral movement authorization (yes/no): {Colors.END}"
    ).strip().lower()

    if confirm != "yes":
        print(f"{Colors.YELLOW}[-] Operation cancelled{Colors.END}")
        return

    # ---------- Tool Check ----------
    if not tool_exists("xfreerdp"):
        print(f"{Colors.RED}[!] xfreerdp not installed{Colors.END}")
        print("Install with: sudo apt install freerdp2-x11")
        return

    # ---------- Inputs ----------
    target = input(f"{Colors.YELLOW}Target host: {Colors.END}").strip()
    username = input(f"{Colors.YELLOW}Username: {Colors.END}").strip()
    password = input(f"{Colors.YELLOW}Password: {Colors.END}")

    # ---------- RDP Port Check ----------
    print(f"\n{Colors.YELLOW}[*] Checking RDP port...{Colors.END}")
    if not port_open(target):
        print(f"{Colors.RED}[!] RDP port 3389 not reachable{Colors.END}")
        return

    print(f"{Colors.GREEN}[+] RDP port reachable{Colors.END}")

    # ---------- Build Command ----------
    cmd = [
        "xfreerdp",
        f"/v:{target}",
        f"/u:{username}",
        f"/p:{password}",
        "/cert-ignore"
    ]

    print(f"\n{Colors.YELLOW}[*] Launching RDP session...{Colors.END}")

    log_event(engagement, f"RDP lateral attempt → {target} as {username}")

    try:
        subprocess.run(cmd)
        success = True
    except Exception as e:
        success = False
        err = str(e)

    # ---------- Reporting ----------
    report = []
    report.append("RDP LATERAL MOVEMENT RESULT")
    report.append("=" * 50)
    report.append(f"Target   : {target}")
    report.append(f"Username : {username}")
    report.append(f"Port 3389: Reachable")

    if success:
        report.append("Result   : Session launched (check operator confirmation)")
        print(f"{Colors.GREEN}[✓] RDP client executed{Colors.END}")
    else:
        report.append(f"Result   : Failed → {err}")
        print(f"{Colors.RED}[!] RDP launch failed{Colors.END}")

    path = save_text_result(
        engagement,
        phase="lateral_movement",
        category="rdp",
        tool="rdp_lateral",
        content="\n".join(report)
    )

    print(f"\n{Colors.BLUE}[+] Result saved:{Colors.END} {path}")
