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
import TicketsManagement from '@/pages/tickets/TicketsManagement';
import TicketCreatePage from '@/pages/tickets/TicketCreatePage';
import TicketDetailPage from '@/pages/tickets/TicketDetailPage';
import TicketEditPage from '@/pages/tickets/TicketEditPage';
import CategoriesManagement from '@/pages/categories/CategoriesManagement';

import EmailConfigTabs from '@/pages/admin/EmailConfigTabs';
import EmailTemplates from '@/pages/admin/EmailTemplates';
import EmailMonitoring from '@/pages/admin/EmailMonitoring';
import EmailConfigForm from '@/pages/admin/EmailConfigForm';
import SLASimple from '@/pages/admin/SLASimple';
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
              <Route path="tickets" element={<TicketsManagement />} />
              <Route path="tickets/new" element={<TicketCreatePage />} />
              <Route path="tickets/:ticketId" element={<TicketDetailPage />} />
              <Route path="tickets/:ticketId/edit" element={<TicketEditPage />} />
              <Route path="categories" element={<CategoriesManagement />} />
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
              <Route path="admin/sla-management" element={<SLASimple />} />
              <Route path="admin/email-config" element={<EmailConfigTabs />} />
              <Route path="admin/email-config/new" element={<EmailConfigForm />} />
              <Route path="admin/email-config/edit/:id" element={<EmailConfigForm />} />
              <Route path="admin/email-templates" element={<EmailTemplates />} />
              <Route path="admin/email-monitoring" element={<EmailMonitoring />} />
              <Route path="admin/system-config" element={<div className="p-6">Configuración Sistema - En desarrollo</div>} />
              <Route path="email-templates" element={<EmailTemplates />} />

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
