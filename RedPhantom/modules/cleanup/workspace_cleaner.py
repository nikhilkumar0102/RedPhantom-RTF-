#!/usr/bin/env python3

import os
import shutil
from datetime import datetime


# ---------- COLORS ----------

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


# ---------- UI ----------

BANNER = f"""
{Colors.BLUE}{Colors.BOLD}
╔════════════════════════════════════════════╗
║          WORKSPACE CLEANER MODULE          ║
║       Engagement Artifact Cleanup          ║
╚════════════════════════════════════════════╝
{Colors.END}
"""


# ---------- CLEAN LOGIC ----------

def collect_targets(engagement):
    targets = []

    if not engagement:
        return targets

    base = engagement.get("base")

    if base and os.path.exists(base):
        targets.append(base)

    # common temp artifact dirs inside project
    extra = [
        "tmp",
        "temp",
        "cache",
        "reports/tmp"
    ]

    for d in extra:
        if os.path.exists(d):
            targets.append(d)

    return targets


def safe_delete(path):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return True, None
    except Exception as e:
        return False, str(e)


# ---------- MAIN ----------

def run(engagement):

    print(BANNER)

    if not engagement or "base" not in engagement:
        print(f"{Colors.RED}[!] No engagement context — aborting{Colors.END}")
        return

    print(f"{Colors.YELLOW}[*] Collecting RedPhantom artifacts...{Colors.END}")

    targets = collect_targets(engagement)

    if not targets:
        print(f"{Colors.GREEN}[✓] Nothing to clean{Colors.END}")
        return

    print(f"\n{Colors.WHITE}Targets:{Colors.END}")
    for t in targets:
        print(f"  - {t}")

    confirm = input(
        f"\n{Colors.RED}Type CLEAN to delete these artifacts: {Colors.END}"
    ).strip()

    if confirm != "CLEAN":
        print(f"{Colors.YELLOW}[*] Cleanup cancelled{Colors.END}")
        return

    results = []

    print(f"\n{Colors.YELLOW}[*] Cleaning...{Colors.END}")

    for path in targets:
        ok, err = safe_delete(path)

        if ok:
            print(f"{Colors.GREEN}[✓] Removed: {path}{Colors.END}")
            results.append({"path": path, "status": "deleted"})
        else:
            print(f"{Colors.RED}[!] Failed: {path} — {err}{Colors.END}")
            results.append({"path": path, "status": "failed", "error": err})

    print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] Workspace cleanup complete{Colors.END}")

    return {
        "module": "workspace_cleaner",
        "timestamp": datetime.utcnow().isoformat(),
        "results": results
    }
