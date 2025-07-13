import React, { useEffect, useState } from 'react';
import { apiService } from '@/services/api';
import { ApiResponse } from '@/types';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LineChart,
  Line,
  ResponsiveContainer
} from 'recharts';

interface ChartData {
  tickets_by_status: Array<{
    name: string;
    value: number;
    status: string;
  }>;
  tickets_trend: Array<{
    date: string;
    creados: number;
    resueltos: number;
  }>;
  sla_compliance: {
    overall: number;
    response: number;
    resolution: number;
    total_tickets: number;
  };
  priority_distribution: Array<{
    priority: string;
    total: number;
    abiertos: number;
    cerrados: number;
  }>;
  technician_performance?: Array<{
    name: string;
    asignados: number;
    resueltos: number;
    tiempo_promedio: number;
  }>;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658'];

const DashboardCharts: React.FC = () => {
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadChartData();
  }, []);

  const loadChartData = async () => {
    try {
      const response = await apiService.get('/dashboard/charts') as ApiResponse<ChartData>;
      if (response.success) {
        setChartData(response.data);
      }
    } catch (error) {
      console.error('Error loading chart data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white p-6 rounded-lg shadow animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!chartData) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No se pudieron cargar los datos de los gráficos</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Tickets by Status - Pie Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Tickets por Estado</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData.tickets_by_status}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.tickets_by_status.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Tickets Trend - Line Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Tendencia de Tickets (30 días)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData.tickets_trend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="creados" 
              stroke="#8884d8" 
              name="Creados"
              strokeWidth={2}
            />
            <Line 
              type="monotone" 
              dataKey="resueltos" 
              stroke="#82ca9d" 
              name="Resueltos"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* SLA Compliance - Gauge-like display */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Cumplimiento SLA</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">General</span>
            <span className="text-2xl font-bold text-blue-600">{chartData.sla_compliance.overall}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-blue-600 h-3 rounded-full transition-all duration-300"
              style={{ width: `${chartData.sla_compliance.overall}%` }}
            ></div>
          </div>
          
          <div className="grid grid-cols-2 gap-4 mt-6">
            <div className="text-center">
              <div className="text-lg font-semibold text-green-600">{chartData.sla_compliance.response}%</div>
              <div className="text-sm text-gray-500">Respuesta</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-orange-600">{chartData.sla_compliance.resolution}%</div>
              <div className="text-sm text-gray-500">Resolución</div>
            </div>
          </div>
          
          <div className="text-center text-sm text-gray-500 mt-4">
            Basado en {chartData.sla_compliance.total_tickets} tickets resueltos
          </div>
        </div>
      </div>

      {/* Priority Distribution - Bar Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Distribución por Prioridad</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData.priority_distribution}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="priority" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="abiertos" fill="#FF8042" name="Abiertos" />
            <Bar dataKey="cerrados" fill="#00C49F" name="Cerrados" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Technician Performance - Bar Chart (Admin only) */}
      {chartData.technician_performance && chartData.technician_performance.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow lg:col-span-2">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Rendimiento de Técnicos (30 días)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData.technician_performance}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="asignados" fill="#8884d8" name="Asignados" />
              <Bar dataKey="resueltos" fill="#82ca9d" name="Resueltos" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default DashboardCharts;
