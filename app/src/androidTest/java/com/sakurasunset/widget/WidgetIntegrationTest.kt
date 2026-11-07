package com.sakurasunset.widget

import android.appwidget.AppWidgetHostView
import android.appwidget.AppWidgetManager
import android.content.Intent
import android.graphics.drawable.BitmapDrawable
import android.os.Parcel
import android.widget.AdapterViewFlipper
import android.widget.ImageView
import android.view.View
import android.view.ViewGroup
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith

/** Real framework integration tests. Separate launcher captures verify home-screen behavior. */
@RunWith(AndroidJUnit4::class)
class WidgetIntegrationTest {
    private val instrumentation = InstrumentationRegistry.getInstrumentation()
    private val context = instrumentation.targetContext

    @Test fun collectionParcelIsSmallAndHasNoEmbeddedBitmaps() {
        val parcel = Parcel.obtain()
        try {
            val views = SakuraWidgetProvider.createViews(context, 42)
            views.writeToParcel(parcel, 0)
            assertTrue("Resource-only parcel is ${parcel.dataSize()} bytes", parcel.dataSize() < 100_000)
            android.util.Log.i("SakuraVerification", "RemoteViews parcel: ${parcel.dataSize()} bytes")
        } finally { parcel.recycle(); ArtworkStore.delete(context, 42) }
    }

    @Test fun everyBundledFrameDecodesWithoutFiltering() {
      Artwork.entries.forEach { art ->
        assertEquals(96, art.frames.size)
        art.frames.forEach { id ->
            val drawable = context.getDrawable(id) as BitmapDrawable
            assertEquals(if (art == Artwork.IMMORTALS) 480 else 320, drawable.bitmap.width)
            assertEquals(if (art == Artwork.IMMORTALS) 270 else 180, drawable.bitmap.height)
            assertFalse(drawable.paint.isFilterBitmap)
        }
      }
    }

    @Test fun legacyFactoryIsStableAndSafeForInvalidPositions() {
        val factory = SakuraFramesService.FramesFactory(context)
        factory.onCreate()
        assertEquals(96, factory.count)
        assertTrue(factory.hasStableIds())
        assertNotNull(factory.loadingView)
        for (i in 0 until factory.count) {
            assertEquals(i.toLong(), factory.getItemId(i))
            assertNotNull(factory.getViewAt(i))
        }
        assertNull(factory.getViewAt(-1))
        assertNull(factory.getViewAt(96))
        factory.onDestroy()
    }

    @Test fun choicesAreIndependentAndSurviveRestore() {
        val ids = intArrayOf(-8101, -8102)
        val oldDefault = ArtworkStore.default(context)
        try {
            ArtworkStore.save(context, ids[0], Artwork.SUNSET)
            ArtworkStore.save(context, ids[1], Artwork.IMMORTALS)
            ArtworkStore.setDefault(context, Artwork.IMMORTALS)
            assertEquals(Artwork.SUNSET, ArtworkStore.forWidget(context, ids[0]))
            assertEquals(Artwork.IMMORTALS, ArtworkStore.forWidget(context, ids[1]))
            ArtworkStore.restore(context, ids, ids.reversedArray())
            assertEquals(Artwork.IMMORTALS, ArtworkStore.forWidget(context, ids[0]))
            assertEquals(Artwork.SUNSET, ArtworkStore.forWidget(context, ids[1]))
            val factory = SakuraFramesService.FramesFactory(context, Artwork.IMMORTALS)
            assertEquals(96, factory.count)
            assertEquals(1000L, factory.getItemId(0))
            assertNotNull(factory.getViewAt(95))
            assertNull(factory.getViewAt(96))
            val parcel = Parcel.obtain()
            try {
                SakuraWidgetProvider.createViews(context, ids[0]).writeToParcel(parcel, 0)
                assertTrue(parcel.dataSize() < 100_000)
            } finally { parcel.recycle() }
        } finally {
            ids.forEach { ArtworkStore.delete(context, it) }
            ArtworkStore.setDefault(context, oldDefault)
        }
    }

    @Test fun actualRemoteViewsAdvanceAndWrapInAndroidHost() = verifyHost(Artwork.SUNSET)
    @Test fun immortalsAdvanceAndWrapInAndroidHost() = verifyHost(Artwork.IMMORTALS)
    @Test fun winterAdvancesAndWrapsInAndroidHost() = verifyHost(Artwork.WINTER)

    @Test fun winterChoiceAndLegacyFactoryRemainSeparate() {
        val id = -8201
        try {
            ArtworkStore.save(context, id, Artwork.WINTER)
            assertEquals(Artwork.WINTER, ArtworkStore.forWidget(context, id))
            val factory = SakuraFramesService.FramesFactory(context, Artwork.WINTER)
            assertEquals(96, factory.count)
            assertEquals(2000L, factory.getItemId(0))
            assertNotNull(factory.getViewAt(95))
            assertNull(factory.getViewAt(96))
            val parcel = Parcel.obtain()
            try {
                SakuraWidgetProvider.createViews(context, id).writeToParcel(parcel, 0)
                assertTrue(parcel.dataSize() < 100_000)
            } finally { parcel.recycle() }
        } finally { ArtworkStore.delete(context, id) }
    }

    private fun verifyHost(art: Artwork) {
        ArtworkStore.save(context, 1234, art)
        val activity = instrumentation.startActivitySync(
            Intent(context, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
        lateinit var flipper: AdapterViewFlipper
        try {
            instrumentation.runOnMainSync {
                val info = AppWidgetManager.getInstance(context).installedProviders.first {
                    it.provider.className == SakuraWidgetProvider::class.java.name
                }
                assertEquals(-1, info.autoAdvanceViewId)
                assertEquals(0, info.updatePeriodMillis)
                val host = AppWidgetHostView(activity)
                host.setAppWidget(1234, info)
                host.updateAppWidget(SakuraWidgetProvider.createViews(context, 1234))
                activity.setContentView(host)
                flipper = host.findViewById(R.id.frames)
                assertEquals(125, flipper.flipInterval)
                assertTrue(flipper.isAutoStart)
                assertEquals(0L, flipper.inAnimation.duration)
                assertEquals(0L, flipper.outAnimation.duration)
            }
            instrumentation.waitForIdleSync()
            Thread.sleep(1000)
            var first = -1
            instrumentation.runOnMainSync {
                assertEquals(96, flipper.adapter.count)
                first = flipper.displayedChild
                // AdapterChildHostView is a root namespace: findViewById deliberately
                // does not traverse it from the flipper's wrapper FrameLayout.
                fun frameImage(view: View): ImageView? {
                    if (view is ImageView && view.id == R.id.frame_image) return view
                    if (view is ViewGroup) for (i in 0 until view.childCount) {
                        frameImage(view.getChildAt(i))?.let { return it }
                    }
                    return null
                }
                val currentImage = frameImage(flipper.currentView)
                assertNotNull(currentImage)
                assertNotNull(currentImage!!.drawable)
                flipper.displayedChild = 95
            }
            Thread.sleep(350)
            instrumentation.runOnMainSync {
                assertTrue("Wrapped to ${flipper.displayedChild}", flipper.displayedChild in 0..4)
            }
            Thread.sleep(1000)
            instrumentation.runOnMainSync {
                assertTrue(flipper.displayedChild in 5..15)
                assertTrue("Initial timer advanced: $first", first in 1..16)
                android.util.Log.i("SakuraVerification", "Host advanced and wrapped: ${flipper.displayedChild}")
            }
        } finally {
            instrumentation.runOnMainSync { activity.finish() }
            ArtworkStore.delete(context, 1234)
        }
    }
}
