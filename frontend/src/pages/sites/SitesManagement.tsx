import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';
import { 
  Building2, 
  Search, 
  Plus, 
  Eye, 
  Edit, 
  Trash2, 
  MapPin, 
  Ticket,
  ChevronLeft,
  ChevronRight,
  Filter
} from 'lucide-react';
import SiteForm from '../../components/sites/SiteForm';
import SiteDetail from '../../components/sites/SiteDetail';

interface Site {
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
  client_name?: string;
  assigned_users?: number;
  total_tickets?: number;
}

interface Client {
  client_id: string;
  name: string;
}

const SitesManagement: React.FC = () => {
  const { user } = useAuth();
  const [allSites, setAllSites] = useState<Site[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedClient, setSelectedClient] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedSite, setSelectedSite] = useState<Site | null>(null);
  const itemsPerPage = 10;

  // Check permissions
  const canManageSites = user?.role === 'superadmin' || user?.role === 'admin';
  const canViewAllSites = user?.role === 'superadmin' || user?.role === 'admin' || user?.role === 'technician';

  // Filter sites based on search term and selected client
  const filteredSites = useMemo(() => {
    let filtered = allSites;

    // Filter by client if selected
    if (selectedClient) {
      filtered = filtered.filter(site => site.client_id === selectedClient);
    }

    // Filter by search term
    if (searchTerm.trim()) {
      const searchLower = searchTerm.toLowerCase().trim();
      filtered = filtered.filter(site => 
        site.name.toLowerCase().includes(searchLower) ||
        site.client_name?.toLowerCase().includes(searchLower) ||
        site.city.toLowerCase().includes(searchLower) ||
        site.address.toLowerCase().includes(searchLower)
      );
    }

    return filtered;
  }, [allSites, searchTerm, selectedClient]);

  // Calculate pagination for filtered results
  const paginatedSites = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredSites.slice(startIndex, endIndex);
  }, [filteredSites, currentPage, itemsPerPage]);

  // Update total pages when filtered sites change
  const totalPages = Math.ceil(filteredSites.length / itemsPerPage);

  useEffect(() => {
    // Reset to page 1 if current page is beyond available pages
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(1);
    }
  }, [filteredSites.length, currentPage, totalPages]);

  // Load data on component mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load sites and clients in parallel
      const [sitesResponse, clientsResponse] = await Promise.all([
        apiService.get('/sites?per_page=1000'),
        apiService.get('/clients?per_page=1000')
      ]);
      
      if (sitesResponse.success) {
        setAllSites(sitesResponse.data.sites || sitesResponse.data || []);
      }
      
      if (clientsResponse.success) {
        setClients(clientsResponse.data.clients || clientsResponse.data || []);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSite = () => {
    setSelectedSite(null);
    setShowCreateForm(true);
  };

  const handleEditSite = (site: Site) => {
    setSelectedSite(site);
    setShowEditForm(true);
  };

  const handleViewSite = (site: Site) => {
    setSelectedSite(site);
    setShowDetailModal(true);
  };

  const handleDeleteSite = async (site: Site) => {
    const confirmed = window.confirm(
      `¿Estás seguro de que deseas eliminar el sitio "${site.name}"? Esta acción no se puede deshacer.`
    );

    if (confirmed) {
      try {
        const response = await apiService.delete(`/sites/${site.site_id}`);
        if (response.success) {
          await loadData(); // Reload data
        }
      } catch (error) {
        console.error('Error deleting site:', error);
      }
    }
  };

  const handleFormSuccess = () => {
    setShowCreateForm(false);
    setShowEditForm(false);
    setSelectedSite(null);
    loadData(); // Reload data
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Building2 className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Gestión de Sitios</h1>
              <p className="text-gray-600">Administra las ubicaciones de todos los clientes</p>
            </div>
          </div>
          
          {canManageSites && (
            <button
              onClick={handleCreateSite}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Plus className="w-4 h-4 mr-2" />
              Nuevo Sitio
            </button>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Buscar sitios por nombre, cliente, ciudad..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Client Filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <select
              value={selectedClient}
              onChange={(e) => setSelectedClient(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
            >
              <option value="">Todos los clientes</option>
              {clients.map((client) => (
                <option key={client.client_id} value={client.client_id}>
                  {client.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Sites Table */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Sitio
                </th>
                <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cliente
                </th>
                <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ubicación
                </th>
                <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estadísticas
                </th>
                <th className="hidden sm:table-cell px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {paginatedSites.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-3 sm:px-6 py-12 text-center text-gray-500">
                    <Building2 className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p className="text-lg font-medium">No se encontraron sitios</p>
                    <p className="text-sm">
                      {searchTerm || selectedClient ? 'Intenta con otros filtros de búsqueda' : 'Comienza creando tu primer sitio'}
                    </p>
                  </td>
                </tr>
              ) : (
                paginatedSites.map((site) => (
                  <tr key={site.site_id} className="hover:bg-gray-50">
                    <td className="px-3 sm:px-6 py-4">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-8 w-8 sm:h-10 sm:w-10">
                          <div className="h-8 w-8 sm:h-10 sm:w-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <Building2 className="h-4 w-4 sm:h-5 sm:w-5 text-blue-600" />
                          </div>
                        </div>
                        <div className="ml-3 sm:ml-4">
                          <div className="text-sm font-medium text-gray-900 truncate max-w-[150px] sm:max-w-none">
                            {site.name}
                          </div>
                          <div className="text-sm text-gray-500 truncate max-w-[150px] sm:max-w-none">
                            ID: {site.site_id.slice(0, 8)}...
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-3 sm:px-6 py-4">
                      <div className="text-sm font-medium text-gray-900 truncate max-w-[150px] sm:max-w-none">
                        {site.client_name}
                      </div>
                    </td>
                    <td className="px-3 sm:px-6 py-4">
                      <div className="text-sm text-gray-900">
                        <div className="flex items-center">
                          <MapPin className="w-3 h-3 mr-1 text-gray-400 flex-shrink-0" />
                          <span className="truncate">{site.city}, {site.state}</span>
                        </div>
                        <div className="text-xs text-gray-500 truncate mt-1">
                          {site.address}
                        </div>
                      </div>
                    </td>
                    <td className="px-3 sm:px-6 py-4">
                      <div className="flex items-center text-orange-600">
                        <Ticket className="w-4 h-4 mr-2 flex-shrink-0" />
                        <span className="font-semibold">{site.total_tickets || 0}</span>
                        <span className="ml-1 text-sm">tickets</span>
                      </div>
                    </td>
                    <td className="hidden sm:table-cell px-3 sm:px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        site.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {site.is_active ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleViewSite(site)}
                          className="text-blue-600 hover:text-blue-900 p-1"
                          title="Ver detalles"
                        >
                          <Eye className="w-3 h-3 sm:w-4 sm:h-4" />
                        </button>
                        {canManageSites && (
                          <>
                            <button
                              onClick={() => handleEditSite(site)}
                              className="text-yellow-600 hover:text-yellow-900 p-1"
                              title="Editar"
                            >
                              <Edit className="w-3 h-3 sm:w-4 sm:h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteSite(site)}
                              className="text-red-600 hover:text-red-900 p-1"
                              title="Eliminar"
                            >
                              <Trash2 className="w-3 h-3 sm:w-4 sm:h-4" />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
            <div className="flex items-center justify-between">
              <div className="flex-1 flex justify-between sm:hidden">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                >
                  Anterior
                </button>
                <button
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                  className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                >
                  Siguiente
                </button>
              </div>
              <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700">
                    Mostrando <span className="font-medium">{((currentPage - 1) * itemsPerPage) + 1}</span> a{' '}
                    <span className="font-medium">{Math.min(currentPage * itemsPerPage, filteredSites.length)}</span> de{' '}
                    <span className="font-medium">{filteredSites.length}</span> sitios
                    {(searchTerm || selectedClient) && (
                      <span className="text-gray-500"> (filtrados de {allSites.length} total)</span>
                    )}
                  </p>
                </div>
                <div>
                  <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                    <button
                      onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                      disabled={currentPage === 1}
                      className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                    >
                      Anterior
                    </button>
                    <button
                      onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                      disabled={currentPage === totalPages}
                      className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                    >
                      Siguiente
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      {showCreateForm && (
        <SiteForm
          isOpen={showCreateForm}
          onClose={() => setShowCreateForm(false)}
          onSuccess={handleFormSuccess}
        />
      )}

      {showEditForm && selectedSite && (
        <SiteForm
          isOpen={showEditForm}
          onClose={() => setShowEditForm(false)}
          onSuccess={handleFormSuccess}
          site={selectedSite}
          clientId={selectedSite.client_id}
        />
      )}

      {showDetailModal && selectedSite && (
        <SiteDetail
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          site={selectedSite}
        />
      )}
    </div>
  );
};

export default SitesManagement;
