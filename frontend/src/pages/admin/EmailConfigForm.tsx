import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { emailService } from '../../services/emailService';
import { 
  ArrowLeft, 
  Save, 
  TestTube, 
  AlertCircle 
} from 'lucide-react';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ErrorMessage from '../../components/common/ErrorMessage';

const EmailConfigForm: React.FC = () => {
  const { hasRole } = useAuth();
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditing = Boolean(id); // If there's an ID in the URL, we're editing

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    smtp_host: '',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '',
    smtp_use_tls: true,
    smtp_use_ssl: false,
    smtp_reply_to: '',
    imap_host: '',
    imap_port: 993,
    imap_username: '',
    imap_password: '',
    imap_use_ssl: true,
    imap_folder: 'INBOX',
    enable_email_to_ticket: true,
    default_priority: 'media',
    subject_prefix: '[LANET]',
    ticket_number_regex: '\\[#?([A-Z]+-\\d+)\\]',
    is_active: true
  });

  useEffect(() => {
    if (isEditing && id) {
      loadConfiguration();
    }
  }, [id]); // Only depend on id, not isEditing

  const loadConfiguration = async () => {
    try {
      setLoading(true);
      console.log('Loading configuration for ID:', id);
      const config = await emailService.getEmailConfigurationById(id!);
      console.log('Loaded configuration:', config);
      setFormData({
        name: config.name,
        description: config.description || '',
        smtp_host: config.smtp_host,
        smtp_port: config.smtp_port,
        smtp_username: config.smtp_username,
        smtp_password: '', // Don't populate password for security
        smtp_use_tls: config.smtp_use_tls,
        smtp_use_ssl: config.smtp_use_ssl,
        smtp_reply_to: config.smtp_reply_to || '',
        imap_host: config.imap_host || '',
        imap_port: config.imap_port || 993,
        imap_username: config.imap_username || '',
        imap_password: '', // Don't populate password for security
        imap_use_ssl: config.imap_use_ssl,
        imap_folder: config.imap_folder,
        enable_email_to_ticket: config.enable_email_to_ticket,
        default_priority: config.default_priority,
        subject_prefix: config.subject_prefix || '',
        ticket_number_regex: config.ticket_number_regex || '',
        is_active: config.is_active
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error loading email configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      setError(null);

      console.log('Submitting form data:', formData);

      if (isEditing) {
        const result = await emailService.updateEmailConfiguration(id!, formData);
        console.log('Update result:', result);
        setSuccess('Configuración actualizada exitosamente');
      } else {
        const result = await emailService.createEmailConfiguration(formData);
        console.log('Create result:', result);
        setSuccess('Configuración creada exitosamente');
      }

      // Redirect back to list after a short delay
      setTimeout(() => {
        navigate('/admin/email-config');
      }, 1500);

    } catch (err: unknown) {
      console.error('Form submission error:', err);
      setError(err instanceof Error ? err.message : 'Error saving email configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleTestConnection = async () => {
    if (!isEditing) {
      setError('Debe guardar la configuración antes de probar la conexión');
      return;
    }

    try {
      setTesting(true);
      const result = await emailService.testEmailConnection(id!);
      
      if (result.success) {
        setSuccess('Conexión exitosa: ' + result.message);
      } else {
        setError('Error de conexión: ' + result.message);
      }
    } catch (err: unknown) {
      setError('Error probando conexión: ' + (err instanceof Error ? err.message : 'Error desconocido'));
    } finally {
      setTesting(false);
    }
  };

  const handleCancel = () => {
    navigate('/admin/email-config');
  };

  if (!hasRole(['superadmin', 'admin'])) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-red-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Acceso Denegado</h3>
          <p className="mt-1 text-sm text-gray-500">
            No tiene permisos para acceder a la configuración de email.
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={handleCancel}
            className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {isEditing ? 'Editar Configuración de Email' : 'Nueva Configuración de Email'}
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Configure los parámetros SMTP/IMAP para el sistema de email-to-ticket
            </p>
          </div>
        </div>
        
        <div className="flex space-x-3">
          {isEditing && (
            <button
              onClick={handleTestConnection}
              disabled={testing}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {testing ? (
                <LoadingSpinner size="sm" />
              ) : (
                <TestTube className="h-4 w-4 mr-2" />
              )}
              Probar Conexión
            </button>
          )}
        </div>
      </div>

      {error && <ErrorMessage message={error} />}
      
      {success && (
        <div className="bg-green-50 border border-green-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-green-800">{success}</p>
            </div>
          </div>
        </div>
      )}

      {/* Form */}
      <div className="bg-white shadow rounded-lg">
        <form onSubmit={handleSubmit} className="space-y-6 p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">Información Básica</h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Nombre *</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Ej: Configuración Principal"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Descripción</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  rows={3}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Descripción opcional de la configuración"
                />
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-900">Configuración activa</label>
              </div>
            </div>

            {/* SMTP Configuration */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">Configuración SMTP</h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Servidor SMTP *</label>
                <input
                  type="text"
                  required
                  value={formData.smtp_host}
                  onChange={(e) => setFormData({...formData, smtp_host: e.target.value})}
                  placeholder="smtp.gmail.com"
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Puerto SMTP *</label>
                <input
                  type="number"
                  required
                  value={formData.smtp_port}
                  onChange={(e) => setFormData({...formData, smtp_port: parseInt(e.target.value)})}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Usuario SMTP *</label>
                <input
                  type="email"
                  required
                  value={formData.smtp_username}
                  onChange={(e) => setFormData({...formData, smtp_username: e.target.value})}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Contraseña SMTP *</label>
                <input
                  type="password"
                  required={!isEditing}
                  value={formData.smtp_password}
                  onChange={(e) => setFormData({...formData, smtp_password: e.target.value})}
                  placeholder={isEditing ? "Dejar en blanco para mantener actual" : ""}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Reply-To (Responder a)
                  <span className="text-xs text-gray-500 ml-1">
                    - Para comunicación bidireccional
                  </span>
                </label>
                <input
                  type="email"
                  value={formData.smtp_reply_to}
                  onChange={(e) => setFormData({...formData, smtp_reply_to: e.target.value})}
                  placeholder="respuestas@empresa.com (opcional)"
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Dirección de email donde se recibirán las respuestas. Útil cuando el servidor SMTP es solo de envío.
                </p>
              </div>
              
              <div className="flex space-x-4">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.smtp_use_tls}
                    onChange={(e) => setFormData({...formData, smtp_use_tls: e.target.checked})}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 block text-sm text-gray-900">Usar TLS</label>
                </div>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.smtp_use_ssl}
                    onChange={(e) => setFormData({...formData, smtp_use_ssl: e.target.checked})}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 block text-sm text-gray-900">Usar SSL</label>
                </div>
              </div>
            </div>
          </div>

          {/* IMAP Configuration */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Configuración IMAP (Email-to-Ticket)</h3>

            <div className="flex items-center mb-4">
              <input
                type="checkbox"
                checked={formData.enable_email_to_ticket}
                onChange={(e) => setFormData({...formData, enable_email_to_ticket: e.target.checked})}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-900">Habilitar Email-to-Ticket</label>
            </div>

            {formData.enable_email_to_ticket && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Servidor IMAP</label>
                    <input
                      type="text"
                      value={formData.imap_host}
                      onChange={(e) => setFormData({...formData, imap_host: e.target.value})}
                      placeholder="imap.gmail.com"
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Puerto IMAP</label>
                    <input
                      type="number"
                      value={formData.imap_port}
                      onChange={(e) => setFormData({...formData, imap_port: parseInt(e.target.value)})}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Usuario IMAP</label>
                    <input
                      type="email"
                      value={formData.imap_username}
                      onChange={(e) => setFormData({...formData, imap_username: e.target.value})}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Contraseña IMAP</label>
                    <input
                      type="password"
                      value={formData.imap_password}
                      onChange={(e) => setFormData({...formData, imap_password: e.target.value})}
                      placeholder={isEditing ? "Dejar en blanco para mantener actual" : ""}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Carpeta IMAP</label>
                    <input
                      type="text"
                      value={formData.imap_folder}
                      onChange={(e) => setFormData({...formData, imap_folder: e.target.value})}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Prioridad por Defecto</label>
                    <select
                      value={formData.default_priority}
                      onChange={(e) => setFormData({...formData, default_priority: e.target.value})}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="baja">Baja</option>
                      <option value="media">Media</option>
                      <option value="alta">Alta</option>
                      <option value="critica">Crítica</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Prefijo de Asunto</label>
                    <input
                      type="text"
                      value={formData.subject_prefix}
                      onChange={(e) => setFormData({...formData, subject_prefix: e.target.value})}
                      placeholder="[LANET]"
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Regex Número de Ticket</label>
                    <input
                      type="text"
                      value={formData.ticket_number_regex}
                      onChange={(e) => setFormData({...formData, ticket_number_regex: e.target.value})}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.imap_use_ssl}
                      onChange={(e) => setFormData({...formData, imap_use_ssl: e.target.checked})}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 block text-sm text-gray-900">Usar SSL para IMAP</label>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t">
            <button
              type="button"
              onClick={handleCancel}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saving}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {saving ? (
                <LoadingSpinner size="sm" />
              ) : (
                <Save className="h-4 w-4 mr-2" />
              )}
              {isEditing ? 'Actualizar' : 'Crear'} Configuración
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EmailConfigForm;
