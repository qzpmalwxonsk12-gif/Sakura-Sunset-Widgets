package com.sakurasunset.widget

import android.content.Context

enum class Artwork(val key: String, val title: Int, val description: Int, val preview: Int) {
    SUNSET("sunset", R.string.sunset_title, R.string.art_description, R.drawable.scene_preview),
    IMMORTALS("immortals", R.string.immortals_title, R.string.immortals_description, R.drawable.immortals_preview),
    WINTER("winter", R.string.winter_title, R.string.winter_description, R.drawable.winter_preview);

    val frames: IntArray get() = when (this) {
        SUNSET -> FrameCatalog.resources
        IMMORTALS -> ImmortalsFrames.resources
        WINTER -> WinterFrames.resources
    }

    companion object {
        fun fromKey(key: String?) = entries.firstOrNull { it.key == key } ?: SUNSET
    }
}

/** One saved choice per widget. Changing the default never changes an existing painting. */
object ArtworkStore {
    private fun preferences(context: Context) = context.getSharedPreferences("artwork", Context.MODE_PRIVATE)
    fun default(context: Context) = Artwork.fromKey(preferences(context).getString("default", null))
    fun setDefault(context: Context, artwork: Artwork) {
        preferences(context).edit().putString("default", artwork.key).apply()
    }
    fun forWidget(context: Context, id: Int): Artwork {
        val prefs = preferences(context)
        if (!prefs.contains("widget_$id")) save(context, id, default(context))
        return Artwork.fromKey(prefs.getString("widget_$id", null))
    }
    fun save(context: Context, id: Int, artwork: Artwork) {
        preferences(context).edit().putString("widget_$id", artwork.key).apply()
    }
    fun delete(context: Context, id: Int) { preferences(context).edit().remove("widget_$id").apply() }
    fun restore(context: Context, oldIds: IntArray, newIds: IntArray) {
        // Snapshot before writing: restored IDs can overlap the old ID set.
        val choices = oldIds.map { forWidget(context, it) }
        val editor = preferences(context).edit()
        oldIds.forEach { editor.remove("widget_$it") }
        newIds.forEachIndexed { index, id -> editor.putString("widget_$id", choices[index].key) }
        editor.apply()
    }
}
