# Wear OS App Development Guide
## Pixel Watch 3 Squash Analytics App

---

## 1. Project Setup

### 1.1 Prerequisites

```bash
# Required tools
- Android Studio (latest version)
- Pixel Watch 3 (or emulator)
- JDK 17+
- Kotlin 1.9+
```

### 1.2 Create Wear OS Project

```bash
# Android Studio
File → New → New Project
→ Select "Wear OS App"
→ Choose "Compose for Wear OS"
→ Name: SquashWatch
→ Package: com.squashanalytics.watch
→ Minimum SDK: API 30 (Wear OS 3.0)
```

### 1.3 Project Structure

```
SquashWatch/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── kotlin/com/squashanalytics/watch/
│   │   │   │   ├── MainActivity.kt
│   │   │   │   ├── ui/
│   │   │   │   │   ├── screens/
│   │   │   │   │   │   ├── HomeScreen.kt
│   │   │   │   │   │   ├── MatchScreen.kt
│   │   │   │   │   │   └── SettingsScreen.kt
│   │   │   │   │   └── components/
│   │   │   │   │       ├── ScoreButton.kt
│   │   │   │   │       ├── HRDisplay.kt
│   │   │   │   │       └── Timer.kt
│   │   │   │   ├── data/
│   │   │   │   │   ├── local/
│   │   │   │   │   │   ├── MatchDatabase.kt
│   │   │   │   │   │   ├── dao/
│   │   │   │   │   │   │   ├── SessionDao.kt
│   │   │   │   │   │   │   ├── PointDao.kt
│   │   │   │   │   │   │   └── HRDataDao.kt
│   │   │   │   │   │   └── entities/
│   │   │   │   │   │       ├── SessionEntity.kt
│   │   │   │   │   │       ├── PointEntity.kt
│   │   │   │   │   │       └── HRDataEntity.kt
│   │   │   │   │   └── repository/
│   │   │   │   │       └── MatchRepository.kt
│   │   │   │   ├── services/
│   │   │   │   │   ├── HeartRateService.kt
│   │   │   │   │   ├── SensorService.kt
│   │   │   │   │   └── SyncService.kt
│   │   │   │   ├── utils/
│   │   │   │   │   ├── HRZoneCalculator.kt
│   │   │   │   │   └── TimeFormatter.kt
│   │   │   │   └── viewmodel/
│   │   │   │       └── MatchViewModel.kt
│   │   │   └── AndroidManifest.xml
│   │   └── build.gradle.kts
│   └── build.gradle.kts
└── gradle/
```

---

## 2. Dependencies

### 2.1 build.gradle.kts (Module-level)

```kotlin
plugins {
    id("com.android.application")
    kotlin("android")
    kotlin("kapt")
    id("com.google.dagger.hilt.android")
}

android {
    namespace = "com.squashanalytics.watch"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.squashanalytics.watch"
        minSdk = 30  // Wear OS 3.0+
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildFeatures {
        compose = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.3"
    }
}

dependencies {
    // Wear OS Compose
    implementation("androidx.wear.compose:compose-material:1.2.1")
    implementation("androidx.wear.compose:compose-foundation:1.2.1")
    implementation("androidx.wear.compose:compose-navigation:1.2.1")

    // Health Services (HR monitoring)
    implementation("androidx.health:health-services-client:1.0.0-beta03")

    // Room Database
    implementation("androidx.room:room-runtime:2.6.0")
    implementation("androidx.room:room-ktx:2.6.0")
    kapt("androidx.room:room-compiler:2.6.0")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-play-services:1.7.3")

    // Lifecycle
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.6.2")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.6.2")

    // Hilt (Dependency Injection)
    implementation("com.google.dagger:hilt-android:2.48")
    kapt("com.google.dagger:hilt-compiler:2.48")

    // Sensors
    implementation("androidx.core:core-ktx:1.12.0")

    // Work Manager (for sync)
    implementation("androidx.work:work-runtime-ktx:2.9.0")

    // Retrofit (API calls)
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")

    // OkHttp (logging)
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")

    // DataStore (preferences)
    implementation("androidx.datastore:datastore-preferences:1.0.0")
}
```

---

## 3. Core Components

### 3.1 Heart Rate Monitoring Service

```kotlin
// services/HeartRateService.kt
package com.squashanalytics.watch.services

import androidx.health.services.client.HealthServices
import androidx.health.services.client.data.DataType
import androidx.health.services.client.data.HeartRateAccuracy
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject

data class HeartRateData(
    val heartRate: Float,
    val timestamp: Long,
    val accuracy: HeartRateAccuracy
)

class HeartRateService @Inject constructor(
    private val healthServicesClient: HealthServices
) {
    /**
     * Continuous heart rate monitoring
     * Returns Flow of heart rate updates
     */
    fun startHeartRateMonitoring(): Flow<HeartRateData> {
        val measureClient = healthServicesClient.measureClient

        return measureClient.getDataUpdates(
            setOf(DataType.HEART_RATE_BPM)
        ).map { dataUpdate ->
            val hrData = dataUpdate.getData(DataType.HEART_RATE_BPM)
            val samplePoint = hrData.firstOrNull()

            HeartRateData(
                heartRate = samplePoint?.value?.asDouble()?.toFloat() ?: 0f,
                timestamp = System.currentTimeMillis(),
                accuracy = samplePoint?.accuracy as? HeartRateAccuracy
                    ?: HeartRateAccuracy.UNKNOWN
            )
        }
    }

    suspend fun getCurrentHeartRate(): Float? {
        // Get single HR reading
        val measureClient = healthServicesClient.measureClient
        val capabilities = measureClient.getCapabilitiesAsync().await()

        if (DataType.HEART_RATE_BPM !in capabilities.supportedDataTypesMeasure) {
            return null
        }

        // Implementation depends on Health Services API
        return null  // TODO: Implement single reading
    }
}
```

### 3.2 Sensor Data Collection Service

```kotlin
// services/SensorService.kt
package com.squashanalytics.watch.services

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import javax.inject.Inject

data class SensorReading(
    val timestamp: Long,
    val accelerometer: Triple<Float, Float, Float>?,
    val gyroscope: Triple<Float, Float, Float>?
)

class SensorService @Inject constructor(
    private val context: Context
) {
    private val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager

    /**
     * Collect accelerometer and gyroscope data in background
     * Sample rate: 10 Hz (configurable)
     */
    fun startSensorCollection(sampleRateHz: Int = 10): Flow<SensorReading> = callbackFlow {
        val accelSensor = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        val gyroSensor = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)

        var lastAccelData: Triple<Float, Float, Float>? = null
        var lastGyroData: Triple<Float, Float, Float>? = null

        val listener = object : SensorEventListener {
            override fun onSensorChanged(event: SensorEvent) {
                when (event.sensor.type) {
                    Sensor.TYPE_ACCELEROMETER -> {
                        lastAccelData = Triple(event.values[0], event.values[1], event.values[2])
                    }
                    Sensor.TYPE_GYROSCOPE -> {
                        lastGyroData = Triple(event.values[0], event.values[1], event.values[2])
                    }
                }

                // Emit combined reading
                trySend(SensorReading(
                    timestamp = System.currentTimeMillis(),
                    accelerometer = lastAccelData,
                    gyroscope = lastGyroData
                ))
            }

            override fun onAccuracyChanged(sensor: Sensor, accuracy: Int) {
                // Handle accuracy changes
            }
        }

        // Register listeners
        val delayMicros = (1_000_000 / sampleRateHz)  // Convert Hz to microseconds
        accelSensor?.let {
            sensorManager.registerListener(listener, it, delayMicros)
        }
        gyroSensor?.let {
            sensorManager.registerListener(listener, it, delayMicros)
        }

        awaitClose {
            sensorManager.unregisterListener(listener)
        }
    }

    fun stopSensorCollection() {
        // Cleanup handled by Flow cancellation
    }
}
```

### 3.3 Local Database (Room)

```kotlin
// data/local/entities/SessionEntity.kt
package com.squashanalytics.watch.data.local.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "sessions")
data class SessionEntity(
    @PrimaryKey val sessionId: String,
    val userId: String,
    val sessionType: String,  // "match" or "training"
    val startTime: Long,
    val endTime: Long? = null,
    val durationSeconds: Int? = null,
    val watchPosition: String,  // "playing_hand" or "non_playing_hand"
    val finalScoreMe: Int = 0,
    val finalScoreOpponent: Int = 0,
    val totalGames: Int = 0,
    val syncStatus: String = "pending"  // "pending", "syncing", "synced", "failed"
)

@Entity(tableName = "points")
data class PointEntity(
    @PrimaryKey val pointId: String,
    val sessionId: String,
    val pointNumber: Int,
    val gameNumber: Int,
    val timestamp: Long,
    val scoreMeBefore: Int,
    val scoreOpponentBefore: Int,
    val scoreMeAfter: Int,
    val scoreOpponentAfter: Int,
    val winner: String,  // "me" or "opponent"
    val hrAtPointEnd: Float? = null
)

@Entity(tableName = "heart_rate_data")
data class HRDataEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val sessionId: String,
    val timestamp: Long,
    val heartRate: Float,
    val hrZone: Int,
    val confidence: Float
)

@Entity(tableName = "sensor_data_batches")
data class SensorBatchEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val sessionId: String,
    val startTime: Long,
    val endTime: Long,
    val sampleRateHz: Float,
    val dataBlob: ByteArray  // Compressed sensor data
)
```

```kotlin
// data/local/MatchDatabase.kt
package com.squashanalytics.watch.data.local

import androidx.room.Database
import androidx.room.RoomDatabase

@Database(
    entities = [
        SessionEntity::class,
        PointEntity::class,
        HRDataEntity::class,
        SensorBatchEntity::class
    ],
    version = 1,
    exportSchema = false
)
abstract class MatchDatabase : RoomDatabase() {
    abstract fun sessionDao(): SessionDao
    abstract fun pointDao(): PointDao
    abstract fun hrDataDao(): HRDataDao
    abstract fun sensorBatchDao(): SensorBatchDao
}
```

```kotlin
// data/local/dao/SessionDao.kt
package com.squashanalytics.watch.data.local.dao

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Dao
interface SessionDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertSession(session: SessionEntity)

    @Update
    suspend fun updateSession(session: SessionEntity)

    @Query("SELECT * FROM sessions WHERE sessionId = :sessionId")
    suspend fun getSession(sessionId: String): SessionEntity?

    @Query("SELECT * FROM sessions WHERE syncStatus = 'pending' LIMIT 10")
    suspend fun getPendingSessions(): List<SessionEntity>

    @Query("SELECT * FROM sessions ORDER BY startTime DESC")
    fun getAllSessions(): Flow<List<SessionEntity>>

    @Delete
    suspend fun deleteSession(session: SessionEntity)
}
```

### 3.4 HR Zone Calculator Utility (Port from Python)

```kotlin
// utils/HRZoneCalculator.kt
package com.squashanalytics.watch.utils

/**
 * Port of calculate_hr_zones() from core/metrics_framework.py
 *
 * Zones:
 * - Zone 0: Below 50% max HR
 * - Zone 1: 50-60% max HR (Recovery/Rest)
 * - Zone 2: 60-70% max HR (Active Recovery)
 * - Zone 3: 70-80% max HR (Aerobic/Moderate)
 * - Zone 4: 80-90% max HR (Anaerobic/Hard)
 * - Zone 5: 90-100% max HR (Maximum)
 */
object HRZoneCalculator {
    fun calculateZone(heartRate: Float, maxHR: Float): Int {
        val pct = (heartRate / maxHR) * 100

        return when {
            pct < 50 -> 0
            pct < 60 -> 1
            pct < 70 -> 2
            pct < 80 -> 3
            pct < 90 -> 4
            else -> 5
        }
    }

    /**
     * Estimate max HR if not provided
     * Uses 208 - (0.7 × age) formula (Tanaka formula)
     */
    fun estimateMaxHR(age: Int): Float {
        return 208 - (0.7f * age)
    }

    /**
     * Get zone name
     */
    fun getZoneName(zone: Int): String {
        return when (zone) {
            0 -> "Rest"
            1 -> "Recovery"
            2 -> "Light"
            3 -> "Moderate"
            4 -> "Hard"
            5 -> "Maximum"
            else -> "Unknown"
        }
    }

    /**
     * Get zone color for UI
     */
    fun getZoneColor(zone: Int): androidx.compose.ui.graphics.Color {
        return when (zone) {
            0 -> androidx.compose.ui.graphics.Color.Gray
            1 -> androidx.compose.ui.graphics.Color.Blue
            2 -> androidx.compose.ui.graphics.Color.Green
            3 -> androidx.compose.ui.graphics.Color.Yellow
            4 -> androidx.compose.ui.graphics.Color(0xFFFF8C00)  // Orange
            5 -> androidx.compose.ui.graphics.Color.Red
            else -> androidx.compose.ui.graphics.Color.White
        }
    }
}
```

---

## 4. Main Match Screen UI

```kotlin
// ui/screens/MatchScreen.kt
package com.squashanalytics.watch.ui.screens

import androidx.compose.runtime.*
import androidx.wear.compose.material.*
import androidx.compose.foundation.layout.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel

@Composable
fun MatchScreen(
    viewModel: MatchViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        timeText = {
            TimeText()
        }
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceEvenly
        ) {
            // Heart Rate Display
            HRDisplay(
                heartRate = uiState.currentHR,
                hrZone = uiState.currentZone
            )

            // Score Display
            ScoreDisplay(
                myScore = uiState.myScore,
                opponentScore = uiState.opponentScore,
                gameNumber = uiState.gameNumber
            )

            // Score Buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                // "Me" Button
                Button(
                    onClick = { viewModel.onPointWon("me") },
                    colors = ButtonDefaults.primaryButtonColors()
                ) {
                    Text("Me")
                }

                // "Them" Button
                Button(
                    onClick = { viewModel.onPointWon("opponent") },
                    colors = ButtonDefaults.secondaryButtonColors()
                ) {
                    Text("Them")
                }
            }

            // Match Timer
            Text(
                text = formatDuration(uiState.elapsedSeconds),
                style = MaterialTheme.typography.body1
            )

            // End Match Button (small)
            if (uiState.isMatchInProgress) {
                Button(
                    onClick = { viewModel.endMatch() },
                    modifier = Modifier.size(48.dp),
                    colors = ButtonDefaults.secondaryButtonColors()
                ) {
                    Text("End", style = MaterialTheme.typography.caption2)
                }
            }
        }
    }
}

@Composable
fun HRDisplay(heartRate: Float, hrZone: Int) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "${heartRate.toInt()}",
            style = MaterialTheme.typography.display1,
            color = HRZoneCalculator.getZoneColor(hrZone)
        )
        Text(
            text = "bpm · ${HRZoneCalculator.getZoneName(hrZone)}",
            style = MaterialTheme.typography.caption1
        )
    }
}

@Composable
fun ScoreDisplay(myScore: Int, opponentScore: Int, gameNumber: Int) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Row {
            Text(
                text = "$myScore",
                style = MaterialTheme.typography.display2
            )
            Text(
                text = " - ",
                style = MaterialTheme.typography.display2
            )
            Text(
                text = "$opponentScore",
                style = MaterialTheme.typography.display2
            )
        }
        Text(
            text = "Game $gameNumber",
            style = MaterialTheme.typography.caption1
        )
    }
}

fun formatDuration(seconds: Int): String {
    val mins = seconds / 60
    val secs = seconds % 60
    return "%d:%02d".format(mins, secs)
}
```

---

## 5. ViewModel (State Management)

```kotlin
// viewmodel/MatchViewModel.kt
package com.squashanalytics.watch.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.util.UUID
import javax.inject.Inject

data class MatchUiState(
    val isMatchInProgress: Boolean = false,
    val sessionId: String? = null,
    val myScore: Int = 0,
    val opponentScore: Int = 0,
    val gameNumber: Int = 1,
    val currentHR: Float = 0f,
    val currentZone: Int = 0,
    val elapsedSeconds: Int = 0
)

@HiltViewModel
class MatchViewModel @Inject constructor(
    private val heartRateService: HeartRateService,
    private val sensorService: SensorService,
    private val matchRepository: MatchRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(MatchUiState())
    val uiState: StateFlow<MatchUiState> = _uiState.asStateFlow()

    private var sessionId: String? = null

    init {
        // Start HR monitoring when ViewModel is created
        startHeartRateMonitoring()
    }

    fun startMatch() {
        sessionId = UUID.randomUUID().toString()

        viewModelScope.launch {
            // Create session in database
            matchRepository.createSession(
                sessionId = sessionId!!,
                sessionType = "match",
                startTime = System.currentTimeMillis()
            )

            _uiState.update { it.copy(
                isMatchInProgress = true,
                sessionId = sessionId
            )}

            // Start sensor collection
            startSensorCollection()

            // Start timer
            startMatchTimer()
        }
    }

    fun onPointWon(winner: String) {
        viewModelScope.launch {
            val currentState = _uiState.value

            // Update scores
            val newMyScore = if (winner == "me") currentState.myScore + 1 else currentState.myScore
            val newOppScore = if (winner == "opponent") currentState.opponentScore + 1 else currentState.opponentScore

            // Save point to database
            sessionId?.let {
                matchRepository.recordPoint(
                    sessionId = it,
                    pointNumber = newMyScore + newOppScore,
                    gameNumber = currentState.gameNumber,
                    winner = winner,
                    scoreMeBefore = currentState.myScore,
                    scoreOpponentBefore = currentState.opponentScore,
                    scoreMeAfter = newMyScore,
                    scoreOpponentAfter = newOppScore,
                    hrAtPointEnd = currentState.currentHR
                )
            }

            // Check if game is over (first to 11, win by 2)
            val gameOver = (newMyScore >= 11 || newOppScore >= 11) &&
                    Math.abs(newMyScore - newOppScore) >= 2

            if (gameOver) {
                // Start new game
                _uiState.update { it.copy(
                    myScore = 0,
                    opponentScore = 0,
                    gameNumber = it.gameNumber + 1
                )}
            } else {
                _uiState.update { it.copy(
                    myScore = newMyScore,
                    opponentScore = newOppScore
                )}
            }
        }
    }

    fun endMatch() {
        viewModelScope.launch {
            sessionId?.let {
                matchRepository.endSession(
                    sessionId = it,
                    endTime = System.currentTimeMillis(),
                    finalScoreMe = _uiState.value.myScore,
                    finalScoreOpponent = _uiState.value.opponentScore
                )

                // Trigger sync to backend
                matchRepository.syncSession(it)
            }

            _uiState.update { MatchUiState() }  // Reset state
        }
    }

    private fun startHeartRateMonitoring() {
        viewModelScope.launch {
            heartRateService.startHeartRateMonitoring()
                .collect { hrData ->
                    // Calculate HR zone
                    val maxHR = 185f  // TODO: Get from user profile
                    val zone = HRZoneCalculator.calculateZone(hrData.heartRate, maxHR)

                    _uiState.update { it.copy(
                        currentHR = hrData.heartRate,
                        currentZone = zone
                    )}

                    // Save to database if match in progress
                    if (_uiState.value.isMatchInProgress) {
                        sessionId?.let { sid ->
                            matchRepository.saveHRData(
                                sessionId = sid,
                                timestamp = hrData.timestamp,
                                heartRate = hrData.heartRate,
                                hrZone = zone
                            )
                        }
                    }
                }
        }
    }

    private fun startSensorCollection() {
        viewModelScope.launch {
            sensorService.startSensorCollection(sampleRateHz = 10)
                .collect { reading ->
                    // Batch and save sensor data
                    sessionId?.let { sid ->
                        matchRepository.saveSensorData(sid, reading)
                    }
                }
        }
    }

    private fun startMatchTimer() {
        // TODO: Implement timer using Flow.interval
    }
}
```

---

## 6. Sync Service (Background Upload)

```kotlin
// services/SyncService.kt
package com.squashanalytics.watch.services

import android.content.Context
import androidx.work.*
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject

class SyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        // Fetch pending sessions from database
        // Upload to backend API
        // Mark as synced

        return try {
            // Implementation here
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Schedule periodic sync
fun scheduleSync(context: Context) {
    val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .setRequiresBatteryNotLow(true)
                .build()
        )
        .build()

    WorkManager.getInstance(context).enqueueUniquePeriodicWork(
        "sync_sessions",
        ExistingPeriodicWorkPolicy.KEEP,
        syncRequest
    )
}
```

---

## 7. Permissions (AndroidManifest.xml)

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Required permissions -->
    <uses-permission android:name="android.permission.BODY_SENSORS" />
    <uses-permission android:name="android.permission.ACTIVITY_RECOGNITION" />
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    <uses-permission android:name="android.permission.VIBRATE" />

    <!-- Wear OS specific -->
    <uses-feature android:name="android.hardware.type.watch" />

    <application
        android:name=".SquashWatchApp"
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@android:style/Theme.DeviceDefault">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@android:style/Theme.DeviceDefault">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Health Services -->
        <uses-library
            android:name="androidx.health.services.client"
            android:required="false" />

    </application>
</manifest>
```

---

## 8. Next Steps

1. ✅ Wear OS structure defined
2. Implement HomeScreen and navigation
3. Add settings screen (user profile, max HR, watch hand)
4. Implement FIT file export (for offline backup)
5. Add haptic feedback for button presses
6. Implement voice commands ("Point for me")

See next document: `integration_architecture.md` for complete system integration strategy.
