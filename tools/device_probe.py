"""ADB evidence helper; only operates on the isolated development emulator.

Override SAKURA_ADB_SERIAL and SAKURA_ADB_PORT explicitly for another test device.
"""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ADB = Path(os.environ["LOCALAPPDATA"])/"Android/Sdk/platform-tools/adb.exe"
PREFIX = [str(ADB), "-P", os.environ.get("SAKURA_ADB_PORT", "5038"),
          "-s", os.environ.get("SAKURA_ADB_SERIAL", "127.0.0.1:5557")]


def adb(*args, **kwargs):
    result = subprocess.run(PREFIX+list(args), capture_output=True, **kwargs)
    if result.returncode:
        raise RuntimeError((result.stdout + result.stderr).decode(errors="replace"))
    return result.stdout


if __name__ == "__main__":
    command = sys.argv[1]
    if command == "shot":
        path = ROOT/"docs/evidence"/(sys.argv[2]+".png")
        path.write_bytes(adb("exec-out", "screencap", "-p"))
        print(path)
    elif command == "dump":
        result = adb("shell", "uiautomator", "dump", "/sdcard/sakura-ui.xml").decode()
        if "dumped to" not in result:
            raise RuntimeError("UI dump did not finish (continuous animation may prevent idle): " + result)
        xml = adb("shell", "cat", "/sdcard/sakura-ui.xml").decode()
        (ROOT/"docs/evidence/current-ui.xml").write_text(xml, encoding="utf-8")
        print(xml)
    elif command == "record":
        name = sys.argv[2]
        seconds = sys.argv[3] if len(sys.argv) > 3 else "30"
        adb("shell", "screenrecord", "--bit-rate", "6000000", "--time-limit", seconds,
            f"/sdcard/{name}.mp4")
        adb("pull", f"/sdcard/{name}.mp4", str(ROOT/f"docs/evidence/{name}.mp4"))
        print(f"Recorded {name}.mp4")
    else:
        print(adb(*sys.argv[1:]).decode(errors="replace"))
