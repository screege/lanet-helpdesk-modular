import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  Building2,
  Users,
  MapPin,
  Plus,
  Search,
  Eye,
  Edit,
  Trash2,
  Filter,
  Ticket
} from 'lucide-react';
import { apiService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

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
  created_at: string;
  is_active: boolean;
}

const ClientList: React.FC = () => {
  const { user } = useAuth();
  const [allClients, setAllClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const itemsPerPage = 10;

  // Filter clients based on search term (instant filtering)
  const filteredClients = useMemo(() => {
    if (!searchTerm.trim()) {
      return allClients;
    }

    const searchLower = searchTerm.toLowerCase().trim();
    return allClients.filter(client =>
      client.name.toLowerCase().includes(searchLower) ||
      client.email.toLowerCase().includes(searchLower) ||
      (client.rfc && client.rfc.toLowerCase().includes(searchLower))
    );
  }, [allClients, searchTerm]);

  // Calculate pagination for filtered results
  const paginatedClients = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredClients.slice(startIndex, endIndex);
  }, [filteredClients, currentPage, itemsPerPage]);

  // Update total pages when filtered clients change
  useEffect(() => {
    const newTotalPages = Math.ceil(filteredClients.length / itemsPerPage);
    setTotalPages(newTotalPages);

    // Reset to page 1 if current page is beyond available pages
    if (currentPage > newTotalPages && newTotalPages > 0) {
      setCurrentPage(1);
    }
  }, [filteredClients.length, itemsPerPage, currentPage]);

  // Load all clients once on component mount
  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async () => {
    try {
      setLoading(true);
      // Load all clients for client-side filtering and pagination
      const response = await apiService.get('/clients?per_page=1000');

      if (response.success) {
        setAllClients(response.data.clients || response.data || []);
        console.log('✅ All clients loaded for filtering:', response.data);
      } else {
        console.error('Failed to load clients:', response.error);
        setAllClients([]);
      }
    } catch (error) {
      console.error('Error loading clients:', error);
      setAllClients([]);
    } finally {
      setLoading(false);
    }
  };



  const handleDeleteClient = async (client: Client) => {
    const confirmed = window.confirm(
      `¿Estás seguro de que deseas eliminar el cliente "${client.name}"? Esta acción no se puede deshacer.`
    );

    if (confirmed) {
      try {
        const response = await apiService.delete(`/clients/${client.client_id}`);
        if (response.success) {
          // Reload the clients list
          await loadClients();
          // Show success message (you could use a toast notification here)
          console.log(`Cliente "${client.name}" eliminado exitosamente`);
        } else {
          alert('Error al eliminar el cliente: ' + (response.error || 'Error desconocido'));
        }
      } catch (error) {
        console.error('Error deleting client:', error);
        alert('Error al eliminar el cliente');
      }
    }
  };

  const canCreateClients = user?.role === 'superadmin' || user?.role === 'admin';

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gestión de Clientes</h1>
          <p className="text-gray-600">Administra las organizaciones del sistema MSP</p>
        </div>
        {canCreateClients && (
          <Link
            to="/clients/create"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4 mr-2" />
            Nuevo Cliente
          </Link>
        )}
      </div>

      {/* Search */}
      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Buscar clientes por nombre, email o RFC..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Clients Table */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cliente
                </th>
                <th className="hidden md:table-cell px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contacto
                </th>
                <th className="hidden lg:table-cell px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ubicación
                </th>
                <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estadísticas
                </th>
                <th className="hidden sm:table-cell px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {paginatedClients.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-3 sm:px-6 py-12 text-center text-gray-500">
                    <Building2 className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p className="text-lg font-medium">No se encontraron clientes</p>
                    <p className="text-sm">
                      {searchTerm ? 'Intenta con otros términos de búsqueda' : 'Comienza creando tu primer cliente'}
                    </p>
                  </td>
                </tr>
              ) : (
                paginatedClients.map((client) => (
                  <tr key={client.client_id} className="hover:bg-gray-50">
                    <td className="px-3 sm:px-6 py-4">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-8 w-8 sm:h-10 sm:w-10">
                          <div className="h-8 w-8 sm:h-10 sm:w-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <Building2 className="w-4 h-4 sm:w-5 sm:h-5 text-blue-600" />
                          </div>
                        </div>
                        <div className="ml-3 sm:ml-4 min-w-0 flex-1">
                          <div className="text-sm font-medium text-gray-900 truncate">{client.name}</div>
                          {client.rfc && (
                            <div className="text-xs sm:text-sm text-gray-500 truncate">RFC: {client.rfc}</div>
                          )}
                          {/* Show contact info on mobile */}
                          <div className="md:hidden mt-1">
                            <div className="text-xs text-gray-600 truncate">{client.email}</div>
                            {client.phone && (
                              <div className="text-xs text-gray-500">{client.phone}</div>
                            )}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="hidden md:table-cell px-3 sm:px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 truncate">{client.email}</div>
                      {client.phone && (
                        <div className="text-sm text-gray-500">{client.phone}</div>
                      )}
                    </td>
                    <td className="hidden lg:table-cell px-3 sm:px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-sm text-gray-500">
                        <MapPin className="w-4 h-4 mr-1 flex-shrink-0" />
                        <div className="min-w-0">
                          {client.city && client.state ? (
                            <div className="truncate">{client.city}, {client.state}</div>
                          ) : (
                            <div className="text-gray-400">No especificada</div>
                          )}
                          {client.country && (
                            <div className="text-xs truncate">{client.country}</div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-3 sm:px-6 py-4">
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-2 sm:gap-3 text-xs sm:text-sm">
                        <div className="flex items-center text-gray-600">
                          <MapPin className="w-4 h-4 mr-2 flex-shrink-0 text-blue-500" />
                          <span className="font-medium">{client.total_sites || 0}</span>
                          <span className="ml-1 text-gray-500">sitios</span>
                        </div>
                        <div className="flex items-center text-orange-600">
                          <Ticket className="w-4 h-4 mr-2 flex-shrink-0" />
                          <span className="font-semibold">{client.open_tickets || 0}</span>
                          <span className="ml-1">tickets abiertos</span>
                        </div>
                      </div>
                    </td>
                    <td className="hidden sm:table-cell px-3 sm:px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        client.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {client.is_active ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-1 sm:space-x-2">
                        <Link
                          to={`/clients/${client.client_id}`}
                          className="text-blue-600 hover:text-blue-900 p-1 rounded"
                          title="Ver detalles"
                        >
                          <Eye className="w-3 h-3 sm:w-4 sm:h-4" />
                        </Link>
                        {canCreateClients && (
                          <>
                            <Link
                              to={`/clients/${client.client_id}/edit`}
                              className="text-indigo-600 hover:text-indigo-900 p-1 rounded"
                              title="Editar"
                            >
                              <Edit className="w-3 h-3 sm:w-4 sm:h-4" />
                            </Link>
                            <button
                              className="text-red-600 hover:text-red-900 p-1 rounded"
                              title="Eliminar"
                              onClick={() => handleDeleteClient(client)}
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
                    <span className="font-medium">{Math.min(currentPage * itemsPerPage, filteredClients.length)}</span> de{' '}
                    <span className="font-medium">{filteredClients.length}</span> clientes
                    {searchTerm && (
                      <span className="text-gray-500"> (filtrados de {allClients.length} total)</span>
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
    </div>
  );
};

export default ClientList;
