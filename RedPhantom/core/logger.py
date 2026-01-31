from datetime import datetime

def log_event(engagement, message):
    logfile = f"{engagement['base']}/logs/activity.log"
    with open(logfile, "a") as f:
        f.write(f"[{datetime.now()}] {message}\n")
