import React, { useState, useEffect } from 'react';
import { X, Users, Search, Plus } from 'lucide-react';
import { usersService } from '../../services/usersService';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';

interface User {
  user_id: string;
  name: string;
  email: string;
  role: string;
  phone?: string;
  is_active: boolean;
  created_at: string;
}

interface AssignUserToSiteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  clientId: string;
  clientName: string;
  siteId: string;
  siteName: string;
}

const AssignUserToSiteModal: React.FC<AssignUserToSiteModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  clientId,
  clientName,
  siteId,
  siteName
}) => {
  const [users, setUsers] = useState<User[]>([]);
  const [filteredUsers, setFilteredUsers] = useState<User[]>([]);
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && clientId) {
      loadUsers();
    }
  }, [isOpen, clientId]);

  useEffect(() => {
    if (searchTerm) {
      const filtered = users.filter(user =>
        user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredUsers(filtered);
    } else {
      setFilteredUsers(users);
    }
  }, [searchTerm, users]);

  const loadUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await usersService.getUsersByClient(clientId, 'solicitante');
      if (response.success) {
        setUsers(response.data.users || []);
        setFilteredUsers(response.data.users || []);
      } else {
        setError('Error al cargar solicitantes');
      }
    } catch (error) {
      console.error('Error loading users:', error);
      setError('Error al cargar solicitantes');
    } finally {
      setLoading(false);
    }
  };

  const handleUserToggle = (userId: string) => {
    setSelectedUsers(prev => 
      prev.includes(userId) 
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const handleSubmit = async () => {
    if (selectedUsers.length === 0) {
      setError('Selecciona al menos un solicitante');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      // Assign each selected user to the site
      for (const userId of selectedUsers) {
        await usersService.assignUserToSites(userId, [siteId]);
      }
      
      onSuccess();
      onClose();
    } catch (error: any) {
      console.error('Error assigning users:', error);
      setError(error.message || 'Error al asignar solicitantes');
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    setSelectedUsers([]);
    setSearchTerm('');
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 flex items-center">
              <Users className="w-5 h-5 mr-2 text-blue-600" />
              Asignar Solicitantes al Sitio
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Cliente: <span className="font-medium">{clientName}</span> | 
              Sitio: <span className="font-medium">{siteName}</span>
            </p>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {error && (
            <ErrorMessage message={error} onClose={() => setError(null)} />
          )}

          {/* Search */}
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Buscar solicitantes..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Users List */}
          <div className="max-h-96 overflow-y-auto border border-gray-200 rounded-md">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <LoadingSpinner />
              </div>
            ) : filteredUsers.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                {users.length === 0 ? 'No hay solicitantes para este cliente' : 'No se encontraron solicitantes'}
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {filteredUsers.map((user) => (
                  <div
                    key={user.user_id}
                    className="p-4 hover:bg-gray-50 cursor-pointer"
                    onClick={() => handleUserToggle(user.user_id)}
                  >
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedUsers.includes(user.user_id)}
                        onChange={() => handleUserToggle(user.user_id)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <div className="ml-3 flex-1">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-900">{user.name}</p>
                            <p className="text-sm text-gray-500">{user.email}</p>
                            {user.phone && (
                              <p className="text-sm text-gray-500">{user.phone}</p>
                            )}
                          </div>
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            {user.role}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Selected Count */}
          {selectedUsers.length > 0 && (
            <div className="mt-4 p-3 bg-blue-50 rounded-md">
              <p className="text-sm text-blue-700">
                {selectedUsers.length} solicitante{selectedUsers.length !== 1 ? 's' : ''} seleccionado{selectedUsers.length !== 1 ? 's' : ''}
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-3 px-6 py-4 border-t border-gray-200 bg-gray-50">
          <button
            type="button"
            onClick={handleClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={submitting || selectedUsers.length === 0}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? (
              <>
                <LoadingSpinner />
                <span className="ml-2">Asignando...</span>
              </>
            ) : (
              <>
                <Plus className="w-4 h-4 mr-2" />
                Asignar Solicitantes
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AssignUserToSiteModal;
