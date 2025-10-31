package com.tracket.wear.ui

import android.content.Context
import android.util.Log
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.wear.compose.material.*
import com.tracket.wear.models.PointData
import com.tracket.wear.services.ApiClient
import com.tracket.wear.services.HealthServicesManager
import kotlinx.coroutines.launch

/**
 * Main score tracking screen for matches
 * Optimized for Pixel Watch round display
 */
@Composable
fun ScoreTrackingScreen(
    sessionId: String,
    sessionName: String,
    onEndSession: () -> Unit
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()

    // API client
    val apiClient = remember { ApiClient.getInstance(context) }

    // Health services
    val healthManager = remember { HealthServicesManager.getInstance(context) }
    val heartRate by healthManager.heartRate.collectAsState()

    // Score state
    var scoreMe by remember { mutableStateOf(0) }
    var scoreOpponent by remember { mutableStateOf(0) }
    var gameNumber by remember { mutableStateOf(1) }

    // History for undo
    data class PointHistory(val scoreMe: Int, val scoreOpp: Int, val game: Int)
    var history by remember { mutableStateOf<List<PointHistory>>(emptyList()) }

    // UI state
    var isRecording by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    // Start heart rate monitoring and load existing points on launch
    LaunchedEffect(Unit) {
        Log.d("ScoreTrackingScreen", "LaunchedEffect started")

        // Load existing points from backend
        try {
            Log.d("ScoreTrackingScreen", "Loading existing points...")
            val existingPoints = apiClient.api.getPoints(sessionId)

            if (existingPoints.isNotEmpty()) {
                val lastPoint = existingPoints.last()
                scoreMe = lastPoint.scoreMeAfter
                scoreOpponent = lastPoint.scoreOpponentAfter
                gameNumber = lastPoint.gameNumber
                Log.d("ScoreTrackingScreen", "Loaded ${existingPoints.size} points. Current score: $scoreMe-$scoreOpponent, Game: $gameNumber")
            }
        } catch (e: Exception) {
            Log.e("ScoreTrackingScreen", "Failed to load existing points", e)
        }

        // Start heart rate monitoring
        try {
            Log.d("ScoreTrackingScreen", "Starting heart rate monitoring...")
            healthManager.startHeartRateMonitoring()
            Log.d("ScoreTrackingScreen", "Heart rate monitoring started successfully")
        } catch (e: Exception) {
            Log.e("ScoreTrackingScreen", "Failed to start heart rate monitoring", e)
        }

        // Save current session ID for health manager
        context.getSharedPreferences("tracket_prefs", Context.MODE_PRIVATE)
            .edit()
            .putString("current_session_id", sessionId)
            .apply()
        Log.d("ScoreTrackingScreen", "Session ID saved: $sessionId")
    }

    // Stop monitoring on dispose
    DisposableEffect(Unit) {
        onDispose {
            scope.launch {
                healthManager.stopHeartRateMonitoring()
            }
        }
    }

    // Function to record point
    fun recordPoint(winner: String, isLet: Boolean = false) {
        // Save current state for undo
        history = history + PointHistory(scoreMe, scoreOpponent, gameNumber)

        // Update local score immediately (optimistic update)
        if (!isLet) {
            if (winner == "me") {
                scoreMe += 1
            } else {
                scoreOpponent += 1
            }
        }

        // Try to sync with backend in background (don't block UI)
        scope.launch {
            try {
                val pointData = PointData(
                    winner = winner,
                    scoreMeBefore = history.last().scoreMe,
                    scoreOpponentBefore = history.last().scoreOpp,
                    scoreMeAfter = scoreMe,
                    scoreOpponentAfter = scoreOpponent,
                    gameNumber = gameNumber,
                    isLet = if (isLet) "true" else "false"
                )

                apiClient.api.recordPoint(sessionId, pointData)
                errorMessage = null // Clear error on success
            } catch (e: Exception) {
                // Don't show error - just work offline
                // Points are still saved locally
            }
        }
    }

    // Undo last point
    fun undoLastPoint() {
        if (history.isNotEmpty()) {
            val last = history.last()
            scoreMe = last.scoreMe
            scoreOpponent = last.scoreOpp
            gameNumber = last.game
            history = history.dropLast(1)
            errorMessage = null
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .padding(horizontal = 16.dp, vertical = 12.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.SpaceBetween
    ) {
        // Top: Game number and heart rate - centered to avoid round cutoff
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Game $gameNumber",
                fontSize = 15.sp,
                color = Color.White,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = if (heartRate > 0) "❤️$heartRate" else "❤️--",
                fontSize = 13.sp,
                color = if (heartRate > 0) Color(0xFFFF6B6B) else Color.Gray,
                fontWeight = FontWeight.Bold
            )
        }

        // Score display - more compact
        Row(
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = scoreMe.toString(),
                fontSize = 42.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF00D4AA)
            )
            Text(
                text = "-",
                fontSize = 30.sp,
                color = Color.Gray,
                modifier = Modifier.padding(horizontal = 6.dp)
            )
            Text(
                text = scoreOpponent.toString(),
                fontSize = 42.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFFE74C3C)
            )
        }

        // Three buttons in one row: ME, LET, OPP
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            Button(
                onClick = { recordPoint("me") },
                modifier = Modifier
                    .weight(1f)
                    .height(50.dp)
                    .padding(horizontal = 1.dp),
                colors = ButtonDefaults.buttonColors(
                    backgroundColor = Color(0xFF00D4AA)
                )
            ) {
                Text(text = "ME", fontSize = 14.sp, fontWeight = FontWeight.Bold)
            }

            Button(
                onClick = { recordPoint("me", isLet = true) },
                modifier = Modifier
                    .weight(1f)
                    .height(50.dp)
                    .padding(horizontal = 1.dp),
                colors = ButtonDefaults.buttonColors(
                    backgroundColor = Color(0xFFFF9800)
                )
            ) {
                Text(text = "LET", fontSize = 14.sp, fontWeight = FontWeight.Bold)
            }

            Button(
                onClick = { recordPoint("opponent") },
                modifier = Modifier
                    .weight(1f)
                    .height(50.dp)
                    .padding(horizontal = 1.dp),
                colors = ButtonDefaults.buttonColors(
                    backgroundColor = Color(0xFFE74C3C)
                )
            ) {
                Text(text = "OPP", fontSize = 14.sp, fontWeight = FontWeight.Bold)
            }
        }

        // UNDO button
        Button(
            onClick = { undoLastPoint() },
            enabled = history.isNotEmpty(),
            modifier = Modifier
                .fillMaxWidth(0.9f)
                .height(40.dp),
            colors = ButtonDefaults.buttonColors(
                backgroundColor = Color(0xFF555555)
            )
        ) {
            Text(text = "UNDO", fontSize = 13.sp, fontWeight = FontWeight.Bold)
        }

        // Game/Match controls - centered to avoid cutoff
        Row(
            modifier = Modifier.fillMaxWidth(0.85f),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            // Next Game button
            Button(
                onClick = {
                    gameNumber += 1
                    scoreMe = 0
                    scoreOpponent = 0
                    history = emptyList()
                },
                modifier = Modifier
                    .weight(1f)
                    .height(36.dp)
                    .padding(horizontal = 2.dp),
                colors = ButtonDefaults.buttonColors(
                    backgroundColor = Color(0xFF2196F3)
                )
            ) {
                Text(text = "Next", fontSize = 10.sp)
            }

            // End Match button
            Button(
                onClick = {
                    scope.launch {
                        try {
                            Log.d("ScoreTrackingScreen", "Ending session...")

                            // Calculate final games won (current game number - 1 since games start at 1)
                            val totalGames = if (scoreMe > 0 || scoreOpponent > 0) gameNumber else gameNumber - 1

                            // Prepare update data
                            val updateData = mapOf(
                                "end_time" to java.time.Instant.now().toString(),
                                "total_games" to totalGames
                            )

                            // Call API to end session
                            apiClient.api.updateSession(sessionId, updateData)
                            Log.d("ScoreTrackingScreen", "Session ended successfully")

                            // Stop heart rate monitoring
                            healthManager.stopHeartRateMonitoring()

                            // Return to session list
                            onEndSession()
                        } catch (e: Exception) {
                            Log.e("ScoreTrackingScreen", "Failed to end session", e)
                            // Still return to session list even if API fails
                            onEndSession()
                        }
                    }
                },
                modifier = Modifier
                    .weight(1f)
                    .height(36.dp)
                    .padding(horizontal = 2.dp),
                colors = ButtonDefaults.buttonColors(
                    backgroundColor = Color(0xFF666666)
                )
            ) {
                Text(text = "End", fontSize = 10.sp)
            }
        }
    }
}
