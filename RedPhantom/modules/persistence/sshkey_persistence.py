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
║          SSH KEY PERSISTENCE CHECK         ║
║     Authorized Keys • Backdoor Access      ║
╚════════════════════════════════════════════╝
{Colors.END}
"""


# ================= HELPERS =================

SUSPICIOUS_KEYWORDS = [
    "command=",
    "from=",
    "no-port-forwarding",
    "no-agent-forwarding",
    "permitopen=",
]


def analyze_authorized_keys(path):
    findings = []

    try:
        with open(path, "r", errors="ignore") as f:
            lines = f.readlines()

        for idx, line in enumerate(lines, start=1):
            for key in SUSPICIOUS_KEYWORDS:
                if key in line:
                    findings.append({
                        "line": idx,
                        "pattern": key,
                        "content": line.strip()[:120]
                    })

    except Exception as e:
        findings.append({
            "error": str(e)
        })

    return findings


def save_results(engagement, content):
    base = os.path.join(engagement["base"], "persistence")
    os.makedirs(base, exist_ok=True)

    filename = f"sshkey_persistence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(base, filename)

    with open(path, "w") as f:
        f.write(content)

    return path


# ================= MAIN =================

def run(engagement):
    print(BANNER)

    ssh_paths = [
        os.path.expanduser("~/.ssh/authorized_keys"),
        "/root/.ssh/authorized_keys",
    ]

    report = []
    report.append("SSH KEY PERSISTENCE CHECK")
    report.append("=" * 50)

    results = []

    for path in ssh_paths:

        if os.path.exists(path):
            print(f"{Colors.GREEN}[+] Found: {path}{Colors.END}")
            findings = analyze_authorized_keys(path)

            if findings:
                print(f"{Colors.YELLOW}[!] Suspicious key options detected{Colors.END}")
            else:
                print(f"{Colors.GREEN}[✓] No suspicious key restrictions found{Colors.END}")

            results.append({
                "path": path,
                "exists": True,
                "findings": findings
            })

            report.append(f"\nFILE: {path}")
            report.append(f"Findings: {len(findings)}")

            for f in findings:
                report.append(str(f))

        else:
            print(f"{Colors.RED}[-] Missing: {path}{Colors.END}")
            results.append({
                "path": path,
                "exists": False,
                "findings": []
            })

    # -------- Save Report --------

    output_path = save_results(engagement, "\n".join(report))

    print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] SSH persistence scan complete{Colors.END}")
    print(f"{Colors.BLUE}[+] Results saved to:{Colors.END} {output_path}")

    structured_data = {
        "module": "sshkey_persistence",
        "checked_paths": ssh_paths,
        "results": results,
        "report_file": output_path,
        "timestamp": datetime.utcnow().isoformat()
    }

    return structured_data
