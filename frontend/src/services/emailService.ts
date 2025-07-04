import { apiService } from './api';

export interface EmailConfiguration {
  config_id: string;
  name: string;
  description?: string;
  smtp_host: string;
  smtp_port: number;
  smtp_username: string;
  smtp_password_encrypted?: string;
  smtp_use_tls: boolean;
  smtp_use_ssl: boolean;
  imap_host?: string;
  imap_port?: number;
  imap_username?: string;
  imap_password_encrypted?: string;
  imap_use_ssl: boolean;
  imap_folder: string;
  enable_email_to_ticket: boolean;
  default_priority: string;
  subject_prefix?: string;
  ticket_number_regex?: string;
  auto_assign_to?: string;
  default_client_id?: string;
  default_category_id?: string;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface EmailTemplate {
  template_id: string;
  name: string;
  description?: string;
  template_type: string;
  subject_template: string;
  body_template: string;
  is_html: boolean;
  available_variables: string[];
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface EmailQueueItem {
  queue_id: string;
  config_id: string;
  to_email: string;
  cc_emails?: string[];
  bcc_emails?: string[];
  subject: string;
  body_text?: string;
  body_html?: string;
  ticket_id?: string;
  user_id?: string;
  status: 'pending' | 'sending' | 'sent' | 'failed' | 'cancelled';
  priority: number;
  attempts: number;
  max_attempts: number;
  next_attempt_at?: string;
  error_message?: string;
  created_at: string;
  sent_at?: string;
}

export interface EmailProcessingLog {
  log_id: string;
  config_id: string;
  message_id: string;
  from_email: string;
  to_email: string;
  subject: string;
  processing_status: 'pending' | 'processed' | 'failed' | 'ignored';
  ticket_id?: string;
  action_taken?: string;
  error_message?: string;
  processed_at?: string;
  created_at: string;
}

export interface ConnectionTestResult {
  success: boolean;
  message: string;
  smtp_test?: boolean;
  imap_test?: boolean;
  error_details?: string;
}

class EmailService {
  // Email Configuration Management
  async getEmailConfigurations(): Promise<EmailConfiguration[]> {
    const response = await apiService.get('/email/configurations');
    return response.data;
  }

  async getEmailConfigurationById(configId: string): Promise<EmailConfiguration> {
    const response = await apiService.get(`/email/configurations/${configId}`);
    return response.data;
  }

  async createEmailConfiguration(config: Partial<EmailConfiguration>): Promise<EmailConfiguration> {
    const response = await apiService.post('/email/configurations', config);
    return response.data;
  }

  async updateEmailConfiguration(configId: string, config: Partial<EmailConfiguration>): Promise<EmailConfiguration> {
    const response = await apiService.put(`/email/configurations/${configId}`, config);
    return response.data;
  }

  async deleteEmailConfiguration(configId: string): Promise<void> {
    await apiService.delete(`/email/configurations/${configId}`);
  }

  async testEmailConnection(configId: string): Promise<ConnectionTestResult> {
    const response = await apiService.post(`/email/configurations/${configId}/test`, {});
    return response.data;
  }

  async sendTestEmail(configId: string, toEmail: string): Promise<any> {
    const response = await apiService.post(`/email/configurations/${configId}/send-test`, {
      to_email: toEmail
    });
    return response.data;
  }

  async setDefaultConfiguration(configId: string): Promise<void> {
    await apiService.post(`/email/configurations/${configId}/set-default`);
  }

  // Email Template Management
  async getEmailTemplates(): Promise<EmailTemplate[]> {
    const response = await apiService.get('/email/templates');
    return response.data;
  }

  async getEmailTemplateById(templateId: string): Promise<EmailTemplate> {
    const response = await apiService.get(`/email/templates/${templateId}`);
    return response.data;
  }

  async createEmailTemplate(template: Partial<EmailTemplate>): Promise<EmailTemplate> {
    const response = await apiService.post('/email/templates', template);
    return response.data;
  }

  async updateEmailTemplate(templateId: string, template: Partial<EmailTemplate>): Promise<EmailTemplate> {
    const response = await apiService.put(`/email/templates/${templateId}`, template);
    return response.data;
  }

  async deleteEmailTemplate(templateId: string): Promise<void> {
    await apiService.delete(`/email/templates/${templateId}`);
  }

  async previewEmailTemplate(templateId: string, variables: Record<string, string>): Promise<{ subject: string; body: string }> {
    const response = await apiService.post(`/email/templates/${templateId}/preview`, { variables });
    return response.data;
  }

  // Email Queue Management
  async getEmailQueue(filters?: {
    status?: string;
    priority?: number;
    page?: number;
    per_page?: number;
  }): Promise<{ items: EmailQueueItem[]; total: number; page: number; per_page: number }> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    
    const url = params.toString() ? `/email/queue?${params}` : '/email/queue';
    const response = await apiService.get(url);
    return response.data;
  }

  async retryEmailQueue(queueId: string): Promise<void> {
    await apiService.post(`/email/queue/${queueId}/retry`);
  }

  async cancelEmailQueue(queueId: string): Promise<void> {
    await apiService.post(`/email/queue/${queueId}/cancel`);
  }

  async processEmailQueue(): Promise<{ processed: number; message: string }> {
    const response = await apiService.post('/email/queue/process');
    return response.data;
  }

  // Email Processing Logs
  async getEmailProcessingLogs(filters?: {
    status?: string;
    from_email?: string;
    page?: number;
    per_page?: number;
  }): Promise<{ logs: EmailProcessingLog[]; total: number; page: number; per_page: number }> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    
    const url = params.toString() ? `/email/logs?${params}` : '/email/logs';
    const response = await apiService.get(url);
    return response.data;
  }

  // Email Operations
  async sendCustomTestEmail(configId: string, toEmail: string, subject: string, body: string): Promise<void> {
    await apiService.post(`/email/configurations/${configId}/send-test`, {
      to_email: toEmail,
      subject,
      body
    });
  }

  // Email Checking/Monitoring
  async checkEmails(configId: string): Promise<any> {
    const response = await apiService.post(`/email/configurations/${configId}/check-emails`, {});
    // Return the full response to maintain consistency with response manager format
    return response;
  }

  async checkIncomingEmails(configId?: string): Promise<{ processed_tickets: any[]; message: string }> {
    const response = await apiService.post('/email/incoming/check', { config_id: configId });
    return response.data;
  }

  // Email Statistics
  async getEmailStatistics(): Promise<{
    total_sent: number;
    total_failed: number;
    total_pending: number;
    total_processed_today: number;
    success_rate: number;
  }> {
    const response = await apiService.get('/email/statistics');
    return response.data;
  }
}

export const emailService = new EmailService();
