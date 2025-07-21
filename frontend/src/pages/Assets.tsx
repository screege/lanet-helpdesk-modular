import React, { useState, useEffect } from 'react';
import {
  Monitor,
  Activity,
  HardDrive,
  Cpu,
  MemoryStick,
  Wifi,
  Clock,
  AlertCircle,
  CheckCircle,
  XCircle,
  RefreshCw
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { assetsService } from '@/services/assetsService';
import TechnicianDashboard from '@/components/assets/TechnicianDashboard';

interface Asset {
  asset_id: string;
  name: string;
  agent_status: 'online' | 'offline' | 'warning';
  last_seen: string;
  specifications: any;
  hardware_info?: any;
  software_info?: any;
  system_metrics?: any;
  site_name: string;
  site_id: string;
  site_address?: string;
  client_name?: string;
  client_id?: string;
}

interface AssetsSummary {
  total_assets: number;
  online_assets: number;
  warning_assets: number;
  offline_assets: number;
  last_update: string | null;
}

const Assets: React.FC = () => {

  const { user } = useAuth();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [summary, setSummary] = useState<AssetsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [activeTab, setActiveTab] = useState<'general' | 'hardware' | 'software' | 'metrics'>('general');

  // MSP Hierarchy Filters
  const [selectedClient, setSelectedClient] = useState<string>('');
  const [selectedSite, setSelectedSite] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [clients, setClients] = useState<{client_id: string, name: string}[]>([]);
  const [sites, setSites] = useState<{site_id: string, name: string, client_id: string}[]>([]);

  const fetchAssetsData = async () => {

    try {
      setLoading(true);

      if (user?.role === 'client_admin') {
        // Client admin sees only their organization's assets

        const [dashboardResponse, inventoryResponse] = await Promise.all([
          assetsService.getOrganizationDashboard(),
          assetsService.getOrganizationInventory()
        ]);

        console.log('🔧 Dashboard response:', dashboardResponse);
        console.log('🔧 Inventory response:', inventoryResponse);



        if (dashboardResponse && dashboardResponse.summary) {
          setSummary(dashboardResponse.summary);
        }
        if (inventoryResponse && inventoryResponse.assets) {
          setAssets(inventoryResponse.assets);
        }
      } else if (user?.role === 'superadmin' || user?.role === 'technician') {
        // Superadmin/technician sees all assets

        const response = await assetsService.getAllAssets();
        console.log('🔧 All assets response:', response);



        if (response && response.assets) {
          console.log('✅ ENTERING ASSETS PROCESSING BLOCK');
          console.log('🔧 Assets array:', response.assets);
          setAssets(response.assets);

          // Calculate summary from all assets
          const total = response.assets.length;
          const online = response.assets.filter((a: Asset) => a.agent_status === 'online').length;
          const warning = response.assets.filter((a: Asset) => a.agent_status === 'warning').length;
          const offline = response.assets.filter((a: Asset) => a.agent_status === 'offline').length;

          console.log('🔧 Summary calculated:', { total, online, warning, offline });

        setSummary({
          total_assets: total,
          online_assets: online,
          warning_assets: warning,
          offline_assets: offline,
          last_update: response.assets[0]?.last_seen || null
        });
      } else {

        setAssets([]);
        setSummary({
          total_assets: 0,
          online_assets: 0,
          warning_assets: 0,
          offline_assets: 0,
          last_update: null
        });
        }
      }
    } catch (error) {
      console.error('Error fetching assets:', error);
      alert('Error al cargar información de equipos: ' + error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssetsData();
  }, [user]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'offline':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <XCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      online: { label: 'En línea', className: 'bg-green-100 text-green-800' },
      warning: { label: 'Advertencia', className: 'bg-yellow-100 text-yellow-800' },
      offline: { label: 'Desconectado', className: 'bg-red-100 text-red-800' }
    };

    const config = statusConfig[status as keyof typeof statusConfig] ||
                  { label: 'Desconocido', className: 'bg-gray-100 text-gray-800' };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.className}`}>
        {config.label}
      </span>
    );
  };

  const formatLastSeen = (lastSeen: string) => {
    const date = new Date(lastSeen);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 60) {
      return `Hace ${diffMins} minutos`;
    } else if (diffHours < 24) {
      return `Hace ${diffHours} horas`;
    } else {
      return `Hace ${diffDays} días`;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
        <span className="ml-2">Cargando equipos...</span>
      </div>
    );
  }

  // Show technician dashboard for superadmin and technician roles
  if (user?.role === 'superadmin' || user?.role === 'technician') {
    return <TechnicianDashboard />;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Gestión de Equipos</h1>
        <button
          onClick={fetchAssetsData}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualizar
        </button>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Monitor className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total de Equipos</dt>
                    <dd className="text-lg font-medium text-gray-900">{summary.total_assets}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CheckCircle className="h-6 w-6 text-green-500" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">En Línea</dt>
                    <dd className="text-lg font-medium text-green-600">{summary.online_assets}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <AlertCircle className="h-6 w-6 text-yellow-500" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Con Advertencias</dt>
                    <dd className="text-lg font-medium text-yellow-600">{summary.warning_assets}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <XCircle className="h-6 w-6 text-red-500" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Desconectados</dt>
                    <dd className="text-lg font-medium text-red-600">{summary.offline_assets}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Assets List */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Lista de Equipos</h3>
        </div>
        <div className="px-4 py-5 sm:p-6">
          {assets.length === 0 ? (
            <div className="text-center py-8">
              <Monitor className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No hay equipos registrados</p>
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {assets.map((asset) => (
                <li
                  key={asset.asset_id}
                  className="py-4 hover:bg-gray-50 cursor-pointer transition-colors px-4 rounded"
                  onClick={() => setSelectedAsset(asset)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      {getStatusIcon(asset.agent_status)}
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">{asset.name}</h4>
                        <p className="text-sm text-gray-500">
                          {asset.site_name}
                          {asset.client_name && ` - ${asset.client_name}`}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      {getStatusBadge(asset.agent_status)}
                      <div className="text-right">
                        <p className="text-sm text-gray-500">
                          <Clock className="h-3 w-3 inline mr-1" />
                          {formatLastSeen(asset.last_seen)}
                        </p>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Asset Detail Modal */}
      {selectedAsset && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900">Detalles del Equipo</h2>
              <button
                onClick={() => setSelectedAsset(null)}
                className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
              >
                ×
              </button>
            </div>

            <div className="w-full">
              {/* Tab Navigation */}
              <div className="border-b border-gray-200 mb-4">
                <nav className="-mb-px flex space-x-8">
                    <button
                      onClick={() => setActiveTab('general')}
                      className={`py-2 px-1 border-b-2 font-medium text-sm ${
                        activeTab === 'general'
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                    >
                      General
                    </button>
                    <button
                      onClick={() => setActiveTab('hardware')}
                      className={`py-2 px-1 border-b-2 font-medium text-sm ${
                        activeTab === 'hardware'
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                    >
                      Hardware
                    </button>
                    <button
                      onClick={() => setActiveTab('software')}
                      className={`py-2 px-1 border-b-2 font-medium text-sm ${
                        activeTab === 'software'
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                    >
                      Software
                    </button>
                    <button
                      onClick={() => setActiveTab('metrics')}
                      className={`py-2 px-1 border-b-2 font-medium text-sm ${
                        activeTab === 'metrics'
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                    >
                      Métricas
                    </button>
                  </nav>
              </div>

              {/* Tab Content */}
              <div className="mt-4">
                {activeTab === 'general' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium text-gray-500">Nombre</label>
                        <p className="font-semibold text-gray-900">{selectedAsset.name}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Estado</label>
                        <div className="mt-1">{getStatusBadge(selectedAsset.agent_status)}</div>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Sitio</label>
                        <p className="font-semibold text-gray-900">{selectedAsset.site_name}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Última Conexión</label>
                        <p className="font-semibold text-gray-900">{formatLastSeen(selectedAsset.last_seen)}</p>
                      </div>
                      {selectedAsset.client_name && (
                        <div className="col-span-2">
                          <label className="text-sm font-medium text-gray-500">Cliente</label>
                          <p className="font-semibold text-gray-900">{selectedAsset.client_name}</p>
                        </div>
                      )}
                      {selectedAsset.site_address && (
                        <div className="col-span-2">
                          <label className="text-sm font-medium text-gray-500">Dirección del Sitio</label>
                          <p className="font-semibold text-gray-900">{selectedAsset.site_address}</p>
                        </div>
                      )}
                    </div>
                  </div>
              )}

              {activeTab === 'hardware' && (
                <div className="space-y-4">
                  {selectedAsset.specifications?.hardware_info ? (
                    <div className="space-y-4">
                        {/* System Information */}
                        {selectedAsset.specifications.hardware_info.system && (
                          <div>
                            <h4 className="font-medium text-gray-900 mb-2">Información del Sistema</h4>
                            <div className="bg-gray-50 p-3 rounded">
                              <div className="grid grid-cols-2 gap-2 text-sm">
                                <div><span className="font-medium">Hostname:</span> {selectedAsset.specifications.hardware_info.system.hostname}</div>
                                <div><span className="font-medium">Plataforma:</span> {selectedAsset.specifications.hardware_info.system.platform}</div>
                                <div><span className="font-medium">Procesador:</span> {selectedAsset.specifications.hardware_info.system.processor}</div>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* CPU Information */}
                        {selectedAsset.specifications.hardware_info.cpu && (
                          <div>
                            <h4 className="font-medium text-gray-900 mb-2">Procesador</h4>
                            <div className="bg-gray-50 p-3 rounded">
                              <div className="grid grid-cols-2 gap-2 text-sm">
                                <div><span className="font-medium">Núcleos:</span> {selectedAsset.specifications.hardware_info.cpu.cores || selectedAsset.specifications.hardware?.cpu?.cores}</div>
                                {selectedAsset.specifications.hardware_info.cpu.frequency?.current && (
                                  <div><span className="font-medium">Frecuencia:</span> {Math.round(selectedAsset.specifications.hardware_info.cpu.frequency.current)} MHz</div>
                                )}
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Memory Information */}
                        {selectedAsset.specifications.hardware_info.memory && (
                          <div>
                            <h4 className="font-medium text-gray-900 mb-2">Memoria</h4>
                            <div className="bg-gray-50 p-3 rounded">
                              <div className="text-sm">
                                <span className="font-medium">Memoria Total:</span> {selectedAsset.specifications.hardware_info.memory.total_gb || selectedAsset.specifications.hardware?.memory?.total_gb} GB
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Disk Information */}
                        {selectedAsset.specifications.hardware?.disk && (
                          <div>
                            <h4 className="font-medium text-gray-900 mb-2">Disco Principal</h4>
                            <div className="bg-gray-50 p-3 rounded">
                              <div className="grid grid-cols-2 gap-2 text-sm">
                                <div><span className="font-medium">Tamaño Total:</span> {selectedAsset.specifications.hardware.disk.total_gb} GB</div>
                                <div><span className="font-medium">Espacio Libre:</span> {selectedAsset.specifications.hardware.disk.free_gb} GB</div>
                                <div><span className="font-medium">Espacio Usado:</span> {(selectedAsset.specifications.hardware.disk.total_gb - selectedAsset.specifications.hardware.disk.free_gb).toFixed(2)} GB</div>
                                <div><span className="font-medium">Uso:</span> {((selectedAsset.specifications.hardware.disk.total_gb - selectedAsset.specifications.hardware.disk.free_gb) / selectedAsset.specifications.hardware.disk.total_gb * 100).toFixed(1)}%</div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <HardDrive className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-500">No hay información de hardware disponible</p>
                      </div>
                    )}
                  </div>
              )}

              {activeTab === 'software' && (
                <div className="space-y-4">
                    {selectedAsset.specifications?.software_info ? (
                      <div className="space-y-4">
                        {/* Operating System */}
                        {selectedAsset.specifications.software_info.operating_system && (
                          <div>
                            <h4 className="font-medium text-gray-900 mb-2">Sistema Operativo</h4>
                            <div className="bg-gray-50 p-3 rounded">
                              <div className="grid grid-cols-2 gap-2 text-sm">
                                <div><span className="font-medium">Nombre:</span> {selectedAsset.specifications.software_info.operating_system.name}</div>
                                <div><span className="font-medium">Versión:</span> {selectedAsset.specifications.software_info.operating_system.version}</div>
                                <div><span className="font-medium">Release:</span> {selectedAsset.specifications.software_info.operating_system.release}</div>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Python Information */}
                        {selectedAsset.specifications.software_info.python && (
                          <div>
                            <h4 className="font-medium text-gray-900 mb-2">Python</h4>
                            <div className="bg-gray-50 p-3 rounded">
                              <div className="text-sm">
                                <span className="font-medium">Versión:</span> {selectedAsset.specifications.software_info.python.version}
                                {selectedAsset.specifications.software_info.python.implementation && (
                                  <span> ({selectedAsset.specifications.software_info.python.implementation})</span>
                                )}
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Installed Programs */}
                        {selectedAsset.specifications.software_info.installed_programs && selectedAsset.specifications.software_info.installed_programs.length > 0 && (
                          <div>
                            <h4 className="font-medium text-gray-900 mb-2">Programas Instalados</h4>
                            <div className="max-h-40 overflow-y-auto space-y-1">
                              {selectedAsset.specifications.software_info.installed_programs.slice(0, 10).map((program: any, index: number) => (
                                <div key={index} className="bg-gray-50 p-2 rounded text-sm">
                                  <div className="font-medium">{program.name}</div>
                                  <div className="text-gray-600">Versión: {program.version} | Proveedor: {program.vendor}</div>
                                </div>
                              ))}
                              {selectedAsset.specifications.software_info.installed_programs.length > 10 && (
                                <div className="text-sm text-gray-500 text-center py-2">
                                  ... y {selectedAsset.specifications.software_info.installed_programs.length - 10} programas más
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-500">No hay información de software disponible</p>
                      </div>
                    )}
                  </div>
              )}

              {activeTab === 'metrics' && (
                <div className="space-y-4">
                    {selectedAsset.specifications?.system_metrics ? (
                      <div className="space-y-4">
                        {/* Current Metrics */}
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">Métricas Actuales</h4>
                          <div className="grid grid-cols-2 gap-4">
                            <div className="bg-gray-50 p-3 rounded">
                              <div className="text-sm">
                                <div className="font-medium text-gray-700">CPU</div>
                                <div className="text-2xl font-bold text-blue-600">{selectedAsset.specifications.system_metrics.cpu_usage || 0}%</div>
                              </div>
                            </div>
                            <div className="bg-gray-50 p-3 rounded">
                              <div className="text-sm">
                                <div className="font-medium text-gray-700">Memoria</div>
                                <div className="text-2xl font-bold text-green-600">{selectedAsset.specifications.system_metrics.memory_usage || 0}%</div>
                              </div>
                            </div>
                            <div className="bg-gray-50 p-3 rounded">
                              <div className="text-sm">
                                <div className="font-medium text-gray-700">Disco</div>
                                <div className="text-2xl font-bold text-yellow-600">{Math.round(selectedAsset.specifications.system_metrics.disk_usage || 0)}%</div>
                              </div>
                            </div>
                            <div className="bg-gray-50 p-3 rounded">
                              <div className="text-sm">
                                <div className="font-medium text-gray-700">Red</div>
                                <div className="text-lg font-bold text-purple-600">{selectedAsset.specifications.system_metrics.network_status || 'Desconocido'}</div>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Additional Metrics */}
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">Información Adicional</h4>
                          <div className="bg-gray-50 p-3 rounded">
                            <div className="grid grid-cols-2 gap-2 text-sm">
                              {selectedAsset.specifications.system_metrics.uptime && (
                                <div><span className="font-medium">Tiempo Encendido:</span> {Math.round(selectedAsset.specifications.system_metrics.uptime / 3600)} horas</div>
                              )}
                              {selectedAsset.specifications.system_metrics.processes_count && (
                                <div><span className="font-medium">Procesos:</span> {selectedAsset.specifications.system_metrics.processes_count}</div>
                              )}
                              {selectedAsset.specifications.system_metrics.logged_users !== undefined && (
                                <div><span className="font-medium">Usuarios Conectados:</span> {selectedAsset.specifications.system_metrics.logged_users}</div>
                              )}
                              {selectedAsset.specifications.system_metrics.antivirus_status && (
                                <div><span className="font-medium">Antivirus:</span> {selectedAsset.specifications.system_metrics.antivirus_status}</div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-500">No hay métricas del sistema disponibles</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Assets;
