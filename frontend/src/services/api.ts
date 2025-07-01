import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { ApiResponse, AuthTokens, LoginCredentials, User } from '@/types';

class ApiService {
  private api: AxiosInstance;
  private baseURL = '/api'; // Use relative URL to leverage Vite proxy

  constructor() {
    this.api = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true,
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = this.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle token refresh
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = this.getRefreshToken();
            if (refreshToken) {
              const response = await this.refreshToken();
              if (response.success && response.data) {
                this.setTokens(response.data);
                originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
                return this.api(originalRequest);
              }
            }
          } catch (refreshError) {
            this.clearTokens();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Token management
  private getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  private setTokens(tokens: AuthTokens): void {
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
  }

  private clearTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  // Auth endpoints
  async login(credentials: LoginCredentials): Promise<ApiResponse<{ user: User; access_token: string; refresh_token: string }>> {
    try {
      const response: AxiosResponse<ApiResponse<{ user: User; access_token: string; refresh_token: string }>> = 
        await this.api.post('/auth/login', credentials);
      
      if (response.data.success && response.data.data) {
        this.setTokens({
          access_token: response.data.data.access_token,
          refresh_token: response.data.data.refresh_token,
        });
        localStorage.setItem('user', JSON.stringify(response.data.data.user));
      }
      
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Login failed',
      };
    }
  }

  async logout(): Promise<ApiResponse> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.post('/auth/logout');
      this.clearTokens();
      return response.data;
    } catch (error: any) {
      this.clearTokens();
      return {
        success: false,
        error: error.response?.data?.error || 'Logout failed',
      };
    }
  }

  async refreshToken(): Promise<ApiResponse<AuthTokens>> {
    try {
      const refreshToken = this.getRefreshToken();
      const response: AxiosResponse<ApiResponse<AuthTokens>> = await axios.post(
        `${this.baseURL}/auth/refresh`,
        {},
        {
          headers: {
            Authorization: `Bearer ${refreshToken}`,
          },
        }
      );
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Token refresh failed',
      };
    }
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    try {
      const response: AxiosResponse<ApiResponse<User>> = await this.api.get('/auth/me');
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to get user info',
      };
    }
  }

  async forgotPassword(email: string): Promise<ApiResponse> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.post('/auth/forgot-password', { email });
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Password reset request failed',
      };
    }
  }

  async resetPassword(token: string, password: string): Promise<ApiResponse> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.post('/auth/reset-password', { token, password });
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Password reset failed',
      };
    }
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<ApiResponse> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Password change failed',
      };
    }
  }

  // Health check
  async healthCheck(): Promise<ApiResponse> {
    try {
      const response: AxiosResponse<ApiResponse> = await axios.get(`${this.baseURL.replace('/api', '')}/health`);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: 'Health check failed',
      };
    }
  }

  // Generic CRUD methods
  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<ApiResponse<T>> = await this.api.get(endpoint);
      return response.data;
    } catch (error: any) {
      console.error(`API GET Error for ${endpoint}:`, error.response?.data || error.message);
      throw error; // Throw the original error for proper handling
    }
  }

  async post<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<ApiResponse<T>> = await this.api.post(endpoint, data);
      return response.data;
    } catch (error: any) {
      console.error(`API POST Error for ${endpoint}:`, error.response?.data || error.message);
      throw error; // Throw the original error for proper handling
    }
  }

  async put<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<ApiResponse<T>> = await this.api.put(endpoint, data);
      return response.data;
    } catch (error: any) {
      console.error(`API PUT Error for ${endpoint}:`, error.response?.data || error.message);
      throw error; // Throw the original error for proper handling
    }
  }

  async patch<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<ApiResponse<T>> = await this.api.patch(endpoint, data);
      return response.data;
    } catch (error: any) {
      console.error(`API PATCH Error for ${endpoint}:`, error.response?.data || error.message);
      throw error; // Throw the original error for proper handling
    }
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<ApiResponse<T>> = await this.api.delete(endpoint);
      return response.data;
    } catch (error: any) {
      console.error(`API DELETE Error for ${endpoint}:`, error.response?.data || error.message);
      throw error; // Throw the original error for proper handling
    }
  }
}

export const apiService = new ApiService();
export default apiService;
