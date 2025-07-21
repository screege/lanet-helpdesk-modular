import apiClient from '../api/apiClient';

export interface Asset {
  asset_id: string;
  name: string;
  agent_status: 'online' | 'warning' | 'offline';
  last_seen: string;
  specifications: any;
  site_name: string;
  site_id: string;
  client_name?: string;
  client_id?: string;
}

export interface AssetsDashboard {
  summary: {
    total_assets: number;
    online_assets: number;
    warning_assets: number;
    offline_assets: number;
    last_update: string;
  };
  sites: Array<{
    site_id: string;
    site_name: string;
    total_assets: number;
    online_assets: number;
    warning_assets: number;
    offline_assets: number;
    last_update: string;
  }>;
  alerts: Array<{
    asset_name: string;
    agent_status: string;
    last_seen: string;
    site_name: string;
  }>;
}

export interface AssetsInventory {
  assets: Asset[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface AssetDetail extends Asset {
  client_name: string;
  client_id: string;
}

class AssetsService {
  // =====================================================
  // DASHBOARD ENDPOINTS
  // =====================================================

  /**
   * Get assets dashboard for client admin's organization
   */
  async getOrganizationDashboard(): Promise<AssetsDashboard> {
    try {
      const response = await apiClient.get('/assets/dashboard/my-organization');

      // Handle response format
      const data = response.data?.data || response.data;
      return data as AssetsDashboard;
    } catch (error: any) {
      console.error('Error fetching organization dashboard:', error);
      throw new Error(error.response?.data?.message || error.message || 'Failed to fetch dashboard');
    }
  }

  /**
   * Get assets dashboard for solicitante's assigned sites
   */
  async getSitesDashboard(): Promise<AssetsDashboard> {
    try {
      const response = await apiClient.get('/assets/dashboard/my-sites');
      return response.data as AssetsDashboard;
    } catch (error: any) {
      console.error('Error fetching sites dashboard:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch dashboard');
    }
  }

  // =====================================================
  // INVENTORY ENDPOINTS
  // =====================================================

  /**
   * Get complete inventory for client admin's organization
   */
  async getOrganizationInventory(params?: {
    page?: number;
    per_page?: number;
    search?: string;
    status?: string;
  }): Promise<AssetsInventory> {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.per_page) queryParams.append('per_page', params.per_page.toString());
      if (params?.search) queryParams.append('search', params.search);
      if (params?.status && params.status !== 'all') queryParams.append('status', params.status);

      const url = queryParams.toString()
        ? `/assets/inventory/my-organization?${queryParams}`
        : '/assets/inventory/my-organization';

      const response = await apiClient.get(url);

      // Handle response format
      const data = response.data?.data || response.data;
      return {
        assets: data.assets || [],
        total: data.total || data.assets?.length || 0,
        page: data.page || 1,
        per_page: data.per_page || 10,
        total_pages: data.total_pages || 1
      };
    } catch (error: any) {
      console.error('Error fetching organization inventory:', error);
      throw new Error(error.response?.data?.message || error.message || 'Failed to fetch inventory');
    }
  }

  /**
   * Get inventory for a specific site
   */
  async getSiteInventory(siteId: string): Promise<{ assets: Asset[]; site_id: string }> {
    try {
      const response = await apiClient.get(`/assets/inventory/site/${siteId}`);
      return response.data as { assets: Asset[]; site_id: string };
    } catch (error: any) {
      console.error('Error fetching site inventory:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch site inventory');
    }
  }

  /**
   * Get detailed information for a specific asset
   */
  async getAssetDetail(assetId: string): Promise<{ asset: AssetDetail }> {
    try {
      const response = await apiClient.get(`/assets/${assetId}/detail`);
      return response.data.data as { asset: AssetDetail };
    } catch (error: any) {
      console.error('Error fetching asset detail:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch asset detail');
    }
  }

  // =====================================================
  // SUPERADMIN/TECHNICIAN ENDPOINTS
  // =====================================================

  /**
   * Get all assets (superadmin/technician only)
   */
  async getAllAssets(params?: {
    page?: number;
    per_page?: number;
    search?: string;
    client_id?: string;
    status?: string;
  }): Promise<AssetsInventory> {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.per_page) queryParams.append('per_page', params.per_page.toString());
      if (params?.search) queryParams.append('search', params.search);
      if (params?.client_id) queryParams.append('client_id', params.client_id);
      if (params?.status && params.status !== 'all') queryParams.append('status', params.status);

      const url = queryParams.toString() ? `/assets?${queryParams}` : '/assets';

      const response = await apiClient.get(url);

      // Handle different response formats
      if (response.data && response.data.data) {
        // If response has nested data structure
        return {
          assets: response.data.data.assets || [],
          total: response.data.data.total || 0,
          page: response.data.data.page || 1,
          per_page: response.data.data.per_page || 10,
          total_pages: response.data.data.total_pages || 1
        };
      } else if (response.data && response.data.assets) {
        // If response has direct assets array
        return {
          assets: response.data.assets || [],
          total: response.data.total || response.data.assets?.length || 0,
          page: response.data.page || 1,
          per_page: response.data.per_page || 10,
          total_pages: response.data.total_pages || 1
        };
      } else {
        // Fallback - assume response.data is the assets array
        const assets = Array.isArray(response.data) ? response.data : [];
        return {
          assets: assets,
          total: assets.length,
          page: 1,
          per_page: assets.length,
          total_pages: 1
        };
      }
    } catch (error: any) {
      console.error('Error fetching all assets:', error);
      throw new Error(error.response?.data?.message || error.message || 'Failed to fetch assets');
    }
  }

  /**
   * Get organized dashboard for technicians
   */
  async getTechnicianDashboard(): Promise<{
    overall_summary: any;
    client_summaries: any[];
    alerts: any[];
  }> {
    try {
      const response = await apiClient.get('/assets/dashboard/technician');
      return response.data.data as any;
    } catch (error: any) {
      console.error('Error fetching technician dashboard:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch technician dashboard');
    }
  }

  /**
   * Get filtered assets for technicians
   */
  async getFilteredAssets(params?: {
    client_id?: string;
    site_id?: string;
    status?: string;
    search?: string;
    page?: number;
    per_page?: number;
  }): Promise<{
    assets: Asset[];
    pagination: {
      total: number;
      page: number;
      per_page: number;
      total_pages: number;
      has_next: boolean;
      has_prev: boolean;
    };
  }> {
    try {
      const queryParams = new URLSearchParams();
      if (params?.client_id) queryParams.append('client_id', params.client_id);
      if (params?.site_id) queryParams.append('site_id', params.site_id);
      if (params?.status) queryParams.append('status', params.status);
      if (params?.search) queryParams.append('search', params.search);
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.per_page) queryParams.append('per_page', params.per_page.toString());

      const response = await apiClient.get(`/assets/technician/filtered?${queryParams}`);
      return response.data.data as any;
    } catch (error: any) {
      console.error('Error fetching filtered assets:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch filtered assets');
    }
  }

  /**
   * Get clients with assets (for filter dropdown)
   */
  async getClientsWithAssets(): Promise<{ clients: Array<{ client_id: string; client_name: string; asset_count: number }> }> {
    try {
      const response = await apiClient.get('/assets/clients');
      return response.data.data as any;
    } catch (error: any) {
      console.error('Error fetching clients with assets:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch clients');
    }
  }

  /**
   * Get sites with assets (for filter dropdown)
   */
  async getSitesWithAssets(clientId?: string): Promise<{ sites: Array<{ site_id: string; site_name: string; client_id: string; client_name: string; asset_count: number }> }> {
    try {
      const queryParams = new URLSearchParams();
      if (clientId) queryParams.append('client_id', clientId);

      const response = await apiClient.get(`/assets/sites?${queryParams}`);
      return response.data.data as any;
    } catch (error: any) {
      console.error('Error fetching sites with assets:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch sites');
    }
  }

  // =====================================================
  // UTILITY METHODS
  // =====================================================

  /**
   * Get status color for agent status
   */
  getStatusColor(status: string): string {
    switch (status) {
      case 'online':
        return 'text-green-600 bg-green-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'offline':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  }

  /**
   * Get status icon for agent status
   */
  getStatusIcon(status: string): string {
    switch (status) {
      case 'online':
        return '🟢';
      case 'warning':
        return '🟡';
      case 'offline':
        return '🔴';
      default:
        return '⚪';
    }
  }

  /**
   * Get status text in Spanish
   */
  getStatusText(status: string): string {
    switch (status) {
      case 'online':
        return 'En línea';
      case 'warning':
        return 'Advertencia';
      case 'offline':
        return 'Desconectado';
      default:
        return 'Desconocido';
    }
  }

  /**
   * Format last seen time
   */
  formatLastSeen(lastSeen: string): string {
    if (!lastSeen) return 'Nunca';
    
    const date = new Date(lastSeen);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMinutes < 1) {
      return 'Ahora mismo';
    } else if (diffMinutes < 60) {
      return `Hace ${diffMinutes} minuto${diffMinutes !== 1 ? 's' : ''}`;
    } else if (diffHours < 24) {
      return `Hace ${diffHours} hora${diffHours !== 1 ? 's' : ''}`;
    } else if (diffDays < 7) {
      return `Hace ${diffDays} día${diffDays !== 1 ? 's' : ''}`;
    } else {
      return date.toLocaleDateString('es-MX', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  }

  /**
   * Get system specifications summary
   */
  getSpecsSummary(specifications: any): string {
    if (!specifications || typeof specifications !== 'object') {
      return 'Sin información';
    }

    const parts = [];
    
    if (specifications.system_metrics) {
      const metrics = specifications.system_metrics;
      if (metrics.cpu_usage !== undefined) {
        parts.push(`CPU: ${metrics.cpu_usage}%`);
      }
      if (metrics.memory_usage !== undefined) {
        parts.push(`RAM: ${metrics.memory_usage}%`);
      }
      if (metrics.disk_usage !== undefined) {
        parts.push(`Disco: ${metrics.disk_usage}%`);
      }
    }

    if (specifications.os) {
      parts.push(`OS: ${specifications.os}`);
    }

    return parts.length > 0 ? parts.join(' | ') : 'Sin métricas';
  }

  /**
   * Check if asset needs attention (offline or high resource usage)
   */
  needsAttention(asset: Asset): boolean {
    if (asset.agent_status === 'offline' || asset.agent_status === 'warning') {
      return true;
    }

    if (asset.specifications?.system_metrics) {
      const metrics = asset.specifications.system_metrics;
      return (
        metrics.cpu_usage > 90 ||
        metrics.memory_usage > 90 ||
        metrics.disk_usage > 90
      );
    }

    return false;
  }
}

export const assetsService = new AssetsService();
export default assetsService;
