package com.tracket.wear.models

import com.google.gson.annotations.SerializedName

/**
 * Session data model matching backend structure
 */
data class Session(
    @SerializedName("session_id")
    val sessionId: String,

    @SerializedName("user_id")
    val userId: String, // Changed from Int to String (UUID)

    @SerializedName("session_type")
    val sessionType: String, // "match" or "training"

    @SerializedName("sport")
    val sport: String,

    @SerializedName("scoring_system")
    val scoringSystem: String?, // "par_11", "par_15", etc.

    @SerializedName("opponent_name")
    val opponentName: String? = null,

    @SerializedName("location")
    val location: String? = null,

    @SerializedName("start_time")
    val startTime: String,

    @SerializedName("end_time")
    val endTime: String?,

    @SerializedName("sync_status")
    val syncStatus: String? = null, // "pending", "synced", etc.

    @SerializedName("final_score_me")
    val finalScoreMe: Int?,

    @SerializedName("final_score_opponent")
    val finalScoreOpponent: Int?
) {
    // Computed properties for display
    val isActive: Boolean
        get() = endTime == null // Session is active if no end_time

    val displayName: String
        get() = if (!opponentName.isNullOrEmpty()) {
            "vs $opponentName"
        } else {
            "${sport.replaceFirstChar { it.uppercase() }} ${sessionType.replaceFirstChar { it.uppercase() }}"
        }

    val scoringSystemDisplay: String
        get() = when (scoringSystem) {
            "american" -> "PARS"
            "english" -> "English"
            else -> "Unknown"
        }
}

/**
 * Response when creating or fetching sessions
 */
data class SessionListResponse(
    val sessions: List<Session>
)
