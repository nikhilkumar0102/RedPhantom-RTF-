import os
import shutil
from datetime import datetime

ENGAGEMENTS_DIR = "engagements"


def init_engagement():
    client = input("Client Name: ").strip()
    scope = input("Scope (IPs/Domains): ").strip()
    tester = input("Tester Name: ").strip()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"{ENGAGEMENTS_DIR}/{client}_{ts}"

    os.makedirs(base + "/logs", exist_ok=True)
    os.makedirs(base + "/loot", exist_ok=True)
    os.makedirs(base + "/reports", exist_ok=True)

    return {
        "client": client,
        "scope": scope,
        "tester": tester,
        "base": base
    }


def list_engagements():
    if not os.path.exists(ENGAGEMENTS_DIR):
        return []

    return [
        d for d in os.listdir(ENGAGEMENTS_DIR)
        if os.path.isdir(os.path.join(ENGAGEMENTS_DIR, d))
    ]


def load_engagement():
    engagements = list_engagements()

    if not engagements:
        print("[!] No existing engagements found.")
        return None

    print("\nAvailable Engagements:")
    for i, e in enumerate(engagements, 1):
        print(f"{i}. {e}")

    choice = input("Select engagement number: ").strip()

    if not choice.isdigit() or int(choice) not in range(1, len(engagements) + 1):
        print("[!] Invalid selection")
        return None

    selected = engagements[int(choice) - 1]

    return {
        "client": selected.split("_")[0],
        "scope": "Loaded from previous engagement",
        "tester": "Unknown",
        "base": f"{ENGAGEMENTS_DIR}/{selected}"
    }


def delete_engagement():
    engagements = list_engagements()

    if not engagements:
        print("[!] No engagements to delete.")
        return

    print("\nEngagements:")
    for i, e in enumerate(engagements, 1):
        print(f"{i}. {e}")

    choice = input("Select engagement number to delete: ").strip()

    if not choice.isdigit() or int(choice) not in range(1, len(engagements) + 1):
        print("[!] Invalid selection")
        return

    target = f"{ENGAGEMENTS_DIR}/{engagements[int(choice) - 1]}"
    confirm = input(f"Type DELETE to confirm removal of {target}: ")

    if confirm == "DELETE":
        shutil.rmtree(target)
        print("[+] Engagement deleted successfully.")
    else:
        print("[!] Deletion aborted.")
