import React, { useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { LoginCredentials } from '@/types';

const Login: React.FC = () => {
  const { login, isAuthenticated, loading } = useAuth();
  const location = useLocation();
  const [credentials, setCredentials] = useState<LoginCredentials>({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Redirect if already authenticated
  if (isAuthenticated) {
    const from = location.state?.from?.pathname || '/dashboard';
    return <Navigate to={from} replace />;
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCredentials(prev => ({
      ...prev,
      [name]: value,
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: { [key: string]: string } = {};

    if (!credentials.email.trim()) {
      newErrors.email = 'El correo electrónico es requerido';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(credentials.email)) {
      newErrors.email = 'Formato de correo electrónico inválido';
    }

    if (!credentials.password.trim()) {
      newErrors.password = 'La contraseña es requerida';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      const result = await login(credentials);
      
      if (!result.success) {
        setErrors({
          general: result.error || 'Error de autenticación',
        });
      }
    } catch (error) {
      setErrors({
        general: 'Error de conexión. Por favor, intente nuevamente.',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-lanet-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-16 w-16 flex items-center justify-center bg-lanet-blue-600 rounded-full">
            <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            LANET Helpdesk V3
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Inicia sesión en tu cuenta
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email" className="sr-only">
                Correo electrónico
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className={`appearance-none rounded-none relative block w-full px-3 py-2 border ${
                  errors.email ? 'border-red-300' : 'border-gray-300'
                } placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-lanet-blue-500 focus:border-lanet-blue-500 focus:z-10 sm:text-sm`}
                placeholder="Correo electrónico"
                value={credentials.email}
                onChange={handleInputChange}
                disabled={isSubmitting}
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email}</p>
              )}
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Contraseña
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className={`appearance-none rounded-none relative block w-full px-3 py-2 border ${
                  errors.password ? 'border-red-300' : 'border-gray-300'
                } placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-lanet-blue-500 focus:border-lanet-blue-500 focus:z-10 sm:text-sm`}
                placeholder="Contraseña"
                value={credentials.password}
                onChange={handleInputChange}
                disabled={isSubmitting}
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password}</p>
              )}
            </div>
          </div>

          {errors.general && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">
                    {errors.general}
                  </h3>
                </div>
              </div>
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-lanet-blue-600 hover:bg-lanet-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-lanet-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Iniciando sesión...
                </div>
              ) : (
                'Iniciar sesión'
              )}
            </button>
          </div>

          <div className="text-center space-y-4">
            {/* Demo Credentials - 4 Roles Only (Blueprint Compliant) */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Credenciales Demo:</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => setCredentials({ email: 'ba@lanet.mx', password: 'TestAdmin123!' })}
                  className="text-left p-2 bg-white rounded border hover:bg-gray-50 transition-colors"
                  disabled={isSubmitting}
                >
                  <div className="font-medium text-purple-600">Super Admin</div>
                  <div className="text-gray-500">ba@lanet.mx</div>
                </button>
                <button
                  type="button"
                  onClick={() => setCredentials({ email: 'tech@test.com', password: 'TestTech123!' })}
                  className="text-left p-2 bg-white rounded border hover:bg-gray-50 transition-colors"
                  disabled={isSubmitting}
                >
                  <div className="font-medium text-blue-600">Técnico</div>
                  <div className="text-gray-500">tech@test.com</div>
                </button>
                <button
                  type="button"
                  onClick={() => setCredentials({ email: 'prueba@prueba.com', password: 'Poikl55+*' })}
                  className="text-left p-2 bg-white rounded border hover:bg-gray-50 transition-colors"
                  disabled={isSubmitting}
                >
                  <div className="font-medium text-green-600">Admin Cliente</div>
                  <div className="text-gray-500">prueba@prueba.com</div>
                  <div className="text-xs text-gray-400">Industrias Tebi</div>
                </button>
                <button
                  type="button"
                  onClick={() => setCredentials({ email: 'prueba3@prueba.com', password: 'Poikl55+*' })}
                  className="text-left p-2 bg-white rounded border hover:bg-gray-50 transition-colors"
                  disabled={isSubmitting}
                >
                  <div className="font-medium text-gray-600">Solicitante</div>
                  <div className="text-gray-500">prueba3@prueba.com</div>
                  <div className="text-xs text-gray-400">Industrias Tebi</div>
                </button>
              </div>
            </div>

            <a
              href="#"
              className="font-medium text-lanet-blue-600 hover:text-lanet-blue-500"
              onClick={(e) => {
                e.preventDefault();
                // TODO: Implement forgot password
                alert('Funcionalidad de recuperación de contraseña próximamente');
              }}
            >
              ¿Olvidaste tu contraseña?
            </a>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;
