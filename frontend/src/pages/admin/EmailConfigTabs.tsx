import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { emailService } from '../../services/emailService';
import { EmailConfiguration } from '../../types/email';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Mail, 
  Server, 
  Inbox, 
  Plus, 
  Edit, 
  Trash2, 
  Settings, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  TestTube,
  RefreshCw
} from 'lucide-react';

const EmailConfigTabs: React.FC = () => {
  const { user } = useAuth();
  const [configurations, setConfigurations] = useState<EmailConfiguration[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'smtp' | 'imap'>('smtp');
  const [testingConfig, setTestingConfig] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<{ [key: string]: any }>({});
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState<any>({});
  const [sendingTestEmail, setSendingTestEmail] = useState(false);
  const [testEmail, setTestEmail] = useState('');

  useEffect(() => {
    loadConfigurations();
  }, []);

  useEffect(() => {
    const activeConfig = configurations.find(c => c.is_default) || configurations[0];
    if (activeConfig) {
      // Use config_id as the primary ID
      const configData = {
        ...activeConfig,
        id: activeConfig.config_id
      };
      setFormData(configData);
      console.log('Setting form data:', configData);
    }
  }, [configurations]);

  const loadConfigurations = async () => {
    try {
      setLoading(true);
      const data = await emailService.getEmailConfigurations();
      console.log('🔧 FRONTEND: Raw configurations data:', data);
      console.log('🔧 FRONTEND: First config:', data[0]);
      console.log('🔧 FRONTEND: First config keys:', data[0] ? Object.keys(data[0]) : 'No data');
      if (data[0]) {
        console.log('🔧 FRONTEND: SSL/TLS values:', {
          smtp_use_ssl: data[0].smtp_use_ssl,
          smtp_use_tls: data[0].smtp_use_tls,
          config_id: data[0].config_id
        });
      }
      setConfigurations(data);
    } catch (err: any) {
      setError(err.message || 'Error loading email configurations');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('¿Está seguro de que desea eliminar esta configuración?')) {
      return;
    }

    try {
      await emailService.deleteEmailConfiguration(id);
      await loadConfigurations();
    } catch (err: any) {
      setError(err.message || 'Error deleting configuration');
    }
  };

  const handleSetDefault = async (id: string) => {
    try {
      await emailService.setDefaultConfiguration(id);
      await loadConfigurations();
    } catch (err: any) {
      setError(err.message || 'Error setting default configuration');
    }
  };

  const handleTestConnection = async (id: string, type: 'smtp' | 'imap' | 'both' = 'both') => {
    try {
      console.log('🔧 FRONTEND: Testing connection for ID:', id, 'type:', type);
      setTestingConfig(id);
      setError(null);

      if (!id || id === 'undefined') {
        throw new Error('Invalid configuration ID');
      }

      const result = await emailService.testEmailConnection(id);
      console.log('🔧 FRONTEND: Test result:', result);
      setTestResults(prev => ({ ...prev, [id]: { ...result, type } }));

      if (result.success) {
        // Auto-clear success message after 8 seconds
        setTimeout(() => {
          setTestResults(prev => {
            const newResults = { ...prev };
            delete newResults[id];
            return newResults;
          });
        }, 8000);
      } else {
        // Show detailed error information
        console.error('Connection test failed:', result);
        setError(`Error en prueba de conexión ${type.toUpperCase()}: ${result.error_details || result.message}`);
      }
    } catch (err: any) {
      console.error('🔧 FRONTEND: Error testing connection:', err);
      console.error('🔧 FRONTEND: Error object:', err);
      console.error('🔧 FRONTEND: Error constructor:', err?.constructor);
      const errorMessage = err.response?.data?.error || err.message || 'Unknown error';
      setError(`Error probando conexión ${type.toUpperCase()}: ${errorMessage}`);
      setTestResults(prev => ({
        ...prev,
        [id]: {
          success: false,
          message: errorMessage,
          error_details: err.response?.data?.error_details || 'Failed to connect to email server',
          type
        }
      }));
    } finally {
      setTestingConfig(null);
    }
  };

  const handleCheckEmails = async (id: string) => {
    try {
      setTestingConfig(id);
      console.log('🔧 FRONTEND: Checking emails for config:', id);

      const response = await emailService.checkEmails(id);
      console.log('🔧 FRONTEND: Email check response:', response);

      // The response structure is: { success: true, data: { success: true, emails_found: X, tickets_created: Y, message: "..." } }
      if (response.success && response.data) {
        const data = response.data;
        console.log('🔧 FRONTEND: Email check data:', data);

        if (data.success) {
          const emailsFound = data.emails_found || 0;
          const ticketsCreated = data.tickets_created || 0;
          const emailsProcessed = data.emails_processed || 0;

          let successMessage = `✅ Verificación completada: ${emailsFound} emails encontrados`;
          if (emailsProcessed > 0) {
            successMessage += `, ${emailsProcessed} procesados`;
          }
          if (ticketsCreated > 0) {
            successMessage += `, ${ticketsCreated} tickets creados`;
          }
          if (emailsFound === 0) {
            successMessage = '✅ Verificación completada: No hay emails nuevos';
          }

          setSuccess(successMessage);
          setError(null); // Clear any previous errors
        } else {
          setError(data.message || 'Error verificando emails');
        }
      } else {
        setError(response.error || response.message || 'Error verificando emails');
      }
    } catch (err: any) {
      console.error('🔧 FRONTEND: Error checking emails:', err);

      // Handle different error types
      if (err.response && err.response.data) {
        const errorData = err.response.data;
        setError(`Error verificando emails: ${errorData.error || errorData.message || 'Unknown error'}`);
      } else {
        setError(`Error verificando emails: ${err.message || 'Unknown error'}`);
      }
    } finally {
      setTestingConfig(null);
    }
  };



  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);

      console.log('🔧 FRONTEND: Saving form data:', formData);
      console.log('🔧 FRONTEND: Form data ID:', formData.id);
      console.log('🔧 FRONTEND: SSL value:', formData.smtp_use_ssl, 'type:', typeof formData.smtp_use_ssl);
      console.log('🔧 FRONTEND: TLS value:', formData.smtp_use_tls, 'type:', typeof formData.smtp_use_tls);

      if (!formData.id) {
        setError('Error: ID de configuración no encontrado');
        return;
      }

      const result = await emailService.updateEmailConfiguration(formData.id, formData);
      console.log('🔧 FRONTEND: Save result:', result);
      setSuccess('Configuración actualizada exitosamente');
      await loadConfigurations();

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      console.error('🔧 FRONTEND: Save error:', err);
      setError(err.message || 'Error saving configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSendTestEmail = async () => {
    if (!testEmail) {
      setError('Por favor ingresa una dirección de email');
      return;
    }

    try {
      setSendingTestEmail(true);
      setError(null);

      const result = await emailService.sendTestEmail(formData.config_id || formData.id, testEmail);

      if (result.success) {
        setSuccess(`Email de prueba enviado exitosamente a ${testEmail}`);
        setTestEmail(''); // Clear the email field

        // Clear success message after 5 seconds
        setTimeout(() => setSuccess(null), 5000);
      } else {
        setError(`Error enviando email: ${result.error_details || result.message}`);
      }
    } catch (err: any) {
      console.error('Error sending test email:', err);
      setError(`Error enviando email de prueba: ${err.message || 'Unknown error'}`);
    } finally {
      setSendingTestEmail(false);
    }
  };

  const renderTabContent = () => {
    const activeConfig = configurations.find(c => c.is_default) || configurations[0];
    
    if (!activeConfig) {
      return (
        <div className="text-center py-12">
          <p className="text-gray-500">No hay configuraciones de email disponibles.</p>
          <Link
            to="/admin/email-config/new"
            className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-600 bg-blue-100 hover:bg-blue-200"
          >
            <Plus className="h-4 w-4 mr-2" />
            Crear primera configuración
          </Link>
        </div>
      );
    }

    switch (activeTab) {
      case 'smtp':
        return (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg border">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-medium text-gray-900 flex items-center gap-2">
                  <Mail className="h-5 w-5" />
                  Configuración SMTP - {formData.name || 'Sin nombre'}
                </h3>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleTestConnection(formData.config_id || formData.id, 'smtp')}
                    disabled={testingConfig === (formData.config_id || formData.id)}
                    className="bg-yellow-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-yellow-700 disabled:opacity-50 flex items-center gap-2"
                  >
                    {testingConfig === (formData.config_id || formData.id) ? (
                      <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                    ) : (
                      <TestTube className="h-4 w-4" />
                    )}
                    Probar SMTP
                  </button>

                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
                  >
                    {saving ? (
                      <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                    ) : (
                      <CheckCircle className="h-4 w-4" />
                    )}
                    Guardar
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6 text-sm">
                <div>
                  <label className="block font-medium text-gray-700 mb-1">Servidor SMTP:</label>
                  <input
                    type="text"
                    value={formData.smtp_host || ''}
                    onChange={(e) => handleInputChange('smtp_host', e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block font-medium text-gray-700 mb-1">Puerto:</label>
                  <input
                    type="number"
                    value={formData.smtp_port || ''}
                    onChange={(e) => handleInputChange('smtp_port', parseInt(e.target.value))}
                    className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block font-medium text-gray-700 mb-1">Usuario:</label>
                  <input
                    type="email"
                    value={formData.smtp_username || ''}
                    onChange={(e) => handleInputChange('smtp_username', e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block font-medium text-gray-700 mb-1">Contraseña:</label>
                  <input
                    type="password"
                    value={formData.smtp_password || ''}
                    onChange={(e) => handleInputChange('smtp_password', e.target.value)}
                    placeholder="Dejar vacío para mantener actual"
                    className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block font-medium text-gray-700 mb-1">Reply-To (Responder a):</label>
                  <input
                    type="email"
                    value={formData.smtp_reply_to || ''}
                    onChange={(e) => handleInputChange('smtp_reply_to', e.target.value)}
                    placeholder="respuestas@empresa.com (opcional)"
                    className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">Para comunicación bidireccional</p>
                </div>
                <div className="col-span-2">
                  <label className="block font-medium text-gray-700 mb-2">Seguridad:</label>
                  <div className="flex gap-4">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.smtp_use_ssl || false}
                        onChange={(e) => handleInputChange('smtp_use_ssl', e.target.checked)}
                        className="mr-2"
                      />
                      SSL
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.smtp_use_tls || false}
                        onChange={(e) => handleInputChange('smtp_use_tls', e.target.checked)}
                        className="mr-2"
                      />
                      TLS
                    </label>
                  </div>
                </div>
              </div>

              {/* Test Email Section */}
              <div className="mt-8 pt-6 border-t border-gray-200">
                <h4 className="text-md font-medium text-gray-900 mb-4">Enviar Email de Prueba</h4>
                <div className="flex gap-3 items-end">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Dirección de email:
                    </label>
                    <input
                      type="email"
                      value={testEmail}
                      onChange={(e) => setTestEmail(e.target.value)}
                      placeholder="ejemplo@dominio.com"
                      className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <button
                    onClick={handleSendTestEmail}
                    disabled={sendingTestEmail || !testEmail}
                    className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
                  >
                    {sendingTestEmail ? (
                      <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                    ) : (
                      <Mail className="h-4 w-4" />
                    )}
                    Enviar Prueba
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Se enviará un email de prueba para verificar que la configuración SMTP funciona correctamente.
                </p>
              </div>

              {testResults[formData.config_id || formData.id] && (
                <div className="mt-6 p-4 rounded-lg border">
                  {testResults[formData.config_id || formData.id].success ? (
                    <div className="flex items-center text-green-600">
                      <CheckCircle className="h-5 w-5 mr-2" />
                      <div>
                        <span className="font-medium">Conexión SMTP exitosa</span>
                        <p className="text-sm text-green-700 mt-1">{testResults[formData.config_id || formData.id].message}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="text-red-600">
                      <div className="flex items-center mb-2">
                        <XCircle className="h-5 w-5 mr-2" />
                        <span className="font-medium">Error en conexión SMTP</span>
                      </div>
                      <p className="text-sm ml-7">{testResults[formData.config_id || formData.id].message}</p>
                      {testResults[formData.config_id || formData.id].error_details && (
                        <p className="text-sm ml-7 mt-1 text-red-500">{testResults[formData.config_id || formData.id].error_details}</p>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        );

      case 'imap':
        return (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg border">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-medium text-gray-900 flex items-center gap-2">
                  <Inbox className="h-5 w-5" />
                  Configuración IMAP - {formData.name || 'Sin nombre'}
                </h3>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleTestConnection(formData.config_id || formData.id, 'imap')}
                    disabled={testingConfig === (formData.config_id || formData.id) || !formData.enable_email_to_ticket}
                    className="bg-yellow-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-yellow-700 disabled:opacity-50 flex items-center gap-2"
                  >
                    {testingConfig === (formData.config_id || formData.id) ? (
                      <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                    ) : (
                      <TestTube className="h-4 w-4" />
                    )}
                    Probar IMAP
                  </button>
                  <button
                    onClick={() => handleCheckEmails(formData.config_id || formData.id)}
                    disabled={testingConfig === (formData.config_id || formData.id) || !formData.enable_email_to_ticket}
                    className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
                  >
                    {testingConfig === (formData.config_id || formData.id) ? (
                      <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                    ) : (
                      <RefreshCw className="h-4 w-4" />
                    )}
                    Verificar Emails
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
                  >
                    {saving ? (
                      <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                    ) : (
                      <CheckCircle className="h-4 w-4" />
                    )}
                    Guardar
                  </button>
                </div>
              </div>
              
              {formData.enable_email_to_ticket ? (
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Servidor IMAP <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.imap_host || ''}
                      onChange={(e) => setFormData({...formData, imap_host: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="mail.ejemplo.com"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Puerto <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="number"
                      value={formData.imap_port || 993}
                      onChange={(e) => setFormData({...formData, imap_port: parseInt(e.target.value)})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="993"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Usuario <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="email"
                      value={formData.imap_username || ''}
                      onChange={(e) => setFormData({...formData, imap_username: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="usuario@ejemplo.com"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Contraseña IMAP
                    </label>
                    <input
                      type="password"
                      value={formData.imap_password || ''}
                      onChange={(e) => setFormData({...formData, imap_password: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Dejar vacío para mantener actual"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Carpeta
                    </label>
                    <input
                      type="text"
                      value={formData.imap_folder || 'INBOX'}
                      onChange={(e) => setFormData({...formData, imap_folder: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="INBOX"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Usar SSL
                    </label>
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.imap_use_ssl || false}
                        onChange={(e) => setFormData({...formData, imap_use_ssl: e.target.checked})}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm text-gray-700">
                        {formData.imap_use_ssl ? 'SSL Habilitado' : 'SSL Deshabilitado'}
                      </span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <Inbox className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <h4 className="text-lg font-medium mb-2">Email a Ticket está deshabilitado</h4>
                  <p className="text-sm">Habilítelo en la configuración para usar IMAP</p>
                  <Link
                    to={`/admin/email-config/edit/${formData.config_id || formData.id}`}
                    className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-600 bg-blue-100 hover:bg-blue-200"
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Configurar IMAP
                  </Link>
                </div>
              )}
              
              {testResults[formData.config_id || formData.id] && formData.enable_email_to_ticket && (
                <div className="mt-6 p-4 rounded-lg border">
                  {testResults[formData.config_id || formData.id].success ? (
                    <div className="flex items-center text-green-600">
                      <CheckCircle className="h-5 w-5 mr-2" />
                      <div>
                        <span className="font-medium">Conexión IMAP exitosa</span>
                        <p className="text-sm text-green-700 mt-1">{testResults[formData.config_id || formData.id].message}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="text-red-600">
                      <div className="flex items-center mb-2">
                        <XCircle className="h-5 w-5 mr-2" />
                        <span className="font-medium">Error en conexión IMAP</span>
                      </div>
                      <p className="text-sm ml-7">{testResults[formData.config_id || formData.id].message}</p>
                      {testResults[formData.config_id || formData.id].error_details && (
                        <p className="text-sm ml-7 mt-1 text-red-500">{testResults[formData.config_id || formData.id].error_details}</p>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        );

      default:
        return (
          <div className="text-center py-12">
            <p className="text-gray-500">Selecciona una pestaña para configurar SMTP o IMAP.</p>
          </div>
        );
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Configuración de Email</h1>
        {/* Solo permitir una configuración de email en el sistema */}
        {user?.role === 'superadmin' && configurations.length === 0 && (
          <Link
            to="/admin/email-config/new"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Nueva Configuración
          </Link>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
          {success}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('smtp')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'smtp'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Mail className="h-4 w-4 inline mr-2" />
            SMTP (Envío)
          </button>
          <button
            onClick={() => setActiveTab('imap')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'imap'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Inbox className="h-4 w-4 inline mr-2" />
            IMAP (Recepción)
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {renderTabContent()}
    </div>
  );
};

export default EmailConfigTabs;
