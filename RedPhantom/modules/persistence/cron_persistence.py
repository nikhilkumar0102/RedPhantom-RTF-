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
║          CRON PERSISTENCE ANALYZER         ║
║      Scheduled Tasks • User • System       ║
╚════════════════════════════════════════════╝
{Colors.END}
"""


# ================= HELPERS =================

CRON_PATHS = [
    "/etc/crontab",
    "/etc/cron.d",
    "/etc/cron.daily",
    "/etc/cron.hourly",
    "/etc/cron.weekly",
    "/var/spool/cron",
    "/var/spool/cron/crontabs"
]

SUSPICIOUS_KEYS = [
    "curl",
    "wget",
    "bash -i",
    "nc ",
    "/dev/tcp/",
    "python -c",
    "perl -e",
    "base64",
    "nohup"
]


def scan_file(path):
    hits = []

    try:
        with open(path, "r", errors="ignore") as f:
            data = f.read()

        for key in SUSPICIOUS_KEYS:
            if key in data:
                hits.append(key)

    except Exception as e:
        hits.append(f"read_error:{str(e)}")

    return hits


def save_results(engagement, content):
    base = os.path.join(engagement["base"], "persistence")
    os.makedirs(base, exist_ok=True)

    name = f"cron_persistence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(base, name)

    with open(path, "w") as f:
        f.write(content)

    return path


# ================= MAIN =================

def run(engagement):

    print(BANNER)
    print(f"{Colors.YELLOW}[*] Scanning cron persistence locations...{Colors.END}\n")

    report_lines = []
    report_lines.append("CRON PERSISTENCE ANALYSIS")
    report_lines.append("=" * 50)

    findings = []
    checked = 0

    for path in CRON_PATHS:

        if not os.path.exists(path):
            print(f"{Colors.RED}[✖] Missing: {path}{Colors.END}")
            continue

        print(f"{Colors.GREEN}[✔] Found: {path}{Colors.END}")
        checked += 1

        if os.path.isfile(path):
            hits = scan_file(path)

            if hits:
                print(f"{Colors.YELLOW}    Suspicious patterns: {', '.join(hits)}{Colors.END}")
                findings.append((path, hits))

        elif os.path.isdir(path):
            for fname in os.listdir(path):
                fpath = os.path.join(path, fname)

                if os.path.isfile(fpath):
                    hits = scan_file(fpath)
                    if hits:
                        print(f"{Colors.YELLOW}    Suspicious: {fpath}{Colors.END}")
                        findings.append((fpath, hits))

    # ---------- Build Report ----------

    report_lines.append(f"Paths checked: {checked}\n")

    if findings:
        report_lines.append("Suspicious Entries Found:\n")
        for f, hits in findings:
            report_lines.append(f"{f} → {', '.join(hits)}")
    else:
        report_lines.append("No suspicious cron persistence patterns detected")

    # ---------- Save ----------

    save_path = save_results(engagement, "\n".join(report_lines))

    print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] Cron persistence scan complete{Colors.END}")
    print(f"{Colors.BLUE}[+] Report saved to:{Colors.END} {save_path}")

    # ---------- Structured Return ----------

    structured_data = {
        "module": "cron_persistence",
        "paths_checked": checked,
        "suspicious_found": len(findings),
        "timestamp": datetime.utcnow().isoformat(),
        "report_file": save_path
    }

    return structured_data
