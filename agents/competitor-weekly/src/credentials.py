import os
import subprocess
import sys


KEYCHAIN_SERVICE = "pm-goldfinger-deepseek"


def read_api_key() -> str | None:
    """Read credentials at runtime, without logging or persisting their value."""
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if key:
        return key
    if sys.platform != "darwin":
        return None
    try:
        result = subprocess.run(
            ["/usr/bin/security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, timeout=5, check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip() or None
    except (OSError, subprocess.SubprocessError, UnicodeError):
        pass
    return None
