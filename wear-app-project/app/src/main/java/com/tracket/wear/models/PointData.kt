package com.tracket.wear.models

import com.google.gson.annotations.SerializedName

/**
 * Point data for recording score events
 */
data class PointData(
    @SerializedName("winner")
    val winner: String, // "me" or "opponent"

    @SerializedName("score_me_before")
    val scoreMeBefore: Int,

    @SerializedName("score_opponent_before")
    val scoreOpponentBefore: Int,

    @SerializedName("score_me_after")
    val scoreMeAfter: Int,

    @SerializedName("score_opponent_after")
    val scoreOpponentAfter: Int,

    @SerializedName("game_number")
    val gameNumber: Int,

    @SerializedName("is_let")
    val isLet: String // "true" or "false" (backend expects string)
)

/**
 * Response from backend after recording point
 */
data class PointResponse(
    @SerializedName("point_id")
    val pointId: String,

    @SerializedName("session_id")
    val sessionId: String,

    @SerializedName("winner")
    val winner: String,

    @SerializedName("score_me_before")
    val scoreMeBefore: Int,

    @SerializedName("score_opponent_before")
    val scoreOpponentBefore: Int,

    @SerializedName("score_me_after")
    val scoreMeAfter: Int,

    @SerializedName("score_opponent_after")
    val scoreOpponentAfter: Int,

    @SerializedName("game_number")
    val gameNumber: Int,

    @SerializedName("is_let")
    val isLet: String,

    @SerializedName("timestamp")
    val timestamp: String
)
