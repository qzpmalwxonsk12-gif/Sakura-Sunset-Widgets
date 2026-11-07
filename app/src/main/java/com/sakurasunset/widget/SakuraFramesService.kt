package com.sakurasunset.widget

import android.content.Context
import android.content.Intent
import android.widget.RemoteViews
import android.widget.RemoteViewsService

/** Android 8–11 fallback: on-demand immutable resource references, never a running timer. */
class SakuraFramesService : RemoteViewsService() {
    override fun onGetViewFactory(intent: Intent): RemoteViewsFactory =
        FramesFactory(applicationContext, Artwork.fromKey(intent.getStringExtra("artwork")))

    class FramesFactory(private val context: Context, private val artwork: Artwork = Artwork.SUNSET) : RemoteViewsFactory {
        override fun onCreate() = Unit
        override fun onDataSetChanged() = Unit
        override fun onDestroy() = Unit
        override fun getCount() = artwork.frames.size
        override fun getViewAt(position: Int): RemoteViews? =
            if (position in artwork.frames.indices)
                SakuraWidgetProvider.frameViews(context, position, artwork) else null
        override fun getLoadingView(): RemoteViews =
            SakuraWidgetProvider.frameViews(context, 0, artwork)
        override fun getViewTypeCount() = 1
        override fun getItemId(position: Int) = (artwork.ordinal * 1000 + position).toLong()
        override fun hasStableIds() = true
    }
}
