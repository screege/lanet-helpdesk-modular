import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { emailService, EmailTemplate } from '../../services/emailService';
import { 
  Mail, 
  Plus, 
  Edit, 
  Trash2, 
  Eye, 
  Copy,
  AlertCircle,
  FileText,
  Star,
  StarOff,
  Code,
  Type
} from 'lucide-react';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ErrorMessage from '../../components/common/ErrorMessage';

const EmailTemplates: React.FC = () => {
  const { hasRole } = useAuth();
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<EmailTemplate | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState<{ subject: string; body: string } | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    template_type: 'ticket_created',
    subject_template: '',
    body_template: '',
    is_html: true,
    is_active: true,
    is_default: false
  });

  // Template variables for different types
  const templateVariables = {
    ticket_created: ['{{ticket_number}}', '{{client_name}}', '{{site_name}}', '{{subject}}', '{{description}}', '{{priority}}', '{{affected_person}}', '{{created_date}}'],
    ticket_assigned: ['{{ticket_number}}', '{{client_name}}', '{{technician_name}}', '{{subject}}', '{{priority}}', '{{assigned_date}}'],
    ticket_updated: ['{{ticket_number}}', '{{client_name}}', '{{subject}}', '{{status}}', '{{updated_by}}', '{{update_date}}'],
    ticket_resolved: ['{{ticket_number}}', '{{client_name}}', '{{subject}}', '{{resolution}}', '{{resolved_by}}', '{{resolved_date}}'],
    ticket_closed: ['{{ticket_number}}', '{{client_name}}', '{{subject}}', '{{closed_by}}', '{{closed_date}}'],
    sla_breach: ['{{ticket_number}}', '{{client_name}}', '{{subject}}', '{{priority}}', '{{breach_type}}', '{{time_elapsed}}'],
    auto_response: ['{{sender_name}}', '{{ticket_number}}', '{{subject}}', '{{original_subject}}', '{{client_name}}']
  };

  const templateTypes = [
    { value: 'ticket_created', label: 'Ticket Creado' },
    { value: 'ticket_assigned', label: 'Ticket Asignado' },
    { value: 'ticket_updated', label: 'Ticket Actualizado' },
    { value: 'ticket_resolved', label: 'Ticket Resuelto' },
    { value: 'ticket_closed', label: 'Ticket Cerrado' },
    { value: 'sla_breach', label: 'Violación SLA' },
    { value: 'auto_response', label: 'Respuesta Automática' }
  ];

  useEffect(() => {
    if (hasRole(['superadmin', 'admin'])) {
      loadTemplates();
    }
  }, [hasRole]);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const templateList = await emailService.getEmailTemplates();
      setTemplates(templateList);
    } catch (err: any) {
      setError(err.message || 'Error loading email templates');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingTemplate) {
        await emailService.updateEmailTemplate(editingTemplate.template_id, formData);
      } else {
        await emailService.createEmailTemplate(formData);
      }
      
      setShowForm(false);
      setEditingTemplate(null);
      resetForm();
      await loadTemplates();
    } catch (err: any) {
      setError(err.message || 'Error saving email template');
    }
  };

  const handleEdit = (template: EmailTemplate) => {
    setEditingTemplate(template);
    setFormData({
      name: template.name,
      description: template.description || '',
      template_type: template.template_type,
      subject_template: template.subject_template,
      body_template: template.body_template,
      is_html: template.is_html,
      is_active: template.is_active,
      is_default: template.is_default
    });
    setShowForm(true);
  };

  const handleDelete = async (templateId: string) => {
    if (window.confirm('¿Está seguro de que desea eliminar esta plantilla de email?')) {
      try {
        await emailService.deleteEmailTemplate(templateId);
        await loadTemplates();
      } catch (err: any) {
        setError(err.message || 'Error deleting email template');
      }
    }
  };

  const handlePreview = async (template: EmailTemplate) => {
    try {
      // Sample variables for preview
      const sampleVariables = {
        ticket_number: 'TKT-123456',
        client_name: 'Empresa Demo',
        site_name: 'Oficina Principal',
        subject: 'Problema con impresora',
        description: 'La impresora no funciona correctamente',
        priority: 'Alta',
        affected_person: 'Juan Pérez',
        technician_name: 'María González',
        created_date: new Date().toLocaleDateString('es-MX'),
        sender_name: 'Cliente Demo'
      };

      const preview = await emailService.previewEmailTemplate(template.template_id, sampleVariables);
      setPreviewData(preview);
      setShowPreview(true);
    } catch (err: any) {
      setError(err.message || 'Error generating preview');
    }
  };

  const insertVariable = (variable: string) => {
    const textarea = document.getElementById('body_template') as HTMLTextAreaElement;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const text = formData.body_template;
      const newText = text.substring(0, start) + variable + text.substring(end);
      setFormData({ ...formData, body_template: newText });
      
      // Restore cursor position
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(start + variable.length, start + variable.length);
      }, 0);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      template_type: 'ticket_created',
      subject_template: '',
      body_template: '',
      is_html: true,
      is_active: true,
      is_default: false
    });
  };

  if (!hasRole(['superadmin', 'admin'])) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-red-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Acceso Denegado</h3>
          <p className="mt-1 text-sm text-gray-500">
            No tiene permisos para acceder a las plantillas de email.
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
          <h1 className="text-2xl font-bold text-gray-900">Plantillas de Email</h1>
          <p className="mt-1 text-sm text-gray-500">
            Gestione las plantillas de email para notificaciones automáticas
          </p>
        </div>
        <button
          onClick={() => {
            setShowForm(true);
            setEditingTemplate(null);
            resetForm();
          }}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <Plus className="h-4 w-4 mr-2" />
          Nueva Plantilla
        </button>
      </div>

      {error && <ErrorMessage message={error} />}

      {/* Template Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-6xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {editingTemplate ? 'Editar Plantilla de Email' : 'Nueva Plantilla de Email'}
              </h3>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Basic Information */}
                  <div className="space-y-4">
                    <h4 className="text-md font-medium text-gray-900">Información Básica</h4>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Nombre *</label>
                      <input
                        type="text"
                        required
                        value={formData.name}
                        onChange={(e) => setFormData({...formData, name: e.target.value})}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Descripción</label>
                      <textarea
                        value={formData.description}
                        onChange={(e) => setFormData({...formData, description: e.target.value})}
                        rows={3}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Tipo de Plantilla *</label>
                      <select
                        required
                        value={formData.template_type}
                        onChange={(e) => setFormData({...formData, template_type: e.target.value})}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      >
                        {templateTypes.map(type => (
                          <option key={type.value} value={type.value}>{type.label}</option>
                        ))}
                      </select>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          checked={formData.is_html}
                          onChange={(e) => setFormData({...formData, is_html: e.target.checked})}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 block text-sm text-gray-900">Formato HTML</label>
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          checked={formData.is_active}
                          onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 block text-sm text-gray-900">Plantilla activa</label>
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          checked={formData.is_default}
                          onChange={(e) => setFormData({...formData, is_default: e.target.checked})}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 block text-sm text-gray-900">Plantilla por defecto</label>
                      </div>
                    </div>
                  </div>

                  {/* Template Content */}
                  <div className="lg:col-span-2 space-y-4">
                    <h4 className="text-md font-medium text-gray-900">Contenido de la Plantilla</h4>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Asunto *</label>
                      <input
                        type="text"
                        required
                        value={formData.subject_template}
                        onChange={(e) => setFormData({...formData, subject_template: e.target.value})}
                        placeholder="Ej: [{{ticket_number}}] {{subject}}"
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Cuerpo del Email *</label>
                      <textarea
                        id="body_template"
                        required
                        value={formData.body_template}
                        onChange={(e) => setFormData({...formData, body_template: e.target.value})}
                        rows={12}
                        placeholder={formData.is_html ?
                          "Ej: <p>Estimado {{client_name}},</p><p>Se ha creado el ticket {{ticket_number}}...</p>" :
                          "Ej: Estimado {{client_name}},\n\nSe ha creado el ticket {{ticket_number}}..."
                        }
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                      />
                    </div>

                    {/* Variables Helper */}
                    <div className="bg-gray-50 p-4 rounded-md">
                      <h5 className="text-sm font-medium text-gray-900 mb-2">Variables Disponibles:</h5>
                      <div className="flex flex-wrap gap-2">
                        {templateVariables[formData.template_type as keyof typeof templateVariables]?.map(variable => (
                          <button
                            key={variable}
                            type="button"
                            onClick={() => insertVariable(variable)}
                            className="inline-flex items-center px-2 py-1 border border-gray-300 rounded text-xs font-medium text-gray-700 bg-white hover:bg-gray-50"
                          >
                            <Code className="h-3 w-3 mr-1" />
                            {variable}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Form Actions */}
                <div className="flex justify-end space-x-3 pt-6 border-t">
                  <button
                    type="button"
                    onClick={() => {
                      setShowForm(false);
                      setEditingTemplate(null);
                      resetForm();
                    }}
                    className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    {editingTemplate ? 'Actualizar' : 'Crear'} Plantilla
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {showPreview && previewData && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">Vista Previa de Plantilla</h3>
                <button
                  onClick={() => setShowPreview(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="sr-only">Cerrar</span>
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Asunto:</label>
                  <div className="mt-1 p-3 bg-gray-50 border rounded-md">
                    {previewData.subject}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Cuerpo:</label>
                  <div className="mt-1 p-3 bg-gray-50 border rounded-md max-h-96 overflow-y-auto">
                    {previewData.body.includes('<') ? (
                      <div dangerouslySetInnerHTML={{ __html: previewData.body }} />
                    ) : (
                      <pre className="whitespace-pre-wrap font-sans">{previewData.body}</pre>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex justify-end mt-6">
                <button
                  onClick={() => setShowPreview(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Templates List */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {templates.map((template) => (
            <li key={template.template_id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center">
                    <FileText className="h-5 w-5 text-gray-400 mr-3" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 flex items-center">
                        {template.name}
                        {template.is_default && (
                          <Star className="h-4 w-4 text-yellow-400 ml-2" fill="currentColor" />
                        )}
                      </h3>
                      <p className="text-sm text-gray-500">{template.description}</p>
                      <div className="mt-1 flex items-center space-x-4 text-xs text-gray-500">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {templateTypes.find(t => t.value === template.template_type)?.label || template.template_type}
                        </span>
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          template.is_html 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {template.is_html ? 'HTML' : 'Texto'}
                        </span>
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          template.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {template.is_active ? 'Activo' : 'Inactivo'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handlePreview(template)}
                    className="p-2 text-gray-400 hover:text-blue-600"
                    title="Vista previa"
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                  
                  <button
                    onClick={() => handleEdit(template)}
                    className="p-2 text-gray-400 hover:text-blue-600"
                    title="Editar"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  
                  <button
                    onClick={() => handleDelete(template.template_id)}
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
        
        {templates.length === 0 && (
          <div className="text-center py-12">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No hay plantillas</h3>
            <p className="mt-1 text-sm text-gray-500">
              Comience creando una nueva plantilla de email.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmailTemplates;
