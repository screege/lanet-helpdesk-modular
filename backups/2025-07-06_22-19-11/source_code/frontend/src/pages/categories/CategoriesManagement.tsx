import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  FolderTree, 
  Search, 
  Plus, 
  Edit, 
  Trash2, 
  ChevronRight,
  ChevronDown,
  Move,
  MoreVertical,
  Eye,
  Users,
  Ticket,
  Settings,
  Maximize2,
  Minimize2
} from 'lucide-react';
import { categoriesService, Category } from '../../services/categoriesService';
import CategoryForm from '../../components/categories/CategoryForm';
import CategoryDetail from '../../components/categories/CategoryDetail';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ErrorMessage from '../../components/common/ErrorMessage';

const CategoriesManagement: React.FC = () => {
  const { user } = useAuth();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredCategories, setFilteredCategories] = useState<Category[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Check permissions
  const canManageCategories = user?.role === 'superadmin' || user?.role === 'admin';

  // Load categories
  const loadCategories = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await categoriesService.getCategoriesTree();
      const categoriesData = response.data || [];
      
      // Initialize expansion state
      const categoriesWithState = initializeExpansionState(categoriesData);
      setCategories(categoriesWithState);
      setFilteredCategories(categoriesWithState);
    } catch (error: any) {
      console.error('Error loading categories:', error);
      setError(error.message || 'Failed to load categories');
    } finally {
      setLoading(false);
    }
  };

  // Initialize expansion state for categories
  const initializeExpansionState = (cats: Category[]): Category[] => {
    return cats.map(category => ({
      ...category,
      expanded: false, // Start collapsed
      children: category.children ? initializeExpansionState(category.children) : []
    }));
  };

  useEffect(() => {
    loadCategories();
  }, []);

  // Handle search
  useEffect(() => {
    if (searchTerm.trim()) {
      const filtered = categoriesService.filterCategoriesBySearch(categories, searchTerm);
      setFilteredCategories(filtered);
    } else {
      setFilteredCategories(categories);
    }
  }, [searchTerm, categories]);

  // Handle category expansion toggle
  const handleToggleExpansion = (categoryId: string) => {
    const updatedCategories = categoriesService.toggleCategoryExpansion(categories, categoryId);
    setCategories(updatedCategories);
    
    if (!searchTerm.trim()) {
      setFilteredCategories(updatedCategories);
    }
  };

  // Handle expand all
  const handleExpandAll = () => {
    const expandedCategories = categoriesService.expandAllCategories(categories);
    setCategories(expandedCategories);
    setFilteredCategories(expandedCategories);
  };

  // Handle collapse all
  const handleCollapseAll = () => {
    const collapsedCategories = categoriesService.collapseAllCategories(categories);
    setCategories(collapsedCategories);
    setFilteredCategories(collapsedCategories);
  };

  // Handle create category
  const handleCreateCategory = () => {
    setSelectedCategory(null);
    setShowCreateForm(true);
  };

  // Handle edit category
  const handleEditCategory = (category: Category) => {
    setSelectedCategory(category);
    setShowEditForm(true);
  };

  // Handle view category details
  const handleViewCategory = (category: Category) => {
    setSelectedCategory(category);
    setShowDetailModal(true);
  };

  // Handle delete category
  const handleDeleteCategory = async (category: Category) => {
    if (!window.confirm(`¿Está seguro de que desea eliminar la categoría "${category.name}"?`)) {
      return;
    }

    try {
      await categoriesService.deleteCategory(category.category_id);
      await loadCategories(); // Reload to get updated tree
    } catch (error: any) {
      setError(error.message || 'Failed to delete category');
    }
  };

  // Handle form submission
  const handleFormSubmit = async (categoryData: any) => {
    try {
      if (selectedCategory) {
        await categoriesService.updateCategory(selectedCategory.category_id, categoryData);
      } else {
        await categoriesService.createCategory(categoryData);
      }
      await loadCategories(); // Reload to get updated tree
      setShowCreateForm(false);
      setShowEditForm(false);
    } catch (error: any) {
      setError(error.message || 'Failed to save category');
    }
  };

  // Get icon component for category
  const getCategoryIcon = (iconName: string, color: string) => {
    const iconProps = { className: "w-4 h-4", style: { color } };
    
    switch (iconName) {
      case 'monitor': return <Settings {...iconProps} />;
      case 'users': return <Users {...iconProps} />;
      case 'ticket': return <Ticket {...iconProps} />;
      default: return <FolderTree {...iconProps} />;
    }
  };

  // Render category tree node
  const renderCategoryNode = (category: Category, level: number = 0) => {
    const hasChildren = category.children && category.children.length > 0;
    const stats = categoriesService.getCategoryStats(category);
    
    return (
      <div key={category.category_id} className="select-none">
        {/* Category Row */}
        <div 
          className={`flex items-center py-2 px-3 hover:bg-gray-50 border-l-2 transition-colors ${
            level > 0 ? 'ml-6' : ''
          }`}
          style={{ borderLeftColor: category.color }}
        >
          {/* Expansion Toggle */}
          <div className="w-6 flex justify-center">
            {hasChildren ? (
              <button
                onClick={() => handleToggleExpansion(category.category_id)}
                className="p-1 hover:bg-gray-200 rounded transition-colors"
              >
                {category.expanded ? (
                  <ChevronDown className="w-4 h-4 text-gray-600" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-gray-600" />
                )}
              </button>
            ) : (
              <div className="w-4" />
            )}
          </div>

          {/* Category Icon */}
          <div className="mr-3">
            {getCategoryIcon(category.icon, category.color)}
          </div>

          {/* Category Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <h3 className="font-medium text-gray-900 truncate">{category.name}</h3>
              {stats.totalTickets > 0 && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {stats.totalTickets} tickets
                </span>
              )}
              {stats.subcategories > 0 && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  {stats.subcategories} subcategorías
                </span>
              )}
            </div>
            {category.description && (
              <p className="text-sm text-gray-500 truncate mt-1">{category.description}</p>
            )}
          </div>

          {/* SLA Info */}
          <div className="hidden md:flex items-center space-x-4 text-sm text-gray-500">
            <span>Respuesta: {category.sla_response_hours}h</span>
            <span>Resolución: {category.sla_resolution_hours}h</span>
          </div>

          {/* Actions */}
          {canManageCategories && (
            <div className="flex items-center space-x-1 ml-4">
              <button
                onClick={() => handleViewCategory(category)}
                className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                title="Ver detalles"
              >
                <Eye className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleEditCategory(category)}
                className="p-2 text-gray-400 hover:text-yellow-600 hover:bg-yellow-50 rounded transition-colors"
                title="Editar"
              >
                <Edit className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleDeleteCategory(category)}
                className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                title="Eliminar"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        {/* Children */}
        {hasChildren && category.expanded && (
          <div className="ml-4">
            {category.children!.map(child => renderCategoryNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FolderTree className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Gestión de Categorías</h1>
              <p className="text-gray-600">Organiza y administra las categorías de tickets de forma jerárquica</p>
            </div>
          </div>
          {canManageCategories && (
            <button
              onClick={handleCreateCategory}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Plus className="w-4 h-4 mr-2" />
              Nueva Categoría
            </button>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6">
          <ErrorMessage message={error} onClose={() => setError(null)} />
        </div>
      )}

      {/* Search and Controls */}
      <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
        <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Buscar categorías..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Tree Controls */}
          <div className="flex items-center space-x-2">
            <button
              onClick={handleExpandAll}
              className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Maximize2 className="w-4 h-4 mr-2" />
              Expandir Todo
            </button>
            <button
              onClick={handleCollapseAll}
              className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Minimize2 className="w-4 h-4 mr-2" />
              Colapsar Todo
            </button>
          </div>
        </div>
      </div>

      {/* Categories Tree */}
      <div className="bg-white rounded-lg shadow-sm border">
        {filteredCategories.length === 0 ? (
          <div className="text-center py-12">
            <FolderTree className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              {searchTerm ? 'No se encontraron categorías' : 'No hay categorías'}
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm 
                ? 'Intenta con un término de búsqueda diferente.'
                : 'Comienza creando tu primera categoría.'
              }
            </p>
            {!searchTerm && canManageCategories && (
              <div className="mt-6">
                <button
                  onClick={handleCreateCategory}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Nueva Categoría
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredCategories.map(category => renderCategoryNode(category))}
          </div>
        )}
      </div>

      {/* Modals */}
      {showCreateForm && (
        <CategoryForm
          isOpen={showCreateForm}
          onClose={() => setShowCreateForm(false)}
          onSubmit={handleFormSubmit}
          categories={categories}
        />
      )}

      {showEditForm && selectedCategory && (
        <CategoryForm
          isOpen={showEditForm}
          onClose={() => setShowEditForm(false)}
          onSubmit={handleFormSubmit}
          category={selectedCategory}
          categories={categories}
        />
      )}

      {showDetailModal && selectedCategory && (
        <CategoryDetail
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          category={selectedCategory}
          onEdit={() => {
            setShowDetailModal(false);
            setShowEditForm(true);
          }}
          onDelete={() => {
            setShowDetailModal(false);
            handleDeleteCategory(selectedCategory);
          }}
          canManage={canManageCategories}
        />
      )}
    </div>
  );
};

export default CategoriesManagement;
