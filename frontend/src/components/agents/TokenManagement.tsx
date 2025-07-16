import React, { useState, useEffect } from 'react';
import {
  Plus,
  Copy,
  Eye,
  EyeOff,
  Calendar,
  Activity,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';
import { agentsService, AgentToken, CreateTokenData } from '../../services/agentsService';
import { useAuth } from '../../contexts/AuthContext';

interface TokenManagementProps {
  clientId: string;
  siteId?: string;
  clientName: string;
  siteName?: string;
}

const TokenManagement: React.FC<TokenManagementProps> = ({
  clientId,
  siteId,
  clientName,
  siteName
}) => {
  const { user } = useAuth();
  const [tokens, setTokens] = useState<AgentToken[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [visibleTokens, setVisibleTokens] = useState<Set<string>>(new Set());
  const [copiedToken, setCopiedToken] = useState<string | null>(null);
  const [sites, setSites] = useState<any[]>([]);

  // Load tokens on component mount
  useEffect(() => {
    loadTokens();
    loadSites();
  }, [clientId, siteId]);

  const loadTokens = async () => {
    try {
      setLoading(true);
      setError(null);

      let response;
      if (siteId) {
        response = await agentsService.getTokensForSite(clientId, siteId);
      } else {
        response = await agentsService.getTokensForClient(clientId);
      }

      setTokens(response.tokens);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadSites = async () => {
    if (!siteId) {
      try {
        // Cargar sitios del cliente para el selector
        const response = await fetch(`/api/clients/${clientId}/sites`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        if (response.ok) {
          const data = await response.json();
          setSites(data.data || []);
        }
      } catch (err) {
        console.error('Error loading sites:', err);
      }
    }
  };

  const handleCreateToken = async (data: CreateTokenData & { selectedSiteId?: string }) => {
    const targetSiteId = data.selectedSiteId || siteId;
    if (!targetSiteId) {
      setError('Se requiere seleccionar un sitio específico para crear tokens');
      return;
    }

    try {
      const newToken = await agentsService.createToken(clientId, targetSiteId, data);
      setTokens(prev => [newToken, ...prev]);
      setShowCreateModal(false);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleToggleTokenStatus = async (tokenId: string, currentStatus: boolean) => {
    if (!tokenId) {
      setError('Token ID no válido');
      return;
    }

    try {
      const updatedToken = await agentsService.updateTokenStatus(tokenId, !currentStatus);
      setTokens(prev => prev.map(token =>
        token.token_id === tokenId ? updatedToken : token
      ));
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleCopyToken = async (tokenValue: string) => {
    const success = await agentsService.copyTokenToClipboard(tokenValue);
    if (success) {
      setCopiedToken(tokenValue);
      setTimeout(() => setCopiedToken(null), 2000);
    }
  };

  const toggleTokenVisibility = (tokenId: string) => {
    setVisibleTokens(prev => {
      const newSet = new Set(prev);
      if (newSet.has(tokenId)) {
        newSet.delete(tokenId);
      } else {
        newSet.add(tokenId);
      }
      return newSet;
    });
  };

  const getStatusBadge = (token: AgentToken) => {
    const expiration = agentsService.getTokenExpirationStatus(token);
    
    if (!token.is_active) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
          <AlertCircle className="w-3 h-3 mr-1" />
          Inactivo
        </span>
      );
    }

    if (expiration.status === 'expired') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
          <AlertCircle className="w-3 h-3 mr-1" />
          Expirado
        </span>
      );
    }

    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
        <CheckCircle className="w-3 h-3 mr-1" />
        Activo
      </span>
    );
  };

  const canCreateTokens = user?.role === 'superadmin' || user?.role === 'technician';

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div>
          <h4 className="text-sm font-medium text-gray-900">Tokens de Instalación</h4>
          <p className="text-xs text-gray-500">
            Gestiona tokens para {siteName} en {clientName}
          </p>
        </div>

        {canCreateTokens && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-2 py-1 border border-transparent text-xs font-medium rounded text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-1 focus:ring-offset-1 focus:ring-blue-500"
          >
            <Plus className="w-3 h-3 mr-1" />
            Nuevo Token
          </button>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">{error}</div>
            </div>
          </div>
        </div>
      )}

      {/* Tokens List */}
      {tokens.length === 0 ? (
        <div className="text-center py-4">
          <Activity className="mx-auto h-8 w-8 text-gray-400" />
          <h4 className="mt-2 text-xs font-medium text-gray-900">No hay tokens</h4>
          <p className="mt-1 text-xs text-gray-500">
            No se han generado tokens para este sitio.
          </p>
          {canCreateTokens && (
            <div className="mt-3">
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center px-2 py-1 border border-transparent text-xs font-medium rounded text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-1 focus:ring-offset-1 focus:ring-blue-500"
              >
                <Plus className="w-3 h-3 mr-1" />
                Generar Primer Token
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          {tokens.map((token, index) => (
            <div key={token.token_id || `token-${index}`} className="border border-gray-200 rounded-lg p-3">
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-2">
                    {getStatusBadge(token)}
                    <span className="text-xs text-gray-500">
                      Creado por {token.created_by_name}
                    </span>
                    <span className="text-xs text-gray-500">
                      <Calendar className="w-3 h-3 inline mr-1" />
                      {new Date(token.created_at).toLocaleDateString('es-MX')}
                    </span>
                  </div>

                  <div className="flex items-center space-x-2">
                    <code className="px-2 py-1 bg-gray-100 rounded text-xs font-mono flex-1">
                      {visibleTokens.has(token.token_id)
                        ? token.token_value
                        : '••••••••••••••••••••••••••••••••••••••••••••••••••'
                      }
                    </code>
                    <button
                      onClick={() => toggleTokenVisibility(token.token_id)}
                      className="p-1 text-gray-400 hover:text-gray-600"
                      title={visibleTokens.has(token.token_id) ? 'Ocultar token' : 'Mostrar token'}
                    >
                      {visibleTokens.has(token.token_id) ? (
                        <EyeOff className="w-3 h-3" />
                      ) : (
                        <Eye className="w-3 h-3" />
                      )}
                    </button>
                    <button
                      onClick={() => handleCopyToken(token.token_value)}
                      className="p-1 text-gray-400 hover:text-gray-600"
                      title="Copiar token"
                    >
                      <Copy className="w-3 h-3" />
                    </button>
                    {copiedToken === token.token_value && (
                      <span className="text-xs text-green-600">¡Copiado!</span>
                    )}
                  </div>

                  {token.notes && (
                    <p className="mt-1 text-xs text-gray-600">{token.notes}</p>
                  )}

                  <div className="mt-2 flex items-center space-x-3 text-xs text-gray-500">
                    <span>
                      <Activity className="w-3 h-3 inline mr-1" />
                      Usado {token.usage_count} veces
                    </span>
                    {token.expires_at && (
                      <span>
                        Expira: {agentsService.getTokenExpirationStatus(token).message}
                      </span>
                    )}
                  </div>
                </div>

                {canCreateTokens && (
                  <div className="flex items-center">
                    <button
                      onClick={() => handleToggleTokenStatus(token.token_id, token.is_active)}
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        token.is_active
                          ? 'bg-red-100 text-red-800 hover:bg-red-200'
                          : 'bg-green-100 text-green-800 hover:bg-green-200'
                      }`}
                    >
                      {token.is_active ? 'Desactivar' : 'Activar'}
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Token Modal */}
      {showCreateModal && (
        <CreateTokenModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateToken}
          clientName={clientName}
          siteName={siteName || ''}
          sites={sites}
          requireSiteSelection={!siteId}
        />
      )}
    </div>
  );
};

// Create Token Modal Component
interface CreateTokenModalProps {
  onClose: () => void;
  onSubmit: (data: CreateTokenData & { selectedSiteId?: string }) => void;
  clientName: string;
  siteName: string;
  sites?: any[];
  requireSiteSelection?: boolean;
}

const CreateTokenModal: React.FC<CreateTokenModalProps> = ({
  onClose,
  onSubmit,
  clientName,
  siteName,
  sites = [],
  requireSiteSelection = false
}) => {
  const [formData, setFormData] = useState<CreateTokenData & { selectedSiteId?: string }>({
    expires_days: undefined,
    notes: '',
    selectedSiteId: undefined
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await onSubmit(formData);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Generar Nuevo Token
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Crear token de instalación para {requireSiteSelection ? 'un sitio' : <strong>{siteName}</strong>} en <strong>{clientName}</strong>
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            {requireSiteSelection && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sitio *
                </label>
                <select
                  value={formData.selectedSiteId || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, selectedSiteId: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Seleccionar sitio...</option>
                  {sites.map((site) => (
                    <option key={site.site_id} value={site.site_id}>
                      {site.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Expiración (días)
              </label>
              <input
                type="number"
                min="1"
                max="365"
                value={formData.expires_days || ''}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  expires_days: e.target.value ? parseInt(e.target.value) : undefined
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Dejar vacío para sin expiración"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Notas (opcional)
              </label>
              <textarea
                value={formData.notes || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Descripción del propósito del token..."
              />
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Generando...' : 'Generar Token'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default TokenManagement;
