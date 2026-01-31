import os
from datetime import datetime

# ================= COLORS =================
class Colors:
    RED = '\033[91m'      # Errors / Warnings
    GREEN = '\033[92m'   # Success
    YELLOW = '\033[93m'  # Info
    BLUE = '\033[94m'    # Action
    WHITE = '\033[97m'   # Neutral
    BOLD = '\033[1m'
    END = '\033[0m'


# ================= PATH HELPERS =================
def ensure_dir(path: str):
    """
    Create directory if it does not exist.
    """
    os.makedirs(path, exist_ok=True)


def get_recon_base(engagement: dict, category: str) -> str:
    """
    Returns base path for recon results.
    Example:
    engagements/<engagement>/recon/external/
    """
    base = os.path.join(engagement["base"], "recon", category)
    ensure_dir(base)
    return base


# ================= FILE SAVING =================
def save_recon_result(
    engagement: dict,
    category: str,
    tool_name: str,
    content: str
) -> str:
    """
    Save recon output in a timestamped text file.

    Returns full file path.
    """
    base = get_recon_base(engagement, category)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{tool_name}_{timestamp}.txt"
    filepath = os.path.join(base, filename)

    with open(filepath, "w") as f:
        f.write(content.strip() + "\n")

    return filepath


# ================= SUMMARY HANDLING =================
def append_recon_summary(engagement: dict, message: str):
    """
    Append a single line to recon summary file.
    """
    recon_dir = os.path.join(engagement["base"], "recon")
    ensure_dir(recon_dir)

    summary_file = os.path.join(recon_dir, "summary.txt")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(summary_file, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def init_recon_summary(engagement: dict):
    """
    Initialize recon summary file (run once per engagement).
    """
    recon_dir = os.path.join(engagement["base"], "recon")
    ensure_dir(recon_dir)

    summary_file = os.path.join(recon_dir, "summary.txt")

    if not os.path.exists(summary_file):
        with open(summary_file, "w") as f:
            f.write("RECONNAISSANCE SUMMARY\n")
            f.write("======================\n\n")


# ================= OUTPUT FORMATTERS =================
def format_section(title: str, body: str) -> str:
    """
    Create a clean, report-ready section.
    """
    return f"""
{title.upper()}
{'-' * len(title)}
{body.strip()}
"""


def key_value_block(title: str, data: dict) -> str:
    """
    Format dictionary output into readable blocks.
    """
    lines = [f"{k}: {v}" for k, v in data.items()]
    return format_section(title, "\n".join(lines))


# ================= CLI PRINT HELPERS =================
def info(msg: str):
    print(f"{Colors.BLUE}[*]{Colors.END} {msg}")


def success(msg: str):
    print(f"{Colors.GREEN}[+]{Colors.END} {msg}")


def warn(msg: str):
    print(f"{Colors.YELLOW}[!]{Colors.END} {msg}")


def error(msg: str):
    print(f"{Colors.RED}[-]{Colors.END} {msg}")
