import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { emailService, EmailQueueItem, EmailProcessingLog } from '../../services/emailService';
import { 
  Mail, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  RefreshCw,
  Play,
  Pause,
  RotateCcw,
  Activity,
  TrendingUp,
  Filter,
  Search
} from 'lucide-react';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ErrorMessage from '../../components/common/ErrorMessage';

const EmailMonitoring: React.FC = () => {
  const { hasRole } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'queue' | 'logs' | 'stats'>('queue');
  
  // Queue state
  const [queueItems, setQueueItems] = useState<EmailQueueItem[]>([]);
  const [queueTotal, setQueueTotal] = useState(0);
  const [queuePage, setQueuePage] = useState(1);
  const [queueFilters, setQueueFilters] = useState({
    status: '',
    priority: ''
  });

  // Logs state
  const [logs, setLogs] = useState<EmailProcessingLog[]>([]);
  const [logsTotal, setLogsTotal] = useState(0);
  const [logsPage, setLogsPage] = useState(1);
  const [logsFilters, setLogsFilters] = useState({
    status: '',
    from_email: ''
  });

  // Statistics state
  const [statistics, setStatistics] = useState({
    total_sent: 0,
    total_failed: 0,
    total_pending: 0,
    total_processed_today: 0,
    success_rate: 0
  });

  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    if (hasRole(['superadmin', 'admin'])) {
      loadData();
    }
  }, [hasRole, activeTab, queuePage, logsPage, queueFilters, logsFilters]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      if (activeTab === 'queue') {
        await loadQueue();
      } else if (activeTab === 'logs') {
        await loadLogs();
      } else if (activeTab === 'stats') {
        await loadStatistics();
      }
    } catch (err: any) {
      setError(err.message || 'Error loading data');
    } finally {
      setLoading(false);
    }
  };

  const loadQueue = async () => {
    const response = await emailService.getEmailQueue({
      ...queueFilters,
      page: queuePage,
      per_page: 20
    });
    setQueueItems(response.items);
    setQueueTotal(response.total);
  };

  const loadLogs = async () => {
    const response = await emailService.getEmailProcessingLogs({
      ...logsFilters,
      page: logsPage,
      per_page: 20
    });
    setLogs(response.logs);
    setLogsTotal(response.total);
  };

  const loadStatistics = async () => {
    const stats = await emailService.getEmailStatistics();
    setStatistics(stats);
  };

  const handleProcessQueue = async () => {
    try {
      setProcessing(true);
      const result = await emailService.processEmailQueue();
      alert(`Procesados: ${result.processed} emails. ${result.message}`);
      await loadQueue();
    } catch (err: any) {
      setError(err.message || 'Error processing email queue');
    } finally {
      setProcessing(false);
    }
  };

  const handleRetryEmail = async (queueId: string) => {
    try {
      await emailService.retryEmailQueue(queueId);
      await loadQueue();
    } catch (err: any) {
      setError(err.message || 'Error retrying email');
    }
  };

  const handleCancelEmail = async (queueId: string) => {
    if (window.confirm('¿Está seguro de que desea cancelar este email?')) {
      try {
        await emailService.cancelEmailQueue(queueId);
        await loadQueue();
      } catch (err: any) {
        setError(err.message || 'Error canceling email');
      }
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'sent':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'sending':
        return <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />;
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-gray-500" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const baseClasses = "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium";
    switch (status) {
      case 'sent':
      case 'processed':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'failed':
        return `${baseClasses} bg-red-100 text-red-800`;
      case 'pending':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case 'sending':
        return `${baseClasses} bg-blue-100 text-blue-800`;
      case 'cancelled':
      case 'ignored':
        return `${baseClasses} bg-gray-100 text-gray-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  if (!hasRole(['superadmin', 'admin'])) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertTriangle className="mx-auto h-12 w-12 text-red-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Acceso Denegado</h3>
          <p className="mt-1 text-sm text-gray-500">
            No tiene permisos para acceder al monitoreo de email.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Monitoreo de Email</h1>
          <p className="mt-1 text-sm text-gray-500">
            Supervise el estado de la cola de emails y logs de procesamiento
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => loadData()}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Actualizar
          </button>
          {activeTab === 'queue' && (
            <button
              onClick={handleProcessQueue}
              disabled={processing}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {processing ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Play className="h-4 w-4 mr-2" />
              )}
              Procesar Cola
            </button>
          )}
        </div>
      </div>

      {error && <ErrorMessage message={error} />}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'queue', label: 'Cola de Emails', icon: Mail },
            { id: 'logs', label: 'Logs de Procesamiento', icon: Activity },
            { id: 'stats', label: 'Estadísticas', icon: TrendingUp }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="h-4 w-4 mr-2" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="bg-white shadow rounded-lg">
          {activeTab === 'queue' && (
            <div className="p-6">
              {/* Queue Filters */}
              <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Estado</label>
                  <select
                    value={queueFilters.status}
                    onChange={(e) => setQueueFilters({...queueFilters, status: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Todos</option>
                    <option value="pending">Pendiente</option>
                    <option value="sending">Enviando</option>
                    <option value="sent">Enviado</option>
                    <option value="failed">Fallido</option>
                    <option value="cancelled">Cancelado</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Prioridad</label>
                  <select
                    value={queueFilters.priority}
                    onChange={(e) => setQueueFilters({...queueFilters, priority: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Todas</option>
                    <option value="1">Alta (1)</option>
                    <option value="2">Media (2)</option>
                    <option value="3">Baja (3)</option>
                  </select>
                </div>
              </div>

              {/* Queue Items */}
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Estado
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Destinatario
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Asunto
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Prioridad
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Intentos
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Creado
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Acciones
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {queueItems.map((item) => (
                      <tr key={item.queue_id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            {getStatusIcon(item.status)}
                            <span className={`ml-2 ${getStatusBadge(item.status)}`}>
                              {item.status}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {item.to_email}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                          {item.subject}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {item.priority}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {item.attempts}/{item.max_attempts}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(item.created_at).toLocaleDateString('es-MX')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            {(item.status === 'failed' || item.status === 'cancelled') && (
                              <button
                                onClick={() => handleRetryEmail(item.queue_id)}
                                className="text-blue-600 hover:text-blue-900"
                                title="Reintentar"
                              >
                                <RotateCcw className="h-4 w-4" />
                              </button>
                            )}
                            {(item.status === 'pending' || item.status === 'failed') && (
                              <button
                                onClick={() => handleCancelEmail(item.queue_id)}
                                className="text-red-600 hover:text-red-900"
                                title="Cancelar"
                              >
                                <Pause className="h-4 w-4" />
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {queueTotal > 20 && (
                <div className="mt-6 flex justify-between items-center">
                  <div className="text-sm text-gray-700">
                    Mostrando {((queuePage - 1) * 20) + 1} a {Math.min(queuePage * 20, queueTotal)} de {queueTotal} emails
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setQueuePage(Math.max(1, queuePage - 1))}
                      disabled={queuePage === 1}
                      className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50"
                    >
                      Anterior
                    </button>
                    <button
                      onClick={() => setQueuePage(queuePage + 1)}
                      disabled={queuePage * 20 >= queueTotal}
                      className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50"
                    >
                      Siguiente
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'logs' && (
            <div className="p-6">
              {/* Logs Filters */}
              <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Estado</label>
                  <select
                    value={logsFilters.status}
                    onChange={(e) => setLogsFilters({...logsFilters, status: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Todos</option>
                    <option value="pending">Pendiente</option>
                    <option value="processed">Procesado</option>
                    <option value="failed">Fallido</option>
                    <option value="ignored">Ignorado</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Email Remitente</label>
                  <input
                    type="email"
                    value={logsFilters.from_email}
                    onChange={(e) => setLogsFilters({...logsFilters, from_email: e.target.value})}
                    placeholder="Filtrar por remitente..."
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Processing Logs */}
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Estado
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Remitente
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Asunto
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Acción
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Ticket ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Procesado
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {logs.map((log) => (
                      <tr key={log.log_id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            {getStatusIcon(log.processing_status)}
                            <span className={`ml-2 ${getStatusBadge(log.processing_status)}`}>
                              {log.processing_status}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {log.from_email}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                          {log.subject}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {log.action_taken || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {log.ticket_id ? (
                            <span className="text-blue-600 font-medium">{log.ticket_id}</span>
                          ) : (
                            '-'
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {log.processed_at ?
                            new Date(log.processed_at).toLocaleDateString('es-MX') :
                            'Pendiente'
                          }
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Logs Pagination */}
              {logsTotal > 20 && (
                <div className="mt-6 flex justify-between items-center">
                  <div className="text-sm text-gray-700">
                    Mostrando {((logsPage - 1) * 20) + 1} a {Math.min(logsPage * 20, logsTotal)} de {logsTotal} logs
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setLogsPage(Math.max(1, logsPage - 1))}
                      disabled={logsPage === 1}
                      className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50"
                    >
                      Anterior
                    </button>
                    <button
                      onClick={() => setLogsPage(logsPage + 1)}
                      disabled={logsPage * 20 >= logsTotal}
                      className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50"
                    >
                      Siguiente
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'stats' && (
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
                <div className="bg-blue-50 p-6 rounded-lg">
                  <div className="flex items-center">
                    <Mail className="h-8 w-8 text-blue-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-blue-600">Total Enviados</p>
                      <p className="text-2xl font-bold text-blue-900">{statistics.total_sent}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-red-50 p-6 rounded-lg">
                  <div className="flex items-center">
                    <XCircle className="h-8 w-8 text-red-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-red-600">Total Fallidos</p>
                      <p className="text-2xl font-bold text-red-900">{statistics.total_failed}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-yellow-50 p-6 rounded-lg">
                  <div className="flex items-center">
                    <Clock className="h-8 w-8 text-yellow-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-yellow-600">Pendientes</p>
                      <p className="text-2xl font-bold text-yellow-900">{statistics.total_pending}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-green-50 p-6 rounded-lg">
                  <div className="flex items-center">
                    <Activity className="h-8 w-8 text-green-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-green-600">Hoy</p>
                      <p className="text-2xl font-bold text-green-900">{statistics.total_processed_today}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-purple-50 p-6 rounded-lg">
                  <div className="flex items-center">
                    <TrendingUp className="h-8 w-8 text-purple-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-purple-600">Tasa de Éxito</p>
                      <p className="text-2xl font-bold text-purple-900">{statistics.success_rate.toFixed(1)}%</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Additional Statistics */}
              <div className="mt-8 bg-gray-50 p-6 rounded-lg">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Resumen del Sistema</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Estado de la Cola</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Emails en cola:</span>
                        <span className="text-sm font-medium">{statistics.total_pending}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Procesados hoy:</span>
                        <span className="text-sm font-medium">{statistics.total_processed_today}</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Rendimiento</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Tasa de éxito:</span>
                        <span className="text-sm font-medium">{statistics.success_rate.toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Total procesados:</span>
                        <span className="text-sm font-medium">{statistics.total_sent + statistics.total_failed}</span>
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
  );
};

export default EmailMonitoring;
