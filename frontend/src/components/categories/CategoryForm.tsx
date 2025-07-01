import React, { useState, useEffect } from 'react';
import { X, Save, AlertCircle } from 'lucide-react';
import { Category, CreateCategoryData, UpdateCategoryData, categoriesService } from '../../services/categoriesService';
import { usersService, User } from '../../services/usersService';

interface CategoryFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateCategoryData | UpdateCategoryData) => Promise<void>;
  category?: Category | null;
  categories: Category[];
}

const CategoryForm: React.FC<CategoryFormProps> = ({
  isOpen,
  onClose,
  onSubmit,
  category,
  categories
}) => {
  const [formData, setFormData] = useState({
    parent_id: '',
    name: '',
    description: '',
    color: '#6B7280',
    icon: 'folder',
    sort_order: 0,
    auto_assign_to: '',
    sla_response_hours: 24,
    sla_resolution_hours: 72
  });

  const [technicians, setTechnicians] = useState<User[]>([]);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  // Load technicians for auto-assignment
  useEffect(() => {
    const loadTechnicians = async () => {
      try {
        const response = await usersService.getUsersByRole('technician');
        setTechnicians(response || []);
      } catch (error) {
        console.error('Error loading technicians:', error);
      }
    };

    if (isOpen) {
      loadTechnicians();
    }
  }, [isOpen]);

  // Initialize form data when category changes
  useEffect(() => {
    if (category) {
      setFormData({
        parent_id: category.parent_id || '',
        name: category.name,
        description: category.description || '',
        color: category.color,
        icon: category.icon,
        sort_order: category.sort_order,
        auto_assign_to: category.auto_assign_to || '',
        sla_response_hours: category.sla_response_hours,
        sla_resolution_hours: category.sla_resolution_hours
      });
    } else {
      setFormData({
        parent_id: '',
        name: '',
        description: '',
        color: '#6B7280',
        icon: 'folder',
        sort_order: 0,
        auto_assign_to: '',
        sla_response_hours: 24,
        sla_resolution_hours: 72
      });
    }
    setErrors({});
  }, [category]);

  // Handle input changes
  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  // Validate form
  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'El nombre es requerido';
    }

    if (formData.sla_response_hours < 1) {
      newErrors.sla_response_hours = 'El tiempo de respuesta debe ser mayor a 0';
    }

    if (formData.sla_resolution_hours < 1) {
      newErrors.sla_resolution_hours = 'El tiempo de resolución debe ser mayor a 0';
    }

    if (formData.sla_response_hours > formData.sla_resolution_hours) {
      newErrors.sla_resolution_hours = 'El tiempo de resolución debe ser mayor al tiempo de respuesta';
    }

    // Check for circular reference if editing
    if (category && formData.parent_id) {
      if (formData.parent_id === category.category_id) {
        newErrors.parent_id = 'Una categoría no puede ser padre de sí misma';
      } else if (categoriesService.wouldCreateCircularReference(categories, category.category_id, formData.parent_id)) {
        newErrors.parent_id = 'Esta selección crearía una referencia circular';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      const submitData = {
        ...formData,
        parent_id: formData.parent_id || undefined,
        auto_assign_to: formData.auto_assign_to || undefined
      };

      await onSubmit(submitData);
      onClose();
    } catch (error: any) {
      setErrors({ submit: error.message || 'Error al guardar la categoría' });
    } finally {
      setLoading(false);
    }
  };

  // Get available parent categories (exclude current category and its descendants)
  const getAvailableParents = () => {
    if (!category) return categoriesService.flattenCategoryTree(categories);
    
    const flatCategories = categoriesService.flattenCategoryTree(categories);
    return flatCategories.filter(cat => {
      // Exclude current category
      if (cat.category_id === category.category_id) return false;
      
      // Exclude descendants to prevent circular references
      const categoryPath = categoriesService.getCategoryPath(categories, cat.category_id);
      return !categoryPath.some(pathCat => pathCat.category_id === category.category_id);
    });
  };

  const iconOptions = categoriesService.getIconOptions();
  const colorOptions = categoriesService.getColorOptions();
  const availableParents = getAvailableParents();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {category ? 'Editar Categoría' : 'Nueva Categoría'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Error Message */}
          {errors.submit && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <AlertCircle className="h-5 w-5 text-red-400" />
                <div className="ml-3">
                  <p className="text-sm text-red-800">{errors.submit}</p>
                </div>
              </div>
            </div>
          )}

          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Name */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nombre *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.name ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Nombre de la categoría"
              />
              {errors.name && (
                <p className="mt-1 text-sm text-red-600">{errors.name}</p>
              )}
            </div>

            {/* Parent Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Categoría Padre
              </label>
              <select
                value={formData.parent_id}
                onChange={(e) => handleChange('parent_id', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.parent_id ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value="">Sin categoría padre (raíz)</option>
                {availableParents.map((cat) => (
                  <option key={cat.category_id} value={cat.category_id}>
                    {cat.full_name}
                  </option>
                ))}
              </select>
              {errors.parent_id && (
                <p className="mt-1 text-sm text-red-600">{errors.parent_id}</p>
              )}
            </div>

            {/* Sort Order */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Orden
              </label>
              <input
                type="number"
                value={formData.sort_order}
                onChange={(e) => handleChange('sort_order', parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                min="0"
              />
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Descripción
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Descripción de la categoría"
            />
          </div>

          {/* Visual Settings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Color */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Color
              </label>
              <div className="grid grid-cols-6 gap-2">
                {colorOptions.map((color) => (
                  <button
                    key={color.value}
                    type="button"
                    onClick={() => handleChange('color', color.value)}
                    className={`w-8 h-8 rounded-full border-2 transition-all ${
                      formData.color === color.value 
                        ? 'border-gray-900 scale-110' 
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                    style={{ backgroundColor: color.value }}
                    title={color.label}
                  />
                ))}
              </div>
            </div>

            {/* Icon */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Icono
              </label>
              <select
                value={formData.icon}
                onChange={(e) => handleChange('icon', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {iconOptions.map((icon) => (
                  <option key={icon.value} value={icon.value}>
                    {icon.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* SLA Settings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Response Time */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tiempo de Respuesta (horas) *
              </label>
              <input
                type="number"
                value={formData.sla_response_hours}
                onChange={(e) => handleChange('sla_response_hours', parseInt(e.target.value) || 1)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.sla_response_hours ? 'border-red-500' : 'border-gray-300'
                }`}
                min="1"
              />
              {errors.sla_response_hours && (
                <p className="mt-1 text-sm text-red-600">{errors.sla_response_hours}</p>
              )}
            </div>

            {/* Resolution Time */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tiempo de Resolución (horas) *
              </label>
              <input
                type="number"
                value={formData.sla_resolution_hours}
                onChange={(e) => handleChange('sla_resolution_hours', parseInt(e.target.value) || 1)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.sla_resolution_hours ? 'border-red-500' : 'border-gray-300'
                }`}
                min="1"
              />
              {errors.sla_resolution_hours && (
                <p className="mt-1 text-sm text-red-600">{errors.sla_resolution_hours}</p>
              )}
            </div>
          </div>

          {/* Auto Assignment */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Auto-asignar a Técnico
            </label>
            <select
              value={formData.auto_assign_to}
              onChange={(e) => handleChange('auto_assign_to', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Sin auto-asignación</option>
              {technicians.map((tech) => (
                <option key={tech.user_id} value={tech.user_id}>
                  {tech.name} ({tech.email})
                </option>
              ))}
            </select>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Guardando...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  {category ? 'Actualizar' : 'Crear'} Categoría
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CategoryForm;
