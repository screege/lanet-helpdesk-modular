import React, { useState, useEffect } from 'react';
import { X, Building2, MapPin, Save, Mail, Plus, Trash2 } from 'lucide-react';
import { sitesService, Site, CreateSiteData, UpdateSiteData } from '../../services/sitesService';
import { apiService } from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';

interface SiteFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  site?: Site;
  clientId?: string;
}

const SiteForm: React.FC<SiteFormProps> = ({
  isOpen,
  onClose,
  onSuccess,
  site,
  clientId
}) => {
  const [formData, setFormData] = useState({
    client_id: clientId || site?.client_id || '',
    name: site?.name || '',
    address: site?.address || '',
    city: site?.city || '',
    state: site?.state || '',
    country: site?.country || 'México',
    postal_code: site?.postal_code || '',
    latitude: site?.latitude || '',
    longitude: site?.longitude || '',
    authorized_emails: site?.authorized_emails || []
  });

  const [clients, setClients] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingClients, setLoadingClients] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [newEmail, setNewEmail] = useState('');

  const isEditing = !!site;

  useEffect(() => {
    if (isOpen && !clientId) {
      loadClients();
    }
  }, [isOpen, clientId]);

  // Update form data when site prop changes
  useEffect(() => {
    if (site) {
      setFormData({
        client_id: clientId || site.client_id || '',
        name: site.name || '',
        address: site.address || '',
        city: site.city || '',
        state: site.state || '',
        country: site.country || 'México',
        postal_code: site.postal_code || '',
        latitude: site.latitude || '',
        longitude: site.longitude || '',
        authorized_emails: site.authorized_emails || []
      });
    }
  }, [site, clientId]);

  const loadClients = async () => {
    try {
      setLoadingClients(true);
      const response = await clientsService.getAllClients({ per_page: 100 });
      if (response.success) {
        setClients(response.data.clients || []);
      }
    } catch (err: any) {
      console.error('Error loading clients:', err);
    } finally {
      setLoadingClients(false);
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.client_id) {
      newErrors.client_id = 'Cliente es requerido';
    }
    if (!formData.name.trim()) {
      newErrors.name = 'Nombre del sitio es requerido';
    }
    if (!formData.address.trim()) {
      newErrors.address = 'Dirección es requerida';
    }
    if (!formData.city.trim()) {
      newErrors.city = 'Ciudad es requerida';
    }
    if (!formData.state.trim()) {
      newErrors.state = 'Estado es requerido';
    }
    if (!formData.postal_code.trim()) {
      newErrors.postal_code = 'Código postal es requerido';
    } else if (!/^\d{5}$/.test(formData.postal_code)) {
      newErrors.postal_code = 'Código postal debe tener 5 dígitos';
    }

    // Validate coordinates if provided
    if (formData.latitude && (isNaN(Number(formData.latitude)) || Number(formData.latitude) < -90 || Number(formData.latitude) > 90)) {
      newErrors.latitude = 'Latitud debe estar entre -90 y 90';
    }
    if (formData.longitude && (isNaN(Number(formData.longitude)) || Number(formData.longitude) < -180 || Number(formData.longitude) > 180)) {
      newErrors.longitude = 'Longitud debe estar entre -180 y 180';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Email validation function
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  // Email management functions
  const addEmail = () => {
    const email = newEmail.trim().toLowerCase();
    if (email && validateEmail(email) && !formData.authorized_emails.includes(email)) {
      setFormData(prev => ({
        ...prev,
        authorized_emails: [...prev.authorized_emails, email]
      }));
      setNewEmail('');
      // Clear any email-related errors
      if (errors.newEmail) {
        setErrors(prev => ({ ...prev, newEmail: '' }));
      }
    } else if (!validateEmail(email)) {
      setErrors(prev => ({ ...prev, newEmail: 'Formato de email inválido' }));
    } else if (formData.authorized_emails.includes(email)) {
      setErrors(prev => ({ ...prev, newEmail: 'Este email ya está autorizado' }));
    }
  };

  const removeEmail = (emailToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      authorized_emails: prev.authorized_emails.filter(email => email !== emailToRemove)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const siteData = {
        ...formData,
        latitude: formData.latitude ? Number(formData.latitude) : undefined,
        longitude: formData.longitude ? Number(formData.longitude) : undefined
      };

      let response;
      if (isEditing) {
        const updateData: UpdateSiteData = { ...siteData };
        delete (updateData as any).client_id; // Can't change client_id when editing
        response = await sitesService.updateSite(site.site_id, updateData);
      } else {
        response = await sitesService.createSite(siteData as CreateSiteData);
      }

      if (response.success) {
        onSuccess();
      } else {
        setError(response.message || `Failed to ${isEditing ? 'update' : 'create'} site`);
      }
    } catch (err: any) {
      setError(err.message || `Failed to ${isEditing ? 'update' : 'create'} site`);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <Building2 className="h-6 w-6 text-blue-600" />
            <h3 className="text-lg font-medium text-gray-900">
              {isEditing ? 'Editar Sitio' : 'Agregar Nuevo Sitio'}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {error && <ErrorMessage message={error} />}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Client Selection (only for new sites) */}
          {!isEditing && !clientId && (
            <div>
              <label htmlFor="client_id" className="block text-sm font-medium text-gray-700">
                Cliente *
              </label>
              <select
                id="client_id"
                name="client_id"
                value={formData.client_id}
                onChange={handleInputChange}
                className={`mt-1 block w-full border rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                  errors.client_id ? 'border-red-300' : 'border-gray-300'
                }`}
                disabled={loadingClients}
              >
                <option value="">Seleccionar cliente...</option>
                {clients.map((client) => (
                  <option key={client.client_id} value={client.client_id}>
                    {client.name}
                  </option>
                ))}
              </select>
              {errors.client_id && (
                <p className="mt-1 text-sm text-red-600">{errors.client_id}</p>
              )}
            </div>
          )}

          {/* Site Name */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              Nombre del Sitio *
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className={`mt-1 block w-full border rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                errors.name ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Ej: Oficina Principal, Sucursal Norte"
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-600">{errors.name}</p>
            )}
          </div>

          {/* Address */}
          <div>
            <label htmlFor="address" className="block text-sm font-medium text-gray-700">
              Dirección *
            </label>
            <input
              type="text"
              id="address"
              name="address"
              value={formData.address}
              onChange={handleInputChange}
              className={`mt-1 block w-full border rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                errors.address ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Calle, número, colonia"
            />
            {errors.address && (
              <p className="mt-1 text-sm text-red-600">{errors.address}</p>
            )}
          </div>

          {/* City and State */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="city" className="block text-sm font-medium text-gray-700">
                Ciudad *
              </label>
              <input
                type="text"
                id="city"
                name="city"
                value={formData.city}
                onChange={handleInputChange}
                className={`mt-1 block w-full border rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                  errors.city ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Ciudad"
              />
              {errors.city && (
                <p className="mt-1 text-sm text-red-600">{errors.city}</p>
              )}
            </div>

            <div>
              <label htmlFor="state" className="block text-sm font-medium text-gray-700">
                Estado *
              </label>
              <input
                type="text"
                id="state"
                name="state"
                value={formData.state}
                onChange={handleInputChange}
                className={`mt-1 block w-full border rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                  errors.state ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Estado"
              />
              {errors.state && (
                <p className="mt-1 text-sm text-red-600">{errors.state}</p>
              )}
            </div>
          </div>

          {/* Country and Postal Code */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="country" className="block text-sm font-medium text-gray-700">
                País
              </label>
              <input
                type="text"
                id="country"
                name="country"
                value={formData.country}
                onChange={handleInputChange}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="País"
              />
            </div>

            <div>
              <label htmlFor="postal_code" className="block text-sm font-medium text-gray-700">
                Código Postal *
              </label>
              <input
                type="text"
                id="postal_code"
                name="postal_code"
                value={formData.postal_code}
                onChange={handleInputChange}
                className={`mt-1 block w-full border rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                  errors.postal_code ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="12345"
                maxLength={5}
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
              <h3 className="text-lg font-medium text-gray-900">Emails Autorizados</h3>
            </div>
            <p className="text-sm text-gray-500 mb-4">
              Solo los emails de esta lista podrán crear tickets automáticamente para este sitio
            </p>

            {/* Add Email Input */}
            <div className="flex gap-2 mb-4">
              <input
                type="email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addEmail())}
                className={`flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.newEmail ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="usuario@empresa.com"
              />
              <button
                type="button"
                onClick={addEmail}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 flex items-center"
              >
                <Plus className="h-4 w-4 mr-1" />
                Agregar
              </button>
            </div>
            {errors.newEmail && (
              <p className="mb-3 text-sm text-red-600">{errors.newEmail}</p>
            )}

            {/* Email List */}
            {formData.authorized_emails && formData.authorized_emails.length > 0 && (
              <div className="space-y-2">
                {formData.authorized_emails.map((email, index) => (
                  <div key={index} className="flex items-center justify-between bg-white p-3 rounded-lg border">
                    <span className="text-sm font-medium text-gray-900">{email}</span>
                    <button
                      type="button"
                      onClick={() => removeEmail(email)}
                      className="text-red-600 hover:text-red-800 focus:outline-none"
                      title="Eliminar email"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {formData.authorized_emails.length === 0 && (
              <div className="text-center py-4 text-gray-500 text-sm">
                No hay emails autorizados. Agregue al menos uno para permitir la creación automática de tickets.
              </div>
            )}
          </div>

          {/* Coordinates (Optional) */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="latitude" className="block text-sm font-medium text-gray-700">
                Latitud (Opcional)
              </label>
              <input
                type="number"
                id="latitude"
                name="latitude"
                value={formData.latitude}
                onChange={handleInputChange}
                step="any"
                min="-90"
                max="90"
                className={`mt-1 block w-full border rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                  errors.latitude ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="19.4326"
              />
              {errors.latitude && (
                <p className="mt-1 text-sm text-red-600">{errors.latitude}</p>
              )}
            </div>

            <div>
              <label htmlFor="longitude" className="block text-sm font-medium text-gray-700">
                Longitud (Opcional)
              </label>
              <input
                type="number"
                id="longitude"
                name="longitude"
                value={formData.longitude}
                onChange={handleInputChange}
                step="any"
                min="-180"
                max="180"
                className={`mt-1 block w-full border rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                  errors.longitude ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="-99.1332"
              />
              {errors.longitude && (
                <p className="mt-1 text-sm text-red-600">{errors.longitude}</p>
              )}
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? (
                <LoadingSpinner size="sm" />
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  {isEditing ? 'Actualizar' : 'Crear'} Sitio
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SiteForm;
