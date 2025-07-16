import React from 'react';
import { MapPin, Plus, Eye, Edit, Trash2 } from 'lucide-react';

interface Site {
  site_id: string;
  name: string;
  address: string;
  city: string;
  state: string;
  postal_code: string;
  is_active: boolean;
}

interface SitesTabContentProps {
  sites: Site[];
  canManageSites: boolean;
  onCreateSite: () => void;
  onViewSite: (site: Site) => void;
  onEditSite: (site: Site) => void;
  onDeleteSite: (site: Site) => void;
}

const SitesTabContent: React.FC<SitesTabContentProps> = ({
  sites,
  canManageSites,
  onCreateSite,
  onViewSite,
  onEditSite,
  onDeleteSite
}) => {
  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium text-gray-900">Sitios</h3>
        {canManageSites && (
          <button
            onClick={onCreateSite}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Plus className="w-4 h-4 mr-2" />
            Agregar Sitio
          </button>
        )}
      </div>

      {sites.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sites.map((site) => (
            <div key={site.site_id} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-gray-900 truncate">{site.name}</h4>
                  <p className="text-sm text-gray-600 mt-1">
                    {site.address}
                  </p>
                  <p className="text-xs text-gray-500">
                    {site.city}, {site.state} {site.postal_code}
                  </p>
                  <div className="mt-2">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      site.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {site.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center space-x-1 ml-2">
                  <button
                    onClick={() => onViewSite(site)}
                    className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                    title="Ver Detalles"
                  >
                    <Eye className="w-4 h-4" />
                  </button>

                  {canManageSites && (
                    <>
                      <button
                        onClick={() => onEditSite(site)}
                        className="p-1 text-gray-400 hover:text-yellow-600 transition-colors"
                        title="Editar Sitio"
                      >
                        <Edit className="w-4 h-4" />
                      </button>

                      <button
                        onClick={() => onDeleteSite(site)}
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
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <MapPin className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No hay sitios registrados</h3>
          <p className="mt-1 text-sm text-gray-500">
            Comienza agregando un sitio para este cliente.
          </p>
          {canManageSites && (
            <div className="mt-6">
              <button
                onClick={onCreateSite}
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
  );
};

export default SitesTabContent;
