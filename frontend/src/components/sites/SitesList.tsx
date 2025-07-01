import React, { useState, useEffect } from 'react';
import { Eye, Edit, Trash2, Plus, MapPin, Users, Building2 } from 'lucide-react';
import { sitesService, Site } from '../../services/sitesService';
import { useAuth } from '../../hooks/useAuth';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';
import ConfirmDialog from '../common/ConfirmDialog';
import SiteForm from './SiteForm';
import SiteDetail from './SiteDetail';

interface SitesListProps {
  clientId?: string;
  showClientColumn?: boolean;
}

const SitesList: React.FC<SitesListProps> = ({ 
  clientId, 
  showClientColumn = true 
}) => {
  const { user } = useAuth();
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedSite, setSelectedSite] = useState<Site | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{
    show: boolean;
    site: Site | null;
  }>({ show: false, site: null });

  const canManageSites = user?.role && ['superadmin', 'admin'].includes(user.role);

  useEffect(() => {
    loadSites();
  }, [clientId]);

  const loadSites = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = clientId ? { client_id: clientId } : undefined;
      const response = await sitesService.getAllSites(params);
      
      if (response.success) {
        setSites(response.data.sites || []);
      } else {
        setError(response.message || 'Failed to load sites');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load sites');
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

  const handleDeleteSite = (site: Site) => {
    setDeleteConfirm({ show: true, site });
  };

  const confirmDelete = async () => {
    if (!deleteConfirm.site) return;

    try {
      setError(null);
      const response = await sitesService.deleteSite(deleteConfirm.site.site_id);
      
      if (response.success) {
        await loadSites(); // Reload the list
        setDeleteConfirm({ show: false, site: null });
      } else {
        setError(response.message || 'Failed to delete site');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to delete site');
    }
  };

  const handleFormSuccess = async () => {
    setShowCreateForm(false);
    setShowEditForm(false);
    setSelectedSite(null);
    await loadSites();
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <Building2 className="h-6 w-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">
            {clientId ? 'Sitios del Cliente' : 'Gestión de Sitios'}
          </h2>
        </div>
        
        {canManageSites && (
          <button
            onClick={handleCreateSite}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Plus className="h-4 w-4 mr-2" />
            Agregar Sitio
          </button>
        )}
      </div>

      {error && <ErrorMessage message={error} />}

      {/* Sites Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:p-6">
          {sites.length === 0 ? (
            <div className="text-center py-12">
              <Building2 className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No hay sitios</h3>
              <p className="mt-1 text-sm text-gray-500">
                {clientId 
                  ? 'Este cliente no tiene sitios registrados.'
                  : 'No hay sitios registrados en el sistema.'
                }
              </p>
              {canManageSites && (
                <div className="mt-6">
                  <button
                    onClick={handleCreateSite}
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Agregar Primer Sitio
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Sitio
                    </th>
                    {showClientColumn && (
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Cliente
                      </th>
                    )}
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ubicación
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Usuarios
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tickets
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {sites.map((site) => (
                    <tr key={site.site_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Building2 className="h-5 w-5 text-gray-400 mr-3" />
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {site.name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {site.address}
                            </div>
                          </div>
                        </div>
                      </td>
                      
                      {showClientColumn && (
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {site.client_name || 'N/A'}
                          </div>
                        </td>
                      )}
                      
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center text-sm text-gray-900">
                          <MapPin className="h-4 w-4 text-gray-400 mr-1" />
                          {site.city}, {site.state}
                        </div>
                        <div className="text-sm text-gray-500">
                          {site.country} - {site.postal_code}
                        </div>
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center text-sm text-gray-900">
                          <Users className="h-4 w-4 text-gray-400 mr-1" />
                          {site.assigned_users || 0}
                        </div>
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {site.total_tickets || 0}
                        </div>
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end space-x-2">
                          <button
                            onClick={() => handleViewSite(site)}
                            className="text-blue-600 hover:text-blue-900"
                            title="Ver detalles"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          
                          {canManageSites && (
                            <>
                              <button
                                onClick={() => handleEditSite(site)}
                                className="text-indigo-600 hover:text-indigo-900"
                                title="Editar sitio"
                              >
                                <Edit className="h-4 w-4" />
                              </button>
                              
                              <button
                                onClick={() => handleDeleteSite(site)}
                                className="text-red-600 hover:text-red-900"
                                title="Eliminar sitio"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Create Site Modal */}
      {showCreateForm && (
        <SiteForm
          isOpen={showCreateForm}
          onClose={() => setShowCreateForm(false)}
          onSuccess={handleFormSuccess}
          clientId={clientId}
        />
      )}

      {/* Edit Site Modal */}
      {showEditForm && selectedSite && (
        <SiteForm
          isOpen={showEditForm}
          onClose={() => setShowEditForm(false)}
          onSuccess={handleFormSuccess}
          site={selectedSite}
          clientId={clientId}
        />
      )}

      {/* Site Detail Modal */}
      {showDetailModal && selectedSite && (
        <SiteDetail
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          site={selectedSite}
        />
      )}

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={deleteConfirm.show}
        onClose={() => setDeleteConfirm({ show: false, site: null })}
        onConfirm={confirmDelete}
        title="Eliminar Sitio"
        message={`¿Está seguro de que desea eliminar el sitio "${deleteConfirm.site?.name}"? Esta acción no se puede deshacer.`}
        confirmText="Eliminar"
        cancelText="Cancelar"
        type="danger"
      />
    </div>
  );
};

export default SitesList;
