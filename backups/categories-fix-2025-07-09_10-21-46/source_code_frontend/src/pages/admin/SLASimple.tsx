import React, { useState, useEffect } from 'react';
import {
  Clock,
  Plus,
  Edit,
  Trash2,
  Copy,
  Save,
  X,
  Calendar,
  Timer,
  Settings
} from 'lucide-react';
import slaService, { SLAPolicy } from '../../services/slaService';
import clientsService from '../../services/clientsService';

interface WorkingHours {
  monday: { enabled: boolean; start: string; end: string };
  tuesday: { enabled: boolean; start: string; end: string };
  wednesday: { enabled: boolean; start: string; end: string };
  thursday: { enabled: boolean; start: string; end: string };
  friday: { enabled: boolean; start: string; end: string };
  saturday: { enabled: boolean; start: string; end: string };
  sunday: { enabled: boolean; start: string; end: string };
}

const SLASimple: React.FC = () => {
  const [policies, setPolicies] = useState<SLAPolicy[]>([]);
  const [clients, setClients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingPolicy, setEditingPolicy] = useState<SLAPolicy | null>(null);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    priority: 'media' as 'critica' | 'alta' | 'media' | 'baja',
    client_id: '',
    min_response_hours: 1,
    max_response_hours: 8,
    min_resolution_hours: 4,
    max_resolution_hours: 48,
    working_hours: {
      monday: { enabled: true, start: '08:00', end: '17:00' },
      tuesday: { enabled: true, start: '08:00', end: '17:00' },
      wednesday: { enabled: true, start: '08:00', end: '17:00' },
      thursday: { enabled: true, start: '08:00', end: '17:00' },
      friday: { enabled: true, start: '08:00', end: '17:00' },
      saturday: { enabled: false, start: '08:00', end: '17:00' },
      sunday: { enabled: false, start: '08:00', end: '17:00' }
    } as WorkingHours,
    is_active: true
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [policiesData, clientsData] = await Promise.all([
        slaService.getSLAPolicies(),
        clientsService.getAllClients()
      ]);
      setPolicies(policiesData);
      setClients(Array.isArray(clientsData) ? clientsData : []);
      console.log('Clients loaded:', clientsData); // Debug
    } catch (error) {
      console.error('Error loading data:', error);
      setClients([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePolicy = () => {
    setFormData({
      name: '',
      description: '',
      priority: 'media',
      client_id: '',
      min_response_hours: 1,
      max_response_hours: 8,
      min_resolution_hours: 4,
      max_resolution_hours: 48,
      working_hours: {
        monday: { enabled: true, start: '08:00', end: '17:00' },
        tuesday: { enabled: true, start: '08:00', end: '17:00' },
        wednesday: { enabled: true, start: '08:00', end: '17:00' },
        thursday: { enabled: true, start: '08:00', end: '17:00' },
        friday: { enabled: true, start: '08:00', end: '17:00' },
        saturday: { enabled: false, start: '08:00', end: '17:00' },
        sunday: { enabled: false, start: '08:00', end: '17:00' }
      },
      is_active: true
    });
    setEditingPolicy(null);
    setShowForm(true);
  };

  const handleEditPolicy = (policy: SLAPolicy) => {
    setFormData({
      name: policy.name,
      description: policy.description || '',
      priority: policy.priority,
      client_id: policy.client_id || '',
      min_response_hours: 1,
      max_response_hours: policy.response_time_hours,
      min_resolution_hours: policy.response_time_hours,
      max_resolution_hours: policy.resolution_time_hours,
      working_hours: {
        monday: { enabled: true, start: '08:00', end: '17:00' },
        tuesday: { enabled: true, start: '08:00', end: '17:00' },
        wednesday: { enabled: true, start: '08:00', end: '17:00' },
        thursday: { enabled: true, start: '08:00', end: '17:00' },
        friday: { enabled: true, start: '08:00', end: '17:00' },
        saturday: { enabled: false, start: '08:00', end: '17:00' },
        sunday: { enabled: false, start: '08:00', end: '17:00' }
      },
      is_active: policy.is_active
    });
    setEditingPolicy(policy);
    setShowForm(true);
  };

  const handleCopyPolicy = (policy: SLAPolicy) => {
    setFormData({
      name: `Copia de ${policy.name}`,
      description: policy.description || '',
      priority: policy.priority,
      client_id: '',
      min_response_hours: 1,
      max_response_hours: policy.response_time_hours,
      min_resolution_hours: policy.response_time_hours,
      max_resolution_hours: policy.resolution_time_hours,
      working_hours: {
        monday: { enabled: true, start: '08:00', end: '17:00' },
        tuesday: { enabled: true, start: '08:00', end: '17:00' },
        wednesday: { enabled: true, start: '08:00', end: '17:00' },
        thursday: { enabled: true, start: '08:00', end: '17:00' },
        friday: { enabled: true, start: '08:00', end: '17:00' },
        saturday: { enabled: false, start: '08:00', end: '17:00' },
        sunday: { enabled: false, start: '08:00', end: '17:00' }
      },
      is_active: true
    });
    setEditingPolicy(null);
    setShowForm(true);
  };

  const handleSavePolicy = async () => {
    try {
      // Validate required fields
      if (!formData.name.trim()) {
        alert('El nombre de la política es requerido');
        return;
      }

      const policyData = {
        name: formData.name.trim(),
        description: formData.description?.trim() || '',
        priority: formData.priority,
        client_id: formData.client_id || null,
        response_time_hours: formData.max_response_hours,
        resolution_time_hours: formData.max_resolution_hours,
        business_hours_only: true,
        escalation_enabled: false,
        is_active: formData.is_active
      };

      console.log('Saving policy data:', policyData);

      if (editingPolicy) {
        console.log('Updating policy:', editingPolicy.policy_id);
        await slaService.updateSLAPolicy(editingPolicy.policy_id, policyData);
      } else {
        console.log('Creating new policy');
        await slaService.createSLAPolicy(policyData);
      }

      setShowForm(false);
      setEditingPolicy(null);
      loadData();
      alert('Política SLA guardada exitosamente');
    } catch (error) {
      console.error('Error saving policy:', error);
      alert('Error al guardar la política SLA. Revisa la consola para más detalles.');
    }
  };

  const handleDeletePolicy = async (policyId: string) => {
    if (window.confirm('¿Está seguro de que desea eliminar esta política SLA?')) {
      try {
        await slaService.deleteSLAPolicy(policyId);
        loadData();
      } catch (error) {
        console.error('Error deleting policy:', error);
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

  const updateWorkingHours = (day: keyof WorkingHours, field: 'enabled' | 'start' | 'end', value: boolean | string) => {
    setFormData(prev => ({
      ...prev,
      working_hours: {
        ...prev.working_hours,
        [day]: {
          ...prev.working_hours[day],
          [field]: value
        }
      }
    }));
  };

  const formatWorkingDays = (workingHours: WorkingHours) => {
    const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
    const dayNames = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
    
    const enabledDays = days
      .map((day, index) => workingHours[day as keyof WorkingHours]?.enabled ? dayNames[index] : null)
      .filter(Boolean);
    
    return enabledDays.join(', ');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Configuración SLA</h1>
          <p className="text-gray-600">Gestiona horarios operativos y tiempos de respuesta</p>
        </div>
        <button
          onClick={handleCreatePolicy}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Nueva Política SLA
        </button>
      </div>

      {/* Policies Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Política
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Cliente
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Prioridad
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
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {policy.client_id ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {clients.find(c => c.client_id === policy.client_id)?.name || 'Cliente específico'}
                    </span>
                  ) : (
                    <span className="text-gray-500">Todos los clientes</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${slaService.getPriorityColor(policy.priority)}`}>
                    {policy.priority.charAt(0).toUpperCase() + policy.priority.slice(1)}
                  </span>
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

      {/* Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-2/3 shadow-lg rounded-md bg-white max-h-screen overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                {editingPolicy ? 'Editar Política SLA' : 'Nueva Política SLA'}
              </h3>
              <button
                onClick={() => setShowForm(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <form className="space-y-6">
              {/* Basic Info */}
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
                    placeholder="Ej: SLA Horario Comercial"
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
                  Cliente Específico
                </label>
                <select
                  value={formData.client_id}
                  onChange={(e) => setFormData({ ...formData, client_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Todos los clientes</option>
                  {clients.map((client) => (
                    <option key={client.client_id} value={client.client_id}>
                      {client.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Response Times */}
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-3 flex items-center gap-2">
                  <Timer className="w-5 h-5" />
                  Tiempos de Respuesta y Resolución
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Respuesta Mínima (horas)
                    </label>
                    <input
                      type="number"
                      value={formData.min_response_hours}
                      onChange={(e) => setFormData({ ...formData, min_response_hours: Number(e.target.value) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      min="0.5"
                      step="0.5"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Respuesta Máxima (horas)
                    </label>
                    <input
                      type="number"
                      value={formData.max_response_hours}
                      onChange={(e) => setFormData({ ...formData, max_response_hours: Number(e.target.value) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      min="1"
                      step="1"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Resolución Mínima (horas)
                    </label>
                    <input
                      type="number"
                      value={formData.min_resolution_hours}
                      onChange={(e) => setFormData({ ...formData, min_resolution_hours: Number(e.target.value) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      min="1"
                      step="1"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Resolución Máxima (horas)
                    </label>
                    <input
                      type="number"
                      value={formData.max_resolution_hours}
                      onChange={(e) => setFormData({ ...formData, max_resolution_hours: Number(e.target.value) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      min="1"
                      step="1"
                    />
                  </div>
                </div>
              </div>

              {/* Working Hours */}
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-3 flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  Horarios Operativos
                </h4>
                <div className="space-y-3">
                  {Object.entries(formData.working_hours).map(([day, hours]) => {
                    const dayNames: { [key: string]: string } = {
                      monday: 'Lunes',
                      tuesday: 'Martes', 
                      wednesday: 'Miércoles',
                      thursday: 'Jueves',
                      friday: 'Viernes',
                      saturday: 'Sábado',
                      sunday: 'Domingo'
                    };

                    return (
                      <div key={day} className="flex items-center space-x-4">
                        <div className="w-20">
                          <input
                            type="checkbox"
                            checked={hours.enabled}
                            onChange={(e) => updateWorkingHours(day as keyof WorkingHours, 'enabled', e.target.checked)}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                          <label className="ml-2 text-sm text-gray-900">
                            {dayNames[day]}
                          </label>
                        </div>
                        {hours.enabled && (
                          <>
                            <div>
                              <input
                                type="time"
                                value={hours.start}
                                onChange={(e) => updateWorkingHours(day as keyof WorkingHours, 'start', e.target.value)}
                                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                              />
                            </div>
                            <span className="text-gray-500">a</span>
                            <div>
                              <input
                                type="time"
                                value={hours.end}
                                onChange={(e) => updateWorkingHours(day as keyof WorkingHours, 'end', e.target.value)}
                                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                              />
                            </div>
                          </>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

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
                  onClick={() => setShowForm(false)}
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

export default SLASimple;
