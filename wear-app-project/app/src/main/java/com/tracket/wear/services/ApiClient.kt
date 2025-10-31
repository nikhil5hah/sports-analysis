package com.tracket.wear.services

import android.content.Context
import android.content.SharedPreferences
import com.google.gson.Gson
import com.google.gson.GsonBuilder
import com.tracket.wear.models.*
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*

/**
 * Retrofit API Service interface
 */
interface TRacketApiService {
    @GET("/api/sessions")
    suspend fun getSessions(): List<Session>

    @GET("/api/sessions/{session_id}")
    suspend fun getSession(@Path("session_id") sessionId: String): Session

    @GET("/api/sessions/{session_id}/points")
    suspend fun getPoints(@Path("session_id") sessionId: String): List<PointData>

    @POST("/api/sessions/{session_id}/points")
    suspend fun recordPoint(
        @Path("session_id") sessionId: String,
        @Body pointData: PointData
    ): PointResponse

    @POST("/api/sessions/{session_id}/heart-rate")
    suspend fun uploadHeartRate(
        @Path("session_id") sessionId: String,
        @Body heartRateUpload: HeartRateUpload
    ): HeartRateResponse

    @PATCH("/api/sessions/{session_id}")
    suspend fun updateSession(
        @Path("session_id") sessionId: String,
        @Body updateData: Map<String, Any?>
    ): Session

    @GET("/health")
    suspend fun checkHealth(): Response<Unit>
}

/**
 * API Client singleton for managing backend communication
 */
class ApiClient private constructor(context: Context) {
    private val baseUrl = "http://192.168.1.35:8000"
    private val prefs: SharedPreferences = context.getSharedPreferences("tracket_prefs", Context.MODE_PRIVATE)

    private val gson: Gson = GsonBuilder()
        .setLenient()
        .create()

    // Auth interceptor to add token to requests
    private val authInterceptor = Interceptor { chain ->
        val token = getAuthToken()
        val request = if (token != null) {
            chain.request().newBuilder()
                .addHeader("Authorization", "Bearer $token")
                .build()
        } else {
            chain.request()
        }
        chain.proceed(request)
    }

    // Logging interceptor for debugging
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(authInterceptor)
        .addInterceptor(loggingInterceptor)
        .build()

    private val retrofit = Retrofit.Builder()
        .baseUrl(baseUrl)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create(gson))
        .build()

    val api: TRacketApiService = retrofit.create(TRacketApiService::class.java)

    // Auth token management
    fun saveAuthToken(token: String) {
        prefs.edit().putString("auth_token", token).apply()
    }

    fun getAuthToken(): String? {
        return prefs.getString("auth_token", null)
    }

    fun clearAuthToken() {
        prefs.edit().remove("auth_token").apply()
    }

    fun hasAuthToken(): Boolean {
        return getAuthToken() != null
    }

    companion object {
        @Volatile
        private var instance: ApiClient? = null

        fun getInstance(context: Context): ApiClient {
            return instance ?: synchronized(this) {
                instance ?: ApiClient(context.applicationContext).also { instance = it }
            }
        }
    }
}

/**
 * Extension functions for easier API calls with error handling
 */
suspend fun <T> safeApiCall(apiCall: suspend () -> T): Result<T> {
    return try {
        Result.success(apiCall())
    } catch (e: Exception) {
        Result.failure(e)
    }
}

/**
 * Result wrapper for API responses
 */
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val message: String, val exception: Exception? = null) : ApiResult<Nothing>()
    object Loading : ApiResult<Nothing>()
}
