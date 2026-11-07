"""Package the source tree and APK, excluding caches, SDKs and diagnostic scratch files."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
artifact = ROOT/"artifacts"
apk = artifact/"Sakura-Sunset-1.2.0-debug.apk"
assert apk.is_file()
files = []
for folder in ["app/src", "art", "docs", "gradle", "tools"]:
    for file in (ROOT/folder).rglob("*"):
        if file.is_file() and "__pycache__" not in file.parts:
            files.append(file)
files += [ROOT/name for name in ["README.md", "settings.gradle.kts", "build.gradle.kts",
          "gradle.properties", ".gitignore", "gradlew", "gradlew.bat", "Build-Sakura.cmd",
          "app/build.gradle.kts"]]
files.append(apk)
archive = artifact/"Sakura-Sunset-1.2.0-Android-Studio.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for file in sorted(files):
        z.write(file, Path("SakuraSunset")/file.relative_to(ROOT))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    names = z.namelist()
    assert len([n for n in names if "drawable-nodpi/petal_frame_" in n]) == 96
    assert len([n for n in names if "drawable-nodpi/immortals_frame_" in n]) == 96
    assert len([n for n in names if "drawable-nodpi/winter_frame_" in n]) == 96
    for file in files:
        name = str(Path("SakuraSunset")/file.relative_to(ROOT)).replace("\\", "/")
        assert hashlib.sha256(z.read(name)).digest() == hashlib.sha256(file.read_bytes()).digest()
metadata = {p.name:dict(bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
            for p in [apk, archive]}
(artifact/"SHA256SUMS-1.2.0.txt").write_text("".join(f"{data['sha256']}  {name}\n" for name,data in metadata.items()))
print(json.dumps(dict(files=len(files), verified_all_entries=True, artifacts=metadata), indent=2))
