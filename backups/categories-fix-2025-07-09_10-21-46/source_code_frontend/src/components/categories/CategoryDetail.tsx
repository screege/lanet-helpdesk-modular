import React from 'react';
import { X, Edit, Trash2, Clock, Users, Ticket, FolderTree, Settings } from 'lucide-react';
import { Category, categoriesService } from '../../services/categoriesService';

interface CategoryDetailProps {
  isOpen: boolean;
  onClose: () => void;
  category: Category;
  onEdit: () => void;
  onDelete: () => void;
  canManage: boolean;
}

const CategoryDetail: React.FC<CategoryDetailProps> = ({
  isOpen,
  onClose,
  category,
  onEdit,
  onDelete,
  canManage
}) => {
  if (!isOpen) return null;

  const stats = categoriesService.getCategoryStats(category);

  // Get icon component
  const getCategoryIcon = (iconName: string, color: string) => {
    const iconProps = { className: "w-6 h-6", style: { color } };
    
    switch (iconName) {
      case 'monitor': return <Settings {...iconProps} />;
      case 'users': return <Users {...iconProps} />;
      case 'ticket': return <Ticket {...iconProps} />;
      default: return <FolderTree {...iconProps} />;
    }
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Get priority level based on SLA
  const getPriorityLevel = (responseHours: number) => {
    if (responseHours <= 2) return { level: 'Crítica', color: 'text-red-600', bg: 'bg-red-100' };
    if (responseHours <= 8) return { level: 'Alta', color: 'text-orange-600', bg: 'bg-orange-100' };
    if (responseHours <= 24) return { level: 'Media', color: 'text-yellow-600', bg: 'bg-yellow-100' };
    return { level: 'Baja', color: 'text-green-600', bg: 'bg-green-100' };
  };

  const priority = getPriorityLevel(category.sla_response_hours);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            {getCategoryIcon(category.icon, category.color)}
            <div>
              <h2 className="text-xl font-semibold text-gray-900">{category.name}</h2>
              {category.full_path && (
                <p className="text-sm text-gray-500">{category.full_path}</p>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {canManage && (
              <>
                <button
                  onClick={onEdit}
                  className="p-2 text-gray-400 hover:text-yellow-600 hover:bg-yellow-50 rounded transition-colors"
                  title="Editar categoría"
                >
                  <Edit className="w-5 h-5" />
                </button>
                <button
                  onClick={onDelete}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                  title="Eliminar categoría"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </>
            )}
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Description */}
          {category.description && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Descripción</h3>
              <p className="text-gray-700 bg-gray-50 p-4 rounded-lg">{category.description}</p>
            </div>
          )}

          {/* Statistics */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Estadísticas</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Direct Tickets */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <Ticket className="w-8 h-8 text-blue-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-blue-900">Tickets Directos</p>
                    <p className="text-2xl font-bold text-blue-600">{stats.directTickets}</p>
                  </div>
                </div>
              </div>

              {/* Total Tickets */}
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <FolderTree className="w-8 h-8 text-green-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-green-900">Total (con subcategorías)</p>
                    <p className="text-2xl font-bold text-green-600">{stats.totalTickets}</p>
                  </div>
                </div>
              </div>

              {/* Subcategories */}
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <Settings className="w-8 h-8 text-purple-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-purple-900">Subcategorías</p>
                    <p className="text-2xl font-bold text-purple-600">{stats.subcategories}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* SLA Configuration */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Configuración SLA</h3>
            <div className="bg-gray-50 p-4 rounded-lg space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Response Time */}
                <div className="flex items-center justify-between p-3 bg-white rounded border">
                  <div className="flex items-center">
                    <Clock className="w-5 h-5 text-gray-400 mr-3" />
                    <div>
                      <p className="font-medium text-gray-900">Tiempo de Respuesta</p>
                      <p className="text-sm text-gray-500">Tiempo máximo para primera respuesta</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-gray-900">{category.sla_response_hours}h</p>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${priority.bg} ${priority.color}`}>
                      {priority.level}
                    </span>
                  </div>
                </div>

                {/* Resolution Time */}
                <div className="flex items-center justify-between p-3 bg-white rounded border">
                  <div className="flex items-center">
                    <Settings className="w-5 h-5 text-gray-400 mr-3" />
                    <div>
                      <p className="font-medium text-gray-900">Tiempo de Resolución</p>
                      <p className="text-sm text-gray-500">Tiempo máximo para resolver</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-gray-900">{category.sla_resolution_hours}h</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Auto Assignment */}
          {category.auto_assign_to_name && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Auto-asignación</h3>
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <Users className="w-6 h-6 text-blue-600 mr-3" />
                  <div>
                    <p className="font-medium text-blue-900">Técnico Asignado</p>
                    <p className="text-blue-700">{category.auto_assign_to_name}</p>
                    <p className="text-sm text-blue-600">Los tickets de esta categoría se asignan automáticamente a este técnico</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Visual Settings */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Configuración Visual</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Color */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <div 
                    className="w-8 h-8 rounded-full border-2 border-gray-300 mr-3"
                    style={{ backgroundColor: category.color }}
                  />
                  <div>
                    <p className="font-medium text-gray-900">Color</p>
                    <p className="text-sm text-gray-500 font-mono">{category.color}</p>
                  </div>
                </div>
              </div>

              {/* Icon */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center">
                  {getCategoryIcon(category.icon, category.color)}
                  <div className="ml-3">
                    <p className="font-medium text-gray-900">Icono</p>
                    <p className="text-sm text-gray-500">{category.icon}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Hierarchy Information */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Información de Jerarquía</h3>
            <div className="bg-gray-50 p-4 rounded-lg space-y-3">
              <div className="flex justify-between">
                <span className="text-sm font-medium text-gray-700">Orden de visualización:</span>
                <span className="text-sm text-gray-900">{category.sort_order}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm font-medium text-gray-700">Nivel en jerarquía:</span>
                <span className="text-sm text-gray-900">{category.level || 0}</span>
              </div>
              {category.parent_name && (
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-gray-700">Categoría padre:</span>
                  <span className="text-sm text-gray-900">{category.parent_name}</span>
                </div>
              )}
            </div>
          </div>

          {/* Metadata */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Información del Sistema</h3>
            <div className="bg-gray-50 p-4 rounded-lg space-y-3">
              <div className="flex justify-between">
                <span className="text-sm font-medium text-gray-700">Fecha de creación:</span>
                <span className="text-sm text-gray-900">{formatDate(category.created_at)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm font-medium text-gray-700">Última actualización:</span>
                <span className="text-sm text-gray-900">{formatDate(category.updated_at)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm font-medium text-gray-700">Estado:</span>
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                  category.is_active 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {category.is_active ? 'Activa' : 'Inactiva'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end space-x-3 p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Cerrar
          </button>
          {canManage && (
            <button
              onClick={onEdit}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Edit className="w-4 h-4 mr-2" />
              Editar Categoría
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CategoryDetail;
