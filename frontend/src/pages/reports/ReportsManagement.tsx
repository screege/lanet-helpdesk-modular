import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import { ApiResponse } from '@/types';
import ReportConfigurationForm from './ReportConfigurationForm';
import {
  FileText,
  Calendar,
  Download,
  Plus,
  Settings,
  Clock,
  Users,
  BarChart3,
  Filter,
  Search,
  Eye,
  Edit,
  Trash2,
  Play,
  CheckCircle,
  XCircle,
  AlertCircle,
  Loader
} from 'lucide-react';

interface ReportTemplate {
  template_id: string;
  name: string;
  description: string;
  report_type: string;
  is_system: boolean;
  created_at: string;
}

interface ReportConfiguration {
  config_id: string;
  name: string;
  description: string;
  template_name: string;
  report_type: string;
  client_name?: string;
  output_formats: string[];
  is_active: boolean;
  created_at: string;
}

interface ReportExecution {
  execution_id: string;
  config_name: string;
  execution_type: string;
  status: string;
  output_format: string;
  file_size?: number;
  generation_time_ms?: number;
  started_at: string;
  completed_at?: string;
  first_name?: string;
  last_name?: string;
}

const ReportsManagement: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'templates' | 'configurations' | 'executions' | 'schedules'>('configurations');
  const [currentView, setCurrentView] = useState<'list' | 'form'>('list');
  const [editingConfigId, setEditingConfigId] = useState<string | undefined>();
  const [templates, setTemplates] = useState<ReportTemplate[]>([]);
  const [configurations, setConfigurations] = useState<ReportConfiguration[]>([]);
  const [executions, setExecutions] = useState<ReportExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [generatingReports, setGeneratingReports] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      switch (activeTab) {
        case 'templates':
          await loadTemplates();
          break;
        case 'configurations':
          await loadConfigurations();
          break;
        case 'executions':
          await loadExecutions();
          break;
        case 'schedules':
          // TODO: Load schedules
          break;
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

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

  const loadConfigurations = async () => {
    try {
      const response = await apiService.get('/reports/configurations') as ApiResponse<ReportConfiguration[]>;
      if (response.success) {
        setConfigurations(response.data);
      }
    } catch (error) {
      console.error('Error loading configurations:', error);
    }
  };

  const loadExecutions = async () => {
    try {
      const response = await apiService.get('/reports/executions') as ApiResponse<ReportExecution[]>;
      if (response.success) {
        setExecutions(response.data);
      }
    } catch (error) {
      console.error('Error loading executions:', error);
    }
  };

  const generateReport = async (configId: string, format: string) => {
    const reportKey = `${configId}-${format}`;
    setGeneratingReports(prev => new Set(prev).add(reportKey));

    try {
      const response = await apiService.post('/reports/generate', {
        config_id: configId,
        output_format: format
      });

      if (response.success) {
        // Show success message with Spanish text
        const formatNames = {
          pdf: 'PDF',
          excel: 'Excel',
          csv: 'CSV'
        };

        alert(`Reporte ${formatNames[format as keyof typeof formatNames]} generado exitosamente. Revise la sección de "Ejecuciones" para descargarlo.`);

        // Refresh executions if we're on that tab
        if (activeTab === 'executions') {
          setTimeout(() => loadExecutions(), 1000); // Small delay to allow backend processing
        }
      } else {
        alert('Error al generar el reporte: ' + (response.error || 'Error desconocido'));
      }
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Error al generar el reporte. Por favor, intente nuevamente.');
    } finally {
      setGeneratingReports(prev => {
        const newSet = new Set(prev);
        newSet.delete(reportKey);
        return newSet;
      });
    }
  };

  const downloadReport = async (executionId: string) => {
    try {
      const response = await fetch(`/api/reports/executions/${executionId}/download`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        // Get filename from Content-Disposition header if available
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = `reporte_${executionId}`;

        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
          if (filenameMatch && filenameMatch[1]) {
            filename = filenameMatch[1].replace(/['"]/g, '');
          }
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        // Show success message
        alert('Reporte descargado exitosamente');
      } else {
        const errorText = await response.text();
        alert('Error al descargar el reporte: ' + (errorText || 'Error del servidor'));
      }
    } catch (error) {
      console.error('Error downloading report:', error);
      alert('Error al descargar el reporte. Verifique su conexión a internet.');
    }
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'N/A';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDuration = (ms?: number) => {
    if (!ms) return 'N/A';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: {
        color: 'bg-yellow-100 text-yellow-800',
        text: 'Pendiente',
        icon: <Clock className="h-3 w-3 mr-1" />
      },
      running: {
        color: 'bg-blue-100 text-blue-800',
        text: 'Ejecutando',
        icon: <Loader className="h-3 w-3 mr-1 animate-spin" />
      },
      completed: {
        color: 'bg-green-100 text-green-800',
        text: 'Completado',
        icon: <CheckCircle className="h-3 w-3 mr-1" />
      },
      failed: {
        color: 'bg-red-100 text-red-800',
        text: 'Fallido',
        icon: <XCircle className="h-3 w-3 mr-1" />
      }
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        {config.icon}
        {config.text}
      </span>
    );
  };

  const filteredData = () => {
    const term = searchTerm.toLowerCase();
    switch (activeTab) {
      case 'templates':
        return templates.filter(t => 
          t.name.toLowerCase().includes(term) || 
          t.description?.toLowerCase().includes(term)
        );
      case 'configurations':
        return configurations.filter(c => 
          c.name.toLowerCase().includes(term) || 
          c.template_name.toLowerCase().includes(term)
        );
      case 'executions':
        return executions.filter(e => 
          e.config_name.toLowerCase().includes(term) || 
          e.status.toLowerCase().includes(term)
        );
      default:
        return [];
    }
  };

  const handleNewConfiguration = () => {
    setEditingConfigId(undefined);
    setCurrentView('form');
  };

  const handleEditConfiguration = (configId: string) => {
    setEditingConfigId(configId);
    setCurrentView('form');
  };

  const handleFormBack = () => {
    setCurrentView('list');
    setEditingConfigId(undefined);
  };

  const handleFormSave = () => {
    setCurrentView('list');
    setEditingConfigId(undefined);
    loadConfigurations(); // Refresh the list
  };

  const generateQuickReport = async (format: 'pdf' | 'excel') => {
    console.log('🚀 Generando reporte rápido profesional:', format);
    const reportKey = `quick-${format}`;
    setGeneratingReports(prev => new Set(prev).add(reportKey));

    try {
      const response = await apiService.post('/reports/generate-quick', {
        output_format: format
      });

      if (response.success) {
        const formatNames = {
          pdf: 'PDF',
          excel: 'Excel'
        };

        alert(`Reporte Rápido ${formatNames[format]} generado exitosamente con datos reales. Revise la sección de "Ejecuciones" para descargarlo.`);

        // Switch to executions tab and refresh
        setActiveTab('executions');
        setTimeout(() => loadExecutions(), 1000);
      } else {
        console.error('❌ Error en la respuesta:', response);
        alert('Error al generar el reporte: ' + (response.error || 'Error desconocido'));
      }
    } catch (error) {
      console.error('💥 Error generando reporte rápido:', error);
      alert('Error al generar el reporte. Por favor, intente nuevamente.');
    } finally {
      setGeneratingReports(prev => {
        const newSet = new Set(prev);
        newSet.delete(reportKey);
        return newSet;
      });
    }
  };

  const generateStatisticsReport = async (format: 'pdf' | 'excel') => {
    console.log('📊 Generando reporte de estadísticas:', format);
    const reportKey = `stats-${format}`;
    setGeneratingReports(prev => new Set(prev).add(reportKey));

    try {
      const response = await apiService.post('/reports/generate-statistics', {
        output_format: format,
        date_from: '2025-01-01',
        date_to: new Date().toISOString().split('T')[0]
      });

      if (response.success) {
        const formatNames = {
          pdf: 'PDF',
          excel: 'Excel'
        };

        alert(`Reporte de Estadísticas ${formatNames[format]} generado exitosamente. Incluye análisis completo de tickets, clientes y técnicos.`);

        // Switch to executions tab and refresh
        setActiveTab('executions');
        setTimeout(() => loadExecutions(), 1000);
      } else {
        console.error('❌ Error en la respuesta:', response);
        alert('Error al generar el reporte: ' + (response.error || 'Error desconocido'));
      }
    } catch (error) {
      console.error('💥 Error generando reporte de estadísticas:', error);
      alert('Error al generar el reporte. Por favor, intente nuevamente.');
    } finally {
      setGeneratingReports(prev => {
        const newSet = new Set(prev);
        newSet.delete(reportKey);
        return newSet;
      });
    }
  };

  const generateSLAReport = async (format: 'pdf' | 'excel') => {
    console.log('📈 Generando reporte de SLA:', format);
    const reportKey = `sla-${format}`;
    setGeneratingReports(prev => new Set(prev).add(reportKey));

    try {
      const response = await apiService.post('/reports/generate-sla', {
        output_format: format,
        date_from: '2025-01-01',
        date_to: new Date().toISOString().split('T')[0]
      });

      if (response.success) {
        const formatNames = {
          pdf: 'PDF',
          excel: 'Excel'
        };

        alert(`Reporte de Cumplimiento SLA ${formatNames[format]} generado exitosamente. Incluye métricas de respuesta y resolución.`);

        // Switch to executions tab and refresh
        setActiveTab('executions');
        setTimeout(() => loadExecutions(), 1000);
      } else {
        console.error('❌ Error en la respuesta:', response);
        alert('Error al generar el reporte: ' + (response.error || 'Error desconocido'));
      }
    } catch (error) {
      console.error('💥 Error generando reporte de SLA:', error);
      alert('Error al generar el reporte. Por favor, intente nuevamente.');
    } finally {
      setGeneratingReports(prev => {
        const newSet = new Set(prev);
        newSet.delete(reportKey);
        return newSet;
      });
    }
  };

  const deleteConfiguration = async (configId: string) => {
    if (!confirm('¿Está seguro de que desea eliminar esta configuración de reporte?')) {
      return;
    }

    try {
      const response = await apiService.delete(`/reports/configurations/${configId}`);
      if (response.success) {
        alert('Configuración eliminada exitosamente');
        loadConfigurations();
      } else {
        alert('Error al eliminar la configuración');
      }
    } catch (error) {
      console.error('Error deleting configuration:', error);
      alert('Error al eliminar la configuración');
    }
  };

  // Show form view
  if (currentView === 'form') {
    return (
      <ReportConfigurationForm
        configId={editingConfigId}
        onBack={handleFormBack}
        onSave={handleFormSave}
      />
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Gestión de Reportes</h1>
                <p className="mt-1 text-sm text-gray-500">
                  Administre plantillas, configuraciones y ejecuciones de reportes
                </p>
                <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-md">
                  <p className="text-sm text-blue-800">
                    <strong>📊 Reportes Profesionales:</strong> Genere reportes empresariales con datos reales de tickets,
                    estadísticas de clientes, métricas de técnicos y análisis de cumplimiento SLA.
                  </p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {(user?.role === 'superadmin' || user?.role === 'admin' || user?.role === 'technician' || user?.role === 'client_admin') && (
                  <>
                    {/* Quick Reports */}
                    <div className="flex space-x-1">
                      <button
                        onClick={() => generateQuickReport('pdf')}
                        disabled={generatingReports.has('quick-pdf')}
                        className="inline-flex items-center px-3 py-2 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Reporte Rápido PDF - Dashboard ejecutivo con métricas clave"
                      >
                        {generatingReports.has('quick-pdf') ? (
                          <Loader className="h-3 w-3 mr-1 animate-spin" />
                        ) : (
                          <Download className="h-3 w-3 mr-1" />
                        )}
                        Rápido PDF
                      </button>
                      <button
                        onClick={() => generateQuickReport('excel')}
                        disabled={generatingReports.has('quick-excel')}
                        className="inline-flex items-center px-3 py-2 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Reporte Rápido Excel - Dashboard ejecutivo con métricas clave"
                      >
                        {generatingReports.has('quick-excel') ? (
                          <Loader className="h-3 w-3 mr-1 animate-spin" />
                        ) : (
                          <Download className="h-3 w-3 mr-1" />
                        )}
                        Rápido Excel
                      </button>
                    </div>

                    {/* Statistics Reports */}
                    <div className="flex space-x-1">
                      <button
                        onClick={() => generateStatisticsReport('pdf')}
                        disabled={generatingReports.has('stats-pdf')}
                        className="inline-flex items-center px-3 py-2 border border-blue-300 text-xs font-medium rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Reporte de Estadísticas PDF - Análisis completo de tickets, clientes y técnicos"
                      >
                        {generatingReports.has('stats-pdf') ? (
                          <Loader className="h-3 w-3 mr-1 animate-spin" />
                        ) : (
                          <BarChart3 className="h-3 w-3 mr-1" />
                        )}
                        Estadísticas PDF
                      </button>
                      <button
                        onClick={() => generateStatisticsReport('excel')}
                        disabled={generatingReports.has('stats-excel')}
                        className="inline-flex items-center px-3 py-2 border border-blue-300 text-xs font-medium rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Reporte de Estadísticas Excel - Análisis completo de tickets, clientes y técnicos"
                      >
                        {generatingReports.has('stats-excel') ? (
                          <Loader className="h-3 w-3 mr-1 animate-spin" />
                        ) : (
                          <BarChart3 className="h-3 w-3 mr-1" />
                        )}
                        Estadísticas Excel
                      </button>
                    </div>

                    {/* SLA Reports */}
                    <div className="flex space-x-1">
                      <button
                        onClick={() => generateSLAReport('pdf')}
                        disabled={generatingReports.has('sla-pdf')}
                        className="inline-flex items-center px-3 py-2 border border-green-300 text-xs font-medium rounded-md text-green-700 bg-green-50 hover:bg-green-100 disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Reporte de SLA PDF - Cumplimiento de tiempos de respuesta y resolución"
                      >
                        {generatingReports.has('sla-pdf') ? (
                          <Loader className="h-3 w-3 mr-1 animate-spin" />
                        ) : (
                          <Clock className="h-3 w-3 mr-1" />
                        )}
                        SLA PDF
                      </button>
                      <button
                        onClick={() => generateSLAReport('excel')}
                        disabled={generatingReports.has('sla-excel')}
                        className="inline-flex items-center px-3 py-2 border border-green-300 text-xs font-medium rounded-md text-green-700 bg-green-50 hover:bg-green-100 disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Reporte de SLA Excel - Cumplimiento de tiempos de respuesta y resolución"
                      >
                        {generatingReports.has('sla-excel') ? (
                          <Loader className="h-3 w-3 mr-1 animate-spin" />
                        ) : (
                          <Clock className="h-3 w-3 mr-1" />
                        )}
                        SLA Excel
                      </button>
                    </div>

                    <button
                      onClick={handleNewConfiguration}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Configuración
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white shadow">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {[
              { key: 'templates', label: 'Plantillas', icon: FileText },
              { key: 'configurations', label: 'Configuraciones', icon: Settings },
              { key: 'executions', label: 'Ejecuciones', icon: BarChart3 },
              { key: 'schedules', label: 'Programación', icon: Calendar }
            ].map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key as any)}
                className={`${
                  activeTab === key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
              >
                <Icon className="h-4 w-4 mr-2" />
                {label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white shadow rounded-lg">
        <div className="p-6">
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="h-5 w-5 absolute left-3 top-3 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
              <Filter className="h-4 w-4 mr-2" />
              Filtros
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="bg-white shadow rounded-lg">
        <div className="p-6">
          {activeTab === 'templates' && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">Plantillas de Reportes</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredData().map((template: any) => (
                  <div key={template.template_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="text-sm font-medium text-gray-900">{template.name}</h4>
                        <p className="text-sm text-gray-500 mt-1">{template.description}</p>
                        <div className="mt-2 flex items-center space-x-2">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {template.report_type}
                          </span>
                          {template.is_system && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                              Sistema
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'configurations' && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">Configuraciones de Reportes</h3>
              <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                <table className="min-w-full divide-y divide-gray-300">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Nombre
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Plantilla
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Formatos
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
                    {filteredData().map((config: any) => (
                      <tr key={config.config_id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{config.name}</div>
                            <div className="text-sm text-gray-500">{config.description}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{config.template_name}</div>
                          <div className="text-sm text-gray-500">{config.report_type}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex space-x-1">
                            {config.output_formats.map((format: string) => (
                              <span key={format} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                {format.toUpperCase()}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            config.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {config.is_active ? 'Activo' : 'Inactivo'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            {config.output_formats.map((format: string) => {
                              const reportKey = `${config.config_id}-${format}`;
                              const isGenerating = generatingReports.has(reportKey);

                              return (
                                <button
                                  key={format}
                                  onClick={() => generateReport(config.config_id, format)}
                                  disabled={isGenerating}
                                  className="text-blue-600 hover:text-blue-900 flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                                  title={`Generar ${format.toUpperCase()}`}
                                >
                                  {isGenerating ? (
                                    <Loader className="h-4 w-4 mr-1 animate-spin" />
                                  ) : (
                                    <Play className="h-4 w-4 mr-1" />
                                  )}
                                  {format.toUpperCase()}
                                </button>
                              );
                            })}
                            <button
                              onClick={() => handleEditConfiguration(config.config_id)}
                              className="text-gray-600 hover:text-gray-900"
                              title="Editar"
                            >
                              <Edit className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => deleteConfiguration(config.config_id)}
                              className="text-red-600 hover:text-red-900"
                              title="Eliminar"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'executions' && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">Historial de Ejecuciones</h3>
              <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                <table className="min-w-full divide-y divide-gray-300">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Configuración
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Estado
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Formato
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Tamaño
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Tiempo
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Ejecutado por
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Acciones
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredData().map((execution: any) => (
                      <tr key={execution.execution_id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {execution.config_name || 'Reporte Rápido'}
                          </div>
                          <div className="text-sm text-gray-500">
                            {execution.config_id ? 'Configuración' : 'Generación directa'}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {getStatusBadge(execution.status)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {execution.output_format?.toUpperCase() || 'N/A'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {execution.file_size ? formatFileSize(execution.file_size) : 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {execution.started_at ? new Date(execution.started_at).toLocaleString('es-ES') : 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {execution.executed_by_name ||
                           (execution.first_name && execution.last_name
                            ? `${execution.first_name} ${execution.last_name}`
                            : 'Sistema')
                          }
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          {execution.status === 'completed' && (
                            <button
                              onClick={() => downloadReport(execution.execution_id)}
                              className="text-blue-600 hover:text-blue-900 flex items-center"
                            >
                              <Download className="h-4 w-4 mr-1" />
                              Descargar
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'schedules' && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">Reportes Programados</h3>
              <div className="text-center py-12">
                <Calendar className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Próximamente</h3>
                <p className="mt-1 text-sm text-gray-500">
                  La funcionalidad de programación de reportes estará disponible pronto.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReportsManagement;
