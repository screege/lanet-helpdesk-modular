import React, { useState, useEffect } from 'react';
import { X, Building2, MapPin, Users, Calendar, User, Mail, Phone, Plus, UserPlus, UserMinus } from 'lucide-react';
import { sitesService, Site, SiteUser } from '../../services/sitesService';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';
import SolicitanteForm from '../users/SolicitanteForm';
import AssignUserToSiteModal from '../users/AssignUserToSiteModal';
import UnassignUserFromSiteModal from '../users/UnassignUserFromSiteModal';

interface SiteDetailProps {
  isOpen: boolean;
  onClose: () => void;
  site: Site;
}

const SiteDetail: React.FC<SiteDetailProps> = ({
  isOpen,
  onClose,
  site
}) => {
  const { user } = useAuth();
  const [siteDetails, setSiteDetails] = useState<Site | null>(null);
  const [assignedUsers, setAssignedUsers] = useState<SiteUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateSolicitanteForm, setShowCreateSolicitanteForm] = useState(false);
  const [showAssignUserModal, setShowAssignUserModal] = useState(false);
  const [showUnassignUserModal, setShowUnassignUserModal] = useState(false);

  // Check permissions
  const canManageUsers = user?.role === 'superadmin';

  useEffect(() => {
    if (isOpen && site) {
      loadSiteDetails();
    }
  }, [isOpen, site]);

  const handleSolicitanteFormSuccess = () => {
    setShowCreateSolicitanteForm(false);
    loadSiteDetails(); // Reload to show new solicitante
  };

  const handleAssignUserSuccess = () => {
    setShowAssignUserModal(false);
    loadSiteDetails(); // Reload to show assigned users
  };

  const handleUnassignUserSuccess = () => {
    setShowUnassignUserModal(false);
    loadSiteDetails(); // Reload to show updated users
  };

  const loadSiteDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await sitesService.getSiteById(site.site_id);
      
      if (response.success) {
        // Type guard para validar response.data
        if (response.data && typeof response.data === 'object' && 'site' in response.data) {
          setSiteDetails((response.data as any).site);
          setAssignedUsers((response.data as any).assigned_users || []);
        } else {
          throw new Error('Invalid response format');
        }
      } else {
        setError(response.message || 'Failed to load site details');
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load site details');
    } finally {
      setLoading(false);
    }
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

  const getRoleDisplayName = (role: string) => {
    const roleNames: Record<string, string> = {
      'superadmin': 'Super Administrador',
      'admin': 'Administrador',
      'technician': 'Técnico',
      'client_admin': 'Admin Cliente',
      'solicitante': 'Solicitante'
    };
    return roleNames[role] || role;
  };

  const getRoleBadgeColor = (role: string) => {
    const colors: Record<string, string> = {
      'superadmin': 'bg-purple-100 text-purple-800',
      'admin': 'bg-red-100 text-red-800',
      'technician': 'bg-blue-100 text-blue-800',
      'client_admin': 'bg-green-100 text-green-800',
      'solicitante': 'bg-gray-100 text-gray-800'
    };
    return colors[role] || 'bg-gray-100 text-gray-800';
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <Building2 className="h-6 w-6 text-blue-600" />
            <h3 className="text-lg font-medium text-gray-900">
              Detalles del Sitio
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
          <div className="flex justify-center py-12">
            <LoadingSpinner />
          </div>
        ) : error ? (
          <ErrorMessage message={error} />
        ) : siteDetails ? (
          <div className="space-y-6">
            {/* Site Information */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h4 className="text-lg font-medium text-gray-900 mb-4">
                Información del Sitio
              </h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h5 className="text-sm font-medium text-gray-700 mb-2">Nombre</h5>
                  <p className="text-sm text-gray-900">{siteDetails.name}</p>
                </div>
                
                <div>
                  <h5 className="text-sm font-medium text-gray-700 mb-2">Cliente</h5>
                  <p className="text-sm text-gray-900">{siteDetails.client_name}</p>
                </div>
                
                <div className="md:col-span-2">
                  <h5 className="text-sm font-medium text-gray-700 mb-2">Dirección</h5>
                  <div className="flex items-start space-x-2">
                    <MapPin className="h-4 w-4 text-gray-400 mt-0.5" />
                    <div>
                      <p className="text-sm text-gray-900">{siteDetails.address}</p>
                      <p className="text-sm text-gray-600">
                        {siteDetails.city}, {siteDetails.state}, {siteDetails.country}
                      </p>
                      <p className="text-sm text-gray-600">
                        CP: {siteDetails.postal_code}
                      </p>
                    </div>
                  </div>
                </div>
                
                {(siteDetails.latitude && siteDetails.longitude) && (
                  <div className="md:col-span-2">
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Coordenadas</h5>
                    <p className="text-sm text-gray-900">
                      Lat: {siteDetails.latitude}, Lng: {siteDetails.longitude}
                    </p>
                  </div>
                )}
                
                <div>
                  <h5 className="text-sm font-medium text-gray-700 mb-2">Fecha de Creación</h5>
                  <div className="flex items-center space-x-2">
                    <Calendar className="h-4 w-4 text-gray-400" />
                    <p className="text-sm text-gray-900">
                      {formatDate(siteDetails.created_at)}
                    </p>
                  </div>
                </div>
                
                <div>
                  <h5 className="text-sm font-medium text-gray-700 mb-2">Última Actualización</h5>
                  <div className="flex items-center space-x-2">
                    <Calendar className="h-4 w-4 text-gray-400" />
                    <p className="text-sm text-gray-900">
                      {formatDate(siteDetails.updated_at)}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Assigned Users */}
            <div className="bg-white border rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-lg font-medium text-gray-900 flex items-center">
                  <Users className="h-5 w-5 text-gray-400 mr-2" />
                  Usuarios Asignados ({assignedUsers.length})
                </h4>
                {canManageUsers && (
                  <div className="flex space-x-2">
                    {assignedUsers.length > 0 && (
                      <button
                        onClick={() => setShowUnassignUserModal(true)}
                        className="inline-flex items-center px-3 py-2 border border-red-300 text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                      >
                        <UserMinus className="w-4 h-4 mr-1" />
                        Quitar Usuarios
                      </button>
                    )}
                    <button
                      onClick={() => setShowAssignUserModal(true)}
                      className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      <UserPlus className="w-4 h-4 mr-1" />
                      Asignar Existente
                    </button>
                    <button
                      onClick={() => setShowCreateSolicitanteForm(true)}
                      className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      <Plus className="w-4 h-4 mr-1" />
                      Crear Nuevo
                    </button>
                  </div>
                )}
              </div>
              
              {assignedUsers.length === 0 ? (
                <div className="text-center py-8">
                  <Users className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">
                    No hay usuarios asignados
                  </h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Este sitio no tiene usuarios asignados actualmente.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {assignedUsers.map((user) => (
                    <div
                      key={user.user_id}
                      className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
                    >
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                          <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                            <User className="h-5 w-5 text-gray-500" />
                          </div>
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2">
                            <p className="text-sm font-medium text-gray-900 truncate">
                              {user.name}
                            </p>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeColor(user.role)}`}>
                              {getRoleDisplayName(user.role)}
                            </span>
                          </div>
                          
                          <div className="flex items-center space-x-4 mt-1">
                            <div className="flex items-center space-x-1">
                              <Mail className="h-3 w-3 text-gray-400" />
                              <p className="text-sm text-gray-500 truncate">
                                {user.email}
                              </p>
                            </div>
                            
                            {user.phone && (
                              <div className="flex items-center space-x-1">
                                <Phone className="h-3 w-3 text-gray-400" />
                                <p className="text-sm text-gray-500">
                                  {user.phone}
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className="text-right">
                        <p className="text-xs text-gray-500">
                          Asignado el
                        </p>
                        <p className="text-xs text-gray-900">
                          {formatDate(user.assigned_at)}
                        </p>
                        {user.assigned_by_name && (
                          <p className="text-xs text-gray-500">
                            por {user.assigned_by_name}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex justify-end pt-6 border-t">
              <button
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cerrar
              </button>
            </div>
          </div>
        ) : null}

        {/* Solicitante Form Modal */}
        {showCreateSolicitanteForm && siteDetails && (
          <SolicitanteForm
            isOpen={showCreateSolicitanteForm}
            onClose={() => setShowCreateSolicitanteForm(false)}
            onSuccess={handleSolicitanteFormSuccess}
            clientId={siteDetails.client_id}
            clientName={siteDetails.client_name}
            siteId={site.site_id}
          />
        )}

        {/* Assign User Modal */}
        {showAssignUserModal && siteDetails && (
          <AssignUserToSiteModal
            isOpen={showAssignUserModal}
            onClose={() => setShowAssignUserModal(false)}
            onSuccess={handleAssignUserSuccess}
            clientId={siteDetails.client_id}
            clientName={siteDetails.client_name}
            siteId={site.site_id}
            siteName={siteDetails.name}
          />
        )}

        {/* Unassign User Modal */}
        {showUnassignUserModal && siteDetails && (
          <UnassignUserFromSiteModal
            isOpen={showUnassignUserModal}
            onClose={() => setShowUnassignUserModal(false)}
            onSuccess={handleUnassignUserSuccess}
            siteId={site.site_id}
            siteName={siteDetails.name}
            assignedUsers={assignedUsers}
          />
        )}
      </div>
    </div>
  );
};

export default SiteDetail;
