# Sakura Sunset

## Repository guide

An Android animated-artwork widget application with three selectable artwork families: **Sakura Sunset**, **The Immortals Chess Game** and **Winter Cabin**. This is one application with per-widget artwork choices, not three separate apps.

The source declares version **1.2.0**, min SDK 26 and compile/target SDK 35. Use JDK 17 and Android SDK 35, configure the SDK path locally, then build:

```powershell
.\gradlew.bat :app:assembleDebug
```

`Build-Sakura.cmd` is a local helper with toolchain expectations that should be checked on another machine. Install your locally generated APK, add the widget from the Android launcher's widget picker and select the artwork/settings for that widget. A preview inside the app and an actual launcher widget exercise different lifecycle paths.

The application is under `app/`; authored artwork/source material is under `art/`; rendering/build helpers are under `tools/`; design and historical verification notes are under `docs/`. Historical `artifacts/` APK/Studio ZIP names below are not downloadable files in this source snapshot.

Animation timing, background updates, battery restrictions and widget resizing can vary with the device/launcher. Earlier emulator validation is scoped evidence, not a claim of physical-device or long-duration testing. Existing artwork/dependency rights and notices remain applicable.

A small animated pixel-art painting for your Android home screen. Choose **Sakura Sunset**, **The Immortals Chess Game**, or **Winter Cabin**. The sakura paintings have drifting petals; the winter clearing has falling snow that settles and merges into the ground. No text, controls, clock, ads or network access inside the widget.

## Install

1. Copy `artifacts/Sakura-Sunset-1.2.0-debug.apk` to your phone and open it. Allow installation from that file manager if Android asks. This is a locally signed debug APK, not a Play Store release. It updates earlier versions without removing your widgets.
2. Long-press empty space on your home screen → **Widgets** → **Sakura Sunset**. Drag it onto the screen. You may also open the small Sakura Sunset app and choose **Add to home screen**, if your launcher supports pinning.
3. Start at **4 × 2**. Long-press the widget and drag the resize handles for 3 × 2, 4 × 3, 5 × 3, or other available sizes. Exact grid sizes depend on your launcher.
4. Close the app. The launcher hosts the animation independently.

Open Sakura Sunset to choose **Use for new widgets** beneath any painting. To change an existing widget, scroll to **Your home-screen paintings** and select it, then tap **Use this artwork** under the desired picture. Scroll down for **Winter Cabin**. Every widget keeps its own choice. Supported launchers also offer **Edit** when you long-press the widget. On older Android versions the picker opens when adding a widget; canceling does not apply a new choice.

Requires Android 8.0 / API 26 or later. Android 12+ uses the resource-only collection adapter. See `docs/VERIFICATION.md` for what was actually tested; OxygenOS compatibility is not assumed.

## Open and build

Open this folder in Android Studio. Use JDK 17 or 21 and install Android SDK Platform 35. Let Android Studio generate `local.properties` for your SDK location. All artwork is already bundled; Python is not needed to build the APK.

On Windows, run **Build-Sakura.cmd**. Alternatively:

```powershell
.\gradlew.bat :app:assembleDebug :app:lintDebug --max-workers=1 --no-watch-fs
```

APK output: `app/build/outputs/apk/debug/app-debug.apk`.

The wrapper pins Gradle 8.14.3 with SHA-256 validation; Android Gradle Plugin is 8.7.3 and Kotlin is 1.9.22. First-time dependency resolution needs internet; the installed app does not.

The Windows launcher also disables Gradle's optional instrumentation agent to avoid this machine's transform-cache file locks. If a direct build encounters that issue, add `-Dorg.gradle.internal.instrumentation.agent=false` (quote the argument in PowerShell). Do not delete shared Gradle caches as a first step.

## Assets and verification

- `art/source/sakura-landscape.png`: original landscape.
- `art/scene-base.png`: palette-reduced logical canvas.
- `art/previews/painting.png`: enlarged nearest-neighbor still.
- `art/previews/sakura-loop.gif`: animated development preview, not the Android playback mechanism.
- `app/src/main/res/drawable-nodpi/`: all 288 frame PNGs (96 per painting).
- `art/asset-manifest.json`: frame hashes and size/memory estimates.
- `art/ARTWORK.md`: original generation prompt and asset pipeline.
- `docs/ARCHITECTURE.md`: platform research, rendering, caching and battery limitations.
- `docs/VERIFICATION.md`: build, tests, launcher evidence and untested cases.
- `art/previews/immortals-painting.png` and `immortals-loop.gif`: daytime still and animation.
- `art/go-position.json`: all 361 intersections extracted from the supplied reference, including 101 black and 100 white stones.
- `art/immortals-position.sgf`: the same position as standard Go setup data, suitable for a Go board viewer.
- `art/previews/immortals-board-position.png`: enlarged orthographic position for inspection. Tiny home-screen pixels cannot show each stone as clearly as this view.
- `art/IMMORTALS-ARTWORK.md`: revised natural-stone art prompt and pipeline.
- `docs/IMMORTALS-VERIFICATION.md`: version 1.1 verification, separate from historical version 1.0 results.
- `art/previews/winter-loop.gif`, `winter-painting.png`: winter animation and still preview.
- `art/WINTER-ARTWORK.md`, `art/winter-manifest.json`: generation prompt, snowfall design, hashes and memory estimate.
- `docs/WINTER-VERIFICATION.md`: version 1.2 results and limitations.

To regenerate assets and verify them:

```powershell
python -m pip install -r tools/requirements.txt
python tools/generate_assets.py
python tools/generate_immortals.py
python tools/generate_winter.py
python -m unittest discover -s tools -p 'test*.py' -v
```

To run Android framework tests with an ADB-connected emulator or phone:

```powershell
.\gradlew.bat :app:connectedDebugAndroidTest --max-workers=1 --no-watch-fs
```

## Animation behavior

The launcher inflates a native `AdapterViewFlipper` and advances 96 bundled frames at a requested 125 ms interval: 8 FPS, nominally 12 seconds per loop. API 31+ gets `RemoteCollectionItems`; older versions bind an on-demand `RemoteViewsService`. The app does not broadcast repeated widget updates and does not need to remain open. This uses the supported [Android collection widget mechanism](https://developer.android.com/develop/ui/views/appwidgets/collections).

All scenes use unfiltered bitmap drawables and preserve a 16:9 aspect ratio. Sunset and Winter Cabin use 320 × 180; the Go scene uses 480 × 270 to retain its dense board position. Taller or wider cells leave transparent space around the painting. Backgrounds stay still. The daytime petals descend from the canopy, touch down and accelerate gently off the right edge along the ground. Winter snowflakes settle in the foreground, then shrink and blend into the local snow colour before reappearing above the canvas; the ground never resets or builds up unnaturally.

Launcher implementations control visibility, scheduling and lifecycle. Some may throttle or freeze animation, especially on hidden home pages. Eight FPS is a target, not a timing guarantee. The Android 8–11 service adapter may briefly repeat the loading painting if a frame is not cached. No claim of physical OnePlus/OxygenOS testing is made without recorded device evidence. If animation does not resume, remove and re-add the widget, and note the Android version and launcher when reporting it.


## Source snapshot and validation

See [BACKUP_NOTES.md](BACKUP_NOTES.md) for the omitted build outputs, local settings, credentials and runtime data. Build generated binaries locally using the instructions above; a source checkout is not an installed application. Earlier validation figures in this guide describe their original development runs. This documentation update checks source references and instructions; it does not claim a fresh application, device or gameplay test.
