import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Save } from 'lucide-react';
import { Ticket, ticketsService, UpdateTicketData } from '../../services/ticketsService';
import { usersService } from '../../services/usersService';
import { clientsService } from '../../services/clientsService';
import { sitesService } from '../../services/sitesService';
import { categoriesService } from '../../services/categoriesService';
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

const TicketEditPage: React.FC = () => {
  const { ticketId } = useParams<{ ticketId: string }>();
  const navigate = useNavigate();
  
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form data
  const [formData, setFormData] = useState<UpdateTicketData>({
    subject: '',
    description: '',
    priority: 'media',
    assigned_to: '',
    category_id: '',
    affected_person: '',
    affected_person_contact: ''
  });
  
  // Dropdown data
  const [technicians, setTechnicians] = useState<User[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);

  // Load initial data
  useEffect(() => {
    if (ticketId) {
      loadTicketData();
      loadDropdownData();
    }
  }, [ticketId]);

  const loadTicketData = async () => {
    if (!ticketId) return;

    try {
      setLoading(true);
      setError(null);

      const response = await ticketsService.getTicketById(ticketId);

      // Handle API response structure
      const ticketData = response.success ? response.data : response;

      if (!ticketData) {
        throw new Error('No se pudo cargar el ticket');
      }

      setTicket(ticketData);

      // Populate form with ticket data
      setFormData({
        subject: ticketData.subject || '',
        description: ticketData.description || '',
        priority: ticketData.priority || 'media',
        assigned_to: ticketData.assigned_to || '',
        category_id: ticketData.category_id || '',
        affected_person: ticketData.affected_person || '',
        affected_person_contact: ticketData.affected_person_contact || ''
      });

    } catch (err: any) {
      console.error('Error loading ticket:', err);
      setError(err.response?.data?.error || err.message || 'Error al cargar el ticket');
    } finally {
      setLoading(false);
    }
  };

  const loadDropdownData = async () => {
    try {
      const [techniciansResponse, clientsResponse, categoriesResponse] = await Promise.all([
        usersService.getUsersByRole('technician'),
        clientsService.getAllClients(),
        categoriesService.getFlatCategories()
      ]);

      // Handle API response structures
      const techniciansData = techniciansResponse?.data || techniciansResponse || [];
      const clientsData = clientsResponse?.data || clientsResponse || [];
      const categoriesData = categoriesResponse?.data || categoriesResponse || [];

      setTechnicians(Array.isArray(techniciansData) ? techniciansData : []);
      setClients(Array.isArray(clientsData) ? clientsData : []);
      setCategories(Array.isArray(categoriesData) ? categoriesData : []);

    } catch (err: any) {
      console.error('Error loading dropdown data:', err);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!ticketId) return;

    try {
      setSaving(true);
      setError(null);

      const response = await ticketsService.updateTicket(ticketId, formData);

      if (response.success) {
        // Navigate back to ticket detail
        navigate(`/tickets/${ticketId}`);
      } else {
        throw new Error(response.error || 'Error al actualizar el ticket');
      }

    } catch (err: any) {
      console.error('Error updating ticket:', err);
      setError(err.response?.data?.error || err.message || 'Error al actualizar el ticket');
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

  if (error && !ticket) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="mb-6">
            <button
              onClick={() => navigate('/tickets')}
              className="inline-flex items-center text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Volver a Tickets
            </button>
          </div>
          <ErrorMessage message={error} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate(`/tickets/${ticketId}`)}
                className="inline-flex items-center text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Volver al Ticket
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Editar Ticket {ticket?.ticket_number}
                </h1>
                <p className="text-gray-500">Modifica la información del ticket</p>
              </div>
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

            {/* Basic Information */}
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Información Básica</h2>
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
                  <label htmlFor="assigned_to" className="block text-sm font-medium text-gray-700 mb-1">
                    Asignado a
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
                    <option value="">Sin categoría</option>
                    {categories.map((category) => (
                      <option key={category.category_id} value={category.category_id}>
                        {category.full_path}
                      </option>
                    ))}
                  </select>
                </div>
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
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label htmlFor="affected_person_contact" className="block text-sm font-medium text-gray-700 mb-1">
                    Contacto *
                  </label>
                  <input
                    type="email"
                    id="affected_person_contact"
                    name="affected_person_contact"
                    value={formData.affected_person_contact}
                    onChange={handleInputChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Form Actions */}
            <div className="flex justify-end gap-3 pt-6 border-t border-gray-200">
              <button
                type="button"
                onClick={() => navigate(`/tickets/${ticketId}`)}
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
                {saving ? 'Guardando...' : 'Guardar Cambios'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default TicketEditPage;
