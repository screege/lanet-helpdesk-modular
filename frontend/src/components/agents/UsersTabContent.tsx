import React from 'react';
import { Users, Mail, User } from 'lucide-react';

interface UserData {
  user_id: string;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
}

interface UsersTabContentProps {
  users: UserData[];
}

const UsersTabContent: React.FC<UsersTabContentProps> = ({ users }) => {
  const getRoleDisplayName = (role: string) => {
    const roleMap: { [key: string]: string } = {
      'superadmin': 'Super Administrador',
      'technician': 'Técnico',
      'client_admin': 'Administrador Cliente',
      'solicitante': 'Solicitante'
    };
    return roleMap[role] || role.replace('_', ' ');
  };

  const getRoleBadgeColor = (role: string) => {
    const colorMap: { [key: string]: string } = {
      'superadmin': 'bg-purple-100 text-purple-800',
      'technician': 'bg-blue-100 text-blue-800',
      'client_admin': 'bg-green-100 text-green-800',
      'solicitante': 'bg-gray-100 text-gray-800'
    };
    return colorMap[role] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium text-gray-900">Usuarios</h3>
        <div className="text-sm text-gray-500">
          Total: {users.length} usuario{users.length !== 1 ? 's' : ''}
        </div>
      </div>

      {users.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {users.map((user) => (
            <div key={user.user_id} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center">
                    <User className="w-5 h-5 text-gray-400 mr-2" />
                    <h4 className="text-sm font-medium text-gray-900 truncate">{user.name}</h4>
                  </div>
                  
                  <div className="flex items-center mt-2">
                    <Mail className="w-4 h-4 text-gray-400 mr-2" />
                    <p className="text-sm text-gray-600 truncate">{user.email}</p>
                  </div>
                  
                  <div className="mt-3 flex items-center justify-between">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRoleBadgeColor(user.role)}`}>
                      {getRoleDisplayName(user.role)}
                    </span>
                    
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      user.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {user.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Users className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No hay usuarios registrados</h3>
          <p className="mt-1 text-sm text-gray-500">
            No se han encontrado usuarios para este cliente.
          </p>
        </div>
      )}
    </div>
  );
};

export default UsersTabContent;
