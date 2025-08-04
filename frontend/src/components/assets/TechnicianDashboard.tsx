import React, { useState, useEffect } from 'react';
import {
  Monitor,
  Activity,
  AlertCircle,
  CheckCircle,
  XCircle,
  Clock,
  Search,
  Filter,
  Users,
  Building,
  RefreshCw,
  ChevronDown,
  ChevronRight,
  List,
  BarChart3
} from 'lucide-react';
import { assetsService } from '../../services/assetsService';
import AssetFilters from './AssetFilters';
import FilteredAssetsList from './FilteredAssetsList';
import AssetDetailModal from './AssetDetailModal';

interface ClientSummary {
  client_id: string;
  client_name: string;
  total_assets: number;
  online_assets: number;
  warning_assets: number;
  offline_assets: number;
  last_update: string;
}

interface Alert {
  asset_name: string;
  agent_status: string;
  last_seen: string;
  site_name: string;
  client_name: string;
}

interface TechnicianDashboardData {
  overall_summary: {
    total_assets: number;
    online_assets: number;
    warning_assets: number;
    offline_assets: number;
    last_update: string;
  };
  client_summaries: ClientSummary[];
  alerts: Alert[];
}

const TechnicianDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<TechnicianDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedClients, setExpandedClients] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');
  const [currentView, setCurrentView] = useState<'dashboard' | 'list'>('dashboard');
  const [filters, setFilters] = useState<{
    client_id?: string;
    site_id?: string;
    status?: string;
    search?: string;
  }>({});
  const [selectedAsset, setSelectedAsset] = useState<any>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async (retryCount = 0) => {
    try {
      setLoading(true);
      setError(null);

      // Add small delay on first load to ensure auth is ready
      if (retryCount === 0) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      const data = await assetsService.getTechnicianDashboard();
      setDashboardData(data);
    } catch (err: any) {
      console.error('Dashboard load error:', err);

      // Auto-retry once on network errors
      if (retryCount === 0 && (err.message.includes('Network') || err.message.includes('timeout'))) {
        console.log('Retrying dashboard load...');
        setTimeout(() => loadDashboardData(1), 1000);
        return;
      }

      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleClientExpansion = (clientId: string) => {
    const newExpanded = new Set(expandedClients);
    if (newExpanded.has(clientId)) {
      newExpanded.delete(clientId);
    } else {
      newExpanded.add(clientId);
    }
    setExpandedClients(newExpanded);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'online':
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <CheckCircle className="w-3 h-3 mr-1" />
            En línea
          </span>
        );
      case 'error':
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <AlertCircle className="w-3 h-3 mr-1" />
            Error
          </span>
        );
      case 'offline':
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <XCircle className="w-3 h-3 mr-1" />
            Desconectado
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            <Clock className="w-3 h-3 mr-1" />
            Desconocido
          </span>
        );
    }
  };

  const filteredClients = dashboardData?.client_summaries?.filter(client =>
    client.client_name.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Cargando dashboard...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
          <span className="text-red-800">Error: {error}</span>
        </div>
        <button
          onClick={loadDashboardData}
          className="mt-2 text-red-600 hover:text-red-800 text-sm underline"
        >
          Reintentar
        </button>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="text-center py-8">
        <Monitor className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No hay datos disponibles</h3>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Overall Summary */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-gray-900">Dashboard de Técnico MSP</h2>
          <div className="flex items-center space-x-3">
            {/* View Toggle */}
            <div className="flex rounded-md shadow-sm">
              <button
                onClick={() => setCurrentView('dashboard')}
                className={`px-3 py-2 text-sm font-medium rounded-l-md border ${
                  currentView === 'dashboard'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                <BarChart3 className="w-4 h-4 mr-2 inline" />
                Dashboard
              </button>
              <button
                onClick={() => setCurrentView('list')}
                className={`px-3 py-2 text-sm font-medium rounded-r-md border-l-0 border ${
                  currentView === 'list'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                <List className="w-4 h-4 mr-2 inline" />
                Lista
              </button>
            </div>

            <button
              onClick={loadDashboardData}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Actualizar
            </button>
          </div>
        </div>

        {/* Overall Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Monitor className="w-8 h-8 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-900">Total Assets</p>
                <p className="text-2xl font-bold text-blue-600">{dashboardData.overall_summary.total_assets}</p>
              </div>
            </div>
          </div>

          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center">
              <CheckCircle className="w-8 h-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-green-900">En Línea</p>
                <p className="text-2xl font-bold text-green-600">{dashboardData.overall_summary.online_assets}</p>
              </div>
            </div>
          </div>

          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="flex items-center">
              <AlertCircle className="w-8 h-8 text-yellow-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-yellow-900">Errores</p>
                <p className="text-2xl font-bold text-yellow-600">{dashboardData.overall_summary.warning_assets}</p>
              </div>
            </div>
          </div>

          <div className="bg-red-50 p-4 rounded-lg">
            <div className="flex items-center">
              <XCircle className="w-8 h-8 text-red-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-red-900">Desconectados</p>
                <p className="text-2xl font-bold text-red-600">{dashboardData.overall_summary.offline_assets}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Conditional Content Based on View */}
      {currentView === 'dashboard' ? (
        <>
          {/* Search and Filters for Dashboard */}
          <div className="bg-white shadow rounded-lg p-4">
            <div className="flex items-center space-x-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Buscar clientes..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              <button
                onClick={() => setExpandedClients(new Set(filteredClients.map(c => c.client_id)))}
                className="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Expandir Todo
              </button>
              <button
                onClick={() => setExpandedClients(new Set())}
                className="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Contraer Todo
              </button>
            </div>
          </div>

          {/* Clients List */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                Clientes ({filteredClients.length})
              </h3>
            </div>

            <div className="divide-y divide-gray-200">
              {filteredClients.map((client) => (
                <div key={client.client_id} className="p-6">
                  <div
                    className="flex items-center justify-between cursor-pointer"
                    onClick={() => toggleClientExpansion(client.client_id)}
                  >
                    <div className="flex items-center space-x-3">
                      {expandedClients.has(client.client_id) ? (
                        <ChevronDown className="w-5 h-5 text-gray-400" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-gray-400" />
                      )}
                      <Users className="w-6 h-6 text-blue-600" />
                      <div>
                        <h4 className="text-lg font-medium text-gray-900">{client.client_name}</h4>
                        <p className="text-sm text-gray-500">
                          {client.total_assets} assets total
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <div className="flex items-center space-x-2">
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            {client.online_assets} online
                          </span>
                          {client.warning_assets > 0 && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                              {client.warning_assets} error
                            </span>
                          )}
                          {client.offline_assets > 0 && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                              {client.offline_assets} offline
                            </span>
                          )}
                        </div>
                        {client.last_update && (
                          <p className="text-xs text-gray-500 mt-1">
                            Última actualización: {new Date(client.last_update).toLocaleString('es-MX')}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>

                  {expandedClients.has(client.client_id) && (
                    <div className="mt-4 pl-8">
                      <div className="bg-gray-50 rounded-lg p-4">
                        <p className="text-sm text-gray-600 mb-2">
                          Detalles del cliente expandidos aquí...
                        </p>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setCurrentView('list');
                            setFilters({ client_id: client.client_id });
                          }}
                          className="text-blue-600 hover:text-blue-800 text-sm"
                        >
                          Ver todos los assets de {client.client_name} →
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {filteredClients.length === 0 && (
              <div className="text-center py-8">
                <Users className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No se encontraron clientes</h3>
                <p className="mt-1 text-sm text-gray-500">
                  {searchTerm ? 'Intenta con un término de búsqueda diferente.' : 'No hay clientes con assets disponibles.'}
                </p>
              </div>
            )}
          </div>

          {/* Recent Alerts */}
          {dashboardData.alerts.length > 0 && (
            <div className="bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">
                  Alertas Recientes ({dashboardData.alerts.length})
                </h3>
              </div>
              <div className="divide-y divide-gray-200">
                {dashboardData.alerts.slice(0, 5).map((alert, index) => (
                  <div key={index} className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <AlertCircle className="w-5 h-5 text-red-600" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">{alert.asset_name}</p>
                          <p className="text-xs text-gray-500">{alert.client_name} - {alert.site_name}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        {getStatusBadge(alert.agent_status)}
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(alert.last_seen).toLocaleString('es-MX')}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <>
          {/* Filters for List View */}
          <AssetFilters
            currentFilters={filters}
            onFiltersChange={setFilters}
          />

          {/* Assets List */}
          <FilteredAssetsList
            filters={filters}
            onAssetClick={setSelectedAsset}
          />
        </>
      )}

      {/* Asset Detail Modal */}
      {selectedAsset && (
        <AssetDetailModal
          isOpen={!!selectedAsset}
          onClose={() => setSelectedAsset(null)}
          asset={selectedAsset}
        />
      )}
    </div>
  );
};

export default TechnicianDashboard;
