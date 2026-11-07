# Version 1.2 — Winter Cabin

The third selectable artwork is a snowy timber cabin in a forest clearing. The original Sunset and Immortals images and frame hashes are unchanged. Existing per-widget selections retain their keys and collection IDs.

## Snow loop

- 320 × 180 pixels, 96 unique frames, 125 ms requested interval: nominally 8 FPS and 12 seconds.
- 80 staggered flakes with varied size, colour, drift and oscillation; each arrives from above the canvas.
- Ground contact at 83% of each flake's cycle. A flake settles in the snowy foreground, shrinks, then blends toward the exact local ground colour using a smooth fade. Fully merged by 98%, before rebirth. No background accumulation or sudden ground reset.
- 96 background palette colours plus a protected 16-colour warm set preserve small amber windows; snow blends are mapped to this fixed palette. PNG encoding retains every visible pixel exactly.
- New PNG assets: 3,877,623 bytes. Pessimistic simultaneous ARGB decoding of all winter frames would use 22,118,400 bytes (~21.1 MiB); actual caching is launcher-controlled. Resource IDs, not bundled decoded bitmap arrays, cross Binder.
- Playback still uses native AdapterViewFlipper. No frequent widget update broadcasts, rendering service, network permission or wakelock was added.

The original image and generation prompt are bundled in `art/source/winter-cabin.png` and `art/WINTER-ARTWORK.md`. `tools/generate_winter.py` reproduces the animation. The GIF is a preview; Android displays the bundled PNG frames.

## Executed checks

13 Python asset tests passed: prior artwork hashes, all frame pixels, unique loop frames, normal wrap delta, snow ground contact, completed merging before respawn, bounded snow coverage, and preserved warm window colours. Evidence: `evidence/winter-asset-tests.txt`.

Gradle `assembleDebug`, `lintDebug`, and `assembleDebugAndroidTest` succeeded in 2m13s with a single-use compiler process. Lint: zero errors, 11 existing warnings (target/dependency freshness, legacy attributes, backup configuration, unused intro, intentional touch layer, icon shape). APK v2 signature verifies and the APK requests no permissions. Evidence: `evidence/winter-build.txt`, `winter-apk-signature.txt`, `winter-apk-permissions.txt`.

The standalone GIF was checked: 96 frames, total 12,000 ms and infinite looping. The APK and full source are version 1.2.0; older releases are retained.

All eight Android instrumentation tests passed on the Android 15 / API 35 AOSP emulator, including all 288 frame decodes without filtering, each artwork's real framework host advancement and wrap, independent artwork storage, small resource-only parcels, and the legacy factory's winter resource IDs. Evidence: `evidence/winter-instrumentation.txt`.

### Actual Launcher3 playback

The installed 1.2.0 APK updated the existing emulator installation. Widget 4 was changed from Immortals to Winter Cabin through the artwork chooser; widget 3 retained Sunset. Both paintings remained visible on the same home page. Winter used the existing 5 × 3 allocation, with its complete 16:9 image displayed at screen bounds (39, 838)–(1042, 1402). Evidence: `winter-chooser-loaded.png`, `winter-launcher-ready.png` in `evidence/`.

The app process was stopped with `am kill` after leaving the Activity. The process listing contained Launcher3 and no Sakura app process. A 34.32-second recording then captured all 96 winter frames, 252 observed transitions and three loop crossings. Approximate image matching found only forward steps of one to three frames; mean matching error was 2.29/255. The recording showed no blank painting: mean panel brightness stayed between 142.35 and 142.43. The observed cadence was about 7.34 transitions/second while recording two widgets. This is emulator evidence, not a phone frame-rate guarantee. See `evidence/winter-processes.txt`, `winter-app-closed.mp4`, and `winter-app-closed.json`.

After opening Android Settings and returning home, then sleeping the display, waking and dismissing the emulator keyguard, Winter Cabin continued playing. The subsequent 7.51-second recording captured 46 distinct art frames, 45 forward transitions and one wrap, with no blank panel. Evidence: `evidence/winter-return-home.png`, `winter-unlocked.png`, `winter-after-unlock.mp4`, and `winter-after-unlock.json`. This was the emulator's non-secure keyguard; no PIN/biometric lock test is claimed.

The emulator experienced a system-server restart and a System UI not-responding dialog during startup, before successful installation of this APK. The first installation attempt failed because Android's settings provider was not ready. Installation succeeded after recovery, and the dialog was dismissed with Wait before launcher recordings. This transient is retained in `evidence/winter-startup.png`; it is not counted as a passing test.

Historical testing of earlier artwork is documented separately in `VERIFICATION.md` and `IMMORTALS-VERIFICATION.md`.

## Limitations

Launcher scheduling and visibility determine playback cadence and pausing. No physical OnePlus/OxygenOS testing or new battery/leak measurements are claimed. Android 8–11's service factory is exercised by integration tests where stated, but this is not an old-device launcher test. Resizing, restart and lock behaviour from earlier versions are not claimed as new winter-scene checks unless specifically recorded below.
