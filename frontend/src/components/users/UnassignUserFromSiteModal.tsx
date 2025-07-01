import React, { useState } from 'react';
import { X, UserMinus, AlertTriangle, Trash2 } from 'lucide-react';
import { usersService } from '../../services/usersService';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';

interface SiteUser {
  user_id: string;
  name: string;
  email: string;
  phone?: string;
  role: string;
  assigned_at: string;
}

interface UnassignUserFromSiteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  siteId: string;
  siteName: string;
  assignedUsers: SiteUser[];
}

const UnassignUserFromSiteModal: React.FC<UnassignUserFromSiteModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  siteId,
  siteName,
  assignedUsers
}) => {
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUserToggle = (userId: string) => {
    setSelectedUsers(prev => 
      prev.includes(userId) 
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const handleSubmit = async () => {
    if (selectedUsers.length === 0) {
      setError('Selecciona al menos un usuario para quitar');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      // Unassign each selected user from the site
      for (const userId of selectedUsers) {
        await usersService.unassignUserFromSites(userId, [siteId]);
      }
      
      onSuccess();
      onClose();
    } catch (error: any) {
      console.error('Error unassigning users:', error);
      setError(error.message || 'Error al quitar usuarios del sitio');
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    setSelectedUsers([]);
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
              <UserMinus className="w-5 h-5 mr-2 text-red-600" />
              Quitar Usuarios del Sitio
            </h2>
            <p className="text-sm text-gray-600 mt-1">
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

          {/* Warning */}
          <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
            <div className="flex">
              <AlertTriangle className="h-5 w-5 text-yellow-400" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">
                  Advertencia
                </h3>
                <p className="mt-1 text-sm text-yellow-700">
                  Los usuarios seleccionados ya no tendrán acceso a este sitio. Esta acción se puede revertir asignándolos nuevamente.
                </p>
              </div>
            </div>
          </div>

          {/* Users List */}
          <div className="max-h-96 overflow-y-auto border border-gray-200 rounded-md">
            {assignedUsers.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No hay usuarios asignados a este sitio
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {assignedUsers.map((user) => (
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
                        className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
                      />
                      <div className="ml-3 flex-1">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-900">{user.name}</p>
                            <p className="text-sm text-gray-500">{user.email}</p>
                            {user.phone && (
                              <p className="text-sm text-gray-500">{user.phone}</p>
                            )}
                            <p className="text-xs text-gray-400">
                              Asignado: {new Date(user.assigned_at).toLocaleDateString('es-ES')}
                            </p>
                          </div>
                          <div className="text-right">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {user.role}
                            </span>
                          </div>
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
            <div className="mt-4 p-3 bg-red-50 rounded-md">
              <p className="text-sm text-red-700">
                {selectedUsers.length} usuario{selectedUsers.length !== 1 ? 's' : ''} seleccionado{selectedUsers.length !== 1 ? 's' : ''} para quitar
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
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? (
              <>
                <LoadingSpinner />
                <span className="ml-2">Quitando...</span>
              </>
            ) : (
              <>
                <Trash2 className="w-4 h-4 mr-2" />
                Quitar del Sitio
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UnassignUserFromSiteModal;
