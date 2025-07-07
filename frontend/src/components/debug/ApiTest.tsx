import React, { useState } from 'react';
import { apiService } from '../../services/api';

const ApiTest: React.FC = () => {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const testUsersAPI = async () => {
    setLoading(true);
    try {
      console.log('Testing users API...');
      const response = await apiService.get('/users?per_page=1000');
      console.log('API Response:', response);
      setResult(response);
    } catch (error) {
      console.error('API Error:', error);
      setResult({ error: error instanceof Error ? error.message : 'Unknown error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 border rounded-lg bg-gray-50">
      <h3 className="text-lg font-bold mb-4">API Test Component</h3>
      
      <button
        onClick={testUsersAPI}
        disabled={loading}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Testing...' : 'Test Users API'}
      </button>

      {result && (
        <div className="mt-4">
          <h4 className="font-semibold">Result:</h4>
          <pre className="bg-white p-2 rounded border text-xs overflow-auto max-h-96">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default ApiTest;
