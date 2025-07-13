import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Building2,
  User,
  MapPin,
  ArrowRight,
  ArrowLeft,
  Check,
  AlertCircle
} from 'lucide-react';
import { apiService } from '../../services/api';
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
  allowed_emails: string[];
}

interface AdminUserData {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
  role: string;
  phone?: string;
}

interface SiteData {
  name: string;
  address: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  latitude?: number;
  longitude?: number;
}

interface WizardData {
  client: ClientData;
  admin_user: AdminUserData;
  sites: SiteData[];
}

const ClientCreate: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const [wizardData, setWizardData] = useState<WizardData>({
    client: {
      name: '',
      email: '',
      rfc: '',
      phone: '',
      address: '',
      city: '',
      state: '',
      country: 'México',
      postal_code: '',
      allowed_emails: []
    },
    admin_user: {
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      role: 'client_admin',
      phone: ''
    },
    sites: [{
      name: '',
      address: '',
      city: '',
      state: '',
      country: 'México',
      postal_code: ''
    }]
  });

  const steps = [
    { id: 1, name: 'Cliente', description: 'Información de la organización', icon: Building2 },
    { id: 2, name: 'Admin Principal', description: 'Usuario administrador', icon: User },
    { id: 3, name: 'Sitios', description: 'Ubicaciones del cliente', icon: MapPin },
    { id: 4, name: 'Confirmación', description: 'Revisar y crear', icon: Check }
  ];

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  };

  const validatePhone = (phone: string, required: boolean = false): boolean => {
    if (!phone) return !required; // Required or optional based on parameter

    // Remove all non-digit characters except +
    const cleanPhone = phone.replace(/[\s\-\(\)\.]/g, '');

    // Mexican phone validation (10 digits) or international (+country code + number)
    const mexicanPhoneRegex = /^[0-9]{10}$/;
    const internationalPhoneRegex = /^[\+][1-9][0-9]{7,14}$/;

    return mexicanPhoneRegex.test(cleanPhone) || internationalPhoneRegex.test(cleanPhone);
  };

  const validatePostalCode = (postalCode: string, country: string): boolean => {
    if (!postalCode) return false;

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

    const pattern = patterns[country] || /^.+$/; // Default: any non-empty
    return pattern.test(postalCode);
  };

  const validatePassword = (password: string): string[] => {
    const errors: string[] = [];

    if (password.length < 8) {
      errors.push('Mínimo 8 caracteres');
    }
    if (!/[A-Z]/.test(password)) {
      errors.push('Al menos una mayúscula');
    }
    if (!/[a-z]/.test(password)) {
      errors.push('Al menos una minúscula');
    }
    if (!/\d/.test(password)) {
      errors.push('Al menos un número');
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      errors.push('Al menos un carácter especial');
    }

    return errors;
  };

  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {};

    if (step === 1) {
      // Client name validation
      if (!wizardData.client.name.trim()) {
        newErrors.client_name = 'Nombre de la organización es requerido';
      } else if (wizardData.client.name.trim().length < 3) {
        newErrors.client_name = 'El nombre debe tener al menos 3 caracteres';
      }

      // Client email validation
      if (!wizardData.client.email.trim()) {
        newErrors.client_email = 'Email principal es requerido';
      } else if (!validateEmail(wizardData.client.email)) {
        newErrors.client_email = 'Formato de email inválido';
      }

      // RFC validation (optional but if provided must be valid)
      if (wizardData.client.rfc && wizardData.client.rfc.trim()) {
        const rfcRegex = /^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$/;
        if (!rfcRegex.test(wizardData.client.rfc.trim().toUpperCase())) {
          newErrors.client_rfc = 'Formato de RFC inválido (ej: ABC123456789)';
        }
      }

      // Phone validation (REQUIRED)
      if (!wizardData.client.phone || !wizardData.client.phone.trim()) {
        newErrors.client_phone = 'Teléfono es requerido';
      } else if (!validatePhone(wizardData.client.phone, true)) {
        newErrors.client_phone = 'Formato de teléfono inválido (10 dígitos para México o +código país)';
      }

      // Address validation (REQUIRED)
      if (!wizardData.client.address || !wizardData.client.address.trim()) {
        newErrors.client_address = 'Dirección es requerida';
      } else if (wizardData.client.address.trim().length < 10) {
        newErrors.client_address = 'La dirección debe ser más específica (mínimo 10 caracteres)';
      }

      // City validation (REQUIRED)
      if (!wizardData.client.city || !wizardData.client.city.trim()) {
        newErrors.client_city = 'Ciudad es requerida';
      }

      // State validation (REQUIRED)
      if (!wizardData.client.state || !wizardData.client.state.trim()) {
        newErrors.client_state = 'Estado es requerido';
      }

      // Postal code validation (REQUIRED)
      if (!wizardData.client.postal_code || !wizardData.client.postal_code.trim()) {
        newErrors.client_postal_code = 'Código postal es requerido';
      } else if (!validatePostalCode(wizardData.client.postal_code, wizardData.client.country)) {
        newErrors.client_postal_code = `Código postal inválido para ${wizardData.client.country}`;
      }
    }

    if (step === 2) {
      // Admin name validation
      if (!wizardData.admin_user.name.trim()) {
        newErrors.admin_name = 'Nombre completo es requerido';
      } else if (wizardData.admin_user.name.trim().length < 3) {
        newErrors.admin_name = 'El nombre debe tener al menos 3 caracteres';
      }

      // Admin email validation
      if (!wizardData.admin_user.email.trim()) {
        newErrors.admin_email = 'Email es requerido';
      } else if (!validateEmail(wizardData.admin_user.email)) {
        newErrors.admin_email = 'Formato de email inválido';
      }

      // Password validation
      if (!wizardData.admin_user.password) {
        newErrors.admin_password = 'Contraseña es requerida';
      } else {
        const passwordErrors = validatePassword(wizardData.admin_user.password);
        if (passwordErrors.length > 0) {
          newErrors.admin_password = passwordErrors.join(', ');
        }
      }

      // Confirm password validation
      if (wizardData.admin_user.password !== wizardData.admin_user.confirmPassword) {
        newErrors.admin_confirmPassword = 'Las contraseñas no coinciden';
      }

      // Phone validation (optional for admin user)
      if (wizardData.admin_user.phone && !validatePhone(wizardData.admin_user.phone, false)) {
        newErrors.admin_phone = 'Formato de teléfono inválido (10 dígitos para México o +código país)';
      }
    }

    if (step === 3) {
      if (wizardData.sites.length === 0) {
        newErrors.sites_general = 'Se requiere al menos un sitio';
      }

      wizardData.sites.forEach((site, index) => {
        // Site name validation
        if (!site.name.trim()) {
          newErrors[`site_${index}_name`] = 'Nombre del sitio es requerido';
        } else if (site.name.trim().length < 3) {
          newErrors[`site_${index}_name`] = 'El nombre debe tener al menos 3 caracteres';
        }

        // Address validation
        if (!site.address.trim()) {
          newErrors[`site_${index}_address`] = 'Dirección es requerida';
        } else if (site.address.trim().length < 10) {
          newErrors[`site_${index}_address`] = 'La dirección debe ser más específica';
        }

        // City validation
        if (!site.city.trim()) {
          newErrors[`site_${index}_city`] = 'Ciudad es requerida';
        } else if (site.city.trim().length < 2) {
          newErrors[`site_${index}_city`] = 'Nombre de ciudad inválido';
        }

        // State validation
        if (!site.state.trim()) {
          newErrors[`site_${index}_state`] = 'Estado es requerido';
        } else if (site.state.trim().length < 2) {
          newErrors[`site_${index}_state`] = 'Nombre de estado inválido';
        }

        // Postal code validation
        if (!site.postal_code.trim()) {
          newErrors[`site_${index}_postal_code`] = 'Código postal es requerido';
        } else if (!validatePostalCode(site.postal_code, site.country)) {
          newErrors[`site_${index}_postal_code`] = `Código postal inválido para ${site.country}`;
        }
      });
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const nextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    setCurrentStep(currentStep - 1);
    setErrors({});
  };

  const addSite = () => {
    setWizardData({
      ...wizardData,
      sites: [...wizardData.sites, {
        name: '',
        address: '',
        city: '',
        state: '',
        country: 'México',
        postal_code: ''
      }]
    });
  };

  const removeSite = (index: number) => {
    if (wizardData.sites.length > 1) {
      const newSites = wizardData.sites.filter((_, i) => i !== index);
      setWizardData({ ...wizardData, sites: newSites });
    }
  };

  const updateClient = (field: keyof ClientData, value: string | string[]) => {
    setWizardData({
      ...wizardData,
      client: { ...wizardData.client, [field]: value }
    });
  };

  const updateAdminUser = (field: keyof AdminUserData, value: string) => {
    setWizardData({
      ...wizardData,
      admin_user: { ...wizardData.admin_user, [field]: value }
    });
  };

  const updateSite = (index: number, field: keyof SiteData, value: string | number) => {
    const newSites = [...wizardData.sites];
    newSites[index] = { ...newSites[index], [field]: value };
    setWizardData({ ...wizardData, sites: newSites });
  };

  const submitWizard = async () => {
    if (!validateStep(3)) return;

    setLoading(true);
    try {
      // Prepare data for API
      const apiData = {
        client: {
          ...wizardData.client,
          allowed_emails: wizardData.client.allowed_emails.filter(email => email.trim())
        },
        admin_user: {
          name: wizardData.admin_user.name,
          email: wizardData.admin_user.email,
          password: wizardData.admin_user.password,
          role: wizardData.admin_user.role,
          phone: wizardData.admin_user.phone
        },
        sites: wizardData.sites
      };

      console.log('Submitting wizard data:', apiData);

      const response = await apiService.post('/clients/wizard', apiData);

      if (response.success) {
        console.log('✅ Client wizard completed:', response.data);
        navigate('/clients', {
          state: {
            message: `Cliente "${wizardData.client.name}" creado exitosamente con workflow MSP completo`
          }
        });
      } else {
        console.error('Wizard failed:', response.error);

        // Handle specific validation errors
        if (response.details && typeof response.details === 'object') {
          const newErrors: Record<string, string> = {};

          // Map backend errors to frontend field names
          if (response.details.name) {
            newErrors.client_name = response.details.name;
          }
          if (response.details.email) {
            newErrors.client_email = response.details.email;
          }
          if (response.details.admin_email) {
            newErrors.admin_email = response.details.admin_email;
          }
          if (response.details.general) {
            newErrors.general = response.details.general;
          }

          // If we have specific errors, use them; otherwise use general error
          if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
          } else {
            setErrors({ general: response.error || 'Error al crear el cliente' });
          }
        } else {
          setErrors({ general: response.error || 'Error al crear el cliente' });
        }
      }
    } catch (error) {
      console.error('Error submitting wizard:', error);
      setErrors({ general: 'Error interno del servidor' });
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Información del Cliente</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre de la Organización *
                  </label>
                  <input
                    type="text"
                    value={wizardData.client.name}
                    onChange={(e) => updateClient('name', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.client_name ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Ej: Empresa ABC S.A. de C.V."
                  />
                  {errors.client_name && (
                    <p className="mt-1 text-sm text-red-600">{errors.client_name}</p>
                  )}
                  <div className="mt-1 text-xs text-gray-500">
                    El nombre debe ser único en el sistema
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Principal *
                  </label>
                  <input
                    type="email"
                    value={wizardData.client.email}
                    onChange={(e) => updateClient('email', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.client_email ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="contacto@empresa.com"
                  />
                  {errors.client_email && (
                    <p className="mt-1 text-sm text-red-600">{errors.client_email}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    RFC
                  </label>
                  <input
                    type="text"
                    value={wizardData.client.rfc}
                    onChange={(e) => updateClient('rfc', e.target.value.toUpperCase())}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.client_rfc ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="ABC123456789"
                    maxLength={13}
                  />
                  {errors.client_rfc && (
                    <p className="mt-1 text-sm text-red-600">{errors.client_rfc}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Teléfono *
                  </label>
                  <input
                    type="tel"
                    value={wizardData.client.phone}
                    onChange={(e) => updateClient('phone', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.client_phone ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="5512345678 o +52 55 1234 5678"
                  />
                  {errors.client_phone && (
                    <p className="mt-1 text-sm text-red-600">{errors.client_phone}</p>
                  )}
                  <div className="mt-1 text-xs text-gray-500">
                    10 dígitos para México o formato internacional con +código país
                  </div>
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Dirección *
                  </label>
                  <input
                    type="text"
                    value={wizardData.client.address}
                    onChange={(e) => updateClient('address', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.client_address ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Av. Principal 123, Col. Centro"
                  />
                  {errors.client_address && (
                    <p className="mt-1 text-sm text-red-600">{errors.client_address}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ciudad *
                  </label>
                  <input
                    type="text"
                    value={wizardData.client.city}
                    onChange={(e) => updateClient('city', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.client_city ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Ciudad de México"
                  />
                  {errors.client_city && (
                    <p className="mt-1 text-sm text-red-600">{errors.client_city}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Estado *
                  </label>
                  <StateSelector
                    country={wizardData.client.country}
                    value={wizardData.client.state}
                    onChange={(state) => updateClient('state', state)}
                    error={!!errors.client_state}
                  />
                  {errors.client_state && (
                    <p className="mt-1 text-sm text-red-600">{errors.client_state}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    País
                  </label>
                  <CountrySelector
                    value={wizardData.client.country}
                    onChange={(country) => updateClient('country', country)}
                    error={!!errors.client_country}
                  />
                  {errors.client_country && (
                    <p className="mt-1 text-sm text-red-600">{errors.client_country}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Código Postal *
                  </label>
                  <input
                    type="text"
                    value={wizardData.client.postal_code}
                    onChange={(e) => updateClient('postal_code', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.client_postal_code ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="01000"
                  />
                  {errors.client_postal_code && (
                    <p className="mt-1 text-sm text-red-600">{errors.client_postal_code}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Usuario Administrador Principal</h3>
              <p className="text-sm text-gray-600 mb-6">
                Este usuario será el administrador principal del cliente y podrá gestionar todos los aspectos de la organización.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre Completo *
                  </label>
                  <input
                    type="text"
                    value={wizardData.admin_user.name}
                    onChange={(e) => updateAdminUser('name', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.admin_name ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Juan Pérez García"
                  />
                  {errors.admin_name && (
                    <p className="mt-1 text-sm text-red-600">{errors.admin_name}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    value={wizardData.admin_user.email}
                    onChange={(e) => updateAdminUser('email', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.admin_email ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="admin@empresa.com"
                  />
                  {errors.admin_email && (
                    <p className="mt-1 text-sm text-red-600">{errors.admin_email}</p>
                  )}
                  <div className="mt-1 text-xs text-gray-500">
                    El email debe ser único en el sistema
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Contraseña *
                  </label>
                  <input
                    type="password"
                    value={wizardData.admin_user.password}
                    onChange={(e) => updateAdminUser('password', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.admin_password ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Mínimo 8 caracteres, mayúscula, minúscula, número y símbolo"
                  />
                  {errors.admin_password && (
                    <p className="mt-1 text-sm text-red-600">{errors.admin_password}</p>
                  )}
                  <div className="mt-1 text-xs text-gray-500">
                    Debe contener: mayúscula, minúscula, número y carácter especial
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Confirmar Contraseña *
                  </label>
                  <input
                    type="password"
                    value={wizardData.admin_user.confirmPassword}
                    onChange={(e) => updateAdminUser('confirmPassword', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.admin_confirmPassword ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Repetir contraseña"
                  />
                  {errors.admin_confirmPassword && (
                    <p className="mt-1 text-sm text-red-600">{errors.admin_confirmPassword}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Rol
                  </label>
                  <select
                    value={wizardData.admin_user.role}
                    onChange={(e) => updateAdminUser('role', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="client_admin">Administrador de Cliente</option>
                    <option value="solicitante">Solicitante</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Teléfono
                  </label>
                  <input
                    type="tel"
                    value={wizardData.admin_user.phone}
                    onChange={(e) => updateAdminUser('phone', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.admin_phone ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="+52 55 1234 5678"
                  />
                  {errors.admin_phone && (
                    <p className="mt-1 text-sm text-red-600">{errors.admin_phone}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Sitios del Cliente</h3>
              <p className="text-sm text-gray-600 mb-6">
                Configura las ubicaciones físicas del cliente. Se requiere al menos un sitio.
              </p>

              {wizardData.sites.map((site, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-6 space-y-4">
                  <div className="flex justify-between items-center">
                    <h4 className="text-md font-medium text-gray-900">
                      Sitio {index + 1}
                    </h4>
                    {wizardData.sites.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeSite(index)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Eliminar Sitio
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Nombre del Sitio *
                      </label>
                      <input
                        type="text"
                        value={site.name}
                        onChange={(e) => updateSite(index, 'name', e.target.value)}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                          errors[`site_${index}_name`] ? 'border-red-500' : 'border-gray-300'
                        }`}
                        placeholder="Oficina Principal, Sucursal Norte, etc."
                      />
                      {errors[`site_${index}_name`] && (
                        <p className="mt-1 text-sm text-red-600">{errors[`site_${index}_name`]}</p>
                      )}
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Dirección *
                      </label>
                      <input
                        type="text"
                        value={site.address}
                        onChange={(e) => updateSite(index, 'address', e.target.value)}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                          errors[`site_${index}_address`] ? 'border-red-500' : 'border-gray-300'
                        }`}
                        placeholder="Av. Principal 123, Col. Centro"
                      />
                      {errors[`site_${index}_address`] && (
                        <p className="mt-1 text-sm text-red-600">{errors[`site_${index}_address`]}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Ciudad *
                      </label>
                      <input
                        type="text"
                        value={site.city}
                        onChange={(e) => updateSite(index, 'city', e.target.value)}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                          errors[`site_${index}_city`] ? 'border-red-500' : 'border-gray-300'
                        }`}
                        placeholder="Ciudad de México"
                      />
                      {errors[`site_${index}_city`] && (
                        <p className="mt-1 text-sm text-red-600">{errors[`site_${index}_city`]}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Estado *
                      </label>
                      <StateSelector
                        country={site.country}
                        value={site.state}
                        onChange={(state) => updateSite(index, 'state', state)}
                        error={!!errors[`site_${index}_state`]}
                      />
                      {errors[`site_${index}_state`] && (
                        <p className="mt-1 text-sm text-red-600">{errors[`site_${index}_state`]}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        País *
                      </label>
                      <CountrySelector
                        value={site.country}
                        onChange={(country) => updateSite(index, 'country', country)}
                        error={!!errors[`site_${index}_country`]}
                      />
                      {errors[`site_${index}_country`] && (
                        <p className="mt-1 text-sm text-red-600">{errors[`site_${index}_country`]}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Código Postal *
                      </label>
                      <input
                        type="text"
                        value={site.postal_code}
                        onChange={(e) => updateSite(index, 'postal_code', e.target.value)}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                          errors[`site_${index}_postal_code`] ? 'border-red-500' : 'border-gray-300'
                        }`}
                        placeholder="01000"
                      />
                      {errors[`site_${index}_postal_code`] && (
                        <p className="mt-1 text-sm text-red-600">{errors[`site_${index}_postal_code`]}</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}

              <button
                type="button"
                onClick={addSite}
                className="w-full py-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-500 hover:text-blue-600 transition-colors"
              >
                + Agregar Otro Sitio
              </button>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Confirmación</h3>
              <p className="text-sm text-gray-600 mb-6">
                Revisa la información antes de crear el cliente con el workflow MSP completo.
              </p>

              {/* Client Summary */}
              <div className="bg-gray-50 p-4 rounded-lg mb-4">
                <h4 className="font-medium text-gray-900 mb-2">Cliente</h4>
                <p className="text-sm text-gray-600">
                  <strong>{wizardData.client.name}</strong><br />
                  {wizardData.client.email}<br />
                  {wizardData.client.city && wizardData.client.state && `${wizardData.client.city}, ${wizardData.client.state}`}
                </p>
              </div>

              {/* Admin User Summary */}
              <div className="bg-gray-50 p-4 rounded-lg mb-4">
                <h4 className="font-medium text-gray-900 mb-2">Administrador Principal</h4>
                <p className="text-sm text-gray-600">
                  <strong>{wizardData.admin_user.name}</strong><br />
                  {wizardData.admin_user.email}<br />
                  Rol: {wizardData.admin_user.role === 'client_admin' ? 'Administrador de Cliente' : 'Solicitante'}
                </p>
              </div>

              {/* Sites Summary */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Sitios ({wizardData.sites.length})</h4>
                {wizardData.sites.map((site, index) => (
                  <div key={index} className="text-sm text-gray-600 mb-2">
                    <strong>{site.name}</strong><br />
                    {site.address}, {site.city}, {site.state}, {site.country}
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Crear Nuevo Cliente</h1>
        <p className="text-gray-600">Wizard de creación MSP: Cliente → Admin → Sitios → Confirmación</p>
      </div>

      {/* Progress Steps */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <nav aria-label="Progress">
          <ol className="flex items-center">
            {steps.map((step, stepIdx) => (
              <li key={step.id} className={`relative ${stepIdx !== steps.length - 1 ? 'pr-8 sm:pr-20' : ''}`}>
                <div className="flex items-center">
                  <div className={`relative flex h-8 w-8 items-center justify-center rounded-full ${
                    step.id < currentStep 
                      ? 'bg-blue-600' 
                      : step.id === currentStep 
                        ? 'bg-blue-600' 
                        : 'bg-gray-300'
                  }`}>
                    {step.id < currentStep ? (
                      <Check className="h-5 w-5 text-white" />
                    ) : (
                      <step.icon className={`h-5 w-5 ${
                        step.id === currentStep ? 'text-white' : 'text-gray-500'
                      }`} />
                    )}
                  </div>
                  <div className="ml-4 min-w-0">
                    <p className={`text-sm font-medium ${
                      step.id <= currentStep ? 'text-blue-600' : 'text-gray-500'
                    }`}>
                      {step.name}
                    </p>
                    <p className="text-sm text-gray-500">{step.description}</p>
                  </div>
                </div>
                {stepIdx !== steps.length - 1 && (
                  <div className="absolute top-4 left-4 -ml-px mt-0.5 h-full w-0.5 bg-gray-300" />
                )}
              </li>
            ))}
          </ol>
        </nav>
      </div>

      {/* Step Content */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        {renderStepContent()}

        {/* Error Messages */}
        {errors.general && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <p className="text-sm text-red-800">{errors.general}</p>
              </div>
            </div>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="mt-8 flex justify-between">
          <button
            type="button"
            onClick={currentStep === 1 ? () => navigate('/clients') : prevStep}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            {currentStep === 1 ? 'Cancelar' : 'Anterior'}
          </button>

          {currentStep < 4 ? (
            <button
              type="button"
              onClick={nextStep}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700"
            >
              Siguiente
              <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          ) : (
            <button
              type="button"
              onClick={submitWizard}
              disabled={loading}
              className="inline-flex items-center px-6 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? 'Creando...' : 'Crear Cliente'}
              <Check className="w-4 h-4 ml-2" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ClientCreate;
