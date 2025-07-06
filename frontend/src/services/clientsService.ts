import { apiService } from './api';

export interface Client {
  client_id: string;
  name: string;
  email: string;
  rfc?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  total_users?: number;
  total_sites?: number;
  total_tickets?: number;
  open_tickets?: number;
  created_at: string;
  is_active: boolean;
}

export interface CreateClientData {
  name: string;
  email: string;
  rfc?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
}

export interface UpdateClientData {
  name?: string;
  email?: string;
  rfc?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  is_active?: boolean;
}

class ClientsService {
  async getClients(params?: {
    page?: number;
    per_page?: number;
    search?: string;
  }) {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.per_page) queryParams.append('per_page', params.per_page.toString());
      if (params?.search) queryParams.append('search', params.search);

      const url = queryParams.toString() ? `/clients?${queryParams}` : '/clients';

      const response = await apiService.get(url);
      return response;
    } catch (error: any) {
      console.error('Error fetching clients:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch clients');
    }
  }

  // Get all clients without pagination (for dropdowns)
  async getAllClients() {
    try {
      const response = await this.getClients({ per_page: 1000 });
      return response?.data || [];
    } catch (error: any) {
      console.error('Error fetching all clients:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch clients');
    }
  }

  async getClientById(clientId: string) {
    try {
      const response = await apiService.get(`/clients/${clientId}`);
      return response;
    } catch (error: any) {
      console.error('Error fetching client:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch client');
    }
  }

  async createClient(clientData: CreateClientData) {
    try {
      const response = await apiService.post('/clients', clientData);
      return response;
    } catch (error: any) {
      console.error('Error creating client:', error);
      throw new Error(error.response?.data?.message || 'Failed to create client');
    }
  }

  async updateClient(clientId: string, clientData: UpdateClientData) {
    try {
      const response = await apiService.put(`/clients/${clientId}`, clientData);
      return response;
    } catch (error: any) {
      console.error('Error updating client:', error);
      throw new Error(error.response?.data?.message || 'Failed to update client');
    }
  }

  async deleteClient(clientId: string) {
    try {
      const response = await apiService.delete(`/clients/${clientId}`);
      return response;
    } catch (error: any) {
      console.error('Error deleting client:', error);
      throw new Error(error.response?.data?.message || 'Failed to delete client');
    }
  }

  async getClientStats() {
    try {
      const response = await apiService.get('/clients/stats');
      return response;
    } catch (error: any) {
      console.error('Error fetching client stats:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch client stats');
    }
  }

  async createClientWizard(wizardData: any) {
    try {
      const response = await apiService.post('/clients/wizard', wizardData);
      return response;
    } catch (error: any) {
      console.error('Error creating client with wizard:', error);
      throw new Error(error.response?.data?.message || 'Failed to create client with wizard');
    }
  }
}

export const clientsService = new ClientsService();
export default clientsService;
