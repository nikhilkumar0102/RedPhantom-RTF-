#!/usr/bin/env python3

import os
from datetime import datetime


# -------- COLORS --------

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


# -------- BANNER --------

BANNER = f"""
{Colors.BLUE}{Colors.BOLD}
╔════════════════════════════════════════════╗
║           COMMAND HISTORY REVIEW           ║
║      Bash • Zsh • Root • User History      ║
╚════════════════════════════════════════════╝
{Colors.END}
"""


# -------- TARGET FILES --------

def get_history_files():
    return [
        os.path.expanduser("~/.bash_history"),
        os.path.expanduser("~/.zsh_history"),
        "/root/.bash_history",
    ]


# -------- ANALYSIS --------

SUSPICIOUS_KEYWORDS = [
    "ssh ",
    "scp ",
    "wget ",
    "curl ",
    "nc ",
    "ncat ",
    "chmod",
    "chown",
    "useradd",
    "adduser",
    "passwd",
    "crontab",
    "systemctl",
    "service ",
    "python ",
    "bash ",
]


def analyze_history(path):
    findings = []
    total = 0

    try:
        with open(path, "r", errors="ignore") as f:
            for line in f:
                total += 1
                for key in SUSPICIOUS_KEYWORDS:
                    if key in line:
                        findings.append(line.strip())
                        break

    except Exception as e:
        return {"error": str(e), "lines": 0, "hits": []}

    return {
        "lines": total,
        "hits": findings[:50]  # limit output size
    }


# -------- REPORT SAVE --------

def save_report(engagement, data):
    if not engagement:
        os.makedirs("reports", exist_ok=True)
        path = f"reports/history_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    else:
        base = os.path.join(engagement["base"], "post_exploitation")
        os.makedirs(base, exist_ok=True)
        path = os.path.join(base, "history_review.txt")

    with open(path, "w") as f:
        f.write(data)

    print(f"{Colors.GREEN}[+] Report saved → {path}{Colors.END}")


# -------- MAIN ENTRY --------

def run(engagement):

    print(BANNER)

    results = []
    report_lines = []

    for hist_file in get_history_files():

        print(f"{Colors.YELLOW}[*] Checking {hist_file}{Colors.END}")

        if not os.path.exists(hist_file):
            print(f"{Colors.RED}    Not found{Colors.END}")
            continue

        print(f"{Colors.GREEN}    Found{Colors.END}")

        analysis = analyze_history(hist_file)

        if "error" in analysis:
            print(f"{Colors.RED}    Read error: {analysis['error']}{Colors.END}")
            continue

        hit_count = len(analysis["hits"])

        print(f"{Colors.BLUE}    Lines: {analysis['lines']} | Suspicious: {hit_count}{Colors.END}")

        results.append({
            "file": hist_file,
            "lines": analysis["lines"],
            "suspicious_hits": hit_count,
            "sample_hits": analysis["hits"]
        })

        report_lines.append(f"\n=== {hist_file} ===")
        report_lines.append(f"Total lines: {analysis['lines']}")
        report_lines.append(f"Suspicious hits: {hit_count}")
        report_lines.extend(analysis["hits"])

    # -------- SAVE --------

    save_report(engagement, "\n".join(report_lines))

    return {
        "module": "history_review",
        "files_checked": len(results),
        "details": results
    }
