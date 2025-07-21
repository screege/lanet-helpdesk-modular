import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  X,
  ChevronDown,
  Building,
  MapPin,
  Activity
} from 'lucide-react';
import { assetsService } from '../../services/assetsService';

interface AssetFiltersProps {
  onFiltersChange: (filters: {
    client_id?: string;
    site_id?: string;
    status?: string;
    search?: string;
  }) => void;
  currentFilters: {
    client_id?: string;
    site_id?: string;
    status?: string;
    search?: string;
  };
}

interface Client {
  client_id: string;
  client_name: string;
  asset_count: number;
}

interface Site {
  site_id: string;
  site_name: string;
  client_id: string;
  client_name: string;
  asset_count: number;
}

const AssetFilters: React.FC<AssetFiltersProps> = ({ onFiltersChange, currentFilters }) => {
  const [clients, setClients] = useState<Client[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadClients();
  }, []);

  useEffect(() => {
    if (currentFilters.client_id) {
      loadSites(currentFilters.client_id);
    } else {
      setSites([]);
    }
  }, [currentFilters.client_id]);

  const loadClients = async () => {
    try {
      setLoading(true);
      const response = await assetsService.getClientsWithAssets();
      setClients(response.clients || []);
    } catch (error) {
      console.error('Error loading clients:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSites = async (clientId: string) => {
    try {
      const response = await assetsService.getSitesWithAssets(clientId);
      setSites(response.sites || []);
    } catch (error) {
      console.error('Error loading sites:', error);
    }
  };

  const handleFilterChange = (key: string, value: string) => {
    const newFilters = { ...currentFilters };
    
    if (value === '' || value === 'all') {
      delete newFilters[key as keyof typeof newFilters];
    } else {
      (newFilters as any)[key] = value;
    }

    // If client changes, clear site filter
    if (key === 'client_id' && currentFilters.site_id) {
      delete newFilters.site_id;
    }

    onFiltersChange(newFilters);
  };

  const clearAllFilters = () => {
    onFiltersChange({});
  };

  const hasActiveFilters = Object.keys(currentFilters).some(key => 
    currentFilters[key as keyof typeof currentFilters] && 
    currentFilters[key as keyof typeof currentFilters] !== ''
  );

  const getActiveFiltersCount = () => {
    return Object.keys(currentFilters).filter(key => 
      currentFilters[key as keyof typeof currentFilters] && 
      currentFilters[key as keyof typeof currentFilters] !== ''
    ).length;
  };

  return (
    <div className="bg-white shadow rounded-lg p-4 space-y-4">
      {/* Search Bar */}
      <div className="flex items-center space-x-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Buscar por nombre de equipo, cliente o sitio..."
              value={currentFilters.search || ''}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Filter Toggle Button */}
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`inline-flex items-center px-3 py-2 border rounded-md text-sm font-medium ${
            hasActiveFilters
              ? 'border-blue-300 text-blue-700 bg-blue-50'
              : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
          } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
        >
          <Filter className="w-4 h-4 mr-2" />
          Filtros
          {hasActiveFilters && (
            <span className="ml-2 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-blue-600 rounded-full">
              {getActiveFiltersCount()}
            </span>
          )}
          <ChevronDown className={`w-4 h-4 ml-2 transform transition-transform ${showFilters ? 'rotate-180' : ''}`} />
        </button>

        {/* Clear Filters Button */}
        {hasActiveFilters && (
          <button
            onClick={clearAllFilters}
            className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <X className="w-4 h-4 mr-2" />
            Limpiar
          </button>
        )}
      </div>

      {/* Advanced Filters */}
      {showFilters && (
        <div className="border-t pt-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Client Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Building className="w-4 h-4 inline mr-1" />
                Cliente
              </label>
              <select
                value={currentFilters.client_id || ''}
                onChange={(e) => handleFilterChange('client_id', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
              >
                <option value="">Todos los clientes</option>
                {clients.map((client) => (
                  <option key={client.client_id} value={client.client_id}>
                    {client.client_name} ({client.asset_count} assets)
                  </option>
                ))}
              </select>
            </div>

            {/* Site Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <MapPin className="w-4 h-4 inline mr-1" />
                Sitio
              </label>
              <select
                value={currentFilters.site_id || ''}
                onChange={(e) => handleFilterChange('site_id', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={!currentFilters.client_id || sites.length === 0}
              >
                <option value="">
                  {currentFilters.client_id ? 'Todos los sitios' : 'Selecciona un cliente primero'}
                </option>
                {sites.map((site) => (
                  <option key={site.site_id} value={site.site_id}>
                    {site.site_name} ({site.asset_count} assets)
                  </option>
                ))}
              </select>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Activity className="w-4 h-4 inline mr-1" />
                Estado
              </label>
              <select
                value={currentFilters.status || ''}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Todos los estados</option>
                <option value="online">En línea</option>
                <option value="error">Error</option>
                <option value="offline">Desconectado</option>
              </select>
            </div>
          </div>

          {/* Active Filters Summary */}
          {hasActiveFilters && (
            <div className="mt-4 p-3 bg-blue-50 rounded-md">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-blue-900">Filtros activos:</span>
                  <div className="flex flex-wrap gap-2">
                    {currentFilters.client_id && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        Cliente: {clients.find(c => c.client_id === currentFilters.client_id)?.client_name || 'Seleccionado'}
                      </span>
                    )}
                    {currentFilters.site_id && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        Sitio: {sites.find(s => s.site_id === currentFilters.site_id)?.site_name || 'Seleccionado'}
                      </span>
                    )}
                    {currentFilters.status && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        Estado: {currentFilters.status === 'online' ? 'En línea' :
                                currentFilters.status === 'error' ? 'Error' :
                                currentFilters.status === 'offline' ? 'Desconectado' : currentFilters.status}
                      </span>
                    )}
                    {currentFilters.search && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        Búsqueda: "{currentFilters.search}"
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AssetFilters;
