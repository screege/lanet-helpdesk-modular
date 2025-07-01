import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import DashboardLayout from '@/components/layout/DashboardLayout';
import Login from '@/pages/Login';
import Dashboard from '@/pages/Dashboard';
import ClientList from '@/pages/clients/ClientList';
import ClientCreate from '@/pages/clients/ClientCreate';
import ClientDetail from '@/pages/clients/ClientDetail';
import ClientEdit from '@/pages/clients/ClientEdit';
import SitesManagement from '@/pages/sites/SitesManagement';
import UsersManagement from '@/pages/users/UsersManagement';
import './App.css';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />

            {/* Protected routes with layout */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              {/* Nested routes that will render inside the layout */}
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="tickets" element={<div className="p-6">Tickets - En desarrollo</div>} />
              <Route path="tickets/new" element={<div className="p-6">Crear Ticket - En desarrollo</div>} />
              <Route path="clients" element={<ClientList />} />
              <Route path="clients/create" element={<ClientCreate />} />
              <Route path="clients/:clientId" element={<ClientDetail />} />
              <Route path="clients/:clientId/edit" element={<ClientEdit />} />
              <Route path="users" element={<UsersManagement />} />
              <Route path="sites" element={<SitesManagement />} />
              <Route path="reports" element={<div className="p-6">Reportes - En desarrollo</div>} />
              <Route path="profile" element={<div className="p-6">Mi Perfil - En desarrollo</div>} />
              <Route path="knowledge-base" element={<div className="p-6">Base de Conocimiento - En desarrollo</div>} />

              {/* Admin routes */}
              <Route path="admin/categories" element={<div className="p-6">Categorías - En desarrollo</div>} />
              <Route path="admin/sla-management" element={<div className="p-6">Gestión SLA - En desarrollo</div>} />
              <Route path="admin/email-config" element={<div className="p-6">Configuración Email - En desarrollo</div>} />
              <Route path="admin/system-config" element={<div className="p-6">Configuración Sistema - En desarrollo</div>} />
              <Route path="email-templates" element={<div className="p-6">Plantillas Email - En desarrollo</div>} />

              {/* Default redirect */}
              <Route index element={<Navigate to="/dashboard" replace />} />
            </Route>

            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;
