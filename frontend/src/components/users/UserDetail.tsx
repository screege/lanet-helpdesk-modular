import React, { useState, useEffect } from 'react';
import { X, User as UserIcon, Mail, Phone, Calendar, Building2, Shield, MapPin, Clock } from 'lucide-react';
import { usersService, User } from '../../services/usersService';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';

interface UserDetailProps {
  isOpen: boolean;
  onClose: () => void;
  user: User;
}

interface UserSite {
  site_id: string;
  site_name: string;
  client_name: string;
  city: string;
  state: string;
  assigned_at: string;
}

const UserDetail: React.FC<UserDetailProps> = ({
  isOpen,
  onClose,
  user
}) => {
  const [userDetails, setUserDetails] = useState<User | null>(null);
  const [userSites, setUserSites] = useState<UserSite[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && user) {
      loadUserDetails();
    }
  }, [isOpen, user]);

  const loadUserDetails = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load user details and sites in parallel
      const [userResponse, sitesResponse] = await Promise.all([
        usersService.getUserById(user.user_id),
        usersService.getUserSites(user.user_id).catch(() => ({ success: false, data: [] }))
      ]);

      if (userResponse.success) {
        setUserDetails(userResponse.data);
      } else {
        setError('Error al cargar detalles del usuario');
      }

      if (sitesResponse.success) {
        console.log('Sites response:', sitesResponse);
        // Filter only assigned sites and map to expected format
        const assignedSites = (sitesResponse.data.sites || [])
          .filter((site: unknown) => (site as any).is_assigned)
          .map((site: unknown) => ({
            site_id: (site as any).site_id,
            site_name: (site as any).name,
            client_name: (site as any).client_name || 'Cliente',
            city: (site as any).city,
            state: (site as any).state,
            assigned_at: site.assigned_at || new Date().toISOString()
          }));
        console.log('Mapped assigned sites:', assignedSites);
        setUserSites(assignedSites);
      }
    } catch (error) {
      console.error('Error loading user details:', error);
      setError('Error al cargar información del usuario');
    } finally {
      setLoading(false);
    }
  };

  const getRoleLabel = (role: string) => {
    const roleLabels: Record<string, string> = {
      'superadmin': 'Super Administrador',
      'admin': 'Administrador',
      'technician': 'Técnico',
      'client_admin': 'Admin Cliente',
      'solicitante': 'Solicitante'
    };
    return roleLabels[role] || role;
  };

  const getRoleColor = (role: string) => {
    const roleColors: Record<string, string> = {
      'superadmin': 'bg-red-100 text-red-800',
      'admin': 'bg-blue-100 text-blue-800',
      'technician': 'bg-green-100 text-green-800',
      'client_admin': 'bg-purple-100 text-purple-800',
      'solicitante': 'bg-gray-100 text-gray-800'
    };
    return roleColors[role] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <UserIcon className="h-6 w-6 text-blue-600" />
            <h3 className="text-lg font-medium text-gray-900">
              Detalles del Usuario
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <LoadingSpinner />
          </div>
        ) : error ? (
          <ErrorMessage message={error} />
        ) : userDetails ? (
          <div className="space-y-6">
            {/* Basic Information */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h4 className="text-lg font-medium text-gray-900 mb-4">Información Básica</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* User Avatar and Name */}
                <div className="flex items-center space-x-4">
                  <div className="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center">
                    <UserIcon className="h-8 w-8 text-blue-600" />
                  </div>
                  <div>
                    <h5 className="text-xl font-semibold text-gray-900">{userDetails.name}</h5>
                    <p className="text-gray-600">{userDetails.email}</p>
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      userDetails.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {userDetails.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </div>
                </div>

                {/* Role and Client */}
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <Shield className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-500">Rol</p>
                      <span className={`inline-flex px-2 py-1 text-sm font-semibold rounded-full ${getRoleColor(userDetails.role)}`}>
                        {getRoleLabel(userDetails.role)}
                      </span>
                    </div>
                  </div>

                  {userDetails.client_name && (
                    <div className="flex items-center space-x-3">
                      <Building2 className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-500">Cliente</p>
                        <p className="text-sm text-gray-900">{userDetails.client_name}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Contact Information */}
            <div className="bg-white border rounded-lg p-6">
              <h4 className="text-lg font-medium text-gray-900 mb-4">Información de Contacto</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="flex items-center space-x-3">
                  <Mail className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-500">Email</p>
                    <p className="text-sm text-gray-900">{userDetails.email}</p>
                  </div>
                </div>

                {userDetails.phone && (
                  <div className="flex items-center space-x-3">
                    <Phone className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-500">Teléfono</p>
                      <p className="text-sm text-gray-900">{userDetails.phone}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Account Information */}
            <div className="bg-white border rounded-lg p-6">
              <h4 className="text-lg font-medium text-gray-900 mb-4">Información de Cuenta</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="flex items-center space-x-3">
                  <Calendar className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-500">Fecha de Creación</p>
                    <p className="text-sm text-gray-900">{formatDate(userDetails.created_at)}</p>
                  </div>
                </div>

                {userDetails.last_login && (
                  <div className="flex items-center space-x-3">
                    <Clock className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-500">Último Acceso</p>
                      <p className="text-sm text-gray-900">{formatDate(userDetails.last_login)}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Assigned Sites (for solicitante users) */}
            {userDetails.role === 'solicitante' && (
              <div className="bg-white border rounded-lg p-6">
                <h4 className="text-lg font-medium text-gray-900 mb-4">Sitios Asignados</h4>
                {userSites.length > 0 ? (
                  <div className="space-y-3">
                    {userSites.map((site) => (
                      <div key={site.site_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <MapPin className="h-5 w-5 text-blue-600" />
                          <div>
                            <p className="text-sm font-medium text-gray-900">{site.site_name}</p>
                            <p className="text-xs text-gray-500">{site.client_name}</p>
                            <p className="text-xs text-gray-500">{site.city}, {site.state}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-gray-500">Asignado</p>
                          <p className="text-xs text-gray-900">{formatDate(site.assigned_at)}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <MapPin className="mx-auto h-12 w-12 text-gray-400" />
                    <h3 className="mt-2 text-sm font-medium text-gray-900">Sin sitios asignados</h3>
                    <p className="mt-1 text-sm text-gray-500">
                      Este usuario no tiene sitios asignados actualmente.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* User Statistics */}
            <div className="bg-white border rounded-lg p-6">
              <h4 className="text-lg font-medium text-gray-900 mb-4">Estadísticas</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {userSites.length}
                  </div>
                  <div className="text-sm text-gray-500">Sitios Asignados</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    0
                  </div>
                  <div className="text-sm text-gray-500">Tickets Creados</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    0
                  </div>
                  <div className="text-sm text-gray-500">Tickets Activos</div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <UserIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Usuario no encontrado</h3>
            <p className="mt-1 text-sm text-gray-500">
              No se pudo cargar la información del usuario.
            </p>
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-end pt-6 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserDetail;
