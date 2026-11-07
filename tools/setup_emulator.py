"""Download the official AOSP API 35 image when sdkmanager networking stalls.

Developer-only helper. Verifies Google's repository SHA-1 before extraction.
Uses an isolated AVD and does not alter any existing emulator.
"""
import hashlib
import os
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SDK = Path(os.environ["LOCALAPPDATA"])/"Android/Sdk"
URL = "https://dl.google.com/android/repository/sys-img/android/x86_64-35_r02.zip"
SHA1 = "2d857d170c0d1b827149565da34b3383e5306f7f"
archive = ROOT/".temp-system-image.zip"
if not archive.exists() or archive.stat().st_size != 782404023:
    with urllib.request.urlopen(URL, timeout=60) as response, archive.open("wb") as output:
        read = 0
        while block := response.read(4*1024*1024):
            output.write(block)
            read += len(block)
            if read % (64*1024*1024) == 0:
                print(f"Downloaded {read//1024//1024} MiB", flush=True)
assert hashlib.sha1(archive.read_bytes()).hexdigest() == SHA1, "System image checksum mismatch"
dest = SDK/"system-images/android-35/default"
dest.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(archive) as bundle:
    assert all((dest/name).resolve().is_relative_to(dest.resolve()) for name in bundle.namelist())
    bundle.extractall(dest)
avd = Path(os.environ["USERPROFILE"])/".android/avd/SakuraSunset_API35.avd"
avd.mkdir(parents=True, exist_ok=True)
(avd.parent/"SakuraSunset_API35.ini").write_text(
    f"avd.ini.encoding=UTF-8\npath={avd}\ntarget=android-35\n")
(avd/"config.ini").write_text(
    "AvdId=SakuraSunset_API35\navd.ini.displayname=Sakura Sunset API 35\n"
    "abi.type=x86_64\nhw.cpu.arch=x86_64\nhw.cpu.ncore=2\n"
    "hw.ramSize=1536\nhw.lcd.width=1080\nhw.lcd.height=1920\nhw.lcd.density=420\n"
    "hw.keyboard=yes\nhw.gpu.enabled=yes\nhw.gpu.mode=swiftshader_indirect\n"
    "hw.mainKeys=no\nhw.audioInput=no\nhw.audioOutput=no\n"
    "image.sysdir.1=system-images/android-35/default/x86_64/\n"
    "tag.id=default\ntag.display=Default Android System Image\n"
    "disk.dataPartition.size=2G\nshowDeviceFrame=no\n")
print("Verified image and isolated SakuraSunset_API35 AVD ready.", flush=True)
