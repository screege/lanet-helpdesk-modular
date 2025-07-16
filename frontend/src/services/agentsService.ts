import { apiService } from './api';

export interface AgentToken {
  token_id: string;
  token_value: string;
  client_id: string;
  site_id: string;
  client_name: string;
  site_name: string;
  is_active: boolean;
  created_at: string;
  expires_at?: string;
  usage_count: number;
  last_used_at?: string;
  notes?: string;
  created_by_name: string;
}

export interface CreateTokenData {
  expires_days?: number;
  notes?: string;
}

export interface TokenUsageHistory {
  usage_id: string;
  token_id: string;
  used_at: string;
  ip_address: string;
  user_agent: string;
  computer_name: string;
  hardware_fingerprint: any;
  registration_successful: boolean;
  asset_id?: string;
  error_message?: string;
}

export interface AgentRegistrationData {
  token: string;
  hardware_info: {
    agent_version: string;
    computer_name: string;
    hardware: any;
    software: any[];
    status: any;
  };
}

export interface AgentRegistrationResult {
  success: boolean;
  asset_id: string;
  client_id: string;
  site_id: string;
  client_name: string;
  site_name: string;
  agent_token: string;
  config: {
    heartbeat_interval: number;
    inventory_interval: number;
    metrics_interval: number;
    server_url: string;
  };
}

class AgentsService {
  // =====================================================
  // TOKEN MANAGEMENT
  // =====================================================

  /**
   * Get all tokens for a specific client and site
   */
  async getTokensForSite(clientId: string, siteId: string): Promise<{ tokens: AgentToken[]; total: number }> {
    try {
      const response = await apiService.get(`/agents/clients/${clientId}/sites/${siteId}/tokens`);
      return response.data as { tokens: AgentToken[]; total: number };
    } catch (error: any) {
      console.error('Error fetching tokens for site:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch tokens');
    }
  }

  /**
   * Get all tokens for a specific client (all sites)
   */
  async getTokensForClient(clientId: string): Promise<{ tokens: AgentToken[]; total: number }> {
    try {
      const response = await apiService.get(`/agents/clients/${clientId}/tokens`);
      return response.data as { tokens: AgentToken[]; total: number };
    } catch (error: any) {
      console.error('Error fetching tokens for client:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch tokens');
    }
  }

  /**
   * Get all tokens (superadmin/technician only)
   */
  async getAllTokens(): Promise<{ tokens: AgentToken[]; total: number }> {
    try {
      const response = await apiService.get('/agents/tokens');
      return response.data as { tokens: AgentToken[]; total: number };
    } catch (error: any) {
      console.error('Error fetching all tokens:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch tokens');
    }
  }

  /**
   * Create a new installation token
   */
  async createToken(clientId: string, siteId: string, data: CreateTokenData): Promise<AgentToken> {
    try {
      const response = await apiService.post(`/agents/clients/${clientId}/sites/${siteId}/tokens`, data);
      return response.data as AgentToken;
    } catch (error: any) {
      console.error('Error creating token:', error);
      throw new Error(error.response?.data?.message || 'Failed to create token');
    }
  }

  /**
   * Get specific token by ID
   */
  async getTokenById(tokenId: string): Promise<AgentToken> {
    try {
      const response = await apiService.get(`/agents/tokens/${tokenId}`);
      return response.data as AgentToken;
    } catch (error: any) {
      console.error('Error fetching token:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch token');
    }
  }

  /**
   * Update token status (activate/deactivate)
   */
  async updateTokenStatus(tokenId: string, isActive: boolean): Promise<AgentToken> {
    try {
      const response = await apiService.put(`/agents/tokens/${tokenId}`, { is_active: isActive });
      return response.data as AgentToken;
    } catch (error: any) {
      console.error('Error updating token status:', error);
      throw new Error(error.response?.data?.message || 'Failed to update token');
    }
  }

  /**
   * Delete token (superadmin only)
   */
  async deleteToken(tokenId: string): Promise<AgentToken> {
    try {
      const response = await apiService.delete(`/agents/tokens/${tokenId}`);
      return response.data as AgentToken;
    } catch (error: any) {
      console.error('Error deleting token:', error);
      throw new Error(error.response?.data?.message || 'Failed to delete token');
    }
  }

  // =====================================================
  // AGENT REGISTRATION
  // =====================================================

  /**
   * Register agent with installation token
   */
  async registerAgentWithToken(data: AgentRegistrationData): Promise<AgentRegistrationResult> {
    try {
      const response = await apiService.post('/agents/register-with-token', data);
      return response.data as AgentRegistrationResult;
    } catch (error: any) {
      console.error('Error registering agent:', error);
      throw new Error(error.response?.data?.message || 'Failed to register agent');
    }
  }

  // =====================================================
  // AGENT COMMUNICATION
  // =====================================================

  /**
   * Send agent heartbeat
   */
  async sendHeartbeat(assetId: string, status: any): Promise<{ status: string; next_heartbeat: number }> {
    try {
      const response = await apiService.post('/agents/heartbeat', {
        asset_id: assetId,
        status: status
      });
      return response.data as { status: string; next_heartbeat: number };
    } catch (error: any) {
      console.error('Error sending heartbeat:', error);
      throw new Error(error.response?.data?.message || 'Failed to send heartbeat');
    }
  }

  /**
   * Update agent inventory
   */
  async updateInventory(assetId: string, hardwareSpecs: any, softwareInventory: any[]): Promise<{ status: string; next_update: number }> {
    try {
      const response = await apiService.post('/agents/inventory', {
        asset_id: assetId,
        hardware_specs: hardwareSpecs,
        software_inventory: softwareInventory
      });
      return response.data as { status: string; next_update: number };
    } catch (error: any) {
      console.error('Error updating inventory:', error);
      throw new Error(error.response?.data?.message || 'Failed to update inventory');
    }
  }

  // =====================================================
  // UTILITY METHODS
  // =====================================================

  /**
   * Copy token to clipboard
   */
  async copyTokenToClipboard(tokenValue: string): Promise<boolean> {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(tokenValue);
        return true;
      } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = tokenValue;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        const result = document.execCommand('copy');
        textArea.remove();
        return result;
      }
    } catch (error) {
      console.error('Error copying to clipboard:', error);
      return false;
    }
  }

  /**
   * Format token expiration status
   */
  getTokenExpirationStatus(token: AgentToken): { status: 'active' | 'expired' | 'never'; message: string } {
    if (!token.expires_at) {
      return { status: 'never', message: 'Sin expiración' };
    }

    const expirationDate = new Date(token.expires_at);
    const now = new Date();

    if (expirationDate < now) {
      return { status: 'expired', message: 'Expirado' };
    }

    const daysUntilExpiration = Math.ceil((expirationDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    
    if (daysUntilExpiration <= 7) {
      return { status: 'active', message: `Expira en ${daysUntilExpiration} día${daysUntilExpiration !== 1 ? 's' : ''}` };
    }

    return { status: 'active', message: `Expira el ${expirationDate.toLocaleDateString('es-MX')}` };
  }

  /**
   * Validate token format
   */
  isValidTokenFormat(token: string): boolean {
    const tokenRegex = /^LANET-[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+$/;
    return tokenRegex.test(token);
  }
}

export const agentsService = new AgentsService();
export default agentsService;
