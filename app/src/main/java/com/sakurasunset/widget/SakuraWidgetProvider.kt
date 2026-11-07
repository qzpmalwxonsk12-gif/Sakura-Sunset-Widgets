package com.sakurasunset.widget

import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.widget.RemoteViews

class SakuraWidgetProvider : AppWidgetProvider() {
    override fun onUpdate(context: Context, manager: AppWidgetManager, ids: IntArray) {
        ids.forEach { manager.updateAppWidget(it, createViews(context, it)) }
    }

    override fun onAppWidgetOptionsChanged(
        context: Context, manager: AppWidgetManager, appWidgetId: Int, newOptions: Bundle
    ) {
        // FIT_CENTER responds to host measurements without resizing or decoding in our process.
        manager.updateAppWidget(appWidgetId, createViews(context, appWidgetId))
    }

    override fun onRestored(context: Context, oldWidgetIds: IntArray, newWidgetIds: IntArray) {
        ArtworkStore.restore(context, oldWidgetIds, newWidgetIds)
        onUpdate(context, AppWidgetManager.getInstance(context), newWidgetIds)
    }

    override fun onDeleted(context: Context, appWidgetIds: IntArray) {
        appWidgetIds.forEach { ArtworkStore.delete(context, it) }
    }

    companion object {
        fun createViews(context: Context, widgetId: Int): RemoteViews {
            val artwork = ArtworkStore.forWidget(context, widgetId)
            return RemoteViews(context.packageName, R.layout.widget_sakura).apply {
                setImageViewResource(R.id.underlay, artwork.preview)
                setContentDescription(R.id.painting, context.getString(artwork.description))
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    // Only resource IDs cross Binder. No Bitmap collection, render loop or service.
                    val items = RemoteViews.RemoteCollectionItems.Builder()
                        .setHasStableIds(true).setViewTypeCount(1)
                    artwork.frames.indices.forEach { index ->
                        items.addItem((artwork.ordinal * 1000 + index).toLong(), frameViews(context, index, artwork))
                    }
                    setRemoteAdapter(R.id.frames, items.build())
                } else {
                    @Suppress("DEPRECATION")
                    setRemoteAdapter(R.id.frames, Intent(context, SakuraFramesService::class.java).apply {
                        putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, widgetId)
                        putExtra("artwork", artwork.key)
                        // Intent extras are not part of filterEquals. Separate each widget's adapter.
                        data = Uri.parse("sakura://frames/$widgetId/${artwork.key}")
                    })
                }
            }
        }

        fun frameViews(context: Context, index: Int, artwork: Artwork = Artwork.SUNSET): RemoteViews =
            RemoteViews(context.packageName, R.layout.widget_frame).apply {
                setImageViewResource(R.id.frame_image, artwork.frames[index])
            }
    }
}
