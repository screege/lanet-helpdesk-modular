import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Save } from 'lucide-react';
import { ticketsService, CreateTicketData } from '../../services/ticketsService';
import { usersService } from '../../services/usersService';
import { clientsService } from '../../services/clientsService';
import { sitesService } from '../../services/sitesService';
import { categoriesService } from '../../services/categoriesService';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ErrorMessage from '../../components/common/ErrorMessage';

interface User {
  user_id: string;
  name: string;
  email: string;
  role: string;
}

interface Client {
  client_id: string;
  name: string;
}

interface Site {
  site_id: string;
  name: string;
  client_id: string;
}

interface Category {
  category_id: string;
  name: string;
  full_path: string;
}

const TicketCreatePage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dataLoaded, setDataLoaded] = useState(false);
  
  // Form data
  const [formData, setFormData] = useState<CreateTicketData>({
    client_id: '',
    site_id: '',
    subject: '',
    description: '',
    priority: 'media',
    assigned_to: '',
    category_id: '',
    affected_person: '',
    affected_person_phone: '',
    notification_email: '',
    additional_emails: [],
    channel: 'portal'
  });
  
  // Dropdown data
  const [technicians, setTechnicians] = useState<User[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [filteredSites, setFilteredSites] = useState<Site[]>([]);

  // File attachments
  const [attachments, setAttachments] = useState<File[]>([]);

  // Load initial data once
  useEffect(() => {
    if (user && !dataLoaded) {
      setDataLoaded(true);
      loadInitialData();
    }
  }, [user]);

  // Filter sites when client changes OR load sites for client users
  useEffect(() => {
    const isClientUser = user?.role === 'client_admin' || user?.role === 'solicitante';

    if (isClientUser) {
      // For client users, sites are already filtered by backend, use them directly
      console.log('🎯 Client user - using backend filtered sites:', sites.length);
      setFilteredSites(sites);
    } else if (formData.client_id) {
      // For admin/technician, filter sites by selected client
      const clientSites = sites.filter(site => site.client_id === formData.client_id);
      console.log('🔧 Admin user - filtering sites for client:', formData.client_id, 'Found:', clientSites.length);
      setFilteredSites(clientSites);

      // Reset site selection if current site doesn't belong to selected client
      if (formData.site_id && !clientSites.find(site => site.site_id === formData.site_id)) {
        setFormData(prev => ({ ...prev, site_id: '' }));
      }
    } else {
      // No client selected for admin/technician
      console.log('🔧 Admin user - no client selected, clearing sites');
      setFilteredSites([]);
      setFormData(prev => ({ ...prev, site_id: '' }));
    }
  }, [formData.client_id, sites, user?.role]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);



      // Role-based data loading
      const isClientUser = user?.role === 'client_admin' || user?.role === 'solicitante';

      // Load data individually to avoid Promise.all failures
      let techniciansResponse, categoriesResponse, clientsResponse, sitesResponse;

      try {
        techniciansResponse = await usersService.getUsersByRole('technician');
      } catch (err) {
        console.error('Error loading technicians:', err);
        techniciansResponse = { data: [] };
      }

      try {
        categoriesResponse = await categoriesService.getFlatCategories();
      } catch (err) {
        console.error('Error loading categories:', err);
        categoriesResponse = { data: [] };
      }

      try {
        clientsResponse = await clientsService.getAllClients();
      } catch (err) {
        console.error('Error loading clients:', err);
        clientsResponse = { data: [] };
      }

      try {
        sitesResponse = await sitesService.getAllSites();
      } catch (err) {
        console.error('Error loading sites:', err);
        sitesResponse = { data: [] };
      }



      console.log('📋 Raw API responses:');
      console.log('  Technicians:', techniciansResponse);
      console.log('  Clients:', clientsResponse);
      console.log('  Sites:', sitesResponse);
      console.log('  Categories:', categoriesResponse);

      // Handle API response structures - fix for undefined responses
      const techniciansData = techniciansResponse?.data || techniciansResponse || [];
      const clientsData = clientsResponse?.data || clientsResponse || [];
      const sitesData = sitesResponse?.data?.sites || sitesResponse?.data || sitesResponse || [];
      const categoriesData = categoriesResponse?.data || categoriesResponse || [];

      console.log('🔍 Processing API responses:');
      console.log('  Technicians raw:', techniciansResponse);
      console.log('  Clients raw:', clientsResponse);
      console.log('  Sites raw:', sitesResponse);
      console.log('  Sites extracted:', sitesData);
      console.log('  Categories raw:', categoriesResponse);

      setTechnicians(Array.isArray(techniciansData) ? techniciansData : []);
      setClients(Array.isArray(clientsData) ? clientsData : []);
      setSites(Array.isArray(sitesData) ? sitesData : []);
      setCategories(Array.isArray(categoriesData) ? categoriesData : []);

      console.log('✅ Final state set:');
      console.log('  Technicians count:', Array.isArray(techniciansData) ? techniciansData.length : 0);
      console.log('  Clients count:', Array.isArray(clientsData) ? clientsData.length : 0);
      console.log('  Sites count:', Array.isArray(sitesData) ? sitesData.length : 0);
      console.log('  Categories count:', Array.isArray(categoriesData) ? categoriesData.length : 0);

      console.log('🔍 Detailed data check:');
      console.log('  clientsData type:', typeof clientsData, 'isArray:', Array.isArray(clientsData));
      console.log('  clientsData content:', clientsData);
      console.log('  clients state after set:', clients.length);

      // Pre-fill data based on user role
      if (isClientUser && user?.client_id) {
        // For client users, auto-select their client and set sites directly
        setFormData(prev => ({
          ...prev,
          client_id: user.client_id
        }));

        // For client users, sites are already filtered by backend, so set them directly
        setFilteredSites(Array.isArray(sitesData) ? sitesData : []);

        console.log('🎯 Client user auto-setup:');
        console.log('  Auto-selected client:', user.client_id);
        console.log('  Available sites:', Array.isArray(sitesData) ? sitesData.length : 0);
      }

    } catch (err: any) {
      console.error('Error loading initial data:', err);
      setError(err.response?.data?.error || err.message || 'Error al cargar datos iniciales');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);

    // Validar tamaño máximo (10MB por archivo)
    const maxSize = 10 * 1024 * 1024; // 10MB
    const validFiles = files.filter(file => {
      if (file.size > maxSize) {
        setError(`El archivo ${file.name} excede el tamaño máximo de 10MB`);
        return false;
      }
      return true;
    });

    setAttachments(prev => [...prev, ...validFiles]);
    setError(null);
  };

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setSaving(true);
      setError(null);

      console.log('🎫 Creating ticket with data:', formData);
      console.log('📎 Attachments:', attachments.length);
      console.log('📎 Attachments array:', attachments);

      // Create FormData if there are attachments
      if (attachments.length > 0) {
        console.log('🔄 Creating FormData with attachments...');
        const formDataToSend = new FormData();

        // Add form fields
        Object.entries(formData).forEach(([key, value]) => {
          if (value !== null && value !== undefined && value !== '') {
            if (Array.isArray(value)) {
              formDataToSend.append(key, value.join(','));
            } else {
              formDataToSend.append(key, value.toString());
            }
          }
        });

        // Add files
        attachments.forEach((file) => {
          formDataToSend.append('attachments', file);
        });

        console.log('📤 About to send FormData...');
        console.log('📤 FormData entries:');
        for (let [key, value] of formDataToSend.entries()) {
          console.log(`  ${key}:`, value);
        }

        const ticket = await ticketsService.createTicketWithFiles(formDataToSend);
        console.log('✅ Ticket created successfully with files:', ticket);
        navigate(`/tickets/${ticket.ticket_id}`);
      } else {
        console.log('📝 No attachments, sending as JSON...');
        const ticket = await ticketsService.createTicket(formData);
        console.log('✅ Ticket created successfully:', ticket);
        navigate(`/tickets/${ticket.ticket_id}`);
      }

    } catch (err: any) {
      console.error('❌ Error creating ticket:', err);
      console.error('❌ Error response:', err.response);
      setError(err.response?.data?.message || 'Error al crear el ticket');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/tickets')}
              className="inline-flex items-center text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Volver a Tickets
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Crear Nuevo Ticket</h1>
              <p className="text-gray-500">Completa la información para crear un nuevo ticket</p>
            </div>
          </div>
        </div>

        {/* Form */}
        <div className="bg-white shadow rounded-lg">
          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            {error && (
              <div className="mb-4">
                <ErrorMessage message={error} />
              </div>
            )}

            {/* Client and Site Selection */}
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Ubicación</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Client Selection - Different UI for different roles */}
                {user?.role === 'client_admin' || user?.role === 'solicitante' ? (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Organización
                    </label>
                    <div className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700">
                      {clients.find(c => c.client_id === formData.client_id)?.name || 'Mi Organización'}
                    </div>
                  </div>
                ) : (
                  <div>
                    <label htmlFor="client_id" className="block text-sm font-medium text-gray-700 mb-1">
                      Cliente *
                    </label>
                    <select
                      id="client_id"
                      name="client_id"
                      value={formData.client_id}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">Seleccionar cliente</option>
                      {(() => {
                        console.log('🎯 Rendering client dropdown - clients array:', clients);
                        console.log('🎯 Clients length:', clients.length);
                        return clients.map((client) => (
                          <option key={client.client_id} value={client.client_id}>
                            {client.name}
                          </option>
                        ));
                      })()}
                    </select>
                  </div>
                )}

                <div>
                  <label htmlFor="site_id" className="block text-sm font-medium text-gray-700 mb-1">
                    Sitio *
                  </label>
                  <select
                    id="site_id"
                    name="site_id"
                    value={formData.site_id}
                    onChange={handleInputChange}
                    required
                    disabled={!formData.client_id && !(user?.role === 'client_admin' || user?.role === 'solicitante')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                  >
                    <option value="">Seleccionar sitio</option>
                    {(user?.role === 'client_admin' || user?.role === 'solicitante' ? sites : filteredSites).map((site) => (
                      <option key={site.site_id} value={site.site_id}>
                        {site.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Basic Information */}
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Información del Ticket</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">
                    Asunto *
                  </label>
                  <input
                    type="text"
                    id="subject"
                    name="subject"
                    value={formData.subject}
                    onChange={handleInputChange}
                    required
                    placeholder="Describe brevemente el problema"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div className="md:col-span-2">
                  <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                    Descripción *
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    required
                    rows={4}
                    placeholder="Proporciona una descripción detallada del problema"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
                    Prioridad *
                  </label>
                  <select
                    id="priority"
                    name="priority"
                    value={formData.priority}
                    onChange={handleInputChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="baja">Baja</option>
                    <option value="media">Media</option>
                    <option value="alta">Alta</option>
                    <option value="critica">Crítica</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="category_id" className="block text-sm font-medium text-gray-700 mb-1">
                    Categoría
                  </label>
                  <select
                    id="category_id"
                    name="category_id"
                    value={formData.category_id}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Seleccionar categoría</option>
                    {categories.map((category) => (
                      <option key={category.category_id} value={category.category_id}>
                        {category.full_path}
                      </option>
                    ))}
                  </select>
                </div>

                {(user?.role === 'superadmin' || user?.role === 'admin' || user?.role === 'technician') && (
                  <div>
                    <label htmlFor="assigned_to" className="block text-sm font-medium text-gray-700 mb-1">
                      Asignar a
                    </label>
                    <select
                      id="assigned_to"
                      name="assigned_to"
                      value={formData.assigned_to}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">Sin asignar</option>
                      {technicians.map((tech) => (
                        <option key={tech.user_id} value={tech.user_id}>
                          {tech.name}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
              </div>
            </div>

            {/* Contact Information */}
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Información de Contacto</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="affected_person" className="block text-sm font-medium text-gray-700 mb-1">
                    Persona Afectada *
                  </label>
                  <input
                    type="text"
                    id="affected_person"
                    name="affected_person"
                    value={formData.affected_person}
                    onChange={handleInputChange}
                    required
                    placeholder="Nombre de la persona afectada"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label htmlFor="affected_person_phone" className="block text-sm font-medium text-gray-700 mb-1">
                    Teléfono
                  </label>
                  <input
                    type="tel"
                    id="affected_person_phone"
                    name="affected_person_phone"
                    value={formData.affected_person_phone}
                    onChange={handleInputChange}
                    placeholder="Teléfono de contacto (opcional)"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>



                <div className="md:col-span-2">
                  <label htmlFor="additional_emails" className="block text-sm font-medium text-gray-700 mb-1">
                    Clientes a Notificar (opcional)
                  </label>
                  <input
                    type="text"
                    id="additional_emails"
                    name="additional_emails"
                    value={formData.additional_emails?.join(', ') || ''}
                    onChange={(e) => {
                      const emails = e.target.value.split(',').map(email => email.trim()).filter(email => email);
                      setFormData(prev => ({ ...prev, additional_emails: emails }));
                    }}
                    placeholder="email1@ejemplo.com, email2@ejemplo.com"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="mt-1 text-sm text-gray-500">
                    Separa múltiples emails con comas
                  </p>
                </div>
              </div>
            </div>

            {/* File Attachments */}
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Archivos Adjuntos</h2>
              <div className="space-y-4">
                <div>
                  <input
                    type="file"
                    multiple
                    onChange={handleFileChange}
                    accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                  <p className="mt-1 text-sm text-gray-500">
                    Máximo 10MB por archivo. Formatos: PDF, DOC, DOCX, TXT, JPG, PNG
                  </p>
                </div>

                {/* Lista de archivos seleccionados */}
                {attachments.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">
                      Archivos seleccionados ({attachments.length}):
                    </h3>
                    <div className="space-y-2">
                      {attachments.map((file, index) => (
                        <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                          <span className="text-sm text-gray-700">{file.name}</span>
                          <button
                            type="button"
                            onClick={() => removeAttachment(index)}
                            className="text-red-600 hover:text-red-800 text-sm"
                          >
                            Eliminar
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Form Actions */}
            <div className="flex justify-end gap-3 pt-6 border-t border-gray-200">
              <button
                type="button"
                onClick={() => navigate('/tickets')}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={saving}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Save className="w-4 h-4 mr-2" />
                {saving ? 'Creando...' : 'Crear Ticket'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default TicketCreatePage;
