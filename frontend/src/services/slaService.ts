import api from './api';

export interface SLAPolicy {
  policy_id: string;
  name: string;
  description?: string;
  priority: 'critica' | 'alta' | 'media' | 'baja';
  response_time_hours: number;
  resolution_time_hours: number;
  business_hours_only: boolean;
  escalation_enabled: boolean;
  escalation_levels?: number;
  client_id?: string;
  category_id?: string;
  is_active: boolean;
  is_default: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface SLATracking {
  tracking_id: string;
  ticket_id: string;
  policy_id: string;
  response_deadline: string;
  resolution_deadline: string;
  response_status: 'pending' | 'met' | 'breached';
  resolution_status: 'pending' | 'met' | 'breached';
  first_response_at?: string;
  resolved_at?: string;
  escalation_level: number;
  created_at: string;
  updated_at: string;
}

export interface SLABreach {
  ticket_id: string;
  ticket_number: string;
  breach_type: 'response' | 'resolution';
  deadline: string;
  time_elapsed: string;
  priority: string;
  status: string;
  client_name: string;
  assigned_to_name?: string;
}

export interface SLAStats {
  total_tickets: number;
  within_sla: number;
  breached_sla: number;
  sla_compliance_rate: number;
  avg_response_time: number;
  avg_resolution_time: number;
  breaches_by_priority: {
    critica: number;
    alta: number;
    media: number;
    baja: number;
  };
}

class SLAService {
  // SLA Policies Management
  async getSLAPolicies(): Promise<SLAPolicy[]> {
    const response = await api.get('/sla/policies');
    return response.data;
  }

  async getSLAPolicy(policyId: string): Promise<SLAPolicy> {
    const response = await api.get(`/sla/policies/${policyId}`);
    return response.data;
  }

  async createSLAPolicy(policy: Omit<SLAPolicy, 'policy_id' | 'created_at' | 'updated_at'>): Promise<SLAPolicy> {
    const response = await api.post('/sla/policies', policy);
    return response.data;
  }

  async updateSLAPolicy(policyId: string, policy: Partial<SLAPolicy>): Promise<SLAPolicy> {
    const response = await api.put(`/sla/policies/${policyId}`, policy);
    return response.data;
  }

  async deleteSLAPolicy(policyId: string): Promise<void> {
    await api.delete(`/sla/policies/${policyId}`);
  }

  async setDefaultSLAPolicy(policyId: string): Promise<void> {
    await api.post(`/sla/policies/${policyId}/set-default`);
  }

  // SLA Tracking and Monitoring
  async getSLATracking(ticketId?: string): Promise<SLATracking[]> {
    const url = ticketId ? `/sla/tracking?ticket_id=${ticketId}` : '/sla/tracking';
    const response = await api.get(url);
    return response.data;
  }

  async getSLABreaches(): Promise<SLABreach[]> {
    const response = await api.get('/sla/breaches');
    return response.data;
  }

  async getSLAWarnings(hoursAhead: number = 2): Promise<SLABreach[]> {
    const response = await api.get(`/sla/warnings?hours=${hoursAhead}`);
    return response.data;
  }

  // SLA Statistics and Reports
  async getSLAStats(startDate?: string, endDate?: string, clientId?: string): Promise<SLAStats> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (clientId) params.append('client_id', clientId);
    
    const response = await api.get(`/sla/stats?${params.toString()}`);
    return response.data;
  }

  async getSLAComplianceReport(startDate: string, endDate: string): Promise<any> {
    const response = await api.get(`/sla/reports/compliance?start_date=${startDate}&end_date=${endDate}`);
    return response.data;
  }

  // SLA Actions
  async escalateTicket(ticketId: string): Promise<void> {
    await api.post(`/sla/tickets/${ticketId}/escalate`);
  }

  async sendSLABreachNotification(breachData: SLABreach): Promise<void> {
    await api.post('/sla/notifications/breach', breachData);
  }

  // Business Hours Configuration
  async getBusinessHours(): Promise<any> {
    const response = await api.get('/sla/business-hours');
    return response.data;
  }

  async updateBusinessHours(config: any): Promise<any> {
    const response = await api.put('/sla/business-hours', config);
    return response.data;
  }

  // Utility Methods
  formatSLATime(hours: number): string {
    if (hours < 1) {
      return `${Math.round(hours * 60)} minutos`;
    } else if (hours < 24) {
      return `${hours} horas`;
    } else {
      const days = Math.floor(hours / 24);
      const remainingHours = hours % 24;
      return remainingHours > 0 ? `${days} días ${remainingHours} horas` : `${days} días`;
    }
  }

  getSLAStatusColor(status: 'pending' | 'met' | 'breached'): string {
    switch (status) {
      case 'met':
        return 'text-green-600 bg-green-100';
      case 'breached':
        return 'text-red-600 bg-red-100';
      case 'pending':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  }

  getPriorityColor(priority: string): string {
    switch (priority.toLowerCase()) {
      case 'critica':
        return 'text-red-600 bg-red-100';
      case 'alta':
        return 'text-orange-600 bg-orange-100';
      case 'media':
        return 'text-blue-600 bg-blue-100';
      case 'baja':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  }

  calculateSLACompliance(withinSLA: number, total: number): number {
    return total > 0 ? Math.round((withinSLA / total) * 100) : 0;
  }
}

export default new SLAService();
