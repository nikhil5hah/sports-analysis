# Squash Analytics API Documentation

Base URL: `http://localhost:8000` (local) or your deployed URL

Interactive documentation available at: `http://localhost:8000/docs`

## Authentication

All endpoints except `/api/auth/register` and `/api/auth/login` require authentication.

**Authentication Header:**
```
Authorization: Bearer <jwt_token>
```

---

## Authentication Endpoints

### Register User
Create a new user account.

**Endpoint:** `POST /api/auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### Login
Authenticate and receive JWT token.

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

---

### Get Current User
Get authenticated user's information.

**Endpoint:** `GET /api/auth/me`

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "max_heart_rate": 185,
  "age": 30,
  "skill_level": "intermediate",
  "watch_hand": "left"
}
```

---

## Session Management

### Create Session
Start a new training session or match.

**Endpoint:** `POST /api/sessions`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "session_type": "match",
  "sport": "squash",
  "scoring_system": "pars",
  "start_time": "2024-01-15T18:00:00Z",
  "metadata": {
    "opponent_name": "Jane Smith",
    "court_number": 3,
    "location": "City Sports Club"
  }
}
```

**Response:** `201 Created`
```json
{
  "session_id": "660e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_type": "match",
  "sport": "squash",
  "scoring_system": "pars",
  "start_time": "2024-01-15T18:00:00Z",
  "end_time": null,
  "duration_seconds": null,
  "sync_status": "pending",
  "created_at": "2024-01-15T18:00:00Z"
}
```

---

### List Sessions
Get all sessions for the authenticated user.

**Endpoint:** `GET /api/sessions`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `sport` (optional): Filter by sport (e.g., "squash")
- `session_type` (optional): Filter by type ("match" or "training")
- `status` (optional): Filter by status ("active", "completed")

**Response:** `200 OK`
```json
[
  {
    "session_id": "660e8400-e29b-41d4-a716-446655440000",
    "session_type": "match",
    "sport": "squash",
    "start_time": "2024-01-15T18:00:00Z",
    "end_time": "2024-01-15T19:30:00Z",
    "duration_seconds": 5400,
    "final_score_me": 11,
    "final_score_opponent": 8,
    "avg_hr": 142.5,
    "max_hr": 178.0
  }
]
```

---

### Get Session Details
Get detailed information about a specific session.

**Endpoint:** `GET /api/sessions/{session_id}`

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "session_id": "660e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_type": "match",
  "sport": "squash",
  "scoring_system": "pars",
  "start_time": "2024-01-15T18:00:00Z",
  "end_time": "2024-01-15T19:30:00Z",
  "duration_seconds": 5400,
  "final_score_me": 11,
  "final_score_opponent": 8,
  "total_games": 3,
  "total_points": 33,
  "total_rallies": 30,
  "total_lets": 3,
  "avg_hr": 142.5,
  "max_hr": 178.0,
  "metadata": {
    "opponent_name": "Jane Smith",
    "court_number": 3
  }
}
```

---

### Update Session
Update session details (e.g., end time, final score).

**Endpoint:** `PUT /api/sessions/{session_id}`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "end_time": "2024-01-15T19:30:00Z",
  "final_score_me": 11,
  "final_score_opponent": 8,
  "sync_status": "completed"
}
```

**Response:** `200 OK`
```json
{
  "session_id": "660e8400-e29b-41d4-a716-446655440000",
  "end_time": "2024-01-15T19:30:00Z",
  "duration_seconds": 5400,
  "final_score_me": 11,
  "final_score_opponent": 8
}
```

---

### Delete Session
Delete a session and all associated data.

**Endpoint:** `DELETE /api/sessions/{session_id}`

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "message": "Session deleted successfully"
}
```

---

## Sensor Data Endpoints

### Upload Heart Rate Data
Upload heart rate readings for a session.

**Endpoint:** `POST /api/sessions/{session_id}/heart-rate`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "data_points": [
    {
      "timestamp": "2024-01-15T18:05:00Z",
      "heart_rate": 145.0,
      "hr_zone": 3,
      "confidence": 0.95
    },
    {
      "timestamp": "2024-01-15T18:05:05Z",
      "heart_rate": 147.0,
      "hr_zone": 3,
      "confidence": 0.98
    }
  ]
}
```

**Response:** `201 Created`
```json
{
  "message": "Heart rate data uploaded successfully",
  "records_created": 2
}
```

---

### Upload GPS/Location Data
Upload GPS coordinates and movement data.

**Endpoint:** `POST /api/sessions/{session_id}/gps`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "data_points": [
    {
      "timestamp": "2024-01-15T18:05:00Z",
      "latitude": 37.7749,
      "longitude": -122.4194,
      "altitude": 50.0,
      "speed": 1.5,
      "bearing": 180.0,
      "accuracy": 5.0,
      "vertical_accuracy": 3.0
    }
  ]
}
```

**Response:** `201 Created`
```json
{
  "message": "GPS data uploaded successfully",
  "records_created": 1
}
```

---

### Upload SpO2 Data
Upload blood oxygen saturation readings.

**Endpoint:** `POST /api/sessions/{session_id}/spo2`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "data_points": [
    {
      "timestamp": "2024-01-15T18:05:00Z",
      "spo2_percentage": 97.5,
      "confidence": 0.92,
      "measurement_quality": 0.88
    }
  ]
}
```

**Response:** `201 Created`
```json
{
  "message": "SpO2 data uploaded successfully",
  "records_created": 1
}
```

---

### Upload Temperature Data
Upload skin temperature measurements.

**Endpoint:** `POST /api/sessions/{session_id}/temperature`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "data_points": [
    {
      "timestamp": "2024-01-15T18:05:00Z",
      "temperature_celsius": 34.5,
      "sensor_location": 0.5,
      "confidence": 0.90
    }
  ]
}
```

**Response:** `201 Created`
```json
{
  "message": "Temperature data uploaded successfully",
  "records_created": 1
}
```

---

### Upload Activity Data
Upload activity metrics (steps, calories, distance).

**Endpoint:** `POST /api/sessions/{session_id}/activity`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "data_points": [
    {
      "timestamp": "2024-01-15T18:05:00Z",
      "steps": 150,
      "calories": 25.5,
      "distance": 120.0,
      "active_minutes": 5,
      "floors_climbed": 0,
      "intensity_level": 3
    }
  ]
}
```

**Response:** `201 Created`
```json
{
  "message": "Activity data uploaded successfully",
  "records_created": 1
}
```

---

### Upload Sensor Batch Data
Upload accelerometer/gyroscope data in batches.

**Endpoint:** `POST /api/sessions/{session_id}/sensor-data`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "start_time": "2024-01-15T18:05:00Z",
  "end_time": "2024-01-15T18:06:00Z",
  "sample_rate_hz": 100.0,
  "data_blob": "<base64_encoded_sensor_data>",
  "compression_type": "gzip",
  "data_points_count": 6000
}
```

**Response:** `201 Created`
```json
{
  "message": "Sensor batch uploaded successfully",
  "batch_id": "770e8400-e29b-41d4-a716-446655440000"
}
```

---

## Analytics Endpoints

### Record Match Point
Record a point scored during a match.

**Endpoint:** `POST /api/sessions/{session_id}/points`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "game_number": 1,
  "score_me_before": 5,
  "score_opponent_before": 4,
  "score_me_after": 6,
  "score_opponent_after": 4,
  "winner": "me",
  "hr_at_point_end": 165.0,
  "is_let": false,
  "notes": "Great rally, dropshot winner"
}
```

**Response:** `201 Created`
```json
{
  "point_id": "880e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440000",
  "point_number": 10,
  "game_number": 1,
  "timestamp": "2024-01-15T18:15:32Z",
  "score_me_after": 6,
  "score_opponent_after": 4,
  "winner": "me",
  "hr_at_point_end": 165.0
}
```

---

### Generate Insights
Generate analytics and insights for a session.

**Endpoint:** `POST /api/sessions/{session_id}/insights`

**Headers:** `Authorization: Bearer <token>`

**Response:** `201 Created`
```json
{
  "insight_id": "990e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440000",
  "generated_at": "2024-01-15T19:35:00Z",
  "insight_type": "session_summary",
  "metrics": {
    "avg_heart_rate": 142.5,
    "max_heart_rate": 178.0,
    "hr_zone_distribution": {
      "zone_1": 10,
      "zone_2": 20,
      "zone_3": 45,
      "zone_4": 20,
      "zone_5": 5
    },
    "total_distance": 2500.0,
    "total_calories": 450.0,
    "average_rally_length": 15.2
  },
  "hr_score_correlation": {
    "correlation_coefficient": 0.65,
    "points_won_high_hr": 12,
    "points_lost_high_hr": 8
  },
  "recommendations": [
    "Your heart rate was highest in the third game. Consider pacing yourself better.",
    "You won 60% of points when HR was above 160bpm - your fitness is a strength!"
  ]
}
```

---

### Get Session Insights
Retrieve generated insights for a session.

**Endpoint:** `GET /api/sessions/{session_id}/insights`

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "insight_id": "990e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440000",
  "generated_at": "2024-01-15T19:35:00Z",
  "metrics": { ... },
  "recommendations": [ ... ]
}
```

---

## Health Check

### Health Check
Check API health status.

**Endpoint:** `GET /health`

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request body"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 404 Not Found
```json
{
  "detail": "Session not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email address",
      "type": "value_error.email"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. When deployed to production, consider adding rate limits:
- Authentication endpoints: 5 requests per minute
- Data upload endpoints: 60 requests per minute
- Read endpoints: 120 requests per minute

---

## Best Practices

### Bulk Uploads
Always batch sensor data uploads to reduce API calls:
- **Good:** Upload 30 heart rate readings every 30 seconds
- **Bad:** Upload 1 heart rate reading every second

### Error Handling
Always handle network errors and retry failed uploads:
```javascript
async function uploadWithRetry(data, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await api.uploadHeartRate(data);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(2 ** i * 1000); // Exponential backoff
    }
  }
}
```

### Token Refresh
JWT tokens expire after 30 days. Store the token securely and handle 401 errors by redirecting to login.

---

## Examples

### Complete Session Flow

```bash
# 1. Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'

# 2. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Save the token from response
TOKEN="your_jwt_token_here"

# 3. Create session
curl -X POST http://localhost:8000/api/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"session_type":"match","sport":"squash","start_time":"2024-01-15T18:00:00Z"}'

# Save session_id from response
SESSION_ID="session_uuid_here"

# 4. Upload heart rate data
curl -X POST http://localhost:8000/api/sessions/$SESSION_ID/heart-rate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data_points":[{"timestamp":"2024-01-15T18:05:00Z","heart_rate":145}]}'

# 5. End session
curl -X PUT http://localhost:8000/api/sessions/$SESSION_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"end_time":"2024-01-15T19:00:00Z"}'

# 6. Generate insights
curl -X POST http://localhost:8000/api/sessions/$SESSION_ID/insights \
  -H "Authorization: Bearer $TOKEN"

# 7. Get insights
curl -X GET http://localhost:8000/api/sessions/$SESSION_ID/insights \
  -H "Authorization: Bearer $TOKEN"
```

---

## Interactive Documentation

For interactive API testing, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These interfaces allow you to:
- Try out all endpoints
- See request/response schemas
- Test authentication
- View all available parameters
