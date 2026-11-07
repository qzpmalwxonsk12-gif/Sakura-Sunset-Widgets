package com.sakurasunset.widget

import android.app.Activity
import android.appwidget.AppWidgetManager
import android.content.ComponentName
import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.view.Gravity
import android.widget.Button
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast

/** A small artwork picker; all animation lives in the launcher. */
class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setResult(RESULT_CANCELED)
    }

    override fun onResume() {
        super.onResume()
        showPicker()
    }

    private fun showPicker() {
        val manager = AppWidgetManager.getInstance(this)
        val provider = ComponentName(this, SakuraWidgetProvider::class.java)
        val widgetId = intent.getIntExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, AppWidgetManager.INVALID_APPWIDGET_ID)
        val configuring = widgetId != AppWidgetManager.INVALID_APPWIDGET_ID
        if (configuring && manager.getAppWidgetInfo(widgetId)?.provider != provider) {
            finish()
            return
        }
        val selected = if (configuring) ArtworkStore.forWidget(this, widgetId) else ArtworkStore.default(this)
        val density = resources.displayMetrics.density
        fun dp(value: Int) = (value * density + 0.5f).toInt()
        val column = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER_HORIZONTAL
            setPadding(dp(24), dp(24), dp(24), dp(28))
        }
        val scroll = ScrollView(this).apply { addView(column); isFillViewport = true }
        scroll.setOnApplyWindowInsetsListener { view, insets ->
            @Suppress("DEPRECATION")
            view.setPadding(insets.systemWindowInsetLeft, insets.systemWindowInsetTop,
                insets.systemWindowInsetRight, insets.systemWindowInsetBottom)
            insets
        }
        fun text(value: String, size: Float, top: Int, color: String = "#EEE2E7") {
            column.addView(TextView(this).apply {
                text = value; textSize = size; setTextColor(Color.parseColor(color))
                setLineSpacing(dp(3).toFloat(), 1f)
            }, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(top) })
        }
        fun button(label: String, action: () -> Unit) {
            column.addView(Button(this).apply {
                text = label; isAllCaps = false; setOnClickListener { action() }
            }, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(8) })
        }
        text(getString(R.string.choose_art), 28f, 0, "#FFE0CD")
        text(getString(R.string.choose_hint), 15f, 8, "#DFA2B4")
        Artwork.entries.forEach { art ->
            text(getString(art.title), 21f, 22)
            column.addView(ImageView(this).apply {
                setImageResource(art.preview)
                adjustViewBounds = true
                scaleType = ImageView.ScaleType.FIT_CENTER
                contentDescription = getString(art.description)
            }, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(10) })
            val label = if (configuring) R.string.use_art
                else if (art == selected) R.string.selected_art else R.string.default_art
            button(getString(label)) {
                if (configuring) {
                    ArtworkStore.save(this, widgetId, art)
                    manager.updateAppWidget(widgetId, SakuraWidgetProvider.createViews(this, widgetId))
                    setResult(RESULT_OK, Intent().putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, widgetId))
                    finish()
                } else {
                    ArtworkStore.setDefault(this, art)
                    Toast.makeText(this, R.string.saved_art, Toast.LENGTH_SHORT).show()
                    showPicker()
                }
            }
        }
        if (!configuring) {
            if (manager.isRequestPinAppWidgetSupported) {
                button(getString(R.string.pin_widget)) {
                    manager.requestPinAppWidget(provider, null, null)
                    Toast.makeText(this, R.string.pin_hint, Toast.LENGTH_LONG).show()
                }
            }
            val ids = manager.getAppWidgetIds(provider).sorted()
            if (ids.isNotEmpty()) {
                text(getString(R.string.your_widgets), 21f, 28)
                text(getString(R.string.edit_hint), 14f, 8, "#BEACBE")
                ids.forEachIndexed { index, id ->
                    val art = ArtworkStore.forWidget(this, id)
                    button(getString(R.string.edit_widget, index + 1, getString(art.title))) {
                        startActivity(Intent(this, MainActivity::class.java)
                            .putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, id))
                    }
                }
            }
            text(getString(R.string.instructions), 16f, 24)
            text(getString(R.string.footer), 14f, 18, "#BEACBE")
        }
        setContentView(scroll)
        scroll.requestApplyInsets()
    }
}
