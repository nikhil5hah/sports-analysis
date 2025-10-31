package com.tracket.wear.ui

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
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.wear.compose.material.*
import com.tracket.wear.models.Session
import com.tracket.wear.services.ApiClient
import kotlinx.coroutines.launch

/**
 * Session list screen - displays active sessions for selection
 * Optimized for Pixel Watch round display
 */
@Composable
fun SessionListScreen(
    onSessionSelected: (Session) -> Unit
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()

    // API client
    val apiClient = remember { ApiClient.getInstance(context) }

    // State
    var sessions by remember { mutableStateOf<List<Session>>(emptyList()) }
    var isLoading by remember { mutableStateOf(true) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    // Load sessions on mount
    LaunchedEffect(Unit) {
        try {
            Log.d("SessionListScreen", "Loading sessions...")
            val allSessions = apiClient.api.getSessions()

            // Filter to only active sessions
            sessions = allSessions.filter { it.isActive }

            Log.d("SessionListScreen", "Loaded ${sessions.size} active sessions")
            isLoading = false
        } catch (e: Exception) {
            Log.e("SessionListScreen", "Failed to load sessions", e)
            errorMessage = "Failed to load sessions"
            isLoading = false
        }
    }

    ScalingLazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black),
        contentPadding = PaddingValues(horizontal = 8.dp, vertical = 12.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Header
        item {
            Text(
                text = "Select Session",
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(bottom = 12.dp)
            )
        }

        // Loading indicator
        if (isLoading) {
            item {
                CircularProgressIndicator(
                    modifier = Modifier.size(48.dp).padding(16.dp),
                    indicatorColor = Color(0xFF00D4AA)
                )
            }
        }

        // Error message
        if (errorMessage != null) {
            item {
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = errorMessage!!,
                        fontSize = 14.sp,
                        color = Color(0xFFE74C3C),
                        textAlign = TextAlign.Center
                    )
                    Spacer(modifier = Modifier.height(12.dp))
                    Button(
                        onClick = {
                            scope.launch {
                                try {
                                    isLoading = true
                                    errorMessage = null
                                    val allSessions = apiClient.api.getSessions()
                                    sessions = allSessions.filter { it.isActive }
                                    isLoading = false
                                } catch (e: Exception) {
                                    errorMessage = "Failed to load sessions"
                                    isLoading = false
                                }
                            }
                        },
                        colors = ButtonDefaults.buttonColors(
                            backgroundColor = Color(0xFF2196F3)
                        )
                    ) {
                        Text(text = "Retry")
                    }
                }
            }
        }

        // No sessions message
        if (!isLoading && errorMessage == null && sessions.isEmpty()) {
            item {
                Column(
                    modifier = Modifier.fillMaxWidth().padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "No Active Sessions",
                        fontSize = 14.sp,
                        color = Color.Gray,
                        textAlign = TextAlign.Center
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Start a session on your phone",
                        fontSize = 12.sp,
                        color = Color.Gray,
                        textAlign = TextAlign.Center
                    )
                }
            }
        }

        // Session list
        items(count = sessions.size) { index ->
            SessionCard(
                session = sessions[index],
                onClick = { onSessionSelected(sessions[index]) }
            )
        }
    }
}

/**
 * Individual session card component
 */
@Composable
fun SessionCard(
    session: Session,
    onClick: () -> Unit
) {
    Chip(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        onClick = onClick,
        label = {
            Text(
                text = session.displayName,
                fontSize = 14.sp,
                fontWeight = FontWeight.Bold,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
        },
        secondaryLabel = {
            Column {
                Text(
                    text = session.sessionType.replaceFirstChar { it.uppercase() },
                    fontSize = 11.sp,
                    color = if (session.sessionType == "match") Color(0xFF00D4AA) else Color(0xFFFF9800)
                )
                if (!session.location.isNullOrEmpty()) {
                    Text(
                        text = session.location,
                        fontSize = 10.sp,
                        color = Color.Gray,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
            }
        },
        colors = ChipDefaults.chipColors(
            backgroundColor = Color(0xFF1E1E1E)
        )
    )
}
