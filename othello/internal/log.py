# internal/log.py
from __future__ import annotations
import sys

class DebugLogger:
    def __init__(self):
        self.enabled = False
        self.file = None

    def start(self, filename="debug.txt"):
        self.enabled = True
        self.file = open(filename, "w", encoding="utf-8")

    def stop(self):
        if self.file:
            self.file.close()
        self.enabled = False

    def write(self, msg: str):
        """Write msg to screen and also to debug file if enabled."""
        # Always print to the terminal
        sys.stdout.write(msg)
        sys.stdout.flush()

        # Also write to log file if enabled
        if self.enabled and self.file:
            self.file.write(msg)
            self.file.flush()

# Create ONE shared logger used everywhere
LOGGER = DebugLogger()

def dprint(*args, end="\n"):
    """Debug print: writes to both terminal and debug log file if enabled."""
    msg = " ".join(str(a) for a in args) + end
    LOGGER.write(msg)