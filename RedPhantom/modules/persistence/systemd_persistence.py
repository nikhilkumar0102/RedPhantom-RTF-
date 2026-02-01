import os
from datetime import datetime


# ---------- CONFIG ----------

SYSTEMD_DIRS = [
    "/etc/systemd/system",
    "/lib/systemd/system"
]

# legit common services (reduce false positives)
ALLOWLIST = [
    "NetworkManager",
    "cron",
    "dbus",
    "systemd",
    "display-manager",
    "ssh",
    "rsyslog",
    "smartd",
    "ModemManager",
    "networking",
]

SUSPICIOUS_PATHS = [
    "/tmp/",
    "/dev/shm/",
    "/var/tmp/",
    "/home/"
]

SUSPICIOUS_PATTERNS = [
    "bash -c",
    "curl ",
    "wget ",
    "nc ",
    "python -c",
    "/dev/tcp/"
]


# ---------- REPORT SAVE ----------

def save_report(engagement, content):

    base = os.path.join(engagement["base"], "persistence")
    os.makedirs(base, exist_ok=True)

    name = f"systemd_persistence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(base, name)

    with open(path, "w") as f:
        f.write(content)

    return path


# ---------- ANALYZER ----------

def analyze_unit(file_path):

    try:
        with open(file_path, "r", errors="ignore") as f:
            data = f.read()
    except:
        return None

    exec_lines = [
        line.strip()
        for line in data.splitlines()
        if line.strip().startswith("ExecStart")
    ]

    if not exec_lines:
        return None

    risk = 0
    reasons = []

    for line in exec_lines:

        for p in SUSPICIOUS_PATHS:
            if p in line:
                risk += 2
                reasons.append(f"path:{p}")

        for s in SUSPICIOUS_PATTERNS:
            if s in line:
                risk += 3
                reasons.append(f"pattern:{s}")

    return {
        "exec": exec_lines,
        "risk": risk,
        "reasons": list(set(reasons))
    }


# ---------- MAIN ----------

def run(engagement):

    print("\n[+] SYSTEMD PERSISTENCE ANALYZER")
    print("Scanning systemd units quietly...")

    suspicious = []
    total = 0

    report_lines = []
    report_lines.append("SYSTEMD PERSISTENCE ANALYSIS")
    report_lines.append("="*60)

    for base in SYSTEMD_DIRS:

        if not os.path.exists(base):
            continue

        for root, _, files in os.walk(base):

            for name in files:

                if not name.endswith(".service"):
                    continue

                total += 1

                # allowlist skip
                if any(a.lower() in name.lower() for a in ALLOWLIST):
                    continue

                path = os.path.join(root, name)
                result = analyze_unit(path)

                if not result:
                    continue

                if result["risk"] >= 3:
                    suspicious.append((path, result))

                    report_lines.append(f"\n[!] Suspicious Service: {path}")
                    report_lines.append(f"Risk Score: {result['risk']}")
                    report_lines.append(f"Reasons: {', '.join(result['reasons'])}")
                    for e in result["exec"]:
                        report_lines.append(f"ExecStart: {e}")

    # ---------- Save Full Report ----------

    report_path = save_report(engagement, "\n".join(report_lines))

    # ---------- Quiet Console Summary ----------

    print(f"\n✔ Services scanned : {total}")
    print(f"⚠ High-risk found  : {len(suspicious)}")
    print(f"📄 Full report     : {report_path}\n")

    return {
        "module": "systemd_persistence",
        "services_scanned": total,
        "high_risk": len(suspicious),
        "report": report_path
    }
