# Version 1.1 — The Immortals Chess Game

## Implementation

The revised plate has two unadorned boulder stools with plum cushions and a rough stone slab, daytime natural scenery, and the original sunset's limited-palette pixel treatment. Generated with the built-in image tool; the final prompt is in `art/IMMORTALS-ARTWORK.md`.

The 19 × 19 position was sampled at all 361 intersections of the supplied overhead image, avoiding grid lines. All classifications have a margin greater than 15 intensity levels from either threshold. The annotated extraction preview was inspected against the source: 101 black and 100 white stones. Rows and columns are retained in `art/go-position.json`; its top-left maps to the table's far corner. Stones use darker charcoal and brighter ivory/white, with a subdued incised grid. Their compact projected rendering is necessarily less legible than the included full-size orthographic preview.

96 resource-backed frames at 125 ms, nominal 12 seconds. The new logical canvas is 480 × 270 to retain the Go position. No background renderer or broadcast timer. PNGs total 7,934,994 bytes; an intentionally pessimistic all-96-decoded ARGB estimate is 49,766,400 bytes (~47.5 MiB), although the native adapter caches a subset. Actual launcher memory depends on host caching and concurrent instances. Sunset frames remain unchanged.

Petals originate at canopy points, descend, and move along the ground after 72% of their individual cycle. They leave the right edge before respawning. No duplicated endpoint frame. The background, board and furniture remain stable.

Artwork selection is stored per widget. The app also lets users edit existing widget instances, supporting launchers without a reconfigure affordance. API 31+ collection item IDs and older service URI identities include artwork, preventing stale frames when changing scenes. The underlay/loading view also matches the selected painting. Restore maps choices to replacement IDs, deletion removes only that instance's preference.

Configuration follows [Android's native widget configuration guidance](https://developer.android.com/develop/ui/views/appwidgets/configuration). Reconfiguration and optional initial configuration depend on launcher support. The rendering architecture remains native AdapterViewFlipper with RemoteCollectionItems (API 31+) or RemoteViewsService (API 26–30).

## Executed checks

- `Build-Sakura.cmd`: assembleDebug and lintDebug succeeded (zero errors, 11 warnings: legacy API attributes, dependency/target freshness, backup rules, unused intro, intentional invisible touch layer, icon shape). See `evidence/immortals-build.txt`.
- Nine Python asset checks passed, including all 192 frames, exact visible indexed-color reproduction, source position extraction, wrap continuity, ground-touch continuity and offscreen respawn. See `evidence/immortals-asset-tests.txt`.
- All 96 sunset PNG SHA-256 hashes were compared with the original asset manifest and remained unchanged. The original APK and project archive are retained alongside version 1.1.
- Six Android instrumentation tests passed on a fresh Android 15 AOSP emulator: both paintings advance and wrap in a real Android widget host, all 192 frame resources decode without filtering, collections stay below 100 KB in Parcel form, legacy factory IDs/bounds are valid, and independent preferences survive ID restore. See `evidence/immortals-instrumentation.txt`.
- Added The Immortals Chess Game through the app's pin request and Launcher3's confirmation. Actual painting displayed at 4 × 2, then the app process was killed with `am kill` (not force-stop). Process snapshot contains Launcher3 and no app process.
- `immortals-home-loop.mp4`: 83 unique artwork frames, one wrap, 91 visible transitions in 14.05 captured seconds (~6.48/s), forward-only matching steps of 1–3 frames. Mean matching error 7.16/255; cropped brightness stayed between 120.599 and 120.648 with no blank panel. These are capture-specific observations, not a universal FPS guarantee.
- Long-press showed resize handles and the launcher Edit button. Using Edit, changed that widget from Immortals to Sunset; saved preferences confirmed widget 3 = sunset while the default remained immortals. Adding another widget displayed both scenes together. See `immortals-two-artworks.png` and `immortals-existing-widget-picker.png`.
- Screen off/on and dismiss-keyguard return: both instances resumed. `immortals-two-after-wake.mp4` contains 44 unique Immortals frames and 45 unique Sunset frames, one wrap each, no blank brightness dip. This constrained emulator recording captured only ~3.1 visible changes/sec for each simultaneous widget; it does not demonstrate smooth 8 FPS with two instances.
- Resizing the new painting through 4 × 2, 3 × 2, 4 × 3 and 5 × 3 preserved the entire composition and aspect ratio; see `immortals-resize-3x2.png`, `immortals-resize-4x3.png`, `immortals-resize-5x3.png`.
- Leaving for Android Settings and returning after resizing to 4 × 3 resumed motion: the short `immortals-return-resized.mp4` capture matched 14 unique frames, forward-only progression, and stable brightness (no wrap expected in this 4.26-second captured segment).
- APK v2 signature verified. Manifest permission dump contains no requested permissions. APK archive integrity checked and all 96 new frame PNGs are included.
- Launcher3 memory snapshot with both paintings: total PSS 88,133 KB, native heap allocated 53,490 KB. This includes all launcher costs and is not the incremental widget footprint or a leak test.

The first emulator session suffered an Android system-server watchdog death during user unlock, before the new APK installed. That failed installation and attempted test run are not counted as passing tests. The isolated development emulator was restarted without deleting user data.

The older emulator remained unhealthy, so final version 1.1 tests used a separate fresh `Immortals_API35` AVD (same API 35 system image, 1080 × 1920 at 420 dpi). It had an initial System UI startup ANR, then recovered; successful tests and captures were taken after installation/startup. The existing SakuraSunset_API35 data was preserved. The generic launcher widget-browser preview remains the sunset image; the chosen artwork is displayed after placement.

## Limits

No physical OnePlus/OxygenOS testing, Android 8–11 launcher testing, secured-lock testing, battery profiling or long-duration memory-leak measurement is claimed. A complete reboot cycle was not rerun for version 1.1 after the emulator startup difficulties; preference restore is covered by instrumentation and app-process restart. Frame cadence is controlled by the launcher. Original version 1.0 evidence remains in `VERIFICATION.md`; it is not represented as a fresh test of version 1.1.
