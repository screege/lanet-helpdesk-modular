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
  const [activeTab, setActiveTab] = useState<'executions' | 'monthly'>('monthly');
  const [currentView, setCurrentView] = useState<'list' | 'form'>('list');
  const [editingConfigId, setEditingConfigId] = useState<string | undefined>();
  const [executions, setExecutions] = useState<ReportExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [monthlyStatus, setMonthlyStatus] = useState<any>(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Estados para el generador de reportes
  const [selectedClient, setSelectedClient] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('2025-07-01');
  const [endDate, setEndDate] = useState<string>('2025-07-31');
  const [clients, setClients] = useState<any[]>([]);
  const [generatingReports, setGeneratingReports] = useState<Set<string>>(new Set());



  useEffect(() => {
    console.log('🔄 useEffect triggered, activeTab:', activeTab);
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    console.log('📊 loadData called for tab:', activeTab);
    setLoading(true);
    try {
      switch (activeTab) {
        case 'executions':
          console.log('📈 Loading executions...');
          await loadExecutions();
          break;
        case 'monthly':
          console.log('📅 Loading monthly reports data...');
          await loadMonthlyStatus();
          await loadClients();
          break;
      }
    } catch (error) {
      console.error('❌ Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMonthlyStatus = async () => {
    try {
      const response = await apiService.get('/reports/monthly/status');
      if (response.success) {
        setMonthlyStatus(response.data);
      }
    } catch (error) {
      console.error('Error loading monthly status:', error);
    }
  };

  const loadClients = async () => {
    try {
      const response = await apiService.get('/clients');
      if (response.success) {
        setClients(response.data || []);
      }
    } catch (error) {
      console.error('Error loading clients:', error);
    }
  };

  const generateTestReport = async () => {
    try {
      setLoading(true);

      // Preparar parámetros del reporte
      const reportParams = {
        client_id: selectedClient || null,
        start_date: startDate,
        end_date: endDate
      };

      console.log('📊 Generating report with params:', reportParams);

      const response = await apiService.post('/reports/monthly/generate-test', reportParams);

      if (response.success) {
        const clientName = selectedClient ?
          clients.find(c => c.client_id === selectedClient)?.name || 'Cliente específico' :
          'Todos los clientes';

        console.log(`✅ Reporte generado exitosamente! Cliente: ${clientName}, Período: ${startDate} - ${endDate}`);

        // Refresh executions if on that tab
        if (activeTab === 'executions') {
          loadExecutions();
        }
      } else {
        alert(`❌ Error: ${response.error || 'Error desconocido'}`);
      }
    } catch (error) {
      console.error('Error generating custom report:', error);
      alert(`❌ Error al generar reporte: ${error.message || 'Error de conexión'}`);
    } finally {
      setLoading(false);
    }
  };

  const setupSchedules = async () => {
    if (!user || user.role !== 'superadmin') {
      alert('Solo los superadministradores pueden configurar programaciones');
      return;
    }

    try {
      setLoading(true);
      const response = await apiService.post('/reports/monthly/setup-schedules');

      if (response.success) {
        alert('✅ Programaciones mensuales configuradas exitosamente!\n\nTodos los clientes recibirán reportes automáticamente el día 1 de cada mes.');
        await loadMonthlyStatus(); // Refresh status
      } else {
        alert(`❌ Error: ${response.error || 'Error desconocido'}`);
      }
    } catch (error) {
      console.error('Error setting up schedules:', error);
      alert(`❌ Error al configurar programaciones: ${error.message || 'Error de conexión'}`);
    } finally {
      setLoading(false);
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

  // Helper functions for executions table

  const formatFileSize = (bytes?: number) => {
    if (!bytes || bytes === 0) return 'N/A';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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

        // Silent download - no popup
        console.log('✅ Reporte descargado exitosamente');
      } else {
        const errorText = await response.text();
        alert('Error al descargar el reporte: ' + (errorText || 'Error del servidor'));
      }
    } catch (error) {
      console.error('Error downloading report:', error);
      alert('Error al descargar el reporte. Verifique su conexión a internet.');
    }
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
    if (activeTab === 'executions') {
      return (executions || []).filter(e =>
        (e.config_name || '').toLowerCase().includes(term) ||
        (e.status || '').toLowerCase().includes(term)
      );
    }
    return [];
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
    // No longer needed
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
        // No longer needed
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
                  Genere y descargue reportes mensuales consolidados
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
              { key: 'monthly', label: 'Reportes Mensuales', icon: Calendar },
              { key: 'executions', label: 'Ver Reportes Generados', icon: BarChart3 }
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
          {activeTab === 'executions' && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">Historial de Reportes Generados</h3>
              <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                <table className="min-w-full divide-y divide-gray-300">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Reporte
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
                        Fecha
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
                            {execution.config_name || 'Reporte Consolidado'}
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
                            {execution.output_format?.toUpperCase() || 'EXCEL'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {execution.file_size ? formatFileSize(execution.file_size) : 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {execution.started_at ? new Date(execution.started_at).toLocaleString('es-ES') : 'N/A'}
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

          {activeTab === 'monthly' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">Reportes Consolidados</h3>
                  <p className="text-sm text-gray-600">
                    Genere reportes con todos los tickets de todos los clientes o por cliente específico
                  </p>
                </div>
              </div>

              {/* Generador de Reportes Bajo Demanda */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <BarChart3 className="w-6 h-6 text-blue-600" />
                  <h4 className="text-lg font-medium text-gray-900">Generar Reporte Bajo Demanda</h4>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  {/* Selector de Cliente */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Cliente
                    </label>
                    <select
                      value={selectedClient}
                      onChange={(e) => setSelectedClient(e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                    >
                      <option value="">Todos los clientes</option>
                      {clients.map((client) => (
                        <option key={client.client_id} value={client.client_id}>
                          {client.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Fecha Desde */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Fecha Desde
                    </label>
                    <input
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                    />
                  </div>

                  {/* Fecha Hasta */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Fecha Hasta
                    </label>
                    <input
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                    />
                  </div>
                </div>

                <div className="flex space-x-3">
                  <button
                    onClick={generateTestReport}
                    disabled={loading}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg text-sm transition-colors"
                  >
                    {loading ? 'Generando...' : 'Generar Reporte Excel'}
                  </button>
                  <button
                    onClick={() => setActiveTab('executions')}
                    className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-6 py-2 rounded-lg text-sm transition-colors"
                  >
                    Ver Reportes Generados
                  </button>
                </div>
              </div>

              {/* Programación Automática */}
              {user?.role === 'superadmin' && (
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <div className="flex items-center space-x-3 mb-6">
                    <Calendar className="w-6 h-6 text-green-600" />
                    <h4 className="text-lg font-medium text-gray-900">Programación Automática</h4>
                  </div>

                  <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-4">
                    <div className="flex">
                      <div className="flex-shrink-0">
                        <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <h3 className="text-sm font-medium text-yellow-800">
                          Configuración de Reportes Automáticos
                        </h3>
                        <div className="mt-2 text-sm text-yellow-700">
                          <p>Al configurar las programaciones, cada cliente recibirá automáticamente:</p>
                          <ul className="list-disc list-inside mt-1">
                            <li>Un reporte mensual con TODOS sus tickets</li>
                            <li>Enviado por email el día 1 de cada mes a las 6:00 AM</li>
                            <li>Formato Excel con columnas: Número, Asunto, Estado, Prioridad, Fechas, Técnico, Sitio</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex space-x-3">
                    <button
                      onClick={setupSchedules}
                      disabled={loading}
                      className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg text-sm transition-colors"
                    >
                      {loading ? 'Configurando...' : 'Activar Reportes Automáticos'}
                    </button>
                    <div className="text-sm text-gray-600 flex items-center">
                      Estado: {monthlyStatus?.system_active ?
                        <span className="text-green-600 ml-1">✓ Activo</span> :
                        <span className="text-red-600 ml-1">❌ Inactivo</span>
                      }
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}


        </div>
      </div>
    </div>
  );
};

export default ReportsManagement;
