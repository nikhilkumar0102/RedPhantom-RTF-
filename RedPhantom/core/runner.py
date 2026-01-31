import importlib
import traceback
from core.logger import log_event


def run_phase(engagement, phase):

    print(f"\n[+] Executing {phase.upper()} PHASE")

    # ---------- Safety Check ----------
    if not engagement or "base" not in engagement:
        print("[!] Invalid or missing engagement context")
        return

    module_path = f"modules.{phase}.{phase}_main"

    # ---------- Import Phase Module ----------
    try:
        module = importlib.import_module(module_path)

    except ModuleNotFoundError as e:
        print(f"[!] Phase module not found")
        print(f"[debug] Tried import path: {module_path}")
        print(f"[debug] Python error: {e}")
        return

    except Exception as e:
        print("[!] Error while importing phase module")
        print(f"[debug] Module: {module_path}")
        print(f"[debug] Error: {e}")
        traceback.print_exc()
        return

    # ---------- Validate run() ----------
    if not hasattr(module, "run"):
        print(f"[!] Phase module missing run() function → {module_path}")
        return

    # ---------- Execute Phase ----------
    try:
        log_event(engagement, f"Started phase: {phase}")
        module.run(engagement)
        log_event(engagement, f"Completed phase: {phase}")

    except Exception as e:
        print(f"[!] Phase execution error: {phase}")
        print(f"[debug] {e}")
        traceback.print_exc()
        log_event(engagement, f"Phase failed: {phase} → {e}")
