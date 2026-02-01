from core.logger import log_event

# ================= SAFE OPTIONAL IMPORTS =================

def safe_import(name):
    try:
        module = __import__(f"modules.lateral_movement.{name}", fromlist=["run"])
        return module
    except:
        return None


smb_lateral = safe_import("smb_lateral")
ssh_lateral = safe_import("ssh_lateral")
winrm_lateral = safe_import("winrm_lateral")
wmiexec_lateral = safe_import("wmiexec_lateral")
rdp_lateral = safe_import("rdp_lateral")


# ================= COLORS =================
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'


# ================= BANNER =================
BANNER = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════╗
║                  LATERAL MOVEMENT                     ║
║        Pivot • Remote Execution • Host Spread         ║
╚══════════════════════════════════════════════════════╝
{Colors.END}
"""

PHASE_INFO = f"""
{Colors.DIM}
Using validated credentials to expand access scope.
All actions are logged to the engagement record.
{Colors.END}
"""


# ================= AUTH CONFIRM =================

def confirm():
    ans = input(f"{Colors.RED}[!] Confirm lateral movement authorization (yes/no): {Colors.END}")
    return ans.lower() == "yes"


# ================= MENU =================

def show_menu():
    print(BANNER)
    print(PHASE_INFO)

    print(f"""
{Colors.WHITE}[1]{Colors.END} SMB Lateral Movement
{Colors.WHITE}[2]{Colors.END} SSH Lateral Movement
{Colors.WHITE}[3]{Colors.END} WinRM Lateral Movement
{Colors.WHITE}[4]{Colors.END} WMIExec Lateral Movement
{Colors.WHITE}[5]{Colors.END} RDP Lateral Check
{Colors.WHITE}[6]{Colors.END} Movement Activity Summary
{Colors.RED}[7]{Colors.END} Back
""")

    return input(f"{Colors.BOLD}Select movement method:{Colors.END} ").strip()


# ================= EXEC WRAPPER =================

def exec_module(mod, name, engagement):
    if not mod:
        print(f"{Colors.YELLOW}[!] {name} module not available{Colors.END}")
        return

    if not confirm():
        print(f"{Colors.RED}[!] Authorization denied{Colors.END}")
        return

    log_event(engagement, f"{name} lateral movement started")
    mod.run(engagement)
    log_event(engagement, f"{name} lateral movement completed")


# ================= MAIN =================

def run(engagement):

    log_event(engagement, "Entered Lateral Movement phase")

    while True:
        choice = show_menu()

        if choice == "1":
            exec_module(smb_lateral, "SMB", engagement)

        elif choice == "2":
            exec_module(ssh_lateral, "SSH", engagement)

        elif choice == "3":
            exec_module(winrm_lateral, "WinRM", engagement)

        elif choice == "4":
            exec_module(wmiexec_lateral, "WMIExec", engagement)

        elif choice == "5":
            exec_module(rdp_lateral, "RDP", engagement)

        elif choice == "6":
            show_summary(engagement)

        elif choice == "7":
            log_event(engagement, "Exited Lateral Movement phase")
            break

        else:
            print(f"{Colors.RED}[!] Invalid option{Colors.END}")


# ================= SUMMARY =================

def show_summary(engagement):

    print(f"\n{Colors.BLUE}{Colors.BOLD}Movement Activity Log{Colors.END}")

    log_path = engagement["base"] + "/logs/activity.log"

    try:
        with open(log_path) as f:
            lines = [l for l in f if "lateral" in l.lower()]
    except:
        lines = []

    if not lines:
        print(f"{Colors.YELLOW}No lateral movement activity yet{Colors.END}")
        return

    for line in lines[-20:]:
        print(line.strip())
