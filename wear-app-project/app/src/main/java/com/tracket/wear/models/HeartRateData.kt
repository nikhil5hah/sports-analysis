package com.tracket.wear.models

import com.google.gson.annotations.SerializedName
import java.text.SimpleDateFormat
import java.util.*

/**
 * Heart rate data for sensor tracking
 */
data class HeartRateData(
    @SerializedName("bpm")
    val bpm: Int,

    @SerializedName("timestamp")
    val timestamp: String = getCurrentISOTimestamp()
) {
    companion object {
        private fun getCurrentISOTimestamp(): String {
            val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.US)
            dateFormat.timeZone = TimeZone.getTimeZone("UTC")
            return dateFormat.format(Date())
        }
    }
}

/**
 * Request body for uploading heart rate to backend
 */
data class HeartRateUpload(
    @SerializedName("data_points")
    val data: List<HeartRateData>
)

/**
 * Response from backend after uploading heart rate
 */
data class HeartRateResponse(
    @SerializedName("message")
    val message: String,

    @SerializedName("count")
    val count: Int
)
