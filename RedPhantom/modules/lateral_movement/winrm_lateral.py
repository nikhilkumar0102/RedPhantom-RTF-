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
║          WINRM LATERAL MOVEMENT            ║
║       Credential Pivot • Remote Exec       ║
╚════════════════════════════════════════════╝
{Colors.END}
"""

# ================= HELPERS =================

def tool_exists(name):
    return shutil.which(name) is not None


def run_cmd(cmd):
    try:
        return subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT,
            timeout=30
        ).decode()
    except subprocess.CalledProcessError as e:
        return e.output.decode()
    except Exception as e:
        return str(e)


# ================= MAIN =================

def run(engagement):

    print(BANNER)

    if not tool_exists("evil-winrm"):
        print(f"{Colors.RED}[!] evil-winrm not installed{Colors.END}")
        print("Install with: gem install evil-winrm")
        return

    # ---------- Inputs ----------
    target = input(f"{Colors.YELLOW}[*] Target IP: {Colors.END}").strip()
    username = input(f"{Colors.YELLOW}[*] Username: {Colors.END}").strip()
    password = input(f"{Colors.YELLOW}[*] Password: {Colors.END}")
    domain = input(f"{Colors.YELLOW}[*] Domain (blank if local): {Colors.END}").strip()

    user_full = f"{domain}\\{username}" if domain else username

    print(f"\n{Colors.YELLOW}[*] Testing WinRM authentication...{Colors.END}")

    # ---------- Safe command execution ----------
    cmd = (
        f"evil-winrm -i {target} -u '{user_full}' -p '{password}' "
        f"-c whoami"
    )

    output = run_cmd(cmd)

    report = []
    report.append("WINRM LATERAL MOVEMENT RESULT")
    report.append("=" * 50)
    report.append(f"Target : {target}")
    report.append(f"User   : {user_full}\n")
    report.append("Command: whoami\n")
    report.append(output)

    # ---------- Success Detection ----------
    success = "error" not in output.lower()

    if success:
        print(f"{Colors.GREEN}[+] WinRM authentication successful{Colors.END}")
        print(f"{Colors.GREEN}[+] Remote execution achieved{Colors.END}")
        log_event(engagement, f"WinRM lateral success → {target} as {user_full}")
    else:
        print(f"{Colors.RED}[-] WinRM authentication failed{Colors.END}")
        log_event(engagement, f"WinRM lateral FAILED → {target} as {user_full}")

    # ---------- Save ----------
    path = save_text_result(
        engagement,
        phase="lateral_movement",
        category="winrm",
        tool="winrm_lateral",
        content="\n".join(report)
    )

    print(f"\n{Colors.BOLD}[✓] WinRM lateral movement test complete{Colors.END}")
    print(f"{Colors.BLUE}Saved:{Colors.END} {path}")
