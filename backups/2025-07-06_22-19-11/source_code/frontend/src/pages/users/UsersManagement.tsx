import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';
import { 
  Users, 
  Search, 
  Plus, 
  Eye, 
  Edit, 
  Trash2, 
  Mail, 
  Phone,
  Building2,
  MapPin,
  Filter,
  UserCheck,
  UserX,
  Shield
} from 'lucide-react';
import UserForm from '../../components/users/UserForm';
import UserDetail from '../../components/users/UserDetail';
import SolicitanteForm from '../../components/users/SolicitanteForm';

interface User {
  user_id: string;
  client_id?: string;
  name: string;
  email: string;
  role: string;
  phone?: string;
  is_active: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
  client_name?: string;
}

interface Client {
  client_id: string;
  name: string;
}

const UsersManagement: React.FC = () => {
  const { user } = useAuth();
  const [allUsers, setAllUsers] = useState<User[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedClient, setSelectedClient] = useState<string>('');
  const [selectedRole, setSelectedRole] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showCreateSolicitanteForm, setShowCreateSolicitanteForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const itemsPerPage = 10;

  // Check permissions
  const canManageUsers = user?.role === 'superadmin' || user?.role === 'admin';
  const canViewAllUsers = user?.role === 'superadmin' || user?.role === 'admin' || user?.role === 'technician';

  // Role options for filtering
  const roleOptions = [
    { value: '', label: 'Todos los roles' },
    { value: 'superadmin', label: 'Super Administrador' },
    { value: 'admin', label: 'Administrador' },
    { value: 'technician', label: 'Técnico' },
    { value: 'client_admin', label: 'Admin Cliente' },
    { value: 'solicitante', label: 'Solicitante' }
  ];

  // Filter users based on search term, selected client, and role
  const filteredUsers = useMemo(() => {
    let filtered = allUsers;

    // Filter by client if selected
    if (selectedClient) {
      filtered = filtered.filter(user => user.client_id === selectedClient);
    }

    // Filter by role if selected
    if (selectedRole) {
      filtered = filtered.filter(user => user.role === selectedRole);
    }

    // Filter by search term
    if (searchTerm.trim()) {
      const searchLower = searchTerm.toLowerCase().trim();
      filtered = filtered.filter(user => 
        user.name.toLowerCase().includes(searchLower) ||
        user.email.toLowerCase().includes(searchLower) ||
        user.client_name?.toLowerCase().includes(searchLower)
      );
    }

    return filtered;
  }, [allUsers, searchTerm, selectedClient, selectedRole]);

  // Calculate pagination for filtered results
  const paginatedUsers = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredUsers.slice(startIndex, endIndex);
  }, [filteredUsers, currentPage, itemsPerPage]);

  // Update total pages when filtered users change
  const totalPages = Math.ceil(filteredUsers.length / itemsPerPage);

  useEffect(() => {
    // Reset to page 1 if current page is beyond available pages
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(1);
    }
  }, [filteredUsers.length, currentPage, totalPages]);

  // Load data on component mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);

      // Load users and clients in parallel
      const [usersResponse, clientsResponse] = await Promise.all([
        apiService.get('/users?per_page=1000'),
        apiService.get('/clients?per_page=1000')
      ]);

      if (usersResponse.success) {
        const userData = usersResponse.data;
        setAllUsers(userData.users || userData || []);
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

  const handleCreateUser = () => {
    setSelectedUser(null);
    setShowCreateForm(true);
  };

  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    setShowEditForm(true);
  };

  const handleViewUser = (user: User) => {
    setSelectedUser(user);
    setShowDetailModal(true);
  };

  const handleDeleteUser = async (user: User) => {
    const confirmed = window.confirm(
      `¿Estás seguro de que deseas eliminar al usuario "${user.name}"? Esta acción no se puede deshacer.`
    );

    if (confirmed) {
      try {
        const response = await apiService.delete(`/users/${user.user_id}`);
        if (response.success) {
          await loadData(); // Reload data
        }
      } catch (error) {
        console.error('Error deleting user:', error);
      }
    }
  };

  const handleFormSuccess = () => {
    setShowCreateForm(false);
    setShowEditForm(false);
    setSelectedUser(null);
    loadData(); // Reload data
  };

  const getRoleLabel = (role: string) => {
    const roleOption = roleOptions.find(option => option.value === role);
    return roleOption?.label || role;
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'superadmin':
        return <Shield className="w-4 h-4 text-red-600" />;
      case 'admin':
        return <Shield className="w-4 h-4 text-blue-600" />;
      case 'technician':
        return <UserCheck className="w-4 h-4 text-green-600" />;
      case 'client_admin':
        return <Building2 className="w-4 h-4 text-purple-600" />;
      case 'solicitante':
        return <Users className="w-4 h-4 text-gray-600" />;
      default:
        return <Users className="w-4 h-4 text-gray-400" />;
    }
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
            <Users className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Gestión de Usuarios</h1>
              <p className="text-gray-600">Administra usuarios del sistema y contactos de clientes</p>
            </div>
          </div>

          {canManageUsers && (
            <div className="flex space-x-3">
              <button
                onClick={handleCreateUser}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <Plus className="w-4 h-4 mr-2" />
                Nuevo Usuario
              </button>
              <button
                onClick={() => setShowCreateSolicitanteForm(true)}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <Users className="w-4 h-4 mr-2" />
                Nuevo Solicitante
              </button>
            </div>
          )}
        </div>
      </div>



      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Buscar usuarios por nombre o email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Client Filter */}
          <div className="relative">
            <Building2 className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <select
              value={selectedClient}
              onChange={(e) => setSelectedClient(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
            >
              <option value="">Todos los clientes</option>
              <option value="null">Sin cliente asignado</option>
              {clients.map((client) => (
                <option key={client.client_id} value={client.client_id}>
                  {client.name}
                </option>
              ))}
            </select>
          </div>

          {/* Role Filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
            >
              {roleOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Usuario
                </th>
                <th className="hidden md:table-cell px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cliente
                </th>
                <th className="hidden lg:table-cell px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contacto
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
              {paginatedUsers.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-3 sm:px-6 py-12 text-center text-gray-500">
                    <Users className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p className="text-lg font-medium">No se encontraron usuarios</p>
                    <p className="text-sm">
                      {searchTerm || selectedClient || selectedRole ? 'Intenta con otros filtros de búsqueda' : 'Comienza creando tu primer usuario'}
                    </p>
                  </td>
                </tr>
              ) : (
                paginatedUsers.map((user) => (
                  <tr key={user.user_id} className="hover:bg-gray-50">
                    <td className="px-3 sm:px-6 py-4">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-8 w-8 sm:h-10 sm:w-10">
                          <div className="h-8 w-8 sm:h-10 sm:w-10 rounded-full bg-blue-100 flex items-center justify-center">
                            {getRoleIcon(user.role)}
                          </div>
                        </div>
                        <div className="ml-3 sm:ml-4 min-w-0 flex-1">
                          <div className="text-sm font-medium text-gray-900 truncate">
                            {user.name}
                          </div>
                          <div className="text-sm text-gray-500 truncate">
                            {user.email}
                          </div>
                          {/* Show role and client on mobile */}
                          <div className="md:hidden mt-1">
                            <div className="flex items-center space-x-2">
                              <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                                {getRoleLabel(user.role)}
                              </span>
                              {user.client_name && (
                                <span className="text-xs text-gray-600 truncate">
                                  {user.client_name}
                                </span>
                              )}
                            </div>
                            {user.phone && (
                              <div className="flex items-center mt-1">
                                <Phone className="w-3 h-3 mr-1 text-gray-400" />
                                <span className="text-xs text-gray-600">{user.phone}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="hidden md:table-cell px-3 sm:px-6 py-4">
                      <div className="text-sm text-gray-900 truncate">
                        {user.client_name || 'Sin cliente'}
                      </div>
                      <div className="flex items-center mt-1">
                        {getRoleIcon(user.role)}
                        <span className="ml-1 text-xs text-gray-500">
                          {getRoleLabel(user.role)}
                        </span>
                      </div>
                    </td>
                    <td className="hidden lg:table-cell px-3 sm:px-6 py-4">
                      <div className="text-sm text-gray-900">
                        {user.phone && (
                          <div className="flex items-center mb-1">
                            <Phone className="w-3 h-3 mr-1 text-gray-400 flex-shrink-0" />
                            <span className="truncate">{user.phone}</span>
                          </div>
                        )}
                        <div className="flex items-center">
                          <Mail className="w-3 h-3 mr-1 text-gray-400 flex-shrink-0" />
                          <span className="truncate text-xs">{user.email}</span>
                        </div>
                      </div>
                    </td>
                    <td className="hidden sm:table-cell px-3 sm:px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        user.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {user.is_active ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleViewUser(user)}
                          className="text-blue-600 hover:text-blue-900 p-1"
                          title="Ver detalles"
                        >
                          <Eye className="w-3 h-3 sm:w-4 sm:h-4" />
                        </button>
                        {canManageUsers && (
                          <>
                            <button
                              onClick={() => handleEditUser(user)}
                              className="text-yellow-600 hover:text-yellow-900 p-1"
                              title="Editar"
                            >
                              <Edit className="w-3 h-3 sm:w-4 sm:h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteUser(user)}
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
                    <span className="font-medium">{Math.min(currentPage * itemsPerPage, filteredUsers.length)}</span> de{' '}
                    <span className="font-medium">{filteredUsers.length}</span> usuarios
                    {(searchTerm || selectedClient || selectedRole) && (
                      <span className="text-gray-500"> (filtrados de {allUsers.length} total)</span>
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
        <UserForm
          isOpen={showCreateForm}
          onClose={() => setShowCreateForm(false)}
          onSuccess={handleFormSuccess}
          mode="create"
        />
      )}

      {showEditForm && selectedUser && (
        <UserForm
          isOpen={showEditForm}
          onClose={() => setShowEditForm(false)}
          onSuccess={handleFormSuccess}
          user={selectedUser}
          mode="edit"
        />
      )}

      {showDetailModal && selectedUser && (
        <UserDetail
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          user={selectedUser}
        />
      )}

      {showCreateSolicitanteForm && (
        <SolicitanteForm
          isOpen={showCreateSolicitanteForm}
          onClose={() => setShowCreateSolicitanteForm(false)}
          onSuccess={handleFormSuccess}
        />
      )}
    </div>
  );
};

export default UsersManagement;
