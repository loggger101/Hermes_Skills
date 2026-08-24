# Skill Watchdog Cronjob Template
#
# This template implements a simple watchdog pattern — a cronjob that
# monitors something (disk usage, service health, price changes) and
# alerts when thresholds are exceeded.
#
# Pattern: Use cronjob(action='create') with a no_agent script for
# silent operation (no output = no notification).
#
# Source: product-price-monitor skill uses this pattern

script = """
#!/usr/bin/env python3
import os, sys, json, subprocess
from datetime import datetime

# --- CONFIG ---
THRESHOLD = 0.90  # Alert at 90% disk usage
PARTITION = '/'   # Root partition

# --- CHECK ---
result = subprocess.run(['df', '-h', PARTITION], capture_output=True, text=True)
lines = result.stdout.strip().split('\n')
if len(lines) >= 2:
    parts = lines[1].split()
    usage_str = parts[4].rstrip('%')
    usage = float(usage_str) / 100.0

    # --- ALERT OR SUPPRESS ---
    if usage >= THRESHOLD:
        print(f"ALERT: Disk usage on {PARTITION} is {usage_str}% (threshold: {THRESHOLD*100}%)")
        sys.exit(1)  # Non-zero = error alert
    else:
        # Silence — no output means no delivery (silent watchdog)
        sys.exit(0)
else:
    print(f"ERROR: Could not parse df output")
    sys.exit(1)
"""

cronjob_config = {
    "schedule": "*/30 * * * *",  # Every 30 minutes
    "script": "watchdog.py",
    "no_agent": True,  # Script-only — no LLM
    "deliver": "origin",
    "enabled_toolsets": ["terminal"]
}
