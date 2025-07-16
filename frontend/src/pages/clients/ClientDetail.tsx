import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Building2,
  Mail,
  Phone,
  MapPin,
  Users,
  ArrowLeft,
  Edit,
  Trash2,
  Calendar,
  FileText,
  Plus,
  Eye
} from 'lucide-react';
import { apiService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import SiteForm from '../../components/sites/SiteForm';
import SiteDetail from '../../components/sites/SiteDetail';
import TokenManagement from '../../components/agents/TokenManagement';
import { Site } from '../../services/sitesService';

interface Client {
  client_id: string;
  name: string;
  email: string;
  rfc?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  total_users?: number;
  total_sites?: number;
  total_tickets?: number;
  open_tickets?: number;
  resolved_tickets?: number;
  tickets_last_30_days?: number;
  created_at: string;
  is_active: boolean;
}

interface ClientStats {
  client_name: string;
  total_sites: number;
  total_users: number;
  total_tickets: number;
  open_tickets: number;
  resolved_tickets: number;
  tickets_last_30_days: number;
}



interface User {
  user_id: string;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
}

const ClientDetail: React.FC = () => {
  const { clientId } = useParams<{ clientId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [client, setClient] = useState<Client | null>(null);
  const [sites, setSites] = useState<Site[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [stats, setStats] = useState<ClientStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Site management states
  const [showCreateSiteForm, setShowCreateSiteForm] = useState(false);
  const [showEditSiteForm, setShowEditSiteForm] = useState(false);
  const [showSiteDetail, setShowSiteDetail] = useState(false);
  const [selectedSite, setSelectedSite] = useState<Site | null>(null);



  const canEditClients = user?.role === 'superadmin' || user?.role === 'admin';
  const canManageSites = user?.role === 'superadmin' || user?.role === 'admin';
  const canManageTokens = user?.role === 'superadmin' || user?.role === 'technician';

  useEffect(() => {
    if (clientId) {
      loadClientData();
    }
  }, [clientId]);

  const loadClientData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load client details
      const clientResponse = await apiService.get(`/clients/${clientId}`);
      if (clientResponse.success) {
        // Type guard crítico para datos de cliente
        if (clientResponse.data && typeof clientResponse.data === 'object') {
          setClient(clientResponse.data as Client);
        } else {
          throw new Error('Invalid client data received');
        }
      } else {
        setError('Error al cargar los datos del cliente');
        return;
      }

      // Load client statistics
      const statsResponse = await apiService.get(`/clients/${clientId}/stats`);
      if (statsResponse.success) {
        // Type guard para estadísticas del cliente
        if (statsResponse.data && typeof statsResponse.data === 'object') {
          setStats(statsResponse.data as ClientStats);
        } else {
          console.warn('Invalid client stats format');
        }
      }

      // Load client sites
      const sitesResponse = await apiService.get(`/clients/${clientId}/sites`);
      if (sitesResponse.success) {
        // Type guard para sitios del cliente
        if (sitesResponse.data && Array.isArray(sitesResponse.data)) {
          setSites(sitesResponse.data as Site[]);
        } else {
          console.warn('Invalid sites data format');
          setSites([]);
        }
      }

      // Load client users
      const usersResponse = await apiService.get(`/clients/${clientId}/users`);
      if (usersResponse.success) {
        // Type guard para usuarios del cliente
        if (usersResponse.data && Array.isArray(usersResponse.data)) {
          setUsers(usersResponse.data as User[]);
        } else {
          console.warn('Invalid users data format');
          setUsers([]);
        }
      }

    } catch (error) {
      console.error('Error loading client data:', error);
      setError('Error al cargar los datos del cliente');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!client || !canEditClients) return;

    const confirmed = window.confirm(
      `¿Estás seguro de que deseas eliminar el cliente "${client.name}"? Esta acción no se puede deshacer.`
    );

    if (confirmed) {
      try {
        const response = await apiService.delete(`/clients/${client.client_id}`);
        if (response.success) {
          navigate('/clients', { 
            state: { 
              message: `Cliente "${client.name}" eliminado exitosamente` 
            }
          });
        } else {
          setError('Error al eliminar el cliente');
        }
      } catch (error) {
        console.error('Error deleting client:', error);
        setError('Error al eliminar el cliente');
      }
    }
  };

  // Site management functions
  const handleCreateSite = () => {
    setSelectedSite(null);
    setShowCreateSiteForm(true);
  };

  const handleEditSite = (site: Site) => {
    setSelectedSite(site);
    setShowEditSiteForm(true);
  };

  const handleViewSite = (site: Site) => {
    setSelectedSite(site);
    setShowSiteDetail(true);
  };

  const handleDeleteSite = async (site: Site) => {
    const confirmed = window.confirm(
      `¿Estás seguro de que deseas eliminar el sitio "${site.name}"? Esta acción no se puede deshacer.`
    );

    if (confirmed) {
      try {
        const response = await apiService.delete(`/sites/${site.site_id}`);

        if (response.success) {
          // Show success message
          setError(null);

          // Reload sites data
          const sitesResponse = await apiService.get(`/clients/${clientId}/sites`);
          if (sitesResponse.success) {
            setSites(sitesResponse.data as Site[]);
          }

          // Show success notification (you could use a toast here)
          console.log(`Sitio "${site.name}" eliminado exitosamente`);
        } else {
          // Display specific error message from backend
          let errorMessage = 'Error al eliminar el sitio';

          if (response.error) {
            // Translate common backend error messages to Spanish
            if (response.error.includes('active tickets')) {
              errorMessage = response.error.replace('Cannot delete site with', 'No se puede eliminar el sitio con')
                                        .replace('active tickets. Close all tickets first.', 'tickets activos. Cierre todos los tickets primero.');
            } else if (response.error === 'Site not found') {
              errorMessage = 'El sitio no fue encontrado';
            } else if (response.error === 'Failed to delete site') {
              errorMessage = 'Error al eliminar el sitio';
            } else {
              errorMessage = response.error;
            }
          }

          setError(errorMessage);
        }
      } catch (error) {
        console.error('Error deleting site:', error);
        setError('Error al eliminar el sitio');
      }
    }
  };

  const handleSiteFormSuccess = async () => {
    setShowCreateSiteForm(false);
    setShowEditSiteForm(false);
    setSelectedSite(null);

    // Reload sites data
    try {
      const sitesResponse = await apiService.get(`/clients/${clientId}/sites`);
      if (sitesResponse.success) {
        setSites(sitesResponse.data as Site[]);
      }
    } catch (error) {
      console.error('Error reloading sites:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !client) {
    return (
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/clients')}
            className="inline-flex items-center text-blue-600 hover:text-blue-800"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Volver a Clientes
          </button>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error || 'Cliente no encontrado'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/clients')}
            className="inline-flex items-center text-blue-600 hover:text-blue-800"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Volver a Clientes
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{client.name}</h1>
            <p className="text-gray-600">Detalles del cliente</p>
          </div>
        </div>
        
        {canEditClients && (
          <div className="flex items-center space-x-3">
            <Link
              to={`/clients/${client.client_id}/edit`}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700"
            >
              <Edit className="w-4 h-4 mr-2" />
              Editar
            </Link>
            <button
              onClick={handleDelete}
              className="inline-flex items-center px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Eliminar
            </button>
          </div>
        )}
      </div>

      {/* Client Information */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Información General</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
                <div className="flex items-center">
                  <Building2 className="w-4 h-4 text-gray-400 mr-2" />
                  <span className="text-gray-900">{client.name}</span>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <div className="flex items-center">
                  <Mail className="w-4 h-4 text-gray-400 mr-2" />
                  <a href={`mailto:${client.email}`} className="text-blue-600 hover:text-blue-800">
                    {client.email}
                  </a>
                </div>
              </div>

              {client.rfc && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">RFC</label>
                  <div className="flex items-center">
                    <FileText className="w-4 h-4 text-gray-400 mr-2" />
                    <span className="text-gray-900">{client.rfc}</span>
                  </div>
                </div>
              )}

              {client.phone && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
                  <div className="flex items-center">
                    <Phone className="w-4 h-4 text-gray-400 mr-2" />
                    <a href={`tel:${client.phone}`} className="text-blue-600 hover:text-blue-800">
                      {client.phone}
                    </a>
                  </div>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Estado</label>
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  client.is_active 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {client.is_active ? 'Activo' : 'Inactivo'}
                </span>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Fecha de Creación</label>
                <div className="flex items-center">
                  <Calendar className="w-4 h-4 text-gray-400 mr-2" />
                  <span className="text-gray-900">
                    {new Date(client.created_at).toLocaleDateString('es-ES')}
                  </span>
                </div>
              </div>
            </div>

            {/* Address */}
            {(client.address || client.city || client.state || client.country) && (
              <div className="mt-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">Dirección</label>
                <div className="flex items-start">
                  <MapPin className="w-4 h-4 text-gray-400 mr-2 mt-1" />
                  <div className="text-gray-900">
                    {client.address && <div>{client.address}</div>}
                    <div>
                      {[client.city, client.state, client.postal_code].filter(Boolean).join(', ')}
                    </div>
                    {client.country && <div>{client.country}</div>}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Estadísticas</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Users className="w-4 h-4 text-gray-400 mr-2" />
                  <span className="text-sm text-gray-600">Usuarios</span>
                </div>
                <span className="text-lg font-semibold text-gray-900">
                  {stats?.total_users || users.length || 0}
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <MapPin className="w-4 h-4 text-gray-400 mr-2" />
                  <span className="text-sm text-gray-600">Sitios</span>
                </div>
                <span className="text-lg font-semibold text-gray-900">
                  {stats?.total_sites || sites.length || 0}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <FileText className="w-4 h-4 text-gray-400 mr-2" />
                  <span className="text-sm text-gray-600">Tickets</span>
                </div>
                <span className="text-lg font-semibold text-gray-900">
                  {stats?.total_tickets || 0}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sites and Users */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sites */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Sitios</h2>
            {canManageSites && (
              <button
                onClick={handleCreateSite}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                title="Agregar Sitio"
              >
                <Plus className="w-4 h-4 mr-1" />
                Agregar Sitio
              </button>
            )}
          </div>

          {sites.length > 0 ? (
            <div className="space-y-3">
              {sites.map((site) => (
                <div key={site.site_id} className="border border-gray-200 rounded-lg">
                  {/* Site Header */}
                  <div className="p-4 border-b border-gray-200">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h3 className="font-medium text-gray-900">{site.name}</h3>
                          <div className="flex items-center space-x-2">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              site.is_active
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {site.is_active ? 'Activo' : 'Inactivo'}
                            </span>

                            {/* Action buttons */}
                            <div className="flex items-center space-x-1">
                              <button
                                onClick={() => handleViewSite(site)}
                                className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                                title="Ver Detalles"
                              >
                                <Eye className="w-4 h-4" />
                              </button>

                              {canManageSites && (
                                <>
                                  <button
                                    onClick={() => handleEditSite(site)}
                                    className="p-1 text-gray-400 hover:text-yellow-600 transition-colors"
                                    title="Editar Sitio"
                                  >
                                    <Edit className="w-4 h-4" />
                                  </button>

                                  <button
                                    onClick={() => handleDeleteSite(site)}
                                    className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                                    title="Eliminar Sitio"
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </button>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">
                          {site.address}, {site.city}, {site.state} {site.postal_code}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Tokens Section for this Site */}
                  {canManageTokens && (
                    <div className="p-4 bg-gray-50">
                      <TokenManagement
                        clientId={clientId!}
                        siteId={site.site_id}
                        clientName={client.name}
                        siteName={site.name}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <MapPin className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No hay sitios registrados</h3>
              <p className="mt-1 text-sm text-gray-500">
                Comienza agregando un sitio para este cliente.
              </p>
              {canManageSites && (
                <div className="mt-6">
                  <button
                    onClick={handleCreateSite}
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Agregar Primer Sitio
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Users */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Usuarios</h2>
          {users.length > 0 ? (
            <div className="space-y-3">
              {users.map((user) => (
                <div key={user.user_id} className="border border-gray-200 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-medium text-gray-900">{user.name}</h3>
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      user.is_active 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {user.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">{user.email}</p>
                  <p className="text-xs text-gray-500 capitalize">{user.role.replace('_', ' ')}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No hay usuarios registrados</p>
          )}
        </div>
      </div>



      {/* Site Modals */}
      {showCreateSiteForm && (
        <SiteForm
          isOpen={showCreateSiteForm}
          onClose={() => setShowCreateSiteForm(false)}
          onSuccess={handleSiteFormSuccess}
          clientId={clientId}
        />
      )}

      {showEditSiteForm && selectedSite && (
        <SiteForm
          isOpen={showEditSiteForm}
          onClose={() => setShowEditSiteForm(false)}
          onSuccess={handleSiteFormSuccess}
          site={selectedSite}
          clientId={clientId}
        />
      )}

      {showSiteDetail && selectedSite && (
        <SiteDetail
          isOpen={showSiteDetail}
          onClose={() => setShowSiteDetail(false)}
          site={selectedSite}
        />
      )}


    </div>
  );
};

export default ClientDetail;
