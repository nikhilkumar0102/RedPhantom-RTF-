import os
import subprocess
import shutil
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
║        WEB DIRECTORY DISCOVERY              ║
║        ffuf • gobuster • brute-force        ║
╚════════════════════════════════════════════╝
{Colors.END}
"""

# ================= HELPERS =================
def tool_exists(tool):
    return shutil.which(tool) is not None


def run_cmd(cmd, outfile):
    with open(outfile, "w") as f:
        subprocess.run(cmd, shell=True, stdout=f, stderr=subprocess.DEVNULL)


def ensure_tool(tool):
    if tool_exists(tool):
        return True

    print(f"{Colors.YELLOW}[*] {tool} not found. Installing...{Colors.END}")

    if tool == "ffuf":
        subprocess.run(
            "go install github.com/ffuf/ffuf@latest",
            shell=True
        )
        os.environ["PATH"] += f":{os.path.expanduser('~/go/bin')}"
        return tool_exists("ffuf")

    if tool == "gobuster":
        subprocess.run(
            "sudo apt install -y gobuster",
            shell=True
        )
        return tool_exists("gobuster")

    return False


def prepare_output_dir(engagement):
    base = os.path.join(
        engagement["base"], "recon", "external", "web_discovery"
    )
    os.makedirs(base, exist_ok=True)
    return base


# ================= MAIN =================
def run(engagement):
    print(BANNER)

    target = input(f"{Colors.YELLOW}[*] Target URL (https://example.com): {Colors.END}").strip()
    if target.endswith("/"):
        target = target[:-1]

    wordlist = input(
        f"{Colors.YELLOW}[*] Wordlist path (leave blank for default): {Colors.END}"
    ).strip()

    if not wordlist:
        wordlist = "/usr/share/wordlists/dirb/common.txt"

    if not os.path.exists(wordlist):
        print(f"{Colors.RED}[!] Wordlist not found{Colors.END}")
        return

    print(f"\n{Colors.WHITE}Choose scanning method:{Colors.END}")
    print("[1] ffuf (fast, recommended)")
    print("[2] gobuster (classic)")
    print("[3] run both")
    choice = input("Select option: ").strip()

    outdir = prepare_output_dir(engagement)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    summary = []
    summary.append("WEB DISCOVERY SUMMARY")
    summary.append("=" * 40)
    summary.append(f"Target   : {target}")
    summary.append(f"Wordlist : {wordlist}\n")

    # ---------- FFUF ----------
    if choice in ["1", "3"]:
        if not ensure_tool("ffuf"):
            print(f"{Colors.RED}[!] ffuf installation failed{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}[*] Running ffuf...{Colors.END}")
            ffuf_out = os.path.join(outdir, f"ffuf_{timestamp}.txt")

            cmd = (
                f"ffuf -u {target}/FUZZ "
                f"-w {wordlist} "
                f"-mc 200,204,301,302,307,401,403 "
                f"-t 50 -s"
            )

            run_cmd(cmd, ffuf_out)
            print(f"{Colors.GREEN}[+] ffuf scan completed{Colors.END}")
            summary.append(f"[+] ffuf output : {ffuf_out}")

    # ---------- GOBUSTER ----------
    if choice in ["2", "3"]:
        if not ensure_tool("gobuster"):
            print(f"{Colors.RED}[!] gobuster installation failed{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}[*] Running gobuster...{Colors.END}")
            gobuster_out = os.path.join(outdir, f"gobuster_{timestamp}.txt")

            cmd = (
                f"gobuster dir -u {target} "
                f"-w {wordlist} "
                f"-q -t 50 "
                f"-s 200,204,301,302,307,401,403"
            )

            run_cmd(cmd, gobuster_out)
            print(f"{Colors.GREEN}[+] gobuster scan completed{Colors.END}")
            summary.append(f"[+] gobuster output : {gobuster_out}")

    # ---------- SAVE SUMMARY ----------
    summary_path = os.path.join(outdir, "summary.txt")
    with open(summary_path, "w") as f:
        f.write("\n".join(summary))

    print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] Web discovery completed{Colors.END}")
    print(f"{Colors.BLUE}[+] Summary saved to:{Colors.END} {summary_path}")
