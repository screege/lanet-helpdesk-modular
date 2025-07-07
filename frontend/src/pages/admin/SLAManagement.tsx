import React, { useState, useEffect } from 'react';
import {
  Clock,
  Plus,
  Edit,
  Trash2,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Settings,
  BarChart3,
  Timer,
  X,
  Save,
  Copy
} from 'lucide-react';
import slaService, { SLAPolicy, SLABreach, SLAStats } from '../../services/slaService';
import clientsService from '../../services/clientsService';

const SLAManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'policies' | 'monitoring' | 'stats'>('policies');
  const [policies, setPolicies] = useState<SLAPolicy[]>([]);
  const [breaches, setBreaches] = useState<SLABreach[]>([]);
  const [stats, setStats] = useState<SLAStats | null>(null);
  const [clients, setClients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingPolicy, setEditingPolicy] = useState<SLAPolicy | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    priority: 'media' as 'critica' | 'alta' | 'media' | 'baja',
    response_time_hours: 8,
    resolution_time_hours: 48,
    business_hours_only: true,
    escalation_enabled: true,
    escalation_levels: 3,
    client_id: '',
    is_active: true
  });

  useEffect(() => {
    loadData();
    loadClients();
  }, [activeTab]);

  const loadClients = async () => {
    try {
      const clientsData = await clientsService.getClients();
      setClients(Array.isArray(clientsData) ? clientsData : []);
    } catch (error) {
      console.error('Error loading clients:', error);
      setClients([]);
    }
  };

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'policies') {
        const policiesData = await slaService.getSLAPolicies();
        setPolicies(policiesData);
      } else if (activeTab === 'monitoring') {
        const breachesData = await slaService.getSLABreaches();
        setBreaches(breachesData);
      } else if (activeTab === 'stats') {
        const statsData = await slaService.getSLAStats();
        setStats(statsData);
      }
    } catch (error) {
      console.error('Error loading SLA data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePolicy = async (policyId: string) => {
    if (window.confirm('¿Está seguro de que desea eliminar esta política SLA?')) {
      try {
        await slaService.deleteSLAPolicy(policyId);
        loadData();
      } catch (error) {
        console.error('Error deleting SLA policy:', error);
      }
    }
  };

  const handleSetDefault = async (policyId: string) => {
    try {
      await slaService.setDefaultSLAPolicy(policyId);
      loadData();
    } catch (error) {
      console.error('Error setting default policy:', error);
    }
  };

  const handleCreatePolicy = () => {
    setFormData({
      name: '',
      description: '',
      priority: 'media',
      response_time_hours: 8,
      resolution_time_hours: 48,
      business_hours_only: true,
      escalation_enabled: true,
      escalation_levels: 3,
      client_id: '',
      is_active: true
    });
    setEditingPolicy(null);
    setShowCreateForm(true);
  };

  const handleEditPolicy = (policy: SLAPolicy) => {
    setFormData({
      name: policy.name,
      description: policy.description || '',
      priority: policy.priority,
      response_time_hours: policy.response_time_hours,
      resolution_time_hours: policy.resolution_time_hours,
      business_hours_only: policy.business_hours_only,
      escalation_enabled: policy.escalation_enabled,
      escalation_levels: policy.escalation_levels || 3,
      client_id: policy.client_id || '',
      is_active: policy.is_active
    });
    setEditingPolicy(policy);
    setShowCreateForm(true);
  };

  const handleSavePolicy = async () => {
    try {
      if (editingPolicy) {
        await slaService.updateSLAPolicy(editingPolicy.policy_id, formData);
      } else {
        await slaService.createSLAPolicy(formData);
      }
      setShowCreateForm(false);
      setEditingPolicy(null);
      loadData();
    } catch (error) {
      console.error('Error saving policy:', error);
    }
  };

  const handleCancelForm = () => {
    setShowCreateForm(false);
    setEditingPolicy(null);
  };

  const handleCopyPolicy = (policy: SLAPolicy) => {
    setFormData({
      name: `Copia de ${policy.name}`,
      description: policy.description || '',
      priority: policy.priority,
      response_time_hours: policy.response_time_hours,
      resolution_time_hours: policy.resolution_time_hours,
      business_hours_only: policy.business_hours_only,
      escalation_enabled: policy.escalation_enabled,
      escalation_levels: policy.escalation_levels || 3,
      client_id: '', // No copiar el cliente específico
      is_active: true
    });
    setEditingPolicy(null);
    setShowCreateForm(true);
  };

  const renderPoliciesTab = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Políticas SLA</h2>
          <p className="text-gray-600">Gestiona los acuerdos de nivel de servicio</p>
        </div>
        <button
          onClick={handleCreatePolicy}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Nueva Política
        </button>
      </div>

      {/* Policies List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Política
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Prioridad
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Cliente
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tiempo Respuesta
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tiempo Resolución
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {policies.map((policy) => (
              <tr key={policy.policy_id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <Clock className="w-5 h-5 text-gray-400 mr-3" />
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {policy.name}
                        {policy.is_default && (
                          <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            Por defecto
                          </span>
                        )}
                      </div>
                      {policy.description && (
                        <div className="text-sm text-gray-500">{policy.description}</div>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${slaService.getPriorityColor(policy.priority)}`}>
                    {policy.priority.charAt(0).toUpperCase() + policy.priority.slice(1)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {policy.client_id ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {clients.find(c => c.client_id === policy.client_id)?.name || 'Cliente específico'}
                    </span>
                  ) : (
                    <span className="text-gray-500">Todos los clientes</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {slaService.formatSLATime(policy.response_time_hours)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {slaService.formatSLATime(policy.resolution_time_hours)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    policy.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {policy.is_active ? 'Activa' : 'Inactiva'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleCopyPolicy(policy)}
                      className="text-green-600 hover:text-green-900"
                      title="Copiar política"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                    {!policy.is_default && (
                      <button
                        onClick={() => handleSetDefault(policy.policy_id)}
                        className="text-blue-600 hover:text-blue-900"
                        title="Establecer como predeterminada"
                      >
                        <Settings className="w-4 h-4" />
                      </button>
                    )}
                    <button
                      onClick={() => handleEditPolicy(policy)}
                      className="text-indigo-600 hover:text-indigo-900"
                      title="Editar"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeletePolicy(policy.policy_id)}
                      className="text-red-600 hover:text-red-900"
                      title="Eliminar"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderMonitoringTab = () => (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Monitoreo SLA</h2>
        <p className="text-gray-600">Violaciones y alertas de SLA en tiempo real</p>
      </div>

      {/* Breaches List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            Violaciones de SLA ({breaches.length})
          </h3>
        </div>
        
        {breaches.length === 0 ? (
          <div className="px-6 py-8 text-center">
            <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">¡Sin violaciones de SLA!</h3>
            <p className="text-gray-600">Todos los tickets están dentro de los tiempos de SLA establecidos.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {breaches.map((breach, index) => (
              <div key={index} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <XCircle className="w-6 h-6 text-red-500" />
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        Ticket {breach.ticket_number}
                      </div>
                      <div className="text-sm text-gray-500">
                        {breach.client_name} • {breach.breach_type === 'response' ? 'Tiempo de respuesta' : 'Tiempo de resolución'}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-red-600">
                      Vencido hace {breach.time_elapsed}
                    </div>
                    <div className="text-sm text-gray-500">
                      Vencimiento: {new Date(breach.deadline).toLocaleString()}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  const renderStatsTab = () => (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Estadísticas SLA</h2>
        <p className="text-gray-600">Métricas de rendimiento y cumplimiento</p>
      </div>

      {stats && (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Timer className="w-8 h-8 text-blue-500" />
                </div>
                <div className="ml-4">
                  <div className="text-sm font-medium text-gray-500">Total Tickets</div>
                  <div className="text-2xl font-bold text-gray-900">{stats.total_tickets}</div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CheckCircle className="w-8 h-8 text-green-500" />
                </div>
                <div className="ml-4">
                  <div className="text-sm font-medium text-gray-500">Dentro de SLA</div>
                  <div className="text-2xl font-bold text-gray-900">{stats.within_sla}</div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <XCircle className="w-8 h-8 text-red-500" />
                </div>
                <div className="ml-4">
                  <div className="text-sm font-medium text-gray-500">Violaciones SLA</div>
                  <div className="text-2xl font-bold text-gray-900">{stats.breached_sla}</div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BarChart3 className="w-8 h-8 text-purple-500" />
                </div>
                <div className="ml-4">
                  <div className="text-sm font-medium text-gray-500">Cumplimiento</div>
                  <div className="text-2xl font-bold text-gray-900">{stats.sla_compliance_rate}%</div>
                </div>
              </div>
            </div>
          </div>

          {/* Additional Stats */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Tiempos Promedio</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Tiempo de respuesta:</span>
                  <span className="text-sm font-medium text-gray-900">
                    {slaService.formatSLATime(stats.avg_response_time)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Tiempo de resolución:</span>
                  <span className="text-sm font-medium text-gray-900">
                    {slaService.formatSLATime(stats.avg_resolution_time)}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Violaciones por Prioridad</h3>
              <div className="space-y-3">
                {Object.entries(stats.breaches_by_priority).map(([priority, count]) => (
                  <div key={priority} className="flex justify-between">
                    <span className={`text-sm px-2 py-1 rounded ${slaService.getPriorityColor(priority)}`}>
                      {priority.charAt(0).toUpperCase() + priority.slice(1)}
                    </span>
                    <span className="text-sm font-medium text-gray-900">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'policies', name: 'Políticas', icon: Settings },
            { id: 'monitoring', name: 'Monitoreo', icon: AlertTriangle },
            { id: 'stats', name: 'Estadísticas', icon: BarChart3 },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center gap-2`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'policies' && renderPoliciesTab()}
      {activeTab === 'monitoring' && renderMonitoringTab()}
      {activeTab === 'stats' && renderStatsTab()}

      {/* SLA Policy Form Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                {editingPolicy ? 'Editar Política SLA' : 'Nueva Política SLA'}
              </h3>
              <button
                onClick={handleCancelForm}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <form className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nombre de la Política *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Ej: SLA Crítico"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Prioridad *
                  </label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value as any })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="critica">Crítica</option>
                    <option value="alta">Alta</option>
                    <option value="media">Media</option>
                    <option value="baja">Baja</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Descripción
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Descripción de la política SLA"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Cliente Específico
                </label>
                <select
                  value={formData.client_id}
                  onChange={(e) => setFormData({ ...formData, client_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Todos los clientes (Política general)</option>
                  {clients.map((client) => (
                    <option key={client.client_id} value={client.client_id}>
                      {client.name}
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-sm text-gray-500">
                  Si seleccionas un cliente específico, esta política solo se aplicará a ese cliente.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tiempo de Respuesta (horas) *
                  </label>
                  <input
                    type="number"
                    value={formData.response_time_hours}
                    onChange={(e) => setFormData({ ...formData, response_time_hours: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="0.5"
                    step="0.5"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tiempo de Resolución (horas) *
                  </label>
                  <input
                    type="number"
                    value={formData.resolution_time_hours}
                    onChange={(e) => setFormData({ ...formData, resolution_time_hours: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="1"
                    step="1"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="business_hours_only"
                    checked={formData.business_hours_only}
                    onChange={(e) => setFormData({ ...formData, business_hours_only: e.target.checked })}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="business_hours_only" className="ml-2 block text-sm text-gray-900">
                    Solo horas laborales
                  </label>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="escalation_enabled"
                    checked={formData.escalation_enabled}
                    onChange={(e) => setFormData({ ...formData, escalation_enabled: e.target.checked })}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="escalation_enabled" className="ml-2 block text-sm text-gray-900">
                    Escalación habilitada
                  </label>
                </div>
              </div>

              {formData.escalation_enabled && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Niveles de Escalación
                  </label>
                  <input
                    type="number"
                    value={formData.escalation_levels}
                    onChange={(e) => setFormData({ ...formData, escalation_levels: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="1"
                    max="5"
                  />
                </div>
              )}

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                  Política activa
                </label>
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={handleCancelForm}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="button"
                  onClick={handleSavePolicy}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 flex items-center gap-2"
                >
                  <Save className="w-4 h-4" />
                  {editingPolicy ? 'Actualizar' : 'Crear'} Política
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default SLAManagement;
