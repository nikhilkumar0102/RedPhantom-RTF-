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
║           SMB LATERAL MOVEMENT             ║
║      Controlled • Credential-Based         ║
╚════════════════════════════════════════════╝
{Colors.END}
"""

# ================= HELPERS =================

def run_cmd(cmd):
    try:
        return subprocess.check_output(
            cmd, shell=True, stderr=subprocess.DEVNULL
        ).decode()
    except:
        return ""


def confirm():
    ans = input(f"{Colors.RED}[!] Confirm lateral movement authorization (yes/no): {Colors.END}")
    return ans.lower() == "yes"


def tool_exists(tool):
    return subprocess.call(
        f"which {tool}",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ) == 0


# ================= MAIN =================

def run(engagement):

    print(BANNER)

    if not confirm():
        print(f"{Colors.RED}[-] Operation cancelled{Colors.END}")
        return

    target = input("Target host: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ")

    auth = f"{username}%{password}"

    report = []
    report.append("SMB LATERAL MOVEMENT RESULTS")
    report.append("="*60)
    report.append(f"Target: {target}")
    report.append(f"User  : {username}\n")

    log_event(engagement, f"SMB lateral attempt → {target} ({username})")

    # ---------- Share Access Test ----------
    print(f"{Colors.YELLOW}[*] Testing SMB authenticated access...{Colors.END}")
    shares = run_cmd(f"smbclient -L //{target} -U '{auth}'")

    if shares:
        print(f"{Colors.GREEN}[+] SMB login successful{Colors.END}")
        report.append("[+] SMB authentication SUCCESS")
        report.append(shares)

        if "ADMIN$" in shares or "C$" in shares:
            print(f"{Colors.RED}[!] Administrative share access detected{Colors.END}")
            report.append("[!] ADMIN share access available")
        else:
            report.append("[-] No admin shares accessible")

    else:
        print(f"{Colors.RED}[-] SMB authentication failed{Colors.END}")
        report.append("[-] SMB authentication failed")

        save_text_result(
            engagement,
            phase="lateral_movement",
            category="smb",
            tool="smb_lateral",
            content="\n".join(report)
        )
        return

    # ---------- Remote Command via rpcclient ----------
    print(f"\n{Colors.YELLOW}[*] Checking RPC command capability...{Colors.END}")

    rpc = run_cmd(
        f"rpcclient -U '{auth}' {target} -c 'srvinfo'"
    )

    if rpc:
        print(f"{Colors.GREEN}[+] RPC service accessible{Colors.END}")
        report.append("\n[+] RPC Access:")
        report.append(rpc)
    else:
        report.append("\n[-] RPC access not available")

    # ---------- PsExec Style Execution ----------
    if tool_exists("psexec.py"):
        print(f"\n{Colors.YELLOW}[*] PsExec available — execution option enabled{Colors.END}")
        report.append("\n[+] psexec.py available for remote execution")
    else:
        print(f"{Colors.YELLOW}[-] psexec.py not installed{Colors.END}")
        report.append("\n[-] psexec.py not installed")

    # ---------- Save ----------
    path = save_text_result(
        engagement,
        phase="lateral_movement",
        category="smb",
        tool="smb_lateral",
        content="\n".join(report)
    )

    print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] SMB lateral module completed{Colors.END}")
    print(f"{Colors.BLUE}Results saved →{Colors.END} {path}")
