import React, { useState } from 'react';
import { Shield, Lock, Unlock, Eye, EyeOff, RefreshCw, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

interface BitLockerVolume {
  id: string;
  volume_letter: string;
  volume_label: string;
  protection_status: 'Protected' | 'Unprotected' | 'Unknown';
  encryption_method?: string;
  key_protector_type?: string;
  recovery_key_id?: string;
  recovery_key?: string;
  created_at?: string;
  updated_at?: string;
  last_verified_at?: string;
}

interface BitLockerSummary {
  total_volumes: number;
  protected_volumes: number;
  unprotected_volumes: number;
  protection_percentage: number;
}

interface BitLockerData {
  summary: BitLockerSummary;
  volumes: BitLockerVolume[];
}

interface BitLockerTabProps {
  assetId: string;
  userRole: string;
}

const BitLockerTab: React.FC<BitLockerTabProps> = ({ assetId, userRole }) => {
  const [bitlockerData, setBitlockerData] = useState<BitLockerData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [visibleKeys, setVisibleKeys] = useState<Set<string>>(new Set());

  // Check if user can view recovery keys
  const canViewKeys = userRole === 'superadmin' || userRole === 'technician';

  React.useEffect(() => {
    fetchBitLockerData();
  }, [assetId]);

  const fetchBitLockerData = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/bitlocker/${assetId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      
      if (result.success) {
        setBitlockerData(result.data);
      } else {
        throw new Error(result.error || 'Failed to fetch BitLocker data');
      }
    } catch (err) {
      console.error('Error fetching BitLocker data:', err);
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const toggleKeyVisibility = (volumeId: string) => {
    const newVisibleKeys = new Set(visibleKeys);
    if (newVisibleKeys.has(volumeId)) {
      newVisibleKeys.delete(volumeId);
    } else {
      newVisibleKeys.add(volumeId);
    }
    setVisibleKeys(newVisibleKeys);
  };

  const getProtectionIcon = (status: string) => {
    switch (status) {
      case 'Protected':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'Unprotected':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getProtectionColor = (status: string) => {
    switch (status) {
      case 'Protected':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'Unprotected':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <RefreshCw className="w-6 h-6 animate-spin text-blue-500 mr-2" />
        <span>Cargando información de BitLocker...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
          <span className="text-red-700">Error: {error}</span>
        </div>
        <button
          onClick={fetchBitLockerData}
          className="mt-2 px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
        >
          Reintentar
        </button>
      </div>
    );
  }

  if (!bitlockerData) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <div className="flex items-center">
          <Shield className="w-5 h-5 text-gray-500 mr-2" />
          <span className="text-gray-700">No hay datos de BitLocker disponibles</span>
        </div>
      </div>
    );
  }

  const { summary, volumes } = bitlockerData;

  return (
    <div className="space-y-6">
      {/* Summary Section */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Shield className="w-6 h-6 text-blue-500 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900">Estado General de BitLocker</h3>
          <button
            onClick={fetchBitLockerData}
            className="ml-auto p-2 text-gray-500 hover:text-gray-700 transition-colors"
            title="Actualizar"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="text-2xl font-bold text-blue-600">{summary.total_volumes}</div>
            <div className="text-sm text-blue-700">Volúmenes Total</div>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="text-2xl font-bold text-green-600">{summary.protected_volumes}</div>
            <div className="text-sm text-green-700">Protegidos</div>
          </div>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="text-2xl font-bold text-red-600">{summary.unprotected_volumes}</div>
            <div className="text-sm text-red-700">Sin Proteger</div>
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <div className="text-2xl font-bold text-purple-600">{summary.protection_percentage}%</div>
            <div className="text-sm text-purple-700">Protección</div>
          </div>
        </div>
      </div>

      {/* Volumes Section */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Lock className="w-6 h-6 text-gray-700 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900">Volúmenes ({volumes.length})</h3>
        </div>

        {volumes.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Shield className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p>No se encontraron volúmenes BitLocker</p>
          </div>
        ) : (
          <div className="space-y-4">
            {volumes.map((volume) => (
              <div
                key={volume.id}
                className={`border rounded-lg p-4 ${getProtectionColor(volume.protection_status)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      {getProtectionIcon(volume.protection_status)}
                      <span className="ml-2 font-semibold text-lg">
                        {volume.volume_letter} - {volume.volume_label}
                      </span>
                      <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${getProtectionColor(volume.protection_status)}`}>
                        {volume.protection_status}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium">Método de Encriptación:</span>
                        <span className="ml-2">{volume.encryption_method || 'N/A'}</span>
                      </div>
                      <div>
                        <span className="font-medium">Protector de Clave:</span>
                        <span className="ml-2">{volume.key_protector_type || 'N/A'}</span>
                      </div>
                    </div>

                    {/* Recovery Key Section - Only for authorized users */}
                    {canViewKeys && volume.recovery_key && (
                      <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-yellow-800">Clave de Recuperación:</span>
                          <button
                            onClick={() => toggleKeyVisibility(volume.id)}
                            className="flex items-center px-2 py-1 text-yellow-700 hover:text-yellow-900 transition-colors"
                          >
                            {visibleKeys.has(volume.id) ? (
                              <>
                                <EyeOff className="w-4 h-4 mr-1" />
                                Ocultar
                              </>
                            ) : (
                              <>
                                <Eye className="w-4 h-4 mr-1" />
                                Mostrar
                              </>
                            )}
                          </button>
                        </div>
                        {visibleKeys.has(volume.id) && (
                          <div className="mt-2 p-2 bg-white border rounded font-mono text-sm break-all">
                            {volume.recovery_key}
                          </div>
                        )}
                      </div>
                    )}

                    {/* No access message for non-authorized users */}
                    {!canViewKeys && volume.recovery_key && (
                      <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded">
                        <div className="flex items-center text-gray-600">
                          <Lock className="w-4 h-4 mr-2" />
                          <span className="text-sm">Clave de recuperación disponible (solo para administradores y técnicos)</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Access Control Notice */}
      {!canViewKeys && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <Shield className="w-5 h-5 text-blue-500 mr-2" />
            <span className="text-blue-700 text-sm">
              Las claves de recuperación de BitLocker solo son visibles para usuarios con rol de Administrador o Técnico.
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default BitLockerTab;
