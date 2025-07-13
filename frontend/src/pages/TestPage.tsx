import React from 'react';

const TestPage: React.FC = () => {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-4">Página de Prueba</h1>
      <p className="text-gray-600 mb-4">
        Esta es una página completamente simple sin ningún código que pueda causar errores.
      </p>
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <h3 className="text-green-800 font-medium mb-2">✅ Test Exitoso</h3>
        <p className="text-green-700 text-sm">
          Si esta página se carga sin diálogos de error, significa que el problema está en otro componente específico.
        </p>
      </div>
    </div>
  );
};

export default TestPage;
