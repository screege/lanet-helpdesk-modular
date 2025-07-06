import React, { useState, useEffect } from 'react';
import { X, Save, AlertCircle } from 'lucide-react';
import { CreateTicketData, UpdateTicketData, Ticket } from '../../services/ticketsService';
import { clientsService, Client } from '../../services/clientsService';
import { sitesService, Site } from '../../services/sitesService';
import { usersService, User } from '../../services/usersService';
import { categoriesService, Category } from '../../services/categoriesService';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';

interface TicketFormProps {
  ticket?: Ticket;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateTicketData | UpdateTicketData) => Promise<void>;
  isLoading?: boolean;
}

const TicketForm: React.FC<TicketFormProps> = ({
  ticket,
  isOpen,
  onClose,
  onSubmit,
  isLoading = false
}) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState<CreateTicketData>({
    client_id: '',
    site_id: '',
    asset_id: '',
    assigned_to: '',
    subject: '',
    description: '',
    affected_person: '',
    affected_person_phone: '',
    notification_email: '',
    additional_emails: [],
    priority: 'media',
    category_id: '',
    channel: 'portal'
  });

  const [clients, setClients] = useState<Client[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [technicians, setTechnicians] = useState<User[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loadingData, setLoadingData] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [additionalEmailsText, setAdditionalEmailsText] = useState('');

  const isEditMode = !!ticket;

  // Load initial data
  useEffect(() => {
    if (isOpen) {
      loadInitialData();
      if (ticket) {
        populateFormWithTicket(ticket);
      }
    }
  }, [isOpen, ticket]);

  // Load clients and technicians based on user role
  const loadInitialData = async () => {
    try {
      console.log('🔄 TicketForm: Starting loadInitialData for user:', user?.name, user?.role);
      setLoadingData(true);

      // Always load categories and technicians
      console.log('📡 TicketForm: Loading categories and technicians...');
      const [categoriesResponse, techniciansResponse] = await Promise.all([
        categoriesService.getCategoriesFlat(),
        usersService.getUsersByRole('technician')
      ]);

      console.log('📦 TicketForm: Categories response:', categoriesResponse);
      console.log('📦 TicketForm: Technicians response:', techniciansResponse);

      // Handle categories response
      const categoriesData = categoriesResponse.data;
      if (Array.isArray(categoriesData)) {
        console.log('✅ TicketForm: Setting categories:', categoriesData.length, 'items');
        setCategories(categoriesData);
      } else {
        console.log('❌ TicketForm: Categories data is not array:', categoriesData);
        setCategories([]);
      }

      // Handle technicians response
      // Backend returns: {data: {users: [...], pagination: {...}}, success: true}
      if (Array.isArray(techniciansResponse)) {
        console.log('✅ TicketForm: Setting technicians (direct array):', techniciansResponse.length, 'items');
        setTechnicians(techniciansResponse);
      } else if (techniciansResponse?.data?.users) {
        console.log('✅ TicketForm: Setting technicians (from data.users):', techniciansResponse.data.users.length, 'items');
        setTechnicians(techniciansResponse.data.users);
      } else if (Array.isArray(techniciansResponse?.data)) {
        console.log('✅ TicketForm: Setting technicians (from data array):', techniciansResponse.data.length, 'items');
        setTechnicians(techniciansResponse.data);
      } else {
        console.log('❌ TicketForm: Technicians data invalid:', techniciansResponse);
        setTechnicians([]);
      }

      // Load data based on user role following blueprint workflows
      if (user?.role === 'superadmin' || user?.role === 'admin' || user?.role === 'technician') {
        // Full access users: load all clients
        try {
          console.log('📡 TicketForm: Loading clients for admin user...');
          const clientsResponse = await clientsService.getClients();
          console.log('📦 TicketForm: Clients response:', clientsResponse);

          const clientsData = clientsResponse.data;
          if (Array.isArray(clientsData)) {
            console.log('✅ TicketForm: Setting clients:', clientsData.length, 'items');
            setClients(clientsData);
          } else {
            console.log('❌ TicketForm: Clients data is not array:', clientsData);
            setClients([]);
          }
        } catch (error) {
          console.error('❌ TicketForm: Error loading clients for admin user:', error);
          setClients([]);
        }

      } else if (user?.role === 'client_admin' || user?.role === 'solicitante') {
        // Client users: pre-fill their client data and load their sites
        console.log('👤 TicketForm: Processing client user:', user.role, 'Client ID:', user.client_id);

        if (user.client_id) {
          // Pre-fill form with user's client data
          console.log('📝 TicketForm: Pre-filling form data for client user');
          setFormData(prev => ({
            ...prev,
            client_id: user.client_id,
            affected_person: user.name || '',
            affected_person_contact: user.email || ''
          }));

          // Load sites for their client (backend will filter based on role)
          try {
            console.log('📡 TicketForm: Loading sites for client user...');
            await loadSites(user.client_id);
          } catch (error) {
            console.error('❌ TicketForm: Error loading sites for client user:', error);
            setSites([]);
          }
        }

        // Don't load all clients for client users (they can't access that endpoint)
        console.log('🚫 TicketForm: Skipping clients loading for client user');
        setClients([]);
      }

    } catch (error) {
      console.error('Error loading initial data:', error);
      setClients([]);
      setTechnicians([]);
      setCategories([]);
    } finally {
      setLoadingData(false);
    }
  };

  // Load sites when client changes
  useEffect(() => {
    if (formData.client_id) {
      loadSites(formData.client_id);
    } else {
      setSites([]);
      setFormData(prev => ({ ...prev, site_id: '' }));
    }
  }, [formData.client_id]);

  const loadSites = async (clientId: string) => {
    try {
      console.log('🏢 TicketForm: Loading sites for clientId:', clientId, 'User role:', user?.role);

      // For client users, use the general sites endpoint which applies RLS
      // For admin users, we can use the client-specific endpoint
      let sitesResponse;

      if (user?.role === 'client_admin' || user?.role === 'solicitante') {
        // Client users: use general sites endpoint (backend applies RLS filtering)
        console.log('📡 TicketForm: Using getAllSites for client user (RLS applied)');
        sitesResponse = await sitesService.getAllSites();
      } else {
        // Admin users: use client-specific endpoint
        console.log('📡 TicketForm: Using getSitesByClient for admin user');
        sitesResponse = await sitesService.getSitesByClient(clientId);
      }

      console.log('📦 TicketForm: Sites response:', sitesResponse);

      // Handle different response formats from backend
      let sitesData = [];
      if (sitesResponse?.data?.sites) {
        // Format: {data: {sites: [array], ...}, success: true}
        console.log('✅ TicketForm: Using data.sites format, found:', sitesResponse.data.sites.length, 'sites');
        sitesData = sitesResponse.data.sites;
      } else if (Array.isArray(sitesResponse?.data)) {
        // Format: {data: [array], success: true}
        console.log('✅ TicketForm: Using data array format, found:', sitesResponse.data.length, 'sites');
        sitesData = sitesResponse.data;
      } else if (Array.isArray(sitesResponse)) {
        // Direct array format
        console.log('✅ TicketForm: Using direct array format, found:', sitesResponse.length, 'sites');
        sitesData = sitesResponse;
      } else {
        console.log('❌ TicketForm: Unknown sites response format:', sitesResponse);
      }

      console.log('🏢 TicketForm: Setting sites state with:', sitesData.length, 'sites');
      setSites(sitesData);

      // For solicitante users with only one site, auto-select it
      if (user?.role === 'solicitante' && sitesData.length === 1) {
        console.log('🎯 TicketForm: Auto-selecting single site for solicitante:', sitesData[0].name);
        setFormData(prev => ({
          ...prev,
          site_id: sitesData[0].site_id
        }));
      }

    } catch (error) {
      console.error('❌ TicketForm: Error loading sites:', error);
      setSites([]);
    }
  };

  // Populate form with existing ticket data
  const populateFormWithTicket = (ticketData: Ticket) => {
    setFormData({
      client_id: ticketData.client_id,
      site_id: ticketData.site_id,
      asset_id: ticketData.asset_id || '',
      assigned_to: ticketData.assigned_to || '',
      subject: ticketData.subject,
      description: ticketData.description,
      affected_person: ticketData.affected_person,
      affected_person_contact: ticketData.affected_person_contact,
      additional_emails: ticketData.additional_emails || [],
      priority: ticketData.priority,
      category_id: ticketData.category_id || '',
      channel: ticketData.channel
    });

    if (ticketData.additional_emails && ticketData.additional_emails.length > 0) {
      setAdditionalEmailsText(ticketData.additional_emails.join(', '));
    }
  };

  // Handle form field changes
  const handleChange = (field: keyof CreateTicketData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  // Handle additional emails change
  const handleAdditionalEmailsChange = (value: string) => {
    setAdditionalEmailsText(value);
    // Parse emails from comma-separated string
    const emails = value
      .split(',')
      .map(email => email.trim())
      .filter(email => email.length > 0);
    
    setFormData(prev => ({ ...prev, additional_emails: emails }));
  };

  // Validate form
  const validateForm = (): boolean => {
    const newErrors: { [key: string]: string } = {};

    if (!formData.client_id) newErrors.client_id = 'Cliente es requerido';
    if (!formData.site_id) newErrors.site_id = 'Sitio es requerido';
    if (!formData.subject.trim()) newErrors.subject = 'Asunto es requerido';
    if (!formData.description.trim()) newErrors.description = 'Descripción es requerida';
    if (!formData.affected_person.trim()) newErrors.affected_person = 'Persona afectada es requerida';

    // Validate phone number format if provided
    if (formData.affected_person_phone && formData.affected_person_phone.trim()) {
      const phoneRegex = /^[\+]?[0-9\s\-\(\)\.]{7,20}$/;
      if (!phoneRegex.test(formData.affected_person_phone.trim())) {
        newErrors.affected_person_phone = 'Formato de teléfono inválido';
      }
    }

    // Validate email format if provided
    if (formData.notification_email && formData.notification_email.trim()) {
      const emailRegex = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
      if (!emailRegex.test(formData.notification_email.trim())) {
        newErrors.notification_email = 'Formato de email inválido';
      }
    }
    if (!formData.category_id) newErrors.category_id = 'Categoría es requerida';

    // Validate email format for affected person contact if it looks like an email
    if (formData.affected_person_contact.includes('@')) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.affected_person_contact)) {
        newErrors.affected_person_contact = 'Formato de email inválido';
      }
    }

    // Validate additional emails
    if (formData.additional_emails && formData.additional_emails.length > 0) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      const invalidEmails = formData.additional_emails.filter(email => !emailRegex.test(email));
      if (invalidEmails.length > 0) {
        newErrors.additional_emails = `Emails inválidos: ${invalidEmails.join(', ')}`;
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      await onSubmit(formData);
      handleClose();
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  // Handle modal close
  const handleClose = () => {
    setFormData({
      client_id: '',
      site_id: '',
      asset_id: '',
      assigned_to: '',
      subject: '',
      description: '',
      affected_person: '',
      affected_person_phone: '',
      notification_email: '',
      additional_emails: [],
      priority: 'media',
      category_id: '',
      channel: 'portal'
    });
    setAdditionalEmailsText('');
    setErrors({});
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {isEditMode ? 'Editar Ticket' : 'Crear Nuevo Ticket'}
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {loadingData && (
            <div className="flex justify-center py-4">
              <LoadingSpinner />
            </div>
          )}

          {/* Client and Site Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Only show client selector for admin/technician users */}
            {(user?.role === 'superadmin' || user?.role === 'admin' || user?.role === 'technician') && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cliente *
                </label>
                <select
                  value={formData.client_id}
                  onChange={(e) => handleChange('client_id', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.client_id ? 'border-red-300' : 'border-gray-300'
                  }`}
                  disabled={isEditMode}
                >
                  <option value="">Seleccionar cliente...</option>
                  {clients.map((client) => (
                    <option key={client.client_id} value={client.client_id}>
                      {client.name}
                    </option>
                  ))}
                </select>
                {errors.client_id && (
                  <p className="mt-1 text-sm text-red-600">{errors.client_id}</p>
                )}
              </div>
            )}

            {/* Show client info for client users (read-only) */}
            {(user?.role === 'client_admin' || user?.role === 'solicitante') && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cliente
                </label>
                <div className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-700">
                  {user?.client_name || 'Cliente asignado'}
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sitio *
              </label>
              <select
                value={formData.site_id}
                onChange={(e) => handleChange('site_id', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.site_id ? 'border-red-300' : 'border-gray-300'
                }`}
                disabled={!formData.client_id || isEditMode}
              >
                <option value="">Seleccionar sitio...</option>
                {sites.map((site) => (
                  <option key={site.site_id} value={site.site_id}>
                    {site.name}
                  </option>
                ))}
              </select>
              {errors.site_id && (
                <p className="mt-1 text-sm text-red-600">{errors.site_id}</p>
              )}
            </div>
          </div>

          {/* Subject */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Asunto *
            </label>
            <input
              type="text"
              value={formData.subject}
              onChange={(e) => handleChange('subject', e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.subject ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Ingrese el asunto del ticket..."
            />
            {errors.subject && (
              <p className="mt-1 text-sm text-red-600">{errors.subject}</p>
            )}
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Descripción *
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              rows={4}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.description ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Describa detalladamente el problema o solicitud..."
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-600">{errors.description}</p>
            )}
          </div>

          {/* Affected Person and Phone */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Persona Afectada *
              </label>
              <input
                type="text"
                value={formData.affected_person}
                onChange={(e) => handleChange('affected_person', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.affected_person ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Nombre de la persona afectada..."
              />
              {errors.affected_person && (
                <p className="mt-1 text-sm text-red-600">{errors.affected_person}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Teléfono
              </label>
              <input
                type="tel"
                value={formData.affected_person_phone}
                onChange={(e) => handleChange('affected_person_phone', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.affected_person_phone ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Teléfono de contacto (opcional)..."
              />
              {errors.affected_person_phone && (
                <p className="mt-1 text-sm text-red-600">{errors.affected_person_phone}</p>
              )}
            </div>


          </div>

          {/* Priority, Category and Assignment */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Prioridad *
              </label>
              <select
                value={formData.priority}
                onChange={(e) => handleChange('priority', e.target.value as any)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="baja">Baja</option>
                <option value="media">Media</option>
                <option value="alta">Alta</option>
                <option value="critica">Crítica</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Categoría *
              </label>
              <select
                value={formData.category_id}
                onChange={(e) => handleChange('category_id', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.category_id ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value="">Seleccionar categoría...</option>
                {categories.map((category) => (
                  <option key={category.category_id} value={category.category_id}>
                    {category.full_name || category.name}
                  </option>
                ))}
              </select>
              {errors.category_id && (
                <p className="mt-1 text-sm text-red-600">{errors.category_id}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Asignar a Técnico
              </label>
              <select
                value={formData.assigned_to}
                onChange={(e) => handleChange('assigned_to', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Sin asignar</option>
                {technicians.map((tech) => (
                  <option key={tech.user_id} value={tech.user_id}>
                    {tech.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Additional Emails */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Correos Adicionales para Notificar
            </label>
            <input
              type="text"
              value={additionalEmailsText}
              onChange={(e) => handleAdditionalEmailsChange(e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.additional_emails ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="email1@ejemplo.com, email2@ejemplo.com..."
            />
            <p className="mt-1 text-sm text-gray-500">
              Separe múltiples emails con comas
            </p>
            {errors.additional_emails && (
              <p className="mt-1 text-sm text-red-600">{errors.additional_emails}</p>
            )}
          </div>

          {/* Form Actions */}
          <div className="flex justify-end gap-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              disabled={isLoading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <LoadingSpinner size="sm" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              {isEditMode ? 'Actualizar' : 'Crear'} Ticket
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TicketForm;
