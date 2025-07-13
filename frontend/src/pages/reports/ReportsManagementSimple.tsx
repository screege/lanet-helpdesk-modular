import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';

const ReportsManagementSimple: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'templates' | 'configurations' | 'executions' | 'schedules' | 'enterprise'>('configurations');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Gestión de Reportes - Versión Simple</h2>
          <p className="text-gray-600">Sistema de reportes sin funcionalidades complejas para debugging</p>
        </div>
      </div>

      {/* Debug Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-blue-800 font-medium mb-2">🔍 Debug Information</h3>
        <div className="text-sm text-blue-700 space-y-1">
          <p>Usuario: {user?.name} ({user?.role})</p>
          <p>Tab activo: {activeTab}</p>
          <p>Estado: Componente simple sin APIs</p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { key: 'templates', label: 'Plantillas' },
            { key: 'configurations', label: 'Configuraciones' },
            { key: 'executions', label: 'Ejecuciones' },
            { key: 'schedules', label: 'Programación' },
            { key: 'enterprise', label: 'Reportes Empresariales' }
          ].map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setActiveTab(key as any)}
              className={`${
                activeTab === key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm transition-colors`}
            >
              {label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="bg-white rounded-lg shadow p-6">
        {activeTab === 'templates' && (
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Plantillas de Reportes</h3>
            <p className="text-gray-600">Funcionalidad temporalmente simplificada</p>
          </div>
        )}

        {activeTab === 'configurations' && (
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Configuraciones de Reportes</h3>
            <p className="text-gray-600">Funcionalidad temporalmente simplificada</p>
          </div>
        )}

        {activeTab === 'executions' && (
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Ejecuciones de Reportes</h3>
            <p className="text-gray-600">Funcionalidad temporalmente simplificada</p>
          </div>
        )}

        {activeTab === 'schedules' && (
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Programación de Reportes</h3>
            <p className="text-gray-600">Funcionalidad temporalmente simplificada</p>
          </div>
        )}

        {activeTab === 'enterprise' && (
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Reportes Empresariales</h3>
            <p className="text-gray-600 mb-6">
              Sistema de reportes empresariales con 25+ columnas de datos reales
            </p>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 max-w-md mx-auto">
              <h4 className="text-green-800 font-medium mb-2">✅ Backend Funcionando</h4>
              <ul className="text-sm text-green-700 space-y-1 text-left">
                <li>• API endpoints operativos</li>
                <li>• 25+ columnas empresariales</li>
                <li>• Datos reales de la base de datos</li>
                <li>• Autenticación JWT funcionando</li>
                <li>• Consultas SQL optimizadas</li>
              </ul>
            </div>
            <p className="text-sm text-gray-500 mt-4">
              Frontend simplificado para debugging
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <p className="text-sm text-gray-600 text-center">
          🔧 Versión simplificada para identificar y resolver problemas de diálogos automáticos
        </p>
      </div>
    </div>
  );
};

export default ReportsManagementSimple;
