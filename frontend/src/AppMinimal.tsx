import React from 'react';

const AppMinimal: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">App Mínima</h1>
        <p className="text-gray-600 mb-4">
          Esta es una versión completamente mínima de la aplicación sin ningún import que pueda causar problemas.
        </p>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="text-green-800 font-medium mb-2">✅ Test de Aislamiento</h3>
          <p className="text-green-700 text-sm">
            Si esta página se carga sin diálogos de error, el problema está en algún import específico.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AppMinimal;
