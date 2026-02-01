#!/usr/bin/env python3

import os
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
║        ARTIFACT CLEANUP & HYGIENE          ║
║      Engagement Artifact Remediation       ║
╚════════════════════════════════════════════╝
{Colors.END}
"""


# ================= TARGET ARTIFACT MAP =================

ARTIFACT_PATHS = [
    "/tmp/redphantom",
    "/tmp/rp_payload.sh",
    "/tmp/rp_reverse.sh",
    "/tmp/rp_test.bin",
    "/var/tmp/redphantom",
]

USER_ARTIFACTS = [
    ".rp_history",
    ".rp_payload",
]


# ================= HELPERS =================

def remove_path(path, dry_run=True):
    if not os.path.exists(path):
        return ("missing", path)

    if dry_run:
        return ("would_remove", path)

    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

        return ("removed", path)

    except Exception as e:
        return ("error", f"{path} :: {e}")


# ================= MODULE =================

def run(engagement):

    print(BANNER)

    print(f"{Colors.YELLOW}[!] Cleanup mode is SAFE by default (dry-run){Colors.END}")
    print("[1] Dry Run (show what would be removed)")
    print("[2] Execute Cleanup")
    print("[3] Back")

    choice = input("Select option: ").strip()

    if choice == "3":
        return

    dry_run = True if choice == "1" else False

    results = []
    print()

    # ---------- System Temp Artifacts ----------

    print(f"{Colors.BOLD}[*] Checking system artifact paths{Colors.END}")

    for path in ARTIFACT_PATHS:
        status, info = remove_path(path, dry_run)
        results.append((status, info))
        print(f"{status.upper():12} → {info}")

    # ---------- User Home Artifacts ----------

    home = os.path.expanduser("~")

    print(f"\n{Colors.BOLD}[*] Checking user artifact paths{Colors.END}")

    for name in USER_ARTIFACTS:
        path = os.path.join(home, name)
        status, info = remove_path(path, dry_run)
        results.append((status, info))
        print(f"{status.upper():12} → {info}")

    # ---------- Engagement Output Cleanup ----------

    if engagement and "base" in engagement:

        print(f"\n{Colors.BOLD}[*] Checking engagement output directory{Colors.END}")

        base = engagement["base"]

        status, info = remove_path(base + "/payloads", dry_run)
        results.append((status, info))
        print(f"{status.upper():12} → {info}")

    # ---------- Report ----------

    summary = {
        "phase": "cleanup",
        "timestamp": datetime.utcnow().isoformat(),
        "dry_run": dry_run,
        "actions": results
    }

    save_cleanup_report(summary)

    print(f"\n{Colors.GREEN}[✓] Cleanup phase completed{Colors.END}")

    return summary


# ================= REPORT WRITER =================

def save_cleanup_report(data):

    os.makedirs("reports", exist_ok=True)

    path = f"reports/cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(path, "w") as f:
        for status, item in data["actions"]:
            f.write(f"{status} :: {item}\n")

    print(f"{Colors.BLUE}[+] Cleanup report saved → {path}{Colors.END}")