package com.tracket.wear.presentation

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.*
import androidx.core.content.ContextCompat
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import com.tracket.wear.models.Session
import com.tracket.wear.presentation.theme.TracketWatchTheme
import com.tracket.wear.services.ApiClient
import com.tracket.wear.ui.ScoreTrackingScreen
import com.tracket.wear.ui.SessionListScreen

class MainActivity : ComponentActivity() {

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        // Permissions granted or denied - app will continue either way
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()

        super.onCreate(savedInstanceState)

        setTheme(android.R.style.Theme_DeviceDefault)

        // Request permissions for heart rate
        requestPermissionsIfNeeded()

        // Initialize auth token for API requests
        val apiClient = ApiClient.getInstance(this)
        // TODO: Replace with your JWT token from mobile app
        // Get token from: Mobile App → Active Session Screen → "Token: eyJ..."
        apiClient.saveAuthToken("YOUR_JWT_TOKEN_HERE")

        setContent {
            TracketWatchTheme {
                // State for selected session
                var selectedSession by remember { mutableStateOf<Session?>(null) }

                if (selectedSession == null) {
                    // Show session list for selection
                    SessionListScreen(
                        onSessionSelected = { session ->
                            selectedSession = session
                        }
                    )
                } else {
                    // Show score tracking for selected session
                    ScoreTrackingScreen(
                        sessionId = selectedSession!!.sessionId,
                        sessionName = selectedSession!!.displayName,
                        onEndSession = {
                            selectedSession = null // Return to session list
                        }
                    )
                }
            }
        }
    }

    private fun requestPermissionsIfNeeded() {
        val permissionsToRequest = mutableListOf<String>()

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.BODY_SENSORS)
            != PackageManager.PERMISSION_GRANTED) {
            permissionsToRequest.add(Manifest.permission.BODY_SENSORS)
        }

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACTIVITY_RECOGNITION)
            != PackageManager.PERMISSION_GRANTED) {
            permissionsToRequest.add(Manifest.permission.ACTIVITY_RECOGNITION)
        }

        // Wear OS 4+ requires this permission for Health Services
        if (ContextCompat.checkSelfPermission(this, "android.permission.health.READ_HEART_RATE")
            != PackageManager.PERMISSION_GRANTED) {
            permissionsToRequest.add("android.permission.health.READ_HEART_RATE")
        }

        if (permissionsToRequest.isNotEmpty()) {
            requestPermissionLauncher.launch(permissionsToRequest.toTypedArray())
        }
    }
}
