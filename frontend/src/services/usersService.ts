import { apiService } from './api';

export interface User {
  user_id: string;
  client_id?: string;
  name: string;
  email: string;
  role: string;
  phone?: string;
  is_active: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
  client_name?: string;
}

export interface CreateSolicitanteData {
  client_id: string;
  name: string;
  email: string;
  password: string;
  phone?: string;
  site_ids: string[];
}

export interface CreateTechnicianData {
  name: string;
  email: string;
  password: string;
  phone?: string;
}

export interface CreateUserData {
  name: string;
  email: string;
  password: string;
  role: string;
  phone?: string;
  client_id?: string;
}

export interface UpdateUserData {
  name?: string;
  email?: string;
  role?: string;
  phone?: string;
  client_id?: string;
  is_active?: boolean;
  password?: string;
}

export interface UserRole {
  value: string;
  label: string;
  description: string;
}

class UsersService {
  async getAllUsers(params?: {
    page?: number;
    per_page?: number;
    role?: string;
    client_id?: string;
    search?: string;
  }) {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.per_page) queryParams.append('per_page', params.per_page.toString());
      if (params?.role) queryParams.append('role', params.role);
      if (params?.client_id) queryParams.append('client_id', params.client_id);
      if (params?.search) queryParams.append('search', params.search);

      const url = queryParams.toString() ? `/users?${queryParams}` : '/users';

      const response = await apiService.get(url);
      return response;
    } catch (error: any) {
      console.error('Error fetching users:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch users');
    }
  }

  async getUserById(userId: string) {
    try {
      const response = await apiService.get(`/users/${userId}`);
      return response;
    } catch (error: any) {
      console.error('Error fetching user:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch user');
    }
  }

  async getUsersByClient(clientId: string) {
    try {
      const response = await apiService.get(`/users/client/${clientId}`);
      return response;
    } catch (error: any) {
      console.error('Error fetching client users:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch client users');
    }
  }

  async createSolicitante(userData: CreateSolicitanteData, siteIds: string[] = []) {
    try {
      const requestData = {
        ...userData,
        site_ids: siteIds
      };
      const response = await apiService.post('/users/solicitante', requestData);
      return response;
    } catch (error: any) {
      console.error('Error creating solicitante:', error);
      throw new Error(error.response?.data?.message || 'Failed to create solicitante');
    }
  }

  async getUsersByClient(clientId: string, role?: string) {
    try {
      const params = new URLSearchParams();
      if (role) params.append('role', role);

      const url = `/users/by-client/${clientId}${params.toString() ? `?${params}` : ''}`;
      const response = await apiService.get(url);
      return response;
    } catch (error: any) {
      console.error('Error getting users by client:', error);
      throw new Error(error.response?.data?.message || 'Failed to get users by client');
    }
  }

  async assignUserToSites(userId: string, siteIds: string[]) {
    try {
      const response = await apiService.post(`/users/${userId}/assign-sites`, {
        site_ids: siteIds
      });
      return response;
    } catch (error: any) {
      console.error('Error assigning user to sites:', error);
      throw new Error(error.response?.data?.message || 'Failed to assign user to sites');
    }
  }

  async createTechnician(userData: CreateTechnicianData) {
    try {
      const response = await apiService.post('/users/technician', userData);
      return response;
    } catch (error: any) {
      console.error('Error creating technician:', error);
      throw new Error(error.response?.data?.message || 'Failed to create technician');
    }
  }

  async createUser(userData: CreateUserData) {
    try {
      const response = await apiService.post('/users', userData);
      return response;
    } catch (error: any) {
      console.error('Error creating user:', error);
      throw new Error(error.response?.data?.message || 'Failed to create user');
    }
  }

  async updateUser(userId: string, userData: UpdateUserData) {
    try {
      const response = await apiService.put(`/users/${userId}`, userData);
      return response;
    } catch (error: any) {
      console.error('Error updating user:', error);
      throw new Error(error.response?.data?.message || 'Failed to update user');
    }
  }

  async deleteUser(userId: string) {
    try {
      const response = await apiService.delete(`/users/${userId}`);
      return response;
    } catch (error: any) {
      console.error('Error deleting user:', error);
      throw new Error(error.response?.data?.message || 'Failed to delete user');
    }
  }

  async getUserRoles() {
    try {
      const response = await apiService.get('/users/roles');
      return response;
    } catch (error: any) {
      console.error('Error fetching user roles:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch user roles');
    }
  }

  async getUserStats() {
    try {
      const response = await apiService.get('/users/stats');
      return response;
    } catch (error: any) {
      console.error('Error fetching user stats:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch user stats');
    }
  }

  async getUserSites(userId: string) {
    try {
      const response = await apiService.get(`/users/${userId}/sites`);
      return response;
    } catch (error: any) {
      console.error('Error fetching user sites:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch user sites');
    }
  }

  async assignUserToSites(userId: string, siteIds: string[]) {
    try {
      const response = await apiService.post(`/users/${userId}/assign-sites`, { site_ids: siteIds });
      return response;
    } catch (error: any) {
      console.error('Error assigning user to sites:', error);
      throw new Error(error.response?.data?.message || 'Failed to assign user to sites');
    }
  }
}

export const usersService = new UsersService();
