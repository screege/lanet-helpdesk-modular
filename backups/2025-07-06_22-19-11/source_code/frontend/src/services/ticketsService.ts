import { apiService } from './api';

export interface Ticket {
  ticket_id: string;
  ticket_number: string;
  client_id: string;
  site_id: string;
  asset_id?: string;
  created_by: string;
  assigned_to?: string;
  subject: string;
  description: string;
  affected_person: string;
  affected_person_phone?: string;  // New phone field (optional)
  notification_email?: string;     // New email field (optional)
  // Backward compatibility
  affected_person_contact?: string; // Deprecated, use notification_email instead
  additional_emails?: string[];
  priority: 'baja' | 'media' | 'alta' | 'critica';
  category_id?: string;
  status: 'nuevo' | 'asignado' | 'en_proceso' | 'espera_cliente' | 'resuelto' | 'cerrado' | 'cancelado' | 'pendiente_aprobacion' | 'reabierto';
  channel: 'portal' | 'email' | 'phone' | 'agent';
  is_email_originated: boolean;
  from_email?: string;
  email_message_id?: string;
  email_thread_id?: string;
  approval_status: string;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
  updated_at: string;
  assigned_at?: string;
  resolved_at?: string;
  closed_at?: string;
  resolution_notes?: string;
  // Related data
  client_name?: string;
  site_name?: string;
  created_by_name?: string;
  assigned_to_name?: string;
  category_name?: string;
}

export interface TicketComment {
  comment_id: string;
  ticket_id: string;
  user_id: string;
  content: string;
  is_internal: boolean;
  is_email_reply: boolean;
  email_message_id?: string;
  created_at: string;
  updated_at: string;
  user_name?: string;
  user_role?: string;
}

export interface TicketAttachment {
  attachment_id: string;
  ticket_id: string;
  filename: string;
  original_filename: string;
  file_size: number;
  file_size_display: string;
  mime_type: string;
  uploaded_by: string;
  created_at: string;
  // Related data
  uploaded_by_name?: string;
  uploaded_by_role?: string;
}

export interface TicketActivity {
  activity_id: string;
  ticket_id: string;
  user_id: string;
  action: string;
  description: string;
  created_at: string;
  user_name?: string;
  user_role?: string;
}

export interface CreateTicketData {
  client_id: string;
  site_id: string;
  asset_id?: string;
  assigned_to?: string;
  subject: string;
  description: string;
  affected_person: string;
  affected_person_phone?: string;  // New phone field (optional)
  notification_email?: string;     // New email field (optional)
  // Backward compatibility
  affected_person_contact?: string; // Deprecated, use notification_email instead
  additional_emails?: string[];
  priority: 'baja' | 'media' | 'alta' | 'critica';
  category_id?: string;
  channel?: string;
}

export interface UpdateTicketData {
  subject?: string;
  description?: string;
  affected_person?: string;
  affected_person_phone?: string;  // New phone field (optional)
  notification_email?: string;     // New email field (optional)
  // Backward compatibility
  affected_person_contact?: string; // Deprecated, use notification_email instead
  additional_emails?: string[];
  priority?: 'baja' | 'media' | 'alta' | 'critica';
  category_id?: string;
  status?: string;
  assigned_to?: string;
  resolution_notes?: string;
}

export interface TicketFilters {
  search?: string;
  status?: string;
  priority?: string;
  client_id?: string;
  assigned_to?: string;
  page?: number;
  per_page?: number;
}

export interface TicketStats {
  total_tickets: number;
  new_tickets: number;
  assigned_tickets: number;
  in_progress_tickets: number;
  waiting_customer_tickets: number;
  resolved_tickets: number;
  closed_tickets: number;
  critical_tickets: number;
  high_tickets: number;
  medium_tickets: number;
  low_tickets: number;
  tickets_last_24h: number;
  tickets_last_week: number;
}

export interface PaginatedTicketsResponse {
  tickets: Ticket[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
  };
}

class TicketsService {
  // Get all tickets with pagination and filters
  async getAllTickets(filters?: TicketFilters): Promise<PaginatedTicketsResponse> {
    const params = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value.toString());
        }
      });
    }
    
    const queryString = params.toString();
    const url = queryString ? `/tickets/search?${queryString}` : '/tickets/';
    
    const response = await apiService.get(url);
    return response.data;
  }

  // Get ticket by ID
  async getTicketById(ticketId: string): Promise<Ticket> {
    const response = await apiService.get(`/tickets/${ticketId}`);
    return response.data;
  }

  // Create new ticket
  async createTicket(ticketData: CreateTicketData): Promise<Ticket> {
    const response = await apiService.post('/tickets/', ticketData);
    return response.data;
  }

  // Create new ticket with files
  async createTicketWithFiles(formData: FormData): Promise<Ticket> {
    // Let axios set Content-Type automatically for FormData
    const response = await apiService.post('/tickets/', formData);
    return response.data;
  }

  // Update ticket
  async updateTicket(ticketId: string, ticketData: UpdateTicketData): Promise<Ticket> {
    const response = await apiService.put(`/tickets/${ticketId}`, ticketData);
    return response.data;
  }

  // Assign ticket to technician
  async assignTicket(ticketId: string, assignedTo: string): Promise<{ message: string }> {
    const response = await apiService.post(`/tickets/${ticketId}/assign`, { assigned_to: assignedTo });
    return response.data;
  }

  // Update ticket status
  async updateTicketStatus(ticketId: string, status: string, resolutionNotes?: string): Promise<ApiResponse<Ticket>> {
    const data: any = { status };
    if (resolutionNotes) {
      data.resolution_notes = resolutionNotes;
    }
    const response = await apiService.patch(`/tickets/${ticketId}/status`, data);
    return response;
  }

  // Get ticket comments
  async getTicketComments(ticketId: string): Promise<TicketComment[]> {
    const response = await apiService.get(`/tickets/${ticketId}/comments`);
    return response.data;
  }

  // Add comment to ticket
  async addTicketComment(ticketId: string, content: string, isInternal: boolean = false): Promise<TicketComment> {
    const response = await apiService.post(`/tickets/${ticketId}/comments`, {
      content,
      is_internal: isInternal
    });
    return response.data;
  }

  // Get ticket activities
  async getTicketActivities(ticketId: string): Promise<TicketActivity[]> {
    const response = await apiService.get(`/tickets/${ticketId}/activities`);
    return response.data;
  }

  // Get ticket resolutions
  async getTicketResolutions(ticketId: string): Promise<any[]> {
    const response = await apiService.get(`/tickets/${ticketId}/resolutions`);
    return response.data;
  }

  // Get ticket attachments
  async getTicketAttachments(ticketId: string): Promise<TicketAttachment[]> {
    const response = await apiService.get(`/tickets/${ticketId}/attachments`);
    return response.data;
  }

  // Get ticket statistics
  async getTicketStats(): Promise<TicketStats> {
    const response = await apiService.get('/tickets/stats');
    return response.data;
  }

  // Search tickets
  async searchTickets(filters: TicketFilters): Promise<PaginatedTicketsResponse> {
    return this.getAllTickets(filters);
  }
}

export const ticketsService = new TicketsService();
