import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Upload, X, FileText, AlertCircle, Phone, Mail, User, Monitor } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';

interface FormData {
  client_id: string;
  site_id: string;
  subject: string;
  description: string;
  priority: string;
  affected_person: string;
  affected_person_phone: string;
  notification_email: string;
  category_id: string;
  assigned_to: string;
  additional_emails: string[];
}

const TicketCreatePageNew: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [attachments, setAttachments] = useState<File[]>([]);

  const [formData, setFormData] = useState<FormData>({
    client_id: '',
    site_id: '',
    subject: '',
    description: '',
    priority: 'media',
    affected_person: '',
    affected_person_phone: '',
    notification_email: '',
    category_id: '',
    assigned_to: '',
    additional_emails: []
  });

  const [clients, setClients] = useState<any[]>([]);
  const [sites, setSites] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [technicians, setTechnicians] = useState<any[]>([]);
  const [filteredSites, setFilteredSites] = useState<any[]>([]);

  // Load data when component mounts
  useEffect(() => {
    loadData();
  }, []);

  // Filter sites when client changes
  useEffect(() => {
    if (formData.client_id) {
      const clientSites = sites.filter(site => site.client_id === formData.client_id);
      setFilteredSites(clientSites);
    } else {
      setFilteredSites([]);
    }
  }, [formData.client_id, sites]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load all data with correct API endpoints
      const [clientsRes, sitesRes, categoriesRes, techniciansRes] = await Promise.all([
        apiService.get('/clients'),
        apiService.get('/sites'),
        apiService.get('/categories/flat'),
        apiService.get('/users?role=technician&per_page=100')
      ]);

      // Process responses - ensure all are arrays
      const clientsData = Array.isArray(clientsRes?.data) ? clientsRes.data : [];
      const sitesData = Array.isArray(sitesRes?.data?.sites) ? sitesRes.data.sites :
                       Array.isArray(sitesRes?.data) ? sitesRes.data : [];
      const categoriesData = Array.isArray(categoriesRes?.data) ? categoriesRes.data : [];
      const techniciansData = Array.isArray(techniciansRes?.data) ? techniciansRes.data : [];

      setClients(clientsData);
      setSites(sitesData);
      setCategories(categoriesData);
      setTechnicians(techniciansData);

      // Auto-select for client users
      if ((user?.role === 'client_admin' || user?.role === 'solicitante') && user?.client_id) {
        setFormData(prev => ({ ...prev, client_id: user.client_id }));
        const userSites = sitesData.filter((site: any) => site.client_id === user.client_id);
        setFilteredSites(userSites);
      }

    } catch (err: any) {
      setError('Error al cargar datos');
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
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

      // Crear FormData para enviar archivos
      const formDataToSend = new FormData();

      // Agregar datos del ticket
      Object.entries(formData).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          formDataToSend.append(key, value.toString());
        }
      });

      formDataToSend.append('channel', 'portal');

      // Agregar archivos
      console.log('🔍 DEBUG: Attachments count:', attachments.length);
      attachments.forEach((file, index) => {
        console.log(`🔍 DEBUG: Adding file ${index}:`, file.name, file.size, file.type);
        formDataToSend.append(`attachments`, file);
      });

      // Debug: Log FormData contents
      console.log('🔍 DEBUG: FormData keys:', Array.from(formDataToSend.keys()));
      console.log('🔍 DEBUG: Files in FormData:', formDataToSend.getAll('attachments'));

      // Don't set Content-Type header for FormData - let browser set it with boundary
      const response = await apiService.post('/tickets/', formDataToSend);
      
      if (response?.ticket_id) {
        navigate(`/tickets/${response.ticket_id}`);
      } else {
        navigate('/tickets');
      }
      
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al crear el ticket');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center mb-4">
          <button
            onClick={() => navigate('/tickets')}
            className="mr-4 p-2 text-gray-400 hover:text-gray-600"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Crear Nuevo Ticket</h1>
        </div>
        <p className="text-sm text-gray-600">
          Complete la información para crear un nuevo ticket de soporte.
        </p>
      </div>

      {/* Form */}
      <div className="max-w-4xl">
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-700">{error}</div>
            </div>
          )}

          {/* Información Básica */}
          <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Información Básica</h3>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div className="sm:col-span-2">
                  <label htmlFor="subject" className="block text-sm font-medium text-gray-700">
                    Asunto *
                  </label>
                  <input
                    type="text"
                    name="subject"
                    id="subject"
                    required
                    value={formData.subject}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="Descripción breve del problema"
                  />
                </div>

                <div>
                  <label htmlFor="priority" className="block text-sm font-medium text-gray-700">
                    Prioridad *
                  </label>
                  <select
                    name="priority"
                    id="priority"
                    required
                    value={formData.priority}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  >
                    <option value="baja">Baja</option>
                    <option value="media">Media</option>
                    <option value="alta">Alta</option>
                    <option value="critica">Crítica</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="category_id" className="block text-sm font-medium text-gray-700">
                    Categoría
                  </label>
                  <select
                    name="category_id"
                    id="category_id"
                    value={formData.category_id}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  >
                    <option value="">Seleccionar categoría...</option>
                    {Array.isArray(categories) && categories.map((category) => (
                      <option key={category.category_id} value={category.category_id}>
                        {category.full_path || category.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="sm:col-span-2">
                  <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                    Descripción *
                  </label>
                  <textarea
                    name="description"
                    id="description"
                    required
                    rows={4}
                    value={formData.description}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="Describa el problema en detalle..."
                  />
                </div>

                <div className="sm:col-span-2">
                  <label htmlFor="affected_person" className="block text-sm font-medium text-gray-700">
                    Persona Afectada *
                  </label>
                  <div className="mt-1 relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <input
                      type="text"
                      name="affected_person"
                      id="affected_person"
                      required
                      value={formData.affected_person}
                      onChange={handleInputChange}
                      className="block w-full pl-10 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      placeholder="Nombre de la persona que experimenta el problema"
                    />
                  </div>
                </div>
              </div>
          </div>

          {/* Información de Contacto */}
          <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Información de Contacto</h3>

              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label htmlFor="affected_person_phone" className="block text-sm font-medium text-gray-700">
                    Teléfono
                  </label>
                  <div className="mt-1 relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <input
                      type="tel"
                      name="affected_person_phone"
                      id="affected_person_phone"
                      value={formData.affected_person_phone}
                      onChange={handleInputChange}
                      className="block w-full pl-10 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      placeholder="Teléfono (opcional)"
                    />
                  </div>
                </div>



              </div>

              <div className="mt-6">
                <label htmlFor="additional_emails" className="block text-sm font-medium text-gray-700">
                  Correos Adicionales
                </label>
                  <div className="mt-1 relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <input
                      type="text"
                      name="additional_emails"
                      id="additional_emails"
                      value={formData.additional_emails.join(', ')}
                      onChange={(e) => setFormData(prev => ({ ...prev, additional_emails: e.target.value.split(',').map(email => email.trim()) }))}
                      className="block w-full pl-10 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      placeholder="email1@ejemplo.com, email2@ejemplo.com"
                    />
                  </div>
                  <p className="mt-1 text-xs text-gray-500">
                    Separe múltiples correos con comas.
                  </p>
                </div>
              </div>
          </div>

          {/* Ubicación */}
          <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Ubicación</h3>

                <div>
                  <label htmlFor="client_id" className="block text-sm font-medium text-gray-700">
                    Cliente *
                  </label>
                  <select
                    name="client_id"
                    id="client_id"
                    required
                    value={formData.client_id}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    disabled={user?.role === 'client_admin' || user?.role === 'solicitante'}
                  >
                    <option value="">Seleccionar cliente...</option>
                    {Array.isArray(clients) && clients.map((client) => (
                      <option key={client.client_id} value={client.client_id}>
                        {client.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="site_id" className="block text-sm font-medium text-gray-700">
                    Sitio *
                  </label>
                  <select
                    name="site_id"
                    id="site_id"
                    required
                    value={formData.site_id}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    disabled={!formData.client_id}
                  >
                    <option value="">Seleccionar sitio...</option>
                    {Array.isArray(filteredSites) && filteredSites.map((site) => (
                      <option key={site.site_id} value={site.site_id}>
                        {site.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

          {/* Asignación (solo para admin/technician) */}
          {(user?.role === 'superadmin' || user?.role === 'admin' || user?.role === 'technician') && (
            <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Asignación</h3>

                <div>
                  <label htmlFor="assigned_to" className="block text-sm font-medium text-gray-700">
                    Asignar a
                  </label>
                  <select
                    name="assigned_to"
                    id="assigned_to"
                    value={formData.assigned_to}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  >
                    <option value="">Sin asignar</option>
                    {Array.isArray(technicians) && technicians.map((tech) => (
                      <option key={tech.user_id} value={tech.user_id}>
                        {tech.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
          )}

          {/* Archivos Adjuntos */}
          <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Archivos Adjuntos</h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Subir Archivos
                  </label>
                  <div className="flex items-center justify-center w-full">
                    <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                      <div className="flex flex-col items-center justify-center pt-5 pb-6">
                        <Upload className="w-8 h-8 mb-2 text-gray-400" />
                        <p className="mb-2 text-sm text-gray-500">
                          <span className="font-semibold">Haga clic para subir</span> o arrastre y suelte
                        </p>
                        <p className="text-xs text-gray-500">
                          PDF, DOC, DOCX, TXT, JPG, PNG (máx. 10MB por archivo)
                        </p>
                      </div>
                      <input
                        type="file"
                        multiple
                        accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                        onChange={handleFileChange}
                        className="hidden"
                      />
                    </label>
                  </div>
                </div>

                {/* Archivos seleccionados */}
                {attachments.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">
                      Archivos seleccionados ({attachments.length}):
                    </h4>
                    <div className="space-y-2">
                      {attachments.map((file, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center">
                            <FileText className="h-5 w-5 text-gray-400 mr-3" />
                            <div>
                              <p className="text-sm font-medium text-gray-900">{file.name}</p>
                              <p className="text-xs text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                            </div>
                          </div>
                          <button
                            type="button"
                            onClick={() => removeAttachment(index)}
                            className="text-red-400 hover:text-red-600"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
          </div>

          {/* Submit Buttons */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => navigate('/tickets')}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saving}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {saving ? 'Creando...' : 'Crear Ticket'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TicketCreatePageNew;
