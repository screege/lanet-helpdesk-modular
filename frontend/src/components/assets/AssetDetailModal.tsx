import React, { useState, useEffect } from 'react';
import {
  X,
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
  RefreshCw,
  Calendar,
  User,
  MapPin,
  Building
} from 'lucide-react';
import { assetsService } from '../../services/assetsService';

interface Asset {
  asset_id: string;
  name: string;
  agent_status: string;
  last_seen: string;
  specifications: any;
  site_name: string;
  site_id: string;
  site_address: string;
  client_name: string;
  client_id: string;
}

interface AssetDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  asset: Asset;
}

const AssetDetailModal: React.FC<AssetDetailModalProps> = ({ isOpen, onClose, asset }) => {
  const [activeTab, setActiveTab] = useState('general');
  const [assetDetails, setAssetDetails] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && asset) {
      loadAssetDetails();
    }
  }, [isOpen, asset]);

  const loadAssetDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await assetsService.getAssetDetail(asset.asset_id);
      setAssetDetails(response.asset);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
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

  const formatLastSeen = (lastSeen: string) => {
    if (!lastSeen) return 'Nunca';
    
    const date = new Date(lastSeen);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 1) return 'Ahora mismo';
    if (diffMins < 60) return `Hace ${diffMins} min`;
    if (diffHours < 24) return `Hace ${diffHours}h`;
    if (diffDays < 7) return `Hace ${diffDays}d`;
    
    return date.toLocaleDateString('es-MX');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-2/3 xl:w-1/2 shadow-lg rounded-md bg-white max-h-[80vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center space-x-3">
            <Monitor className="w-6 h-6 text-blue-600" />
            <div>
              <h2 className="text-xl font-bold text-gray-900">{asset.name}</h2>
              <p className="text-sm text-gray-500">{asset.client_name} - {asset.site_name}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Status Bar */}
        <div className="flex items-center justify-between mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-4">
            <div>
              <span className="text-sm font-medium text-gray-500">Estado:</span>
              <div className="mt-1">{getStatusBadge(asset.agent_status)}</div>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-500">Última conexión:</span>
              <p className="text-sm font-medium text-gray-900">{formatLastSeen(asset.last_seen)}</p>
            </div>
          </div>
          <button
            onClick={loadAssetDetails}
            disabled={loading}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualizar
          </button>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-4">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'general', name: 'General', icon: Monitor },
              { id: 'hardware', name: 'Hardware', icon: Cpu },
              { id: 'software', name: 'Software', icon: HardDrive },
              { id: 'metrics', name: 'Métricas', icon: Activity }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center h-64">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
            <span className="ml-2 text-gray-600">Cargando detalles...</span>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
              <span className="text-red-800">Error: {error}</span>
            </div>
            <button
              onClick={loadAssetDetails}
              className="mt-2 text-red-600 hover:text-red-800 text-sm underline"
            >
              Reintentar
            </button>
          </div>
        )}

        {/* Tab Content */}
        {!loading && !error && (
          <div className="mt-4">
            {activeTab === 'general' && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-gray-500 flex items-center">
                        <Monitor className="w-4 h-4 mr-1" />
                        Nombre del Equipo
                      </label>
                      <p className="font-semibold text-gray-900">{asset.name}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500 flex items-center">
                        <Building className="w-4 h-4 mr-1" />
                        Cliente
                      </label>
                      <p className="font-semibold text-gray-900">{asset.client_name}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500 flex items-center">
                        <MapPin className="w-4 h-4 mr-1" />
                        Sitio
                      </label>
                      <p className="font-semibold text-gray-900">{asset.site_name}</p>
                      {asset.site_address && (
                        <p className="text-sm text-gray-600">{asset.site_address}</p>
                      )}
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-gray-500">Estado del Agente</label>
                      <div className="mt-1">{getStatusBadge(asset.agent_status)}</div>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500 flex items-center">
                        <Clock className="w-4 h-4 mr-1" />
                        Última Conexión
                      </label>
                      <p className="font-semibold text-gray-900">{formatLastSeen(asset.last_seen)}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">ID del Asset</label>
                      <p className="font-mono text-sm text-gray-900">{asset.asset_id}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'hardware' && (
              <div className="space-y-4">
                {assetDetails?.specifications?.hardware_info ? (
                  <div className="space-y-4">
                    {/* System Information */}
                    {assetDetails.specifications.hardware_info.system && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                          <Cpu className="w-4 h-4 mr-2" />
                          Información del Sistema
                        </h4>
                        <div className="bg-gray-50 p-3 rounded">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                            <div><span className="font-medium">Hostname:</span> {assetDetails.specifications.hardware_info.system.hostname}</div>
                            <div><span className="font-medium">Plataforma:</span> {assetDetails.specifications.hardware_info.system.platform}</div>
                            <div><span className="font-medium">Procesador:</span> {assetDetails.specifications.hardware_info.system.processor}</div>
                            <div><span className="font-medium">Arquitectura:</span> {assetDetails.specifications.hardware_info.system.architecture}</div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Memory Information */}
                    {assetDetails.specifications.hardware_info.memory && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                          <MemoryStick className="w-4 h-4 mr-2" />
                          Memoria
                        </h4>
                        <div className="bg-gray-50 p-3 rounded">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                            <div><span className="font-medium">Total:</span> {assetDetails.specifications.hardware_info.memory.total}</div>
                            <div><span className="font-medium">Disponible:</span> {assetDetails.specifications.hardware_info.memory.available}</div>
                            <div><span className="font-medium">Usado:</span> {assetDetails.specifications.hardware_info.memory.used}</div>
                            <div><span className="font-medium">Porcentaje:</span> {assetDetails.specifications.hardware_info.memory.percent}%</div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Disk Information */}
                    {assetDetails.specifications.hardware_info.disk && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                          <HardDrive className="w-4 h-4 mr-2" />
                          Almacenamiento
                        </h4>
                        <div className="space-y-2">
                          {assetDetails.specifications.hardware_info.disk.map((disk: any, index: number) => (
                            <div key={index} className="bg-gray-50 p-3 rounded">
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm">
                                <div><span className="font-medium">Dispositivo:</span> {disk.device}</div>
                                <div><span className="font-medium">Total:</span> {disk.total}</div>
                                <div><span className="font-medium">Usado:</span> {disk.used} ({disk.percent}%)</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Cpu className="mx-auto h-12 w-12 text-gray-400" />
                    <h3 className="mt-2 text-sm font-medium text-gray-900">No hay información de hardware</h3>
                    <p className="mt-1 text-sm text-gray-500">
                      La información de hardware no está disponible para este equipo.
                    </p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'software' && (
              <div className="space-y-4">
                <div className="text-center py-8">
                  <HardDrive className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">Información de software</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Esta funcionalidad estará disponible próximamente.
                  </p>
                </div>
              </div>
            )}

            {activeTab === 'metrics' && (
              <div className="space-y-4">
                {assetDetails?.specifications?.system_metrics ? (
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                        <Activity className="w-4 h-4 mr-2" />
                        Métricas Actuales
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-blue-50 p-4 rounded-lg">
                          <div className="text-sm">
                            <div className="font-medium text-blue-900">CPU</div>
                            <div className="text-2xl font-bold text-blue-600">
                              {assetDetails.specifications.system_metrics.cpu_usage || 0}%
                            </div>
                          </div>
                        </div>
                        <div className="bg-green-50 p-4 rounded-lg">
                          <div className="text-sm">
                            <div className="font-medium text-green-900">Memoria</div>
                            <div className="text-2xl font-bold text-green-600">
                              {assetDetails.specifications.system_metrics.memory_usage || 0}%
                            </div>
                          </div>
                        </div>
                        <div className="bg-yellow-50 p-4 rounded-lg">
                          <div className="text-sm">
                            <div className="font-medium text-yellow-900">Disco</div>
                            <div className="text-2xl font-bold text-yellow-600">
                              {assetDetails.specifications.system_metrics.disk_usage || 0}%
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Activity className="mx-auto h-12 w-12 text-gray-400" />
                    <h3 className="mt-2 text-sm font-medium text-gray-900">No hay métricas disponibles</h3>
                    <p className="mt-1 text-sm text-gray-500">
                      Las métricas del sistema no están disponibles para este equipo.
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AssetDetailModal;
