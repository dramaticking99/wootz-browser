#!/usr/bin/env python3
"""
Run autoninja and count errors.

• Counts every line that contains the word “error:” (case-insensitive) – these are
  compiler / linter / toolchain diagnostics.
• Counts every line that starts with “FAILED:” – these are Ninja actions that
  aborted (e.g. a single .cc file that didn’t compile).
"""

import subprocess
import sys
import re
from pathlib import Path

# --------------------------------------------------------------------------- #
# Configuration – tweak if you need a different target or build directory
# --------------------------------------------------------------------------- #
BUILD_DIR = Path("out/Default")
NINJA_TARGET = "chrome_public_apk"
MAX_FAILURES = "10000"          # same as -k 10000
AUTONINJA = "autoninja"         # or the full path if autoninja is not on $PATH
# --------------------------------------------------------------------------- #

CMD = [AUTONINJA, "-k", MAX_FAILURES, "-C", str(BUILD_DIR), NINJA_TARGET]

error_re   = re.compile(r"\berror:",   re.IGNORECASE)
failed_re  = re.compile(r"^FAILED:")

error_lines   = 0   # compiler / tool errors
failed_tasks  = 0   # ninja “FAILED:” lines

print(f"Running: {' '.join(CMD)}\n")

# Run autoninja and stream combined stdout+stderr line by line
with subprocess.Popen(
        CMD,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,               # line-buffered
    ) as proc:
    try:
        for line in proc.stdout:
            print(line, end="")  # mirror ninja output to our console

            # Counting logic
            if error_re.search(line):
                error_lines += 1
            if failed_re.match(line):
                failed_tasks += 1
    except KeyboardInterrupt:
        print("\nInterrupted by user – passing SIGINT to autoninja …", file=sys.stderr)
        proc.send_signal(subprocess.signal.SIGINT)

    proc.wait()  # make sure the child process is reaped

# --------------------------------------------------------------------------- #
# Summary
# --------------------------------------------------------------------------- #
print("\n" + "-" * 60)
print(f"Autoninja exit code         : {proc.returncode}")
print(f"Compiler/toolchain errors   : {error_lines}")
print(f"Ninja FAILED actions        : {failed_tasks}")
print("-" * 60)

# Propagate the same exit status as the build
sys.exit(proc.returncode)