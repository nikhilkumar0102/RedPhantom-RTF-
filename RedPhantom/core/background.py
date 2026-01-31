import threading
import uuid
import json
import os
from datetime import datetime

JOBS_FILE = "jobs.json"
LOCK = threading.Lock()


def _load_jobs():
    if not os.path.exists(JOBS_FILE):
        return {}
    with open(JOBS_FILE, "r") as f:
        return json.load(f)


def _save_jobs(jobs):
    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=2)


def start_background_job(name, target_func, engagement, *args):
    job_id = str(uuid.uuid4())[:8]

    jobs = _load_jobs()
    jobs[job_id] = {
        "id": job_id,
        "name": name,
        "status": "RUNNING",
        "started": datetime.now().isoformat(),
        "engagement": engagement["base"]
    }
    _save_jobs(jobs)

    def wrapper():
        try:
            target_func(engagement, *args)
            status = "COMPLETED"
        except Exception as e:
            status = f"FAILED: {e}"

        with LOCK:
            jobs = _load_jobs()
            jobs[job_id]["status"] = status
            jobs[job_id]["finished"] = datetime.now().isoformat()
            _save_jobs(jobs)

    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()

    return job_id


def list_jobs():
    return _load_jobs()
                         