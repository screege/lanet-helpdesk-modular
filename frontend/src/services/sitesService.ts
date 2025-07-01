import { apiService } from './api';

export interface Site {
  site_id: string;
  client_id: string;
  name: string;
  address: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  latitude?: number;
  longitude?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  client_name?: string;
  assigned_users?: number;
  total_tickets?: number;
}

export interface SiteUser {
  user_id: string;
  name: string;
  email: string;
  role: string;
  phone?: string;
  assigned_at: string;
  assigned_by?: string;
  assigned_by_name?: string;
}

export interface CreateSiteData {
  client_id: string;
  name: string;
  address: string;
  city: string;
  state: string;
  country?: string;
  postal_code: string;
  latitude?: number;
  longitude?: number;
}

export interface UpdateSiteData {
  name?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  latitude?: number;
  longitude?: number;
}

class SitesService {
  async getAllSites(params?: {
    client_id?: string;
    page?: number;
    per_page?: number;
  }) {
    try {
      const queryParams = new URLSearchParams();
      if (params?.client_id) queryParams.append('client_id', params.client_id);
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.per_page) queryParams.append('per_page', params.per_page.toString());

      const url = queryParams.toString() ? `/sites?${queryParams}` : '/sites';

      const response = await apiService.get(url);
      return response;
    } catch (error: any) {
      console.error('Error fetching sites:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch sites');
    }
  }

  // Alias for getAllSites for compatibility
  async getSites(params?: {
    client_id?: string;
    page?: number;
    per_page?: number;
  }) {
    return this.getAllSites(params);
  }

  async getSiteById(siteId: string) {
    try {
      const response = await apiService.get(`/sites/${siteId}`);
      return response;
    } catch (error: any) {
      console.error('Error fetching site:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch site');
    }
  }

  async createSite(siteData: CreateSiteData) {
    try {
      const response = await apiService.post('/sites', siteData);
      return response;
    } catch (error: any) {
      console.error('Error creating site:', error);
      throw new Error(error.response?.data?.message || 'Failed to create site');
    }
  }

  async updateSite(siteId: string, siteData: UpdateSiteData) {
    try {
      const response = await apiService.put(`/sites/${siteId}`, siteData);
      return response;
    } catch (error: any) {
      console.error('Error updating site:', error);
      throw new Error(error.response?.data?.message || 'Failed to update site');
    }
  }

  async deleteSite(siteId: string) {
    try {
      const response = await apiService.delete(`/sites/${siteId}`);
      return response;
    } catch (error: any) {
      console.error('Error deleting site:', error);
      throw new Error(error.response?.data?.message || 'Failed to delete site');
    }
  }

  async getSiteUsers(siteId: string) {
    try {
      const response = await apiService.get(`/sites/${siteId}/users`);
      return response;
    } catch (error: any) {
      console.error('Error fetching site users:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch site users');
    }
  }

  async assignUserToSite(siteId: string, userId: string) {
    try {
      const response = await apiService.post(`/sites/${siteId}/assign-user`, { user_id: userId });
      return response;
    } catch (error: any) {
      console.error('Error assigning user to site:', error);
      throw new Error(error.response?.data?.message || 'Failed to assign user to site');
    }
  }

  async unassignUserFromSite(siteId: string, userId: string) {
    try {
      const response = await apiService.delete(`/sites/${siteId}/unassign-user/${userId}`);
      return response;
    } catch (error: any) {
      console.error('Error unassigning user from site:', error);
      throw new Error(error.response?.data?.message || 'Failed to unassign user from site');
    }
  }
}

export const sitesService = new SitesService();
