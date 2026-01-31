import os
import subprocess
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
{Colors.BLUE}{Colors.BOLD}
╔════════════════════════════════════════════╗
║        CREDENTIAL VALIDATION               ║
║        SMB • SSH • Access Check            ║
╚════════════════════════════════════════════╝
{Colors.END}
"""

# ================= HELPERS =================
def save_results(engagement, content):
    base = os.path.join(engagement["base"], "recon", "internal")
    os.makedirs(base, exist_ok=True)

    filename = f"cred_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(base, filename)

    with open(path, "w") as f:
        f.write(content)

    return path


def is_port_open(host, port, timeout=2):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def smb_auth_check(target, username, password):
    cmd = f"smbclient -L //{target} -U '{username}%{password}'"
    try:
        result = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT
        ).decode()

        if "NT_STATUS_LOGON_FAILURE" in result:
            return False, "Invalid credentials"
        return True, "Authenticated successfully"
    except subprocess.CalledProcessError as e:
        output = e.output.decode()
        if "NT_STATUS_LOGON_FAILURE" in output:
            return False, "Invalid credentials"
        return False, "SMB error or access denied"


def ssh_auth_check(target, username, password):
    cmd = (
        f"sshpass -p '{password}' ssh "
        f"-o StrictHostKeyChecking=no "
        f"-o ConnectTimeout=5 "
        f"{username}@{target} exit"
    )
    try:
        subprocess.check_output(
            cmd, shell=True, stderr=subprocess.DEVNULL
        )
        return True, "Authenticated successfully"
    except Exception:
        return False, "Authentication failed"


# ================= MAIN LOGIC =================
def run(engagement):
    print(BANNER)

    target = input(f"{Colors.YELLOW}[*] Target IP/Hostname: {Colors.END}").strip()
    username = input(f"{Colors.YELLOW}[*] Username: {Colors.END}").strip()
    password = input(f"{Colors.YELLOW}[*] Password: {Colors.END}")

    report = []
    report.append("CREDENTIAL VALIDATION RESULTS")
    report.append("=" * 50)
    report.append(f"Target  : {target}")
    report.append(f"Username: {username}\n")

    print(f"\n{Colors.YELLOW}[*] Checking reachable services...{Colors.END}")

    smb_open = is_port_open(target, 445)
    ssh_open = is_port_open(target, 22)

    report.append("Service Reachability:")
    report.append(f"SMB (445): {'Open' if smb_open else 'Closed'}")
    report.append(f"SSH (22) : {'Open' if ssh_open else 'Closed'}\n")

    # ---------- SMB Validation ----------
    if smb_open:
        print(f"{Colors.YELLOW}[*] Validating credentials against SMB...{Colors.END}")
        success, msg = smb_auth_check(target, username, password)

        if success:
            print(f"{Colors.GREEN}[✓] SMB authentication successful{Colors.END}")
            report.append("SMB Authentication: SUCCESS")
        else:
            print(f"{Colors.RED}[✗] SMB authentication failed{Colors.END}")
            report.append(f"SMB Authentication: FAILED ({msg})")
    else:
        report.append("SMB Authentication: Skipped (port closed)")

    # ---------- SSH Validation ----------
    if ssh_open:
        print(f"{Colors.YELLOW}[*] Validating credentials against SSH...{Colors.END}")
        success, msg = ssh_auth_check(target, username, password)

        if success:
            print(f"{Colors.GREEN}[✓] SSH authentication successful{Colors.END}")
            report.append("SSH Authentication: SUCCESS")
        else:
            print(f"{Colors.RED}[✗] SSH authentication failed{Colors.END}")
            report.append(f"SSH Authentication: FAILED ({msg})")
    else:
        report.append("SSH Authentication: Skipped (port closed)")

    # ---------- Summary ----------
    report.append("\nSUMMARY:")
    if smb_open or ssh_open:
        report.append("Credential Status: Tested")
    else:
        report.append("Credential Status: No reachable services")

    path = save_results(engagement, "\n".join(report))

    print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] Credential validation completed{Colors.END}")
    print(f"{Colors.BLUE}[+] Results saved to:{Colors.END} {path}")
