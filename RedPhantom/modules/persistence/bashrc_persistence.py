#!/usr/bin/env python3

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


# ================= BANNER =================

BANNER = f"""
{Colors.BLUE}{Colors.BOLD}
╔════════════════════════════════════════════╗
║        BASHRC PERSISTENCE ANALYZER         ║
║     Shell Startup File Persistence Check   ║
╚════════════════════════════════════════════╝
{Colors.END}
"""


# ================= TARGET FILES =================

BASH_FILES = [
    os.path.expanduser("~/.bashrc"),
    os.path.expanduser("~/.profile"),
    os.path.expanduser("~/.bash_profile"),
    "/etc/bash.bashrc",
    "/etc/profile",
]


SUSPICIOUS_PATTERNS = [
    "curl ",
    "wget ",
    "nc ",
    "bash -i",
    "/dev/tcp/",
    "python -c",
    "perl -e",
    "base64",
    "nohup",
    "chmod +x",
]


# ================= HELPERS =================

def scan_file(path):
    hits = []
    lines_flagged = []

    try:
        with open(path, "r", errors="ignore") as f:
            for lineno, line in enumerate(f, start=1):
                for pat in SUSPICIOUS_PATTERNS:
                    if pat in line:
                        hits.append(pat)
                        lines_flagged.append((lineno, line.strip()))

    except Exception as e:
        hits.append(f"read_error:{e}")

    return hits, lines_flagged


def save_results(engagement, content):
    base = os.path.join(engagement["base"], "persistence")
    os.makedirs(base, exist_ok=True)

    fname = f"bashrc_persistence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(base, fname)

    with open(path, "w") as f:
        f.write(content)

    return path


# ================= MAIN ENTRY =================

def run(engagement):

    print(BANNER)
    print(f"{Colors.WHITE}Scanning shell startup files for persistence vectors{Colors.END}\n")

    report = []
    report.append("BASHRC PERSISTENCE CHECK")
    report.append("=" * 50)

    found = 0

    for file_path in BASH_FILES:

        if os.path.exists(file_path):
            found += 1
            print(f"{Colors.GREEN}[+] Found:{Colors.END} {file_path}")

            hits, flagged = scan_file(file_path)

            if hits:
                print(f"{Colors.YELLOW}[!] Suspicious patterns detected{Colors.END}")
                for ln, text in flagged[:5]:
                    print(f"    line {ln}: {text}")

                report.append(f"\n[{file_path}]")
                for ln, text in flagged:
                    report.append(f"line {ln}: {text}")

            else:
                print(f"{Colors.BLUE}[-] No suspicious patterns{Colors.END}")

        else:
            print(f"{Colors.RED}[-] Missing:{Colors.END} {file_path}")
            report.append(f"\n[{file_path}] — NOT FOUND")

        print()

    # ================= SAVE =================

    report.append("\nSUMMARY")
    report.append(f"Files found: {found}/{len(BASH_FILES)}")

    output_path = save_results(engagement, "\n".join(report))

    print(f"{Colors.GREEN}{Colors.BOLD}[✓] Bashrc persistence scan complete{Colors.END}")
    print(f"{Colors.BLUE}[+] Report saved:{Colors.END} {output_path}")
