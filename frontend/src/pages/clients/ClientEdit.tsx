import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Save, X, Plus, Trash2, Mail } from 'lucide-react';
import { apiService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import CountrySelector from '../../components/CountrySelector';
import StateSelector from '../../components/StateSelector';

interface ClientData {
  name: string;
  email: string;
  rfc?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  country: string;
  postal_code?: string;
  authorized_domains?: string[];
  email_routing_enabled?: boolean;
}

const ClientEdit: React.FC = () => {
  const { clientId } = useParams<{ clientId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [newDomain, setNewDomain] = useState('');

  const [clientData, setClientData] = useState<ClientData>({
    name: '',
    email: '',
    rfc: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    country: 'México',
    postal_code: '',
    authorized_domains: [],
    email_routing_enabled: true
  });

  const canEditClients = user?.role === 'superadmin' || user?.role === 'admin';

  useEffect(() => {
    if (!canEditClients) {
      navigate('/clients');
      return;
    }
    
    if (clientId) {
      loadClient();
    }
  }, [clientId, canEditClients]);

  const loadClient = async () => {
    try {
      setLoading(true);
      const response = await apiService.get(`/clients/${clientId}`);
      
      if (response.success) {
        const client = response.data;
        setClientData({
          name: client.name || '',
          email: client.email || '',
          rfc: client.rfc || '',
          phone: client.phone || '',
          address: client.address || '',
          city: client.city || '',
          state: client.state || '',
          country: client.country || 'México',
          postal_code: client.postal_code || '',
          authorized_domains: client.authorized_domains || [],
          email_routing_enabled: client.email_routing_enabled !== false
        });
      } else {
        setErrors({ general: 'Error al cargar los datos del cliente' });
      }
    } catch (error) {
      console.error('Error loading client:', error);
      setErrors({ general: 'Error al cargar los datos del cliente' });
    } finally {
      setLoading(false);
    }
  };

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  };

  const validatePhone = (phone: string): boolean => {
    if (!phone) return true; // Optional field
    const cleanPhone = phone.replace(/[\s\-\(\)\.]/g, '');
    const mexicanPhoneRegex = /^[0-9]{10}$/;
    const internationalPhoneRegex = /^[\+][1-9][0-9]{7,14}$/;
    return mexicanPhoneRegex.test(cleanPhone) || internationalPhoneRegex.test(cleanPhone);
  };

  const validatePostalCode = (postalCode: string, country: string): boolean => {
    if (!postalCode) return true; // Optional field
    
    const patterns: Record<string, RegExp> = {
      'México': /^\d{5}$/,
      'Estados Unidos': /^\d{5}(-\d{4})?$/,
      'Canadá': /^[A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d$/,
      'España': /^\d{5}$/,
      'Colombia': /^\d{6}$/,
      'Argentina': /^[A-Z]?\d{4}[A-Z]{0,3}$/,
      'Chile': /^\d{7}$/,
      'Perú': /^\d{5}$/
    };
    
    const pattern = patterns[country] || /^.+$/;
    return pattern.test(postalCode);
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Name validation
    if (!clientData.name.trim()) {
      newErrors.name = 'Nombre es requerido';
    } else if (clientData.name.trim().length < 3) {
      newErrors.name = 'El nombre debe tener al menos 3 caracteres';
    }

    // Email validation
    if (!clientData.email.trim()) {
      newErrors.email = 'Email es requerido';
    } else if (!validateEmail(clientData.email)) {
      newErrors.email = 'Formato de email inválido';
    }

    // RFC validation (optional but if provided must be valid)
    if (clientData.rfc && clientData.rfc.trim()) {
      const rfcRegex = /^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$/;
      if (!rfcRegex.test(clientData.rfc.trim().toUpperCase())) {
        newErrors.rfc = 'Formato de RFC inválido (ej: ABC123456789)';
      }
    }

    // Phone validation (optional)
    if (clientData.phone && !validatePhone(clientData.phone)) {
      newErrors.phone = 'Formato de teléfono inválido (10 dígitos para México o +código país)';
    }

    // Postal code validation (optional)
    if (clientData.postal_code && !validatePostalCode(clientData.postal_code, clientData.country)) {
      newErrors.postal_code = `Código postal inválido para ${clientData.country}`;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Domain management functions
  const addDomain = () => {
    if (newDomain.trim() && !clientData.authorized_domains?.includes(newDomain.trim())) {
      setClientData(prev => ({
        ...prev,
        authorized_domains: [...(prev.authorized_domains || []), newDomain.trim()]
      }));
      setNewDomain('');
    }
  };

  const removeDomain = (domainToRemove: string) => {
    setClientData(prev => ({
      ...prev,
      authorized_domains: prev.authorized_domains?.filter(domain => domain !== domainToRemove) || []
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      setSaving(true);
      
      // Prepare data for API
      const updateData = {
        ...clientData,
        rfc: clientData.rfc?.toUpperCase() || null,
        phone: clientData.phone || null,
        address: clientData.address || null,
        city: clientData.city || null,
        state: clientData.state || null,
        postal_code: clientData.postal_code || null,
        authorized_domains: clientData.authorized_domains || [],
        email_routing_enabled: clientData.email_routing_enabled !== false
      };

      const response = await apiService.put(`/clients/${clientId}`, updateData);

      if (response.success) {
        navigate(`/clients/${clientId}`, {
          state: {
            message: `Cliente "${clientData.name}" actualizado exitosamente`
          }
        });
      } else {
        // Handle backend validation errors
        if (response.details && typeof response.details === 'object') {
          const newErrors: Record<string, string> = {};

          // Map backend errors to frontend field names with Spanish messages
          if (response.details.name) {
            newErrors.name = response.details.name === 'Client name already exists'
              ? 'Ya existe un cliente con este nombre'
              : response.details.name;
          }
          if (response.details.email) {
            newErrors.email = response.details.email === 'Email already exists'
              ? 'Esta dirección de email ya está en uso'
              : response.details.email === 'Invalid email format'
              ? 'Formato de email inválido'
              : response.details.email;
          }
          if (response.details.rfc) {
            newErrors.rfc = response.details.rfc === 'Invalid RFC format'
              ? 'Formato de RFC inválido'
              : response.details.rfc;
          }
          if (response.details.phone) {
            newErrors.phone = response.details.phone === 'Invalid phone number format'
              ? 'Formato de teléfono inválido'
              : response.details.phone;
          }
          if (response.details.postal_code) {
            newErrors.postal_code = response.details.postal_code === 'Invalid postal code format (must be 5 digits)'
              ? 'Código postal debe tener 5 dígitos'
              : response.details.postal_code;
          }
          if (response.details.general) {
            newErrors.general = response.details.general;
          }

          setErrors(newErrors);
        } else {
          // Handle specific backend error messages
          let errorMessage = response.error || 'Error al actualizar el cliente';
          if (errorMessage === 'Email already exists') {
            setErrors({ email: 'Esta dirección de email ya está en uso' });
          } else if (errorMessage === 'Client name already exists') {
            setErrors({ name: 'Ya existe un cliente con este nombre' });
          } else {
            setErrors({ general: errorMessage });
          }
        }
      }
    } catch (error) {
      console.error('Error updating client:', error);
      setErrors({ general: 'Error interno del servidor' });
    } finally {
      setSaving(false);
    }
  };

  const updateField = (field: keyof ClientData, value: string) => {
    setClientData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate(`/clients/${clientId}`)}
            className="inline-flex items-center text-blue-600 hover:text-blue-800"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Volver a Detalles
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Editar Cliente</h1>
            <p className="text-gray-600">Actualiza la información del cliente</p>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white shadow rounded-lg p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nombre de la Organización *
              </label>
              <input
                type="text"
                value={clientData.name}
                onChange={(e) => updateField('name', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.name ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Ej: Empresa ABC S.A. de C.V."
              />
              {errors.name && (
                <p className="mt-1 text-sm text-red-600">{errors.name}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Principal *
              </label>
              <input
                type="email"
                value={clientData.email}
                onChange={(e) => updateField('email', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.email ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="contacto@empresa.com"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                RFC
              </label>
              <input
                type="text"
                value={clientData.rfc}
                onChange={(e) => updateField('rfc', e.target.value.toUpperCase())}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.rfc ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="ABC123456789"
                maxLength={13}
              />
              {errors.rfc && (
                <p className="mt-1 text-sm text-red-600">{errors.rfc}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Teléfono
              </label>
              <input
                type="tel"
                value={clientData.phone}
                onChange={(e) => updateField('phone', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.phone ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="5512345678 o +52 55 1234 5678"
              />
              {errors.phone && (
                <p className="mt-1 text-sm text-red-600">{errors.phone}</p>
              )}
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Dirección
              </label>
              <input
                type="text"
                value={clientData.address}
                onChange={(e) => updateField('address', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.address ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Av. Principal 123, Col. Centro"
              />
              {errors.address && (
                <p className="mt-1 text-sm text-red-600">{errors.address}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ciudad
              </label>
              <input
                type="text"
                value={clientData.city}
                onChange={(e) => updateField('city', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.city ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Ciudad de México"
              />
              {errors.city && (
                <p className="mt-1 text-sm text-red-600">{errors.city}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                País
              </label>
              <CountrySelector
                value={clientData.country}
                onChange={(country) => updateField('country', country)}
                error={!!errors.country}
              />
              {errors.country && (
                <p className="mt-1 text-sm text-red-600">{errors.country}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Estado
              </label>
              <StateSelector
                country={clientData.country}
                value={clientData.state}
                onChange={(state) => updateField('state', state)}
                error={!!errors.state}
              />
              {errors.state && (
                <p className="mt-1 text-sm text-red-600">{errors.state}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Código Postal
              </label>
              <input
                type="text"
                value={clientData.postal_code}
                onChange={(e) => updateField('postal_code', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.postal_code ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="01000"
              />
              {errors.postal_code && (
                <p className="mt-1 text-sm text-red-600">{errors.postal_code}</p>
              )}
            </div>
          </div>

          {/* Email Authorization Section */}
          <div className="bg-gray-50 p-6 rounded-lg">
            <div className="flex items-center mb-4">
              <Mail className="h-5 w-5 text-blue-600 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Configuración de Email</h3>
            </div>

            {/* Email Routing Toggle */}
            <div className="mb-6">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={clientData.email_routing_enabled}
                  onChange={(e) => updateField('email_routing_enabled', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm font-medium text-gray-700">
                  Habilitar enrutamiento automático de emails
                </span>
              </label>
              <p className="mt-1 text-sm text-gray-500">
                Permite que los emails de este cliente se conviertan automáticamente en tickets
              </p>
            </div>

            {/* Authorized Domains */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Dominios Autorizados
              </label>
              <p className="text-sm text-gray-500 mb-3">
                Solo los emails de estos dominios podrán crear tickets automáticamente
              </p>

              {/* Add Domain Input */}
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={newDomain}
                  onChange={(e) => setNewDomain(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addDomain())}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="ejemplo.com"
                />
                <button
                  type="button"
                  onClick={addDomain}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 flex items-center"
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Agregar
                </button>
              </div>

              {/* Domain List */}
              {clientData.authorized_domains && clientData.authorized_domains.length > 0 && (
                <div className="space-y-2">
                  {clientData.authorized_domains.map((domain, index) => (
                    <div key={index} className="flex items-center justify-between bg-white p-3 rounded-lg border">
                      <span className="text-sm font-medium text-gray-900">{domain}</span>
                      <button
                        type="button"
                        onClick={() => removeDomain(domain)}
                        className="text-red-600 hover:text-red-800 focus:outline-none"
                        title="Eliminar dominio"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {(!clientData.authorized_domains || clientData.authorized_domains.length === 0) && (
                <div className="text-center py-4 text-gray-500 text-sm">
                  No hay dominios autorizados. Agregue al menos uno para habilitar el enrutamiento automático.
                </div>
              )}
            </div>
          </div>

          {/* Error Messages */}
          {errors.general && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800">{errors.general}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate(`/clients/${clientId}`)}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50"
            >
              <X className="w-4 h-4 mr-2" />
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saving}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <Save className="w-4 h-4 mr-2" />
              {saving ? 'Guardando...' : 'Guardar Cambios'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ClientEdit;
