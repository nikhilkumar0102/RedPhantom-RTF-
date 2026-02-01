import sys
from core.engagement import (
    init_engagement,
    load_engagement,
    delete_engagement
)
from core.logger import log_event
from core.runner import run_phase

# ================= COLORS =================
class Colors:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

# ================= BANNER =================
BANNER = f"""
{Colors.RED}{Colors.BOLD}
██████╗ ███████╗██████╗ ██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗
██╔══██╗██╔════╝██╔══██╗██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║
██████╔╝█████╗  ██║  ██║██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
██╔══██╗██╔══╝  ██║  ██║██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
██║  ██║███████╗██████╔╝██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝

        REDPHANTOM – Red Team Adversary Simulation Framework
        Stealth • Persistence • Impact • Reporting
{Colors.END}
"""

# ================= MENUS =================
def show_main_menu():
    print(f"""
{Colors.WHITE}[0] Engagement Management{Colors.END}
{Colors.WHITE}[1] Reconnaissance{Colors.END}
{Colors.YELLOW}[2] Initial Access{Colors.END}
{Colors.YELLOW}[3] Exploitation{Colors.END}
{Colors.YELLOW}[4] Post-Exploitation{Colors.END}
{Colors.YELLOW}[5] Lateral Movement{Colors.END}
{Colors.YELLOW}[6] Persistence{Colors.END}
{Colors.RED}[7] Cleanup & Anti-Forensics{Colors.END}
{Colors.WHITE}[8] AI Exposure & Risk Assessment{Colors.END}
{Colors.YELLOW}[9] Run Full Red Team Simulation{Colors.END}
{Colors.RED}[99] Exit{Colors.END}
""")
    return input("Select option: ").strip()


def show_engagement_menu():
    print("""
Engagement Management
1. Create New Engagement
2. Continue Existing Engagement
3. Delete Engagement
4. Back to Main Menu
""")
    return input("Select option: ").strip()

# ================= MAIN =================
def main():
    print(BANNER)

    engagement = None

    while True:

        # ========= ENGAGEMENT REQUIRED =========
        if engagement is None:
            choice = show_engagement_menu()

            if choice == "1":
                engagement = init_engagement()
                log_event(engagement, "New engagement created")

            elif choice == "2":
                engagement = load_engagement()
                if engagement:
                    log_event(engagement, "Engagement loaded")

            elif choice == "3":
                delete_engagement()

            elif choice == "4":
                continue

            else:
                print(f"{Colors.RED}[!] Invalid option{Colors.END}")
                continue

        # ========= MAIN TOOL MENU =========
        choice = show_main_menu()

        if choice == "0":
            engagement = None  # go back to engagement menu

        elif choice == "1":
            run_phase(engagement, "recon")

        elif choice == "2":
            run_phase(engagement, "initial_access")

        elif choice == "3":
            run_phase(engagement, "exploitation")

        elif choice == "4":
            run_phase(engagement, "post_exploitation")

        elif choice == "5":
            run_phase(engagement, "lateral_movement")

        elif choice == "6":
            run_phase(engagement, "persistence")

        elif choice == "7":
            run_phase(engagement, "cleanup")

        elif choice == "8":
            run_phase(engagement, "ai_scan")

        elif choice == "9":
            for phase in [
                "recon",
                "initial_access",
                "exploitation",
                "post_exploitation",
                "reporting"
            ]:
                run_phase(engagement, phase)

        elif choice == "99":
            print(f"{Colors.RED}[!] Exiting REDPHANTOM. Stay stealthy.{Colors.END}")
            sys.exit(0)

        else:
            print(f"{Colors.RED}[!] Invalid option{Colors.END}")

if __name__ == "__main__":
    main()
