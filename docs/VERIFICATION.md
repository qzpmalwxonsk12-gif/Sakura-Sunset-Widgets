# Verification — 24 October 2026

## Build and artifacts

- `Build-Sakura.cmd`: **BUILD SUCCESSFUL**, Android debug APK and lint completed. See `evidence/final-build.txt`.
- APK uses a verified Android v2 debug signature. No requested permissions appear in the packaged manifest.
- Python asset suite: **6/6 passed**. Tests compare actual decoded pixels, enforce background stability, exact period, natural wrap delta, off-canvas petal lifecycle, distinct frames, drawable filtering and widget scheduling metadata.
- Android instrumentation: **4/4 passed** on Android 15, including actual `RemoteViews` inflation in an `AppWidgetHostView`, autonomous advancement and last-to-first wrap, decoding every drawable without filtering, resource-only parcel size, and legacy factory contracts. See `evidence/instrumentation.txt`.
- The entire modern collection update occupies **10,656 bytes** in its Android Parcel. This verifies resource IDs are transferred instead of 96 decoded bitmaps.
- Lint: **0 errors, 9 warnings**. Warnings cover API-31-only metadata with older-device fallbacks, pinned target/test versions, backup metadata, launcher-icon silhouette, and the deliberately empty touch layer needed for launcher long-press. Full report included.

## Actual launcher environment

Android Emulator 36.6.11, AOSP Android 15 / API 35 x86_64, Launcher3 version 15 (code 35), 1080 × 1920 at 420 dpi. Hardware acceleration uses WHPX; graphics use SwiftShader. The AVD has 2 virtual cores and 1536 MB RAM. It is an actual Android launcher, not a simulated browser or an animated Activity.

Fingerprint: `Android/sdk_phone64_x86_64/emu64x:15/AE3A.240806.019/12368160:userdebug/test-keys`.

## Launcher checks performed

| Check | Observed result | Evidence |
|---|---|---|
| Add with system pin dialog | Widget added, then displayed on home screen | `home-first.png`, `appwidget-initial.txt` |
| Add with home-screen Widgets picker | Searched Sakura Sunset, expanded its preview, dragged a second instance onto the home screen | `picker-search.png`, `picker-expanded.png`, `two-widgets.png` |
| App closed | 30-second launcher recording contains all 96 art frames and two wraps; about 7.9 observed changes/s | `home-loop.mp4`, `home-loop-analysis.json` |
| App process absent | No Sakura process in process snapshot; 15-second home-screen capture still advances through all 96 frames and wraps | `processes-before-loop.txt`, `process-absent.mp4` |
| Leave and return | Opened Android Settings, returned to the same home page; all 96 frames and continuing wraps recorded | `returned-from-settings.mp4` |
| Screen off and unlock | Enabled the emulator's non-secure lock screen, sent sleep, confirmed display asleep, woke to keyguard, then dismissed keyguard using Android's test shell. Both paintings resumed forward motion and wrapped | `screen-off-power.txt`, `lockscreen.png`, `after-unlock.png`, `after-unlock.mp4`, both `after-unlock-*-analysis.json` |
| Resize | Long-press and launcher handles successfully changed 4×2 to 3×2, 4×3, then 5×3; full tree and sun remain visible, aspect ratio preserved | `resize-fixed.png`, `size-3x2.png`, `size-4x3.png`, `size-5x3.png` |
| Animation after resize | 5×3 capture contains all 96 frames, around 7.9 changes/s and two wraps | `resized-5x3.mp4` |
| Multiple instances | Two independently phased widgets animated together on the same page; both wrapped | `two-widgets.mp4`, both `two-widgets-*-analysis.json`, `appwidget-two-instances.txt` |
| Cold restart | Both widget placements and sizes persisted, and both resumed animation without opening Sakura Sunset. Recorded forward progression and a wrap in each widget | `after-reboot.png`, `after-reboot.mp4`, both `after-reboot-*-analysis.json`, `appwidget-after-reboot.txt` |

The two-widget recording was slower on this constrained software-rendered emulator: approximately 4.4–4.5 observed changes/s per painting, with some skipped captured frames. This is not a claim of 8 FPS with arbitrary numbers of widgets. Screen recording and emulator graphics add overhead, and the observed rate must not be extrapolated to a physical phone.

For the cold restart, `adb shell reboot` ended the emulator process; the same persistent AVD was then relaunched with snapshots disabled. Initial post-boot display capture was unstable and was discarded. After the launcher settled, the retained recording showed both widgets animating at approximately 6.6–7.0 observed changes/s. This verifies cold startup on the test AVD, not reboot behavior on physical OxygenOS hardware.

## Visual and timing evidence

`tools/verify_launcher_video.py` decodes the actual launcher screen recordings and matches moving-petal regions against the 96 bundled reference images. It reports unique frames, forward transitions, wraps, matching errors and brightness. Single-widget recordings show sequential motion with occasional skipped captured frames. Painting brightness stays stable; no blank painting frame was detected in these sampled recordings. This does not prove the absence of every sub-frame flash or launcher-specific first-bind issue.

The Android view test initially used `findViewById` across an `AdapterChildHostView` root namespace. That lookup correctly cannot traverse the isolated child host, so the test was corrected to inspect the actual children. The production widget was independently verified in Launcher3.

Launcher testing also found that fast child replacement canceled long-press. The final widget adds a stationary invisible touch layer, and the resize gestures above were tested after that fix. No visible controls or click behavior were added.

## Remaining limits

- **No physical phone or OnePlus/OxygenOS test was available.** Those launchers can differ in visibility, scheduling, clipping, and restoration.
- Android 8–11's `RemoteViewsService` factory is contract-tested, but its full launcher/caching path has not been exercised on those OS versions. A loading frame may repeat there.
- No long-duration battery, thermal, or leak benchmark was performed. Short launcher memory snapshots are supplied for inspection; they include the entire launcher and cannot isolate the widget's cost or establish a leak bound.
- Hidden home-page suppression is host-dependent. Screen-off/resume was tested, but zero background CPU on every launcher is not promised.
- Secure PIN/biometric unlock, landscape phone rotation, launcher backup migration, and non-AOSP third-party launchers remain untested.
- Generated frame continuity is exact by construction and pixel tests. Device frame timing remains subject to UI-thread scheduling.

All media and reports referenced above are in `docs/evidence/`. Source, artwork, generation scripts and the APK are included in the packaged Android Studio project.
