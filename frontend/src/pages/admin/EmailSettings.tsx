import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { emailService, EmailConfiguration } from '../../services/emailService';
import {
  Mail,
  Plus,
  Edit,
  Trash2,
  AlertCircle,
  TestTube,
  Star,
  StarOff
} from 'lucide-react';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ErrorMessage from '../../components/common/ErrorMessage';

const EmailSettings: React.FC = () => {
  const { hasRole } = useAuth();
  const navigate = useNavigate();
  const [configurations, setConfigurations] = useState<EmailConfiguration[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [testingConfig, setTestingConfig] = useState<string | null>(null);



  useEffect(() => {
    if (hasRole(['superadmin', 'admin'])) {
      loadConfigurations();
    }
  }, [hasRole]);

  const loadConfigurations = async () => {
    try {
      setLoading(true);
      const configs = await emailService.getEmailConfigurations();
      setConfigurations(configs);
    } catch (err: any) {
      setError(err.message || 'Error loading email configurations');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (config: EmailConfiguration) => {
    navigate(`/admin/email-config/edit/${config.config_id}`);
  };

  const handleCreate = () => {
    navigate('/admin/email-config/new');
  };

  const handleDelete = async (configId: string) => {
    if (window.confirm('¿Está seguro de que desea eliminar esta configuración de email?')) {
      try {
        await emailService.deleteEmailConfiguration(configId);
        await loadConfigurations();
      } catch (err: any) {
        setError(err.message || 'Error deleting email configuration');
      }
    }
  };

  const handleTestConnection = async (configId: string) => {
    try {
      setTestingConfig(configId);
      const result = await emailService.testEmailConnection(configId);
      
      if (result.success) {
        alert('Conexión exitosa: ' + result.message);
      } else {
        alert('Error de conexión: ' + result.message);
      }
    } catch (err: any) {
      alert('Error probando conexión: ' + err.message);
    } finally {
      setTestingConfig(null);
    }
  };

  const handleSetDefault = async (configId: string) => {
    try {
      await emailService.setDefaultConfiguration(configId);
      await loadConfigurations();
    } catch (err: any) {
      setError(err.message || 'Error setting default configuration');
    }
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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Configuración de Email</h1>
          <p className="mt-1 text-sm text-gray-500">
            Gestione las configuraciones SMTP/IMAP para el sistema de email-to-ticket
          </p>
        </div>
        <button
          onClick={handleCreate}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <Plus className="h-4 w-4 mr-2" />
          Nueva Configuración
        </button>
      </div>

      {error && <ErrorMessage message={error} />}



      {/* Configurations List */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {configurations.map((config) => (
            <li key={config.config_id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center">
                    <Mail className="h-5 w-5 text-gray-400 mr-3" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 flex items-center">
                        {config.name}
                        {config.is_default && (
                          <Star className="h-4 w-4 text-yellow-400 ml-2" fill="currentColor" />
                        )}
                      </h3>
                      <p className="text-sm text-gray-500">{config.description}</p>
                      <div className="mt-1 flex items-center space-x-4 text-xs text-gray-500">
                        <span>SMTP: {config.smtp_host}:{config.smtp_port}</span>
                        {config.imap_host && (
                          <span>IMAP: {config.imap_host}:{config.imap_port}</span>
                        )}
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          config.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {config.is_active ? 'Activo' : 'Inactivo'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  {!config.is_default && (
                    <button
                      onClick={() => handleSetDefault(config.config_id)}
                      className="p-2 text-gray-400 hover:text-yellow-600"
                      title="Establecer como predeterminado"
                    >
                      <StarOff className="h-4 w-4" />
                    </button>
                  )}

                  <button
                    onClick={() => handleTestConnection(config.config_id)}
                    disabled={testingConfig === config.config_id}
                    className="p-2 text-gray-400 hover:text-blue-600 disabled:opacity-50"
                    title="Probar conexión"
                  >
                    {testingConfig === config.config_id ? (
                      <LoadingSpinner size="sm" />
                    ) : (
                      <TestTube className="h-4 w-4" />
                    )}
                  </button>

                  <button
                    onClick={() => handleEdit(config)}
                    className="p-2 text-gray-400 hover:text-blue-600"
                    title="Editar"
                  >
                    <Edit className="h-4 w-4" />
                  </button>

                  <button
                    onClick={() => handleDelete(config.config_id)}
                    className="p-2 text-gray-400 hover:text-red-600"
                    title="Eliminar"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>

        {configurations.length === 0 && (
          <div className="text-center py-12">
            <Mail className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No hay configuraciones</h3>
            <p className="mt-1 text-sm text-gray-500">
              Comience creando una nueva configuración de email.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmailSettings;
