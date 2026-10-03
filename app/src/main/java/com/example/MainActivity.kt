package com.example

import android.annotation.SuppressLint
import android.content.ContentValues
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.view.ViewGroup
import android.webkit.JavascriptInterface
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.FrameLayout
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import java.io.File

class MainActivity : ComponentActivity() {
    private var webView: WebView? = null
    private var filePathCallback: ValueCallback<Array<Uri>>? = null

    private val fileChooserLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (filePathCallback != null) {
            val results = WebChromeClient.FileChooserParams.parseResult(result.resultCode, result.data)
            filePathCallback?.onReceiveValue(results)
            filePathCallback = null
        }
    }

    class WebAppInterface(private val activity: MainActivity) {
        @JavascriptInterface
        fun downloadFile(base64Data: String, fileName: String, mimeType: String) {
            activity.runOnUiThread {
                activity.saveFileToDownloads(base64Data, fileName, mimeType)
            }
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        val darkBgColor = android.graphics.Color.parseColor("#0F172A")
        window.statusBarColor = darkBgColor
        window.navigationBarColor = darkBgColor

        val rootLayout = FrameLayout(this).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(darkBgColor)
        }

        val wv = WebView(this).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(darkBgColor)
        }
        webView = wv
        rootLayout.addView(wv)
        setContentView(rootLayout)

        // Handle system bars insets cleanly
        ViewCompat.setOnApplyWindowInsetsListener(rootLayout) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }

        wv.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            allowFileAccess = true
            allowContentAccess = true
            useWideViewPort = true
            loadWithOverviewMode = true
            cacheMode = WebSettings.LOAD_DEFAULT
            mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
        }

        wv.addJavascriptInterface(WebAppInterface(this), "AndroidBridge")

        wv.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                if (intent.getBooleanExtra("ACTION_QUICK_ADD", false)) {
                    intent.removeExtra("ACTION_QUICK_ADD")
                    wv.evaluateJavascript("window.openTransactionModal ? window.openTransactionModal('expense') : null", null)
                }
            }

            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                if (url != null && (url.startsWith("http://") || url.startsWith("https://"))) {
                    try {
                        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                        startActivity(intent)
                        return true
                    } catch (_: Exception) {
                        return false
                    }
                }
                return false
            }
        }

        wv.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                view: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                this@MainActivity.filePathCallback?.onReceiveValue(null)
                this@MainActivity.filePathCallback = filePathCallback

                try {
                    val intent = fileChooserParams?.createIntent() ?: Intent(Intent.ACTION_GET_CONTENT).apply {
                        type = "image/*"
                    }
                    fileChooserLauncher.launch(intent)
                    return true
                } catch (e: Exception) {
                    this@MainActivity.filePathCallback = null
                    return false
                }
            }
        }

        // Dedicated back button handling: close modals or return to dashboard
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                wv.evaluateJavascript("window.handleAndroidBack ? window.handleAndroidBack() : false") { result ->
                    val handled = result == "true" || result == "\"true\""
                    if (!handled) {
                        if (wv.canGoBack()) {
                            wv.goBack()
                        } else {
                            isEnabled = false
                            onBackPressedDispatcher.onBackPressed()
                        }
                    }
                }
            }
        })

        wv.loadUrl("file:///android_asset/index.html")
    }

    fun saveFileToDownloads(base64Data: String, fileName: String, mimeType: String) {
        try {
            val cleanBase64 = if (base64Data.contains(",")) {
                base64Data.substringAfter(",")
            } else {
                base64Data
            }
            val fileBytes = android.util.Base64.decode(cleanBase64, android.util.Base64.DEFAULT)

            var targetUri: Uri? = null

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                val contentValues = ContentValues().apply {
                    put(MediaStore.MediaColumns.DISPLAY_NAME, fileName)
                    put(MediaStore.MediaColumns.MIME_TYPE, mimeType)
                    put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS)
                }
                targetUri = contentResolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, contentValues)
                if (targetUri != null) {
                    contentResolver.openOutputStream(targetUri)?.use { outputStream ->
                        outputStream.write(fileBytes)
                    }
                }
            } else {
                val downloadsDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
                downloadsDir.mkdirs()
                val file = File(downloadsDir, fileName)
                file.writeBytes(fileBytes)
                targetUri = Uri.fromFile(file)
            }

            Toast.makeText(this, "Saved to Downloads: $fileName", Toast.LENGTH_LONG).show()

            // Automatically open / view file if available
            targetUri?.let { uri ->
                try {
                    val viewIntent = Intent(Intent.ACTION_VIEW).apply {
                        setDataAndType(uri, mimeType)
                        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK)
                    }
                    startActivity(Intent.createChooser(viewIntent, "Open $fileName"))
                } catch (_: Exception) {
                    // No default viewer, file remains safely in Downloads
                }
            }
        } catch (e: Exception) {
            Toast.makeText(this, "Failed to save file: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onDestroy() {
        webView?.destroy()
        webView = null
        super.onDestroy()
    }
}
