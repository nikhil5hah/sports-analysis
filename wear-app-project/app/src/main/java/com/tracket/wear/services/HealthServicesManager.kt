package com.tracket.wear.services

import android.content.Context
import android.util.Log
import androidx.health.services.client.HealthServices
import androidx.health.services.client.MeasureCallback
import androidx.health.services.client.data.Availability
import androidx.health.services.client.data.DataPointContainer
import androidx.health.services.client.data.DataType
import androidx.health.services.client.data.DeltaDataType
import androidx.health.services.client.data.SampleDataPoint
import com.tracket.wear.models.HeartRateData
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.guava.await

/**
 * Manager for Health Services - handles heart rate monitoring on Pixel Watch
 */
class HealthServicesManager(private val context: Context) {
    private val healthServicesClient = HealthServices.getClient(context)
    private val measureClient = healthServicesClient.measureClient

    // Heart rate state
    private val _heartRate = MutableStateFlow(0)
    val heartRate: StateFlow<Int> = _heartRate

    // Heart rate data buffer for batch upload
    private val heartRateBuffer = mutableListOf<HeartRateData>()

    // Availability state
    private val _isAvailable = MutableStateFlow(false)
    val isAvailable: StateFlow<Boolean> = _isAvailable

    // Monitoring state
    private var isMonitoring = false

    // Callback for heart rate measurements
    private val heartRateCallback = object : MeasureCallback {
        override fun onAvailabilityChanged(dataType: DeltaDataType<*, *>, availability: Availability) {
            Log.d(TAG, "Heart rate availability changed")
            _isAvailable.value = true
        }

        override fun onDataReceived(data: DataPointContainer) {
            val heartRateBpm = data.getData(DataType.HEART_RATE_BPM)
            heartRateBpm.forEach { dataPoint ->
                val bpm = (dataPoint as SampleDataPoint<Double>).value.toInt()
                Log.d(TAG, "Heart rate: $bpm BPM")

                // Update state
                _heartRate.value = bpm

                // Add to buffer
                heartRateBuffer.add(HeartRateData(bpm = bpm))

                // Upload in batches of 10
                if (heartRateBuffer.size >= 10) {
                    uploadHeartRateData()
                }
            }
        }
    }

    /**
     * Start monitoring heart rate
     */
    suspend fun startHeartRateMonitoring() {
        if (isMonitoring) {
            Log.d(TAG, "Already monitoring heart rate")
            return
        }

        try {
            measureClient.registerMeasureCallback(
                DataType.HEART_RATE_BPM,
                heartRateCallback
            )
            isMonitoring = true
            Log.d(TAG, "Started heart rate monitoring")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start heart rate monitoring", e)
        }
    }

    /**
     * Stop monitoring heart rate
     */
    suspend fun stopHeartRateMonitoring() {
        if (!isMonitoring) {
            return
        }

        try {
            measureClient.unregisterMeasureCallbackAsync(
                DataType.HEART_RATE_BPM,
                heartRateCallback
            )
            isMonitoring = false
            Log.d(TAG, "Stopped heart rate monitoring")

            // Upload remaining data
            if (heartRateBuffer.isNotEmpty()) {
                uploadHeartRateData()
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to stop heart rate monitoring", e)
        }
    }

    /**
     * Upload heart rate data to backend
     */
    private fun uploadHeartRateData() {
        if (heartRateBuffer.isEmpty()) return

        // Get current session ID (you'll need to pass this from the active session)
        val sessionId = getCurrentSessionId() ?: return

        // Upload in background
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val apiClient = ApiClient.getInstance(context)
                val dataToUpload = heartRateBuffer.toList()
                heartRateBuffer.clear()

                val response = apiClient.api.uploadHeartRate(
                    sessionId = sessionId,
                    heartRateUpload = com.tracket.wear.models.HeartRateUpload(data = dataToUpload)
                )
                Log.d(TAG, "Uploaded ${dataToUpload.size} heart rate samples: ${response.message}")
            } catch (e: Exception) {
                Log.e(TAG, "Failed to upload heart rate data", e)
                // Re-add to buffer if upload failed
                heartRateBuffer.addAll(0, heartRateBuffer)
            }
        }
    }

    /**
     * Get current session ID from shared preferences
     * (Set this when starting a session)
     */
    private fun getCurrentSessionId(): String? {
        val prefs = context.getSharedPreferences("tracket_prefs", Context.MODE_PRIVATE)
        return prefs.getString("current_session_id", null)
    }

    /**
     * Check if heart rate sensor is supported
     */
    suspend fun isHeartRateSensorSupported(): Boolean {
        return try {
            val capabilities = measureClient.getCapabilitiesAsync().await()
            DataType.HEART_RATE_BPM in capabilities.supportedDataTypesMeasure
        } catch (e: Exception) {
            Log.e(TAG, "Failed to check heart rate sensor support", e)
            false
        }
    }

    companion object {
        private const val TAG = "HealthServicesManager"

        @Volatile
        private var instance: HealthServicesManager? = null

        fun getInstance(context: Context): HealthServicesManager {
            return instance ?: synchronized(this) {
                instance ?: HealthServicesManager(context.applicationContext).also { instance = it }
            }
        }
    }
}
