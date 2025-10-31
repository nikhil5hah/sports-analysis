import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Backend API base URL - update this to your Mac's local IP
const API_BASE_URL = 'http://192.168.1.35:8000';

// Storage keys
const TOKEN_KEY = '@squash_analytics_token';
const USER_KEY = '@squash_analytics_user';

class ApiClient {
  constructor() {
    this.axios = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.axios.interceptors.request.use(
      async (config) => {
        const token = await this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid, clear storage
          await this.clearAuth();
        }
        return Promise.reject(error);
      }
    );
  }

  // Token management
  async getToken() {
    try {
      return await AsyncStorage.getItem(TOKEN_KEY);
    } catch (error) {
      return null;
    }
  }

  async setToken(token) {
    try {
      await AsyncStorage.setItem(TOKEN_KEY, token);
    } catch (error) {
      // Error setting token - silently fail
    }
  }

  async getUser() {
    try {
      const userJson = await AsyncStorage.getItem(USER_KEY);
      return userJson ? JSON.parse(userJson) : null;
    } catch (error) {
      return null;
    }
  }

  async setUser(user) {
    try {
      await AsyncStorage.setItem(USER_KEY, JSON.stringify(user));
    } catch (error) {
      // Error setting user - silently fail
    }
  }

  async clearAuth() {
    try {
      await AsyncStorage.multiRemove([TOKEN_KEY, USER_KEY]);
    } catch (error) {
      // Error clearing auth - silently fail
    }
  }

  // Auth endpoints
  async register(email, password, name) {
    try {
      const response = await this.axios.post('/api/auth/register', {
        email,
        password,
        full_name: name,
      });

      // After registration, log in automatically
      if (response.data) {
        return await this.login(email, password);
      }

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async login(email, password) {
    try {
      // Backend expects JSON with email and password
      const response = await this.axios.post('/api/auth/login', {
        email,
        password,
      });

      const { access_token } = response.data;

      // Save token
      await this.setToken(access_token);

      // Fetch and save user info
      const user = await this.getCurrentUser();

      return { token: access_token, user };
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getCurrentUser() {
    try {
      const response = await this.axios.get('/api/auth/me');
      const user = response.data;
      await this.setUser(user);
      return user;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async logout() {
    await this.clearAuth();
  }

  async checkAuth() {
    const token = await this.getToken();
    const user = await this.getUser();

    if (token && user) {
      // Verify token is still valid by fetching current user
      try {
        await this.getCurrentUser();
        return { isAuthenticated: true, user };
      } catch (error) {
        await this.clearAuth();
        return { isAuthenticated: false, user: null };
      }
    }

    return { isAuthenticated: false, user: null };
  }

  // Session endpoints (to be used later)
  async createSession(sessionData) {
    try {
      const response = await this.axios.post('/api/sessions', sessionData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getSessions() {
    try {
      const response = await this.axios.get('/api/sessions');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getSession(sessionId) {
    try {
      const response = await this.axios.get(`/api/sessions/${sessionId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateSession(sessionId, updateData) {
    try {
      const response = await this.axios.patch(`/api/sessions/${sessionId}`, updateData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async deleteSession(sessionId) {
    try {
      const response = await this.axios.delete(`/api/sessions/${sessionId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async uploadHeartRate(sessionId, dataPoints) {
    try {
      const response = await this.axios.post(
        `/api/sessions/${sessionId}/heart-rate`,
        { data_points: dataPoints }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Points endpoints
  async recordPoint(sessionId, pointData) {
    try {
      const response = await this.axios.post(
        `/api/sessions/${sessionId}/points`,
        pointData
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getPoints(sessionId) {
    try {
      const response = await this.axios.get(`/api/sessions/${sessionId}/points`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async undoLastPoint(sessionId) {
    try {
      await this.axios.delete(`/api/sessions/${sessionId}/points/last`);
      return true;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Error handling
  handleError(error) {
    if (error.response) {
      // Server responded with error
      const data = error.response.data;
      let message = 'Server error';

      // Extract error message from various response formats
      if (typeof data === 'string') {
        message = data;
      } else if (data?.detail) {
        // FastAPI validation errors return detail as array or object
        if (Array.isArray(data.detail)) {
          message = data.detail.map(err => err.msg || JSON.stringify(err)).join(', ');
        } else if (typeof data.detail === 'object') {
          message = JSON.stringify(data.detail);
        } else {
          message = String(data.detail);
        }
      } else if (data?.message) {
        message = typeof data.message === 'object' ? JSON.stringify(data.message) : String(data.message);
      } else if (data) {
        message = JSON.stringify(data);
      }

      return new Error(message);
    } else if (error.request) {
      // Request made but no response
      return new Error('Cannot connect to server. Please check your connection.');
    } else {
      // Something else happened
      return new Error(error.message || 'An unexpected error occurred');
    }
  }
}

// Export singleton instance
export default new ApiClient();
