import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, Filter, Eye, Edit, Trash2, UserPlus, Clock, AlertCircle, Ticket as TicketIcon } from 'lucide-react';
import { ticketsService, Ticket, TicketFilters } from '../../services/ticketsService';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ErrorMessage from '../../components/common/ErrorMessage';

const TicketsManagement: React.FC = () => {
  const navigate = useNavigate();

  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<TicketFilters>({
    page: 1,
    per_page: 20
  });
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    total_pages: 0
  });

  // Load tickets
  const loadTickets = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const searchFilters = {
        ...filters,
        search: searchTerm || undefined
      };
      
      const response = await ticketsService.getAllTickets(searchFilters);
      setTickets(response.tickets);
      setPagination(response.pagination);
    } catch (err: any) {
      console.error('Error loading tickets:', err);
      setError(err.response?.data?.message || 'Error al cargar tickets');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTickets();
  }, [filters]);

  // Handle search
  const handleSearch = () => {
    setFilters(prev => ({ ...prev, page: 1 }));
    loadTickets();
  };

  // Handle filter change
  const handleFilterChange = (key: keyof TicketFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      page: 1 // Reset to first page when filtering
    }));
  };

  // Handle page change
  const handlePageChange = (newPage: number) => {
    setFilters(prev => ({ ...prev, page: newPage }));
  };



  // Handle view ticket
  const handleViewTicket = (ticket: Ticket) => {
    navigate(`/tickets/${ticket.ticket_id}`);
  };

  // Handle edit ticket modal
  const handleEditTicketModal = (ticket: Ticket) => {
    navigate(`/tickets/${ticket.ticket_id}/edit`);
  };

  // Get priority badge color
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critica': return 'bg-red-100 text-red-800 border-red-200';
      case 'alta': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'media': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'baja': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Get status badge color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'nuevo': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'asignado': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'en_proceso': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'espera_cliente': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'resuelto': return 'bg-green-100 text-green-800 border-green-200';
      case 'reabierto': return 'bg-red-100 text-red-800 border-red-200';
      case 'cerrado': return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'cancelado': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Format status text
  const formatStatus = (status: string) => {
    const statusMap: { [key: string]: string } = {
      'nuevo': 'Nuevo',
      'asignado': 'Asignado',
      'en_proceso': 'En Proceso',
      'espera_cliente': 'Espera Cliente',
      'resuelto': 'Resuelto',
      'reabierto': 'Reabierto',
      'cerrado': 'Cerrado',
      'cancelado': 'Cancelado',
      'pendiente_aprobacion': 'Pendiente Aprobación'
    };
    return statusMap[status] || status;
  };

  // Format priority text
  const formatPriority = (priority: string) => {
    const priorityMap: { [key: string]: string } = {
      'baja': 'Baja',
      'media': 'Media',
      'alta': 'Alta',
      'critica': 'Crítica'
    };
    return priorityMap[priority] || priority;
  };

  if (loading && tickets.length === 0) {
    return <LoadingSpinner />;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <TicketIcon className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Gestión de Tickets</h1>
              <p className="text-gray-600">Administra todos los tickets del sistema</p>
            </div>
          </div>
          <button
            onClick={() => navigate('/tickets/new')}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Plus className="w-4 h-4 mr-2" />
            Nuevo Ticket
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Buscar tickets..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Status Filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <select
              value={filters.status || ''}
              onChange={(e) => handleFilterChange('status', e.target.value || undefined)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
            >
              <option value="">Todos los estados</option>
              <option value="nuevo">Nuevo</option>
              <option value="asignado">Asignado</option>
              <option value="en_proceso">En Proceso</option>
              <option value="espera_cliente">Espera Cliente</option>
              <option value="resuelto">Resuelto</option>
              <option value="cerrado">Cerrado</option>
            </select>
          </div>

          {/* Priority Filter */}
          <div className="relative">
            <AlertCircle className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <select
              value={filters.priority || ''}
              onChange={(e) => handleFilterChange('priority', e.target.value || undefined)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
            >
              <option value="">Todas las prioridades</option>
              <option value="critica">Crítica</option>
              <option value="alta">Alta</option>
              <option value="media">Media</option>
              <option value="baja">Baja</option>
            </select>
          </div>

          {/* Clear Filters */}
          <div className="flex items-end">
            <button
              onClick={() => {
                setSearchTerm('');
                setFilters({ page: 1, per_page: 20 });
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Limpiar Filtros
            </button>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && <ErrorMessage message={error} />}

      {/* Tickets Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24">
                  Ticket
                </th>
                <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-0">
                  Cliente/Sitio
                </th>
                <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-0">
                  Asunto
                </th>
                <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-20">
                  Estado
                </th>
                <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-20">
                  Prioridad
                </th>
                <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24 hidden sm:table-cell">
                  Asignado
                </th>
                <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-20 hidden md:table-cell">
                  Creado
                </th>
                <th className="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider w-20">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tickets.map((ticket) => (
                <tr key={ticket.ticket_id} className="hover:bg-gray-50">
                  <td className="px-3 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {ticket.ticket_number}
                        </div>
                        <div className="text-xs text-gray-500">
                          {ticket.channel === 'email' && <span className="text-blue-600">📧</span>}
                          {ticket.channel === 'portal' && <span className="text-green-600">🌐</span>}
                          {ticket.channel === 'phone' && <span className="text-yellow-600">📞</span>}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-3 py-4 min-w-0">
                    <div className="text-sm text-gray-900 truncate">{ticket.client_name}</div>
                    <div className="text-xs text-gray-500 truncate">{ticket.site_name}</div>
                  </td>
                  <td className="px-3 py-4 min-w-0">
                    <div className="text-sm text-gray-900 truncate max-w-xs" title={ticket.subject}>
                      {ticket.subject}
                    </div>
                    <div className="text-xs text-gray-500 truncate">
                      {ticket.affected_person}
                    </div>
                  </td>
                  <td className="px-3 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-1 py-1 text-xs font-semibold rounded-full border ${getStatusColor(ticket.status)}`}>
                      {formatStatus(ticket.status)}
                    </span>
                  </td>
                  <td className="px-3 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-1 py-1 text-xs font-semibold rounded-full border ${getPriorityColor(ticket.priority)}`}>
                      {formatPriority(ticket.priority)}
                    </span>
                  </td>
                  <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900 hidden sm:table-cell">
                    <div className="truncate max-w-24">
                      {ticket.assigned_to_name || (
                        <span className="text-gray-400 italic">Sin asignar</span>
                      )}
                    </div>
                  </td>
                  <td className="px-3 py-4 whitespace-nowrap text-xs text-gray-500 hidden md:table-cell">
                    {new Date(ticket.created_at).toLocaleDateString('es-ES')}
                  </td>
                  <td className="px-3 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end gap-1">
                      <button
                        onClick={() => handleViewTicket(ticket)}
                        className="text-blue-600 hover:text-blue-900 p-1 rounded"
                        title="Ver ticket"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleEditTicketModal(ticket)}
                        className="text-yellow-600 hover:text-yellow-900 p-1 rounded"
                        title="Editar ticket"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      {!ticket.assigned_to && (
                        <button
                          onClick={() => handleAssignTicket(ticket)}
                          className="text-green-600 hover:text-green-900 p-1 rounded"
                          title="Asignar ticket"
                        >
                          <UserPlus className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {pagination.total_pages > 1 && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => handlePageChange(pagination.page - 1)}
                disabled={pagination.page <= 1}
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Anterior
              </button>
              <button
                onClick={() => handlePageChange(pagination.page + 1)}
                disabled={pagination.page >= pagination.total_pages}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Siguiente
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Mostrando <span className="font-medium">{((pagination.page - 1) * pagination.per_page) + 1}</span> a{' '}
                  <span className="font-medium">
                    {Math.min(pagination.page * pagination.per_page, pagination.total)}
                  </span>{' '}
                  de <span className="font-medium">{pagination.total}</span> resultados
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <button
                    onClick={() => handlePageChange(pagination.page - 1)}
                    disabled={pagination.page <= 1}
                    className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Anterior
                  </button>
                  {/* Page numbers */}
                  {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
                    const pageNum = i + 1;
                    return (
                      <button
                        key={pageNum}
                        onClick={() => handlePageChange(pageNum)}
                        className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                          pageNum === pagination.page
                            ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                            : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                  <button
                    onClick={() => handlePageChange(pagination.page + 1)}
                    disabled={pagination.page >= pagination.total_pages}
                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Siguiente
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Empty State */}
      {!loading && tickets.length === 0 && (
        <div className="text-center py-12">
          <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No hay tickets</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm || filters.status || filters.priority
              ? 'No se encontraron tickets que coincidan con los filtros aplicados.'
              : 'Comienza creando tu primer ticket.'}
          </p>
          {!searchTerm && !filters.status && !filters.priority && (
            <div className="mt-6">
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <Plus className="w-4 h-4 mr-2" />
                Crear Primer Ticket
              </button>
            </div>
          )}
        </div>
      )}


    </div>
  );
};

export default TicketsManagement;
