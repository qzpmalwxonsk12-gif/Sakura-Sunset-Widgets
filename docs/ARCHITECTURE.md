# Animation architecture and platform limits

## What runs where

`SakuraWidgetProvider` publishes ordinary `RemoteViews` containing an `AdapterViewFlipper`. Its XML sets `autoStart=true`, `flipInterval=125`, and `loopViews=true`. All 96 frames are bundled 320 × 180 drawable resources. Frame changes run on the launcher's UI thread, not in the application Activity or an app-owned timer.

Android 12 / API 31 and later receive `RemoteViews.RemoteCollectionItems`: 96 small resource-reference records, one view type and stable IDs. This avoids collection-service binding, late first-load requests and Bitmap-array Binder limits. Android 8–11 use `RemoteViewsService` / `RemoteViewsFactory` with an explicit service intent and per-widget URI. Its custom loading view shows the same painting instead of a spinner. That older path may show repeated still frames while the host loads uncached rows; it needs separate launcher validation.

Every drawable is a bitmap XML wrapper with `filter=false`, `antialias=false`, and `dither=false`, backed by `drawable-nodpi` PNGs. `ImageView.fitCenter` preserves composition at every supported size. Non-16:9 widget allocations leave transparent space around the painting; this is intentional, so the tree and sun are never stretched or cropped. Non-integer scale factors can produce uneven physical pixel widths but do not interpolate colors. Rounded corners are baked into each frame's alpha mask.

The widget has no click action, controls, labels or branding. The one launcher Activity contains a static preview, installation instructions and an optional system pin request. Closing it does not stop animation. No network permission, foreground service, wakelock, alarm, WorkManager task or periodic update broadcast is used. `updatePeriodMillis=0`. Host/provider events handle initial setup, resize, restore and system re-creation after reboot; no boot receiver is necessary.

## Important implementation details

- Do **not** set `autoAdvanceViewId` in widget metadata. Hosts can then take control through `fyiWillBeAdvancedByHostKThx()`, stopping the flipper's own timer and substituting a much slower slideshow interval.
- Set explicit zero-duration object animators. The framework's default crossfades are inappropriate at 125 ms intervals and can cause ghosting/blank-looking frames.
- No `setBoolean("startFlipping")` or other unapproved reflection: flipper startup and interval are declared in inflated XML. Not every public View method is callable through `RemoteViews`.
- Collection resource IDs are static, so no `notifyAppWidgetViewDataChanged()` call or repeated payload transfer is needed.
- Separate service URI per widget avoids old-platform factory identity collisions. Modern widgets can independently own playback position while sharing immutable resources.
- A stationary transparent touch layer sits above the flipper. Without it, removing the touched frame every 125 ms cancels long-press before Launcher3 can begin dragging/resizing. The layer has no click action or visible UI. Actual launcher resize testing verified this fix.

## Memory and battery

The 96 PNGs total approximately 2.9 MB. One decoded 320 × 180 ARGB frame is 225 KiB; all 96 decoded simultaneously would be about 21.1 MiB before View/GPU/framework overhead. Resource caches, drawable reuse and multiple instances affect actual memory; this is a raw upper bound for a single distinct bitmap set, not a measured process cap. No bitmap decoding or procedural rendering takes place in the app's update receiver.

The launcher still does work eight times per second while animating. This is not zero-cost, and multiple widgets add layout/drawing work. Android's flipper stops when its window becomes invisible or detaches. Screen-off behavior and home-screen page visibility depend on the host; Android 15's implementation checks window visibility rather than maintaining its own screen-off receiver. A launcher may leave an off-page widget attached to a visible window, throttle frames, or refuse animation. The app cannot reliably detect those states from `AppWidgetProvider`. Do not disable phone battery protections as a general workaround.

8 FPS is a requested interval, not a real-time guarantee: the main looper can delay callbacks under load, lengthening the nominal 12-second loop. Pixel motion remains sequential. This implementation does not silently switch the widget to a static product; the matching underlay only covers binding/loading gaps. If a launcher freezes collection animation, try removing/re-adding the widget or another launcher and report the launcher/Android version.

## Primary references inspected

- [Android collection widgets](https://developer.android.com/develop/ui/views/appwidgets/collections)
- [AdapterViewFlipper reference](https://developer.android.com/reference/android/widget/AdapterViewFlipper)
- [RemoteCollectionItems reference](https://developer.android.com/reference/android/widget/RemoteViews.RemoteCollectionItems)
- [AppWidgetProviderInfo / autoAdvanceViewId](https://developer.android.com/reference/android/appwidget/AppWidgetProviderInfo)
- [Android 15 AdapterViewFlipper source](https://github.com/aosp-mirror/platform_frameworks_base/blob/android-15.0.0_r1/core/java/android/widget/AdapterViewFlipper.java)
- [Android 15 RemoteViews source](https://github.com/aosp-mirror/platform_frameworks_base/blob/android-15.0.0_r1/core/java/android/widget/RemoteViews.java)
- [Android 15 AdapterViewAnimator source](https://github.com/aosp-mirror/platform_frameworks_base/blob/android-15.0.0_r1/core/java/android/widget/AdapterViewAnimator.java)

Source inspection establishes the mechanism; see `VERIFICATION.md` for the tested device/launcher and remaining limitations. It does not establish universal launcher or OxygenOS compatibility.
