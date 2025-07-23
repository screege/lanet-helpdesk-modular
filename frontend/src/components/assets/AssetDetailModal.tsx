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
                {assetDetails?.formatted_hardware ? (
                  <div className="space-y-4">
                    {/* System Information */}
                    {assetDetails.formatted_hardware.system && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                          <Cpu className="w-4 h-4 mr-2" />
                          Información del Sistema
                        </h4>
                        <div className="bg-gray-50 p-3 rounded">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                            <div><span className="font-medium">Hostname:</span> {assetDetails.formatted_hardware.system.hostname}</div>
                            <div><span className="font-medium">Plataforma:</span> {assetDetails.formatted_hardware.system.platform}</div>
                            <div><span className="font-medium">Procesador:</span> {assetDetails.formatted_hardware.system.processor}</div>
                            <div><span className="font-medium">Arquitectura:</span> {assetDetails.formatted_hardware.system.architecture}</div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Memory Information */}
                    {assetDetails.formatted_hardware.memory && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                          <MemoryStick className="w-4 h-4 mr-2" />
                          Memoria
                        </h4>
                        <div className="bg-gray-50 p-3 rounded">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                            <div><span className="font-medium">Total:</span> {assetDetails.formatted_hardware.memory.total_gb} GB</div>
                            <div><span className="font-medium">Disponible:</span> {assetDetails.formatted_hardware.memory.available_gb} GB</div>
                            <div><span className="font-medium">Usado:</span> {assetDetails.formatted_hardware.memory.used_gb} GB</div>
                            <div><span className="font-medium">Porcentaje:</span> {assetDetails.formatted_hardware.memory.usage_percent}%</div>
                          </div>
                          {/* Memory Modules */}
                          {assetDetails.formatted_hardware.memory.modules && assetDetails.formatted_hardware.memory.modules.length > 0 && (
                            <div className="mt-3">
                              <h5 className="font-medium text-gray-700 mb-2">Módulos de Memoria ({assetDetails.formatted_hardware.memory.modules.length})</h5>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                {assetDetails.formatted_hardware.memory.modules.map((module: any, index: number) => (
                                  <div key={index} className="bg-white p-2 rounded border text-xs">
                                    <div><span className="font-medium">Slot {index + 1}:</span> {module.capacity_gb} GB</div>
                                    <div><span className="font-medium">Fabricante:</span> {module.manufacturer}</div>
                                    <div><span className="font-medium">Velocidad:</span> {module.speed_mhz} MHz</div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Disk Information */}
                    {assetDetails.formatted_hardware.disks && assetDetails.formatted_hardware.disks.length > 0 && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                          <HardDrive className="w-4 h-4 mr-2" />
                          Almacenamiento
                        </h4>
                        <div className="space-y-3">
                          {assetDetails.formatted_hardware.disks.map((disk: any, index: number) => (
                            <div key={index} className="bg-gray-50 p-3 rounded">
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                <div className="space-y-1 text-sm">
                                  <div><span className="font-medium">Dispositivo:</span> {disk.device}</div>
                                  <div><span className="font-medium">Tipo:</span> {disk.fstype || 'N/A'}</div>
                                  <div><span className="font-medium">Total:</span> {disk.total_gb} GB</div>
                                  <div><span className="font-medium">Usado:</span> {disk.used_gb} GB ({disk.usage_percent}%)</div>
                                </div>
                                <div className="space-y-1 text-sm">
                                  {disk.model && <div><span className="font-medium">Modelo:</span> {disk.model}</div>}
                                  {disk.serial_number && <div><span className="font-medium">Serie:</span> {disk.serial_number}</div>}
                                  {disk.interface_type && <div><span className="font-medium">Interfaz:</span> {disk.interface_type}</div>}
                                  <div>
                                    <span className="font-medium">Estado SMART:</span>
                                    <span className={`ml-1 px-2 py-1 rounded text-xs ${
                                      disk.health_status === 'OK' ? 'bg-green-100 text-green-800' :
                                      disk.health_status === 'Warning' ? 'bg-yellow-100 text-yellow-800' :
                                      'bg-red-100 text-red-800'
                                    }`}>
                                      {disk.health_status || 'Desconocido'}
                                    </span>
                                  </div>
                                  {disk.temperature && disk.temperature !== 'Not available' && (
                                    <div><span className="font-medium">Temperatura:</span> {disk.temperature}°C</div>
                                  )}
                                </div>
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
                {assetDetails?.specifications?.software_info ? (
                  <div className="space-y-4">
                    {/* Operating System */}
                    {assetDetails.specifications.software_info.operating_system && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                          <Monitor className="w-4 h-4 mr-2" />
                          Sistema Operativo
                        </h4>
                        <div className="bg-gray-50 p-3 rounded">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                            <div><span className="font-medium">Nombre:</span> {assetDetails.specifications.software_info.operating_system.name}</div>
                            <div><span className="font-medium">Versión:</span> {assetDetails.specifications.software_info.operating_system.version}</div>
                            <div><span className="font-medium">Arquitectura:</span> {assetDetails.specifications.software_info.operating_system.architecture}</div>
                            <div><span className="font-medium">Build:</span> {assetDetails.specifications.software_info.operating_system.build}</div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* System Information */}
                    {assetDetails.specifications.software_info.system_info && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                          <Cpu className="w-4 h-4 mr-2" />
                          Información del Sistema
                        </h4>
                        <div className="bg-gray-50 p-3 rounded">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                            <div><span className="font-medium">Nombre del Equipo:</span> {assetDetails.specifications.software_info.system_info.computer_name}</div>
                            <div><span className="font-medium">Arquitectura:</span> {assetDetails.specifications.software_info.system_info.architecture}</div>
                            <div><span className="font-medium">Procesador:</span> {assetDetails.specifications.software_info.system_info.processor}</div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Installed Programs */}
                    {assetDetails.specifications.software_info.installed_programs && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                          <HardDrive className="w-4 h-4 mr-2" />
                          Programas Instalados ({assetDetails.specifications.software_info.installed_programs.length})
                        </h4>
                        <div className="bg-gray-50 p-3 rounded max-h-96 overflow-y-auto">
                          <div className="space-y-2">
                            {assetDetails.specifications.software_info.installed_programs.map((program: any, index: number) => (
                              <div key={index} className="flex justify-between items-center py-2 px-3 bg-white rounded border">
                                <div className="flex-1">
                                  <div className="font-medium text-sm text-gray-900">{program.name}</div>
                                  <div className="text-xs text-gray-500">
                                    Versión: {program.version || 'N/A'} | Editor: {program.publisher || 'N/A'}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Python Information */}
                    {assetDetails.specifications.software_info.python && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                          <Activity className="w-4 h-4 mr-2" />
                          Python
                        </h4>
                        <div className="bg-gray-50 p-3 rounded">
                          <div className="text-sm">
                            <div><span className="font-medium">Versión:</span> {assetDetails.specifications.software_info.python.version}</div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <HardDrive className="mx-auto h-12 w-12 text-gray-400" />
                    <h3 className="mt-2 text-sm font-medium text-gray-900">No hay información de software</h3>
                    <p className="mt-1 text-sm text-gray-500">
                      La información de software no está disponible para este equipo.
                    </p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'metrics' && (
              <div className="space-y-4">
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                      <Activity className="w-4 h-4 mr-2" />
                      Métricas en Tiempo Real
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <div className="text-sm">
                          <div className="font-medium text-blue-900">CPU</div>
                          <div className="text-2xl font-bold text-blue-600">
                            {assetDetails?.cpu_percent || 0}%
                          </div>
                          <div className="text-xs text-blue-700 mt-1">Uso actual del procesador</div>
                        </div>
                      </div>
                      <div className="bg-green-50 p-4 rounded-lg">
                        <div className="text-sm">
                          <div className="font-medium text-green-900">Memoria</div>
                          <div className="text-2xl font-bold text-green-600">
                            {assetDetails?.memory_percent || 0}%
                          </div>
                          <div className="text-xs text-green-700 mt-1">Uso actual de RAM</div>
                        </div>
                      </div>
                      <div className="bg-yellow-50 p-4 rounded-lg">
                        <div className="text-sm">
                          <div className="font-medium text-yellow-900">Disco</div>
                          <div className="text-2xl font-bold text-yellow-600">
                            {assetDetails?.disk_percent || 0}%
                          </div>
                          <div className="text-xs text-yellow-700 mt-1">Uso del disco principal</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Additional System Info */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                      <Clock className="w-4 h-4 mr-2" />
                      Información del Sistema
                    </h4>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">Estado de Conexión:</span>
                          <span className={`ml-2 px-2 py-1 rounded text-xs ${
                            assetDetails?.connection_status === 'online' ? 'bg-green-100 text-green-800' :
                            assetDetails?.connection_status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {assetDetails?.connection_status === 'online' ? 'En línea' :
                             assetDetails?.connection_status === 'warning' ? 'Advertencia' : 'Desconectado'}
                          </span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Último Heartbeat:</span>
                          <span className="ml-2 text-gray-600">
                            {assetDetails?.last_heartbeat ? formatLastSeen(assetDetails.last_heartbeat) : 'N/A'}
                          </span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Última Actualización:</span>
                          <span className="ml-2 text-gray-600">
                            {formatLastSeen(assetDetails?.last_seen || asset.last_seen)}
                          </span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Alertas Activas:</span>
                          <span className="ml-2 text-gray-600">
                            {assetDetails?.alert_count || 0}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AssetDetailModal;
