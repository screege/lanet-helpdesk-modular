// User types
export type UserRole = 'superadmin' | 'admin' | 'technician' | 'client_admin' | 'solicitante';

export interface User {
  user_id: string;
  client_id?: string;
  name: string;
  email: string;
  role: UserRole;
  phone?: string;
  is_active: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
}

// Client types
export interface Client {
  client_id: string;
  name: string;
  rfc?: string;
  email: string;
  phone?: string;
  allowed_emails?: string[];
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Site types
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
}

// Ticket types
export type TicketPriority = 'baja' | 'media' | 'alta' | 'critica';
export type TicketStatus = 'nuevo' | 'asignado' | 'en_proceso' | 'espera_cliente' | 'resuelto' | 'cerrado' | 'cancelado' | 'pendiente_aprobacion' | 'reabierto';
export type TicketChannel = 'portal' | 'email' | 'agente' | 'telefono';

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
  affected_person_contact: string;
  additional_emails?: string[];
  priority: TicketPriority;
  category_id?: string;
  status: TicketStatus;
  channel: TicketChannel;
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
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  details?: any;
}

export interface PaginatedResponse<T = any> {
  items: T[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

// Auth types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

export interface AuthUser extends User {
  tokens: AuthTokens;
}

// Form types
export interface FormErrors {
  [key: string]: string;
}

// Dashboard types
export interface DashboardStats {
  total_tickets: number;
  open_tickets: number;
  assigned_tickets: number;
  resolved_tickets: number;
  overdue_tickets: number;
  sla_compliance: number;
}

// Navigation types
export interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<any>;
  current: boolean;
  roles?: UserRole[];
}
