import axios, {AxiosInstance, AxiosError, InternalAxiosRequestConfig} from 'axios';
import {API_URL} from '../config';
import {getToken} from './keychain';

// Create axios instance with base configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Ensure HTTPS in production
    if (config.url && !config.url.startsWith('https://') && !__DEV__) {
      console.error('HTTPS required in production');
      throw new Error('HTTPS required for API requests');
    }

    // Add authorization token
    const token = await getToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Log request (sanitized)
    if (__DEV__) {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    }

    return config;
  },
  (error: AxiosError) => {
    console.error('Request interceptor error:', error.message);
    return Promise.reject(error);
  },
);

// Response interceptor - Handle errors and retries
let retryCount = 0;
const MAX_RETRIES = 3;

apiClient.interceptors.response.use(
  response => {
    // Reset retry count on success
    retryCount = 0;
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // Handle 401 - Unauthorized (trigger logout)
    if (error.response?.status === 401) {
      console.error('Unauthorized - token expired or invalid');
      // TODO: Trigger logout action from auth store
      return Promise.reject(error);
    }

    // Handle network errors with retry
    if (!error.response && retryCount < MAX_RETRIES && !originalRequest._retry) {
      originalRequest._retry = true;
      retryCount++;

      // Exponential backoff: 2^retryCount seconds
      const delay = Math.pow(2, retryCount) * 1000;
      console.log(`Retrying request (${retryCount}/${MAX_RETRIES}) after ${delay}ms`);

      await new Promise(resolve => setTimeout(resolve, delay));
      return apiClient(originalRequest);
    }

    // Log error (sanitized - no sensitive data)
    if (__DEV__) {
      console.error('API Error:', {
        method: error.config?.method,
        url: error.config?.url,
        status: error.response?.status,
        message: error.message,
      });
    }

    // Return user-friendly error message
    if (!error.response) {
      return Promise.reject(
        new Error('Unable to connect. Please check your internet connection.'),
      );
    }

    return Promise.reject(error);
  },
);

export default apiClient;
