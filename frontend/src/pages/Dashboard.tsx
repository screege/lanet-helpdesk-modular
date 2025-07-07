import React, { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import {
  Ticket,
  Clock,
  Users,
  Building2,
  AlertTriangle,
  CheckCircle,
  Plus,
  Activity,
} from 'lucide-react';

interface DashboardStats {
  total_tickets: number;
  open_tickets: number;
  assigned_tickets: number;
  resolved_tickets: number;
  overdue_tickets: number;
  sla_compliance: number;
  total_clients?: number;
  total_users?: number;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    total_tickets: 0,
    open_tickets: 0,
    assigned_tickets: 0,
    resolved_tickets: 0,
    overdue_tickets: 0,
    sla_compliance: 0,
    total_clients: 0,
    total_users: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Load real dashboard stats from backend
      const response = await apiService.get('/dashboard/stats');

      if (response.success) {
        const realStats: DashboardStats = {
          total_tickets: response.data.total_tickets || 0,
          open_tickets: response.data.open_tickets || 0,
          assigned_tickets: response.data.assigned_tickets || 0,
          resolved_tickets: response.data.resolved_tickets || 0,
          overdue_tickets: response.data.overdue_tickets || 0,
          sla_compliance: response.data.sla_compliance || 0,
          total_clients: response.data.total_clients,
          total_users: response.data.total_users,
          client_users: response.data.client_users,
          client_sites: response.data.client_sites,
        };

        setStats(realStats);
        console.log('✅ Dashboard loaded with real data:', realStats);
      } else {
        console.error('Failed to load dashboard stats:', response.error);
        // Fallback to empty stats
        setStats({
          total_tickets: 0,
          open_tickets: 0,
          assigned_tickets: 0,
          resolved_tickets: 0,
          overdue_tickets: 0,
          sla_compliance: 0
        });
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      // Fallback to empty stats
      setStats({
        total_tickets: 0,
        open_tickets: 0,
        assigned_tickets: 0,
        resolved_tickets: 0,
        overdue_tickets: 0,
        sla_compliance: 0
      });
    } finally {
      setLoading(false);
    }
  };

  const getRoleDisplayName = (role: string): string => {
    const roleNames: { [key: string]: string } = {
      superadmin: 'Super Administrador',
      admin: 'Administrador',
      technician: 'Técnico',
      client_admin: 'Administrador de Cliente',
      solicitante: 'Solicitante',
    };
    return roleNames[role] || role;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-lanet-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Panel Principal</h1>
        <p className="mt-1 text-sm text-gray-600">
          Bienvenido de vuelta, {user?.name}. Aquí tienes un resumen de tu actividad.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Acciones Rápidas</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <button className="flex items-center p-4 bg-lanet-blue-50 rounded-lg hover:bg-lanet-blue-100 transition-colors">
              <Plus className="h-8 w-8 text-lanet-blue-600" />
              <div className="ml-3 text-left">
                <p className="text-sm font-medium text-gray-900">Crear Ticket</p>
                <p className="text-xs text-gray-500">Nuevo ticket de soporte</p>
              </div>
            </button>

            {(user?.role === 'superadmin' || user?.role === 'admin') && (
              <>
                <button className="flex items-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
                  <Users className="h-8 w-8 text-green-600" />
                  <div className="ml-3 text-left">
                    <p className="text-sm font-medium text-gray-900">Nuevo Usuario</p>
                    <p className="text-xs text-gray-500">Agregar usuario</p>
                  </div>
                </button>

                <button className="flex items-center p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
                  <Building2 className="h-8 w-8 text-purple-600" />
                  <div className="ml-3 text-left">
                    <p className="text-sm font-medium text-gray-900">Nuevo Cliente</p>
                    <p className="text-xs text-gray-500">Agregar organización</p>
                  </div>
                </button>
              </>
            )}

            <button className="flex items-center p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors">
              <Activity className="h-8 w-8 text-orange-600" />
              <div className="ml-3 text-left">
                <p className="text-sm font-medium text-gray-900">Ver Reportes</p>
                <p className="text-xs text-gray-500">Análisis y métricas</p>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Ticket className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Tickets</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.total_tickets}</dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <span className="font-medium text-green-600">+12%</span>
              <span className="text-gray-500"> vs mes anterior</span>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Clock className="h-6 w-6 text-yellow-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Tickets Abiertos</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.open_tickets}</dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <span className="font-medium text-yellow-600">{stats.assigned_tickets} asignados</span>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircle className="h-6 w-6 text-green-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Resueltos</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.resolved_tickets}</dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <span className="font-medium text-green-600">{stats.sla_compliance}%</span>
              <span className="text-gray-500"> cumplimiento SLA</span>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <AlertTriangle className="h-6 w-6 text-red-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Vencidos</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.overdue_tickets}</dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <span className="font-medium text-red-600">Requieren atención</span>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Stats for Admins */}
      {(user?.role === 'superadmin' || user?.role === 'admin') && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Building2 className="h-6 w-6 text-purple-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Clientes</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.total_clients}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Users className="h-6 w-6 text-blue-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Usuarios</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.total_users}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Actividad Reciente</h3>
          <div className="flow-root">
            <ul className="-mb-8">
              <li>
                <div className="relative pb-8">
                  <div className="relative flex space-x-3">
                    <div>
                      <span className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center ring-8 ring-white">
                        <CheckCircle className="h-5 w-5 text-white" />
                      </span>
                    </div>
                    <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                      <div>
                        <p className="text-sm text-gray-500">
                          Ticket <span className="font-medium text-gray-900">#TKT-000123</span> resuelto
                        </p>
                      </div>
                      <div className="text-right text-sm whitespace-nowrap text-gray-500">
                        <time>Hace 2 horas</time>
                      </div>
                    </div>
                  </div>
                </div>
              </li>

              <li>
                <div className="relative pb-8">
                  <div className="relative flex space-x-3">
                    <div>
                      <span className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center ring-8 ring-white">
                        <Plus className="h-5 w-5 text-white" />
                      </span>
                    </div>
                    <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                      <div>
                        <p className="text-sm text-gray-500">
                          Nuevo ticket <span className="font-medium text-gray-900">#TKT-000124</span> creado
                        </p>
                      </div>
                      <div className="text-right text-sm whitespace-nowrap text-gray-500">
                        <time>Hace 4 horas</time>
                      </div>
                    </div>
                  </div>
                </div>
              </li>

              <li>
                <div className="relative">
                  <div className="relative flex space-x-3">
                    <div>
                      <span className="h-8 w-8 rounded-full bg-purple-500 flex items-center justify-center ring-8 ring-white">
                        <Users className="h-5 w-5 text-white" />
                      </span>
                    </div>
                    <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                      <div>
                        <p className="text-sm text-gray-500">
                          Nuevo usuario <span className="font-medium text-gray-900">María García</span> registrado
                        </p>
                      </div>
                      <div className="text-right text-sm whitespace-nowrap text-gray-500">
                        <time>Hace 6 horas</time>
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
