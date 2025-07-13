import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import { ApiResponse } from '@/types';
import {
  ArrowLeft,
  Save,
  Calendar,
  FileText,
  Settings,
  Mail,
  Clock
} from 'lucide-react';

interface ReportTemplate {
  template_id: string;
  name: string;
  description: string;
  report_type: string;
  is_system: boolean;
}

interface Client {
  client_id: string;
  name: string;
}

interface ReportConfigurationFormProps {
  onBack: () => void;
  onSave: () => void;
  configId?: string;
}

const ReportConfigurationForm: React.FC<ReportConfigurationFormProps> = ({
  onBack,
  onSave,
  configId
}) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [templates, setTemplates] = useState<ReportTemplate[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    template_id: '',
    client_id: '',
    output_formats: ['pdf'],
    report_filters: {
      report_period: 'monthly',
      include_charts: true,
      include_details: true
    },
    schedule_enabled: false,
    schedule_config: {
      type: 'monthly',
      day: 1,
      hour: 9,
      recipients: []
    }
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    loadTemplates();
    if (user?.role === 'superadmin' || user?.role === 'admin' || user?.role === 'technician') {
      loadClients();
    }
    if (configId) {
      loadConfiguration(configId);
    }
  }, [configId]);

  const loadTemplates = async () => {
    try {
      const response = await apiService.get('/reports/templates') as ApiResponse<ReportTemplate[]>;
      if (response.success) {
        setTemplates(response.data);
      }
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const loadClients = async () => {
    try {
      const response = await apiService.get('/clients') as ApiResponse<Client[]>;
      if (response.success) {
        setClients(response.data);
      }
    } catch (error) {
      console.error('Error loading clients:', error);
    }
  };

  const loadConfiguration = async (id: string) => {
    try {
      const response = await apiService.get(`/reports/configurations/${id}`);
      if (response.success) {
        setFormData(response.data);
      }
    } catch (error) {
      console.error('Error loading configuration:', error);
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'El nombre es requerido';
    }

    if (!formData.template_id) {
      newErrors.template_id = 'Debe seleccionar una plantilla';
    }

    if (formData.output_formats.length === 0) {
      newErrors.output_formats = 'Debe seleccionar al menos un formato de salida';
    }

    if (formData.schedule_enabled && formData.schedule_config.recipients.length === 0) {
      newErrors.recipients = 'Debe agregar al menos un destinatario para reportes programados';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      const endpoint = configId ? `/reports/configurations/${configId}` : '/reports/configurations';
      const method = configId ? 'PUT' : 'POST';
      
      const response = await apiService[method.toLowerCase() as 'post' | 'put'](endpoint, formData);
      
      if (response.success) {
        alert('Configuración guardada exitosamente');
        onSave();
      } else {
        alert('Error al guardar la configuración');
      }
    } catch (error) {
      console.error('Error saving configuration:', error);
      alert('Error al guardar la configuración');
    } finally {
      setLoading(false);
    }
  };

  const handleFormatChange = (format: string, checked: boolean) => {
    if (checked) {
      setFormData(prev => ({
        ...prev,
        output_formats: [...prev.output_formats, format]
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        output_formats: prev.output_formats.filter(f => f !== format)
      }));
    }
  };

  const addRecipient = () => {
    const email = prompt('Ingrese el email del destinatario:');
    if (email && email.includes('@')) {
      setFormData(prev => ({
        ...prev,
        schedule_config: {
          ...prev.schedule_config,
          recipients: [...prev.schedule_config.recipients, email]
        }
      }));
    }
  };

  const removeRecipient = (index: number) => {
    setFormData(prev => ({
      ...prev,
      schedule_config: {
        ...prev.schedule_config,
        recipients: prev.schedule_config.recipients.filter((_, i) => i !== index)
      }
    }));
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={onBack}
          className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Volver a Reportes
        </button>
        <h1 className="text-2xl font-bold text-gray-900">
          {configId ? 'Editar Configuración de Reporte' : 'Nueva Configuración de Reporte'}
        </h1>
        <p className="text-sm text-gray-500">
          Configure los parámetros para generar reportes automáticos o bajo demanda
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Basic Information */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center mb-4">
            <FileText className="h-5 w-5 text-blue-500 mr-2" />
            <h2 className="text-lg font-medium text-gray-900">Información Básica</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nombre del Reporte *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                className={`w-full px-3 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500 ${
                  errors.name ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Ej: Reporte Mensual de Tickets"
              />
              {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Plantilla *
              </label>
              <select
                value={formData.template_id}
                onChange={(e) => setFormData(prev => ({ ...prev, template_id: e.target.value }))}
                className={`w-full px-3 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500 ${
                  errors.template_id ? 'border-red-300' : 'border-gray-300'
                }`}
              >
                <option value="">Seleccionar plantilla...</option>
                {templates.map(template => (
                  <option key={template.template_id} value={template.template_id}>
                    {template.name}
                  </option>
                ))}
              </select>
              {errors.template_id && <p className="text-red-500 text-sm mt-1">{errors.template_id}</p>}
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descripción
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                placeholder="Descripción opcional del reporte..."
              />
            </div>

            {(user?.role === 'superadmin' || user?.role === 'admin' || user?.role === 'technician') && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cliente (Opcional)
                </label>
                <select
                  value={formData.client_id}
                  onChange={(e) => setFormData(prev => ({ ...prev, client_id: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Todos los clientes</option>
                  {clients.map(client => (
                    <option key={client.client_id} value={client.client_id}>
                      {client.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        </div>

        {/* Output Formats */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Settings className="h-5 w-5 text-blue-500 mr-2" />
            <h2 className="text-lg font-medium text-gray-900">Formatos de Salida</h2>
          </div>
          
          <div className="space-y-3">
            {[
              { value: 'pdf', label: 'PDF', description: 'Formato ideal para impresión y visualización' },
              { value: 'excel', label: 'Excel', description: 'Formato ideal para análisis de datos' },
              { value: 'csv', label: 'CSV', description: 'Formato ideal para importar a otras herramientas' }
            ].map(format => (
              <label key={format.value} className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.output_formats.includes(format.value)}
                  onChange={(e) => handleFormatChange(format.value, e.target.checked)}
                  className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <div>
                  <div className="text-sm font-medium text-gray-900">{format.label}</div>
                  <div className="text-sm text-gray-500">{format.description}</div>
                </div>
              </label>
            ))}
            {errors.output_formats && <p className="text-red-500 text-sm">{errors.output_formats}</p>}
          </div>
        </div>

        {/* Report Filters */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Calendar className="h-5 w-5 text-blue-500 mr-2" />
            <h2 className="text-lg font-medium text-gray-900">Configuración del Reporte</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Período del Reporte
              </label>
              <select
                value={formData.report_filters.report_period}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  report_filters: { ...prev.report_filters, report_period: e.target.value }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="monthly">Mensual (mes anterior)</option>
                <option value="weekly">Semanal (última semana)</option>
                <option value="daily">Diario (último día)</option>
                <option value="custom">Personalizado</option>
              </select>
            </div>

            <div className="space-y-3">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.report_filters.include_charts}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    report_filters: { ...prev.report_filters, include_charts: e.target.checked }
                  }))}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-900">Incluir gráficos y visualizaciones</span>
              </label>

              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.report_filters.include_details}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    report_filters: { ...prev.report_filters, include_details: e.target.checked }
                  }))}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-900">Incluir detalles y métricas avanzadas</span>
              </label>
            </div>
          </div>
        </div>

        {/* Scheduling */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Clock className="h-5 w-5 text-blue-500 mr-2" />
            <h2 className="text-lg font-medium text-gray-900">Programación Automática</h2>
          </div>

          <div className="space-y-4">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.schedule_enabled}
                onChange={(e) => setFormData(prev => ({ ...prev, schedule_enabled: e.target.checked }))}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="text-sm font-medium text-gray-900">Habilitar generación automática</span>
            </label>

            {formData.schedule_enabled && (
              <div className="ml-6 space-y-4 border-l-2 border-blue-200 pl-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Frecuencia
                    </label>
                    <select
                      value={formData.schedule_config.type}
                      onChange={(e) => setFormData(prev => ({
                        ...prev,
                        schedule_config: { ...prev.schedule_config, type: e.target.value }
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="monthly">Mensual</option>
                      <option value="weekly">Semanal</option>
                      <option value="daily">Diario</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {formData.schedule_config.type === 'monthly' ? 'Día del mes' : 'Día'}
                    </label>
                    <input
                      type="number"
                      min="1"
                      max={formData.schedule_config.type === 'monthly' ? "28" : "7"}
                      value={formData.schedule_config.day}
                      onChange={(e) => setFormData(prev => ({
                        ...prev,
                        schedule_config: { ...prev.schedule_config, day: parseInt(e.target.value) }
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Hora (24h)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="23"
                      value={formData.schedule_config.hour}
                      onChange={(e) => setFormData(prev => ({
                        ...prev,
                        schedule_config: { ...prev.schedule_config, hour: parseInt(e.target.value) }
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-sm font-medium text-gray-700">
                      Destinatarios de Email
                    </label>
                    <button
                      type="button"
                      onClick={addRecipient}
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      + Agregar destinatario
                    </button>
                  </div>

                  <div className="space-y-2">
                    {formData.schedule_config.recipients.map((email, index) => (
                      <div key={index} className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded">
                        <span className="text-sm text-gray-900">{email}</span>
                        <button
                          type="button"
                          onClick={() => removeRecipient(index)}
                          className="text-red-600 hover:text-red-800 text-sm"
                        >
                          Eliminar
                        </button>
                      </div>
                    ))}
                    {formData.schedule_config.recipients.length === 0 && (
                      <p className="text-sm text-gray-500 italic">No hay destinatarios configurados</p>
                    )}
                  </div>
                  {errors.recipients && <p className="text-red-500 text-sm mt-1">{errors.recipients}</p>}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={onBack}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            <Save className="h-4 w-4 mr-2" />
            {loading ? 'Guardando...' : 'Guardar Configuración'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ReportConfigurationForm;
