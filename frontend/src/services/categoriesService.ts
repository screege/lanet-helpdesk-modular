import { apiService } from './api';

export interface Category {
  category_id: string;
  parent_id?: string;
  name: string;
  description?: string;
  color: string;
  icon: string;
  is_active: boolean;
  sort_order: number;
  auto_assign_to?: string;
  auto_assign_to_name?: string;
  sla_response_hours: number;
  sla_resolution_hours: number;
  created_at: string;
  updated_at: string;
  children?: Category[];
  full_name?: string;
  full_path?: string;
  parent_name?: string;
  level?: number;
  direct_ticket_count?: number;
  total_ticket_count?: number;
  subcategory_count?: number;
  ticket_count?: number;
  expanded?: boolean; // For UI tree state
}

export interface CreateCategoryData {
  parent_id?: string;
  name: string;
  description?: string;
  color?: string;
  icon?: string;
  sort_order?: number;
  auto_assign_to?: string;
  sla_response_hours?: number;
  sla_resolution_hours?: number;
}

export interface UpdateCategoryData {
  parent_id?: string;
  name?: string;
  description?: string;
  color?: string;
  icon?: string;
  is_active?: boolean;
  sort_order?: number;
  auto_assign_to?: string;
  sla_response_hours?: number;
  sla_resolution_hours?: number;
}

export interface MoveCategoryData {
  new_parent_id?: string;
  new_sort_order?: number;
}

export interface ReorderCategoryData {
  sibling_orders: Array<{
    category_id: string;
    sort_order: number;
  }>;
}

class CategoriesService {
  async getCategories() {
    try {
      const response = await apiService.get('/categories/');
      return response;
    } catch (error: any) {
      console.error('Error fetching categories:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch categories');
    }
  }

  async getCategoriesTree() {
    try {
      const response = await apiService.get('/categories/tree');
      return response;
    } catch (error: any) {
      console.error('Error fetching categories tree:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch categories tree');
    }
  }

  async getCategoriesFlat() {
    try {
      const response = await apiService.get('/categories/flat');
      return response;
    } catch (error: any) {
      console.error('Error fetching flat categories:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch categories');
    }
  }

  // Alias for consistency
  async getFlatCategories() {
    return this.getCategoriesFlat();
  }

  async getCategoryById(categoryId: string) {
    try {
      const response = await apiService.get(`/categories/${categoryId}`);
      return response;
    } catch (error: any) {
      console.error('Error fetching category:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch category');
    }
  }

  async createCategory(categoryData: CreateCategoryData) {
    try {
      const response = await apiService.post('/categories/', categoryData);
      return response;
    } catch (error: any) {
      console.error('Error creating category:', error);
      throw new Error(error.response?.data?.message || 'Failed to create category');
    }
  }

  async updateCategory(categoryId: string, categoryData: UpdateCategoryData) {
    try {
      const response = await apiService.put(`/categories/${categoryId}`, categoryData);
      return response;
    } catch (error: any) {
      console.error('Error updating category:', error);
      throw new Error(error.response?.data?.message || 'Failed to update category');
    }
  }

  async deleteCategory(categoryId: string) {
    try {
      const response = await apiService.delete(`/categories/${categoryId}`);
      return response;
    } catch (error: any) {
      console.error('Error deleting category:', error);
      throw new Error(error.response?.data?.message || 'Failed to delete category');
    }
  }

  async moveCategory(categoryId: string, moveData: MoveCategoryData) {
    try {
      const response = await apiService.post(`/categories/${categoryId}/move`, moveData);
      return response;
    } catch (error: any) {
      console.error('Error moving category:', error);
      throw new Error(error.response?.data?.message || 'Failed to move category');
    }
  }

  async reorderCategories(categoryId: string, reorderData: ReorderCategoryData) {
    try {
      const response = await apiService.post(`/categories/${categoryId}/reorder`, reorderData);
      return response;
    } catch (error: any) {
      console.error('Error reordering categories:', error);
      throw new Error(error.response?.data?.message || 'Failed to reorder categories');
    }
  }

  async searchCategories(searchTerm: string) {
    try {
      const response = await apiService.get(`/categories/search?q=${encodeURIComponent(searchTerm)}`);
      return response;
    } catch (error: any) {
      console.error('Error searching categories:', error);
      throw new Error(error.response?.data?.message || 'Failed to search categories');
    }
  }

  // Helper methods
  getIconOptions() {
    return [
      { value: 'monitor', label: '🖥️ Monitor', icon: 'monitor' },
      { value: 'code', label: '💻 Código', icon: 'code' },
      { value: 'wifi', label: '📶 WiFi', icon: 'wifi' },
      { value: 'shield', label: '🛡️ Escudo', icon: 'shield' },
      { value: 'plus-circle', label: '➕ Más', icon: 'plus-circle' },
      { value: 'folder', label: '📁 Carpeta', icon: 'folder' },
      { value: 'settings', label: '⚙️ Configuración', icon: 'settings' },
      { value: 'database', label: '🗄️ Base de datos', icon: 'database' },
      { value: 'server', label: '🖥️ Servidor', icon: 'server' },
      { value: 'smartphone', label: '📱 Móvil', icon: 'smartphone' },
      { value: 'printer', label: '🖨️ Impresora', icon: 'printer' },
      { value: 'mail', label: '📧 Email', icon: 'mail' },
      { value: 'phone', label: '📞 Teléfono', icon: 'phone' },
      { value: 'users', label: '👥 Usuarios', icon: 'users' },
      { value: 'key', label: '🔑 Acceso', icon: 'key' },
      { value: 'alert-triangle', label: '⚠️ Alerta', icon: 'alert-triangle' },
      { value: 'tool', label: '🔧 Herramienta', icon: 'tool' },
      { value: 'bug', label: '🐛 Error', icon: 'bug' },
      { value: 'help-circle', label: '❓ Ayuda', icon: 'help-circle' },
      { value: 'file-text', label: '📄 Documento', icon: 'file-text' }
    ];
  }

  getColorOptions() {
    return [
      { value: '#EF4444', label: 'Rojo', color: '#EF4444' },
      { value: '#F59E0B', label: 'Naranja', color: '#F59E0B' },
      { value: '#EAB308', label: 'Amarillo', color: '#EAB308' },
      { value: '#10B981', label: 'Verde', color: '#10B981' },
      { value: '#3B82F6', label: 'Azul', color: '#3B82F6' },
      { value: '#8B5CF6', label: 'Púrpura', color: '#8B5CF6' },
      { value: '#EC4899', label: 'Rosa', color: '#EC4899' },
      { value: '#6B7280', label: 'Gris', color: '#6B7280' },
      { value: '#1F2937', label: 'Negro', color: '#1F2937' },
      { value: '#DC2626', label: 'Rojo Oscuro', color: '#DC2626' },
      { value: '#059669', label: 'Verde Oscuro', color: '#059669' },
      { value: '#1D4ED8', label: 'Azul Oscuro', color: '#1D4ED8' }
    ];
  }

  getPriorityColors() {
    return {
      'critica': '#DC2626',
      'alta': '#F59E0B', 
      'media': '#10B981',
      'baja': '#6B7280'
    };
  }

  // Utility function to build category tree from flat array
  buildCategoryTree(categories: Category[]): Category[] {
    const categoryMap = new Map<string, Category>();
    const rootCategories: Category[] = [];

    // First pass: create map and initialize children arrays
    categories.forEach(category => {
      category.children = [];
      categoryMap.set(category.category_id, category);
    });

    // Second pass: build tree structure
    categories.forEach(category => {
      if (category.parent_id) {
        const parent = categoryMap.get(category.parent_id);
        if (parent) {
          parent.children!.push(category);
        }
      } else {
        rootCategories.push(category);
      }
    });

    return rootCategories;
  }

  // Utility function to flatten category tree
  flattenCategoryTree(categories: Category[]): Category[] {
    const result: Category[] = [];

    const flatten = (cats: Category[], level = 0, parentPath = '') => {
      cats.forEach(category => {
        const flatCategory = { ...category };
        const currentPath = parentPath ? `${parentPath} > ${category.name}` : category.name;
        flatCategory.full_name = level > 0 ? `${'  '.repeat(level)}${category.name}` : category.name;
        flatCategory.full_path = currentPath;
        flatCategory.level = level;
        result.push(flatCategory);

        if (category.children && category.children.length > 0) {
          flatten(category.children, level + 1, currentPath);
        }
      });
    };

    flatten(categories);
    return result;
  }

  // Find category by ID in tree structure
  findCategoryInTree(categories: Category[], categoryId: string): Category | null {
    for (const category of categories) {
      if (category.category_id === categoryId) {
        return category;
      }
      if (category.children && category.children.length > 0) {
        const found = this.findCategoryInTree(category.children, categoryId);
        if (found) return found;
      }
    }
    return null;
  }

  // Get all parent categories for a given category
  getCategoryPath(categories: Category[], categoryId: string): Category[] {
    const path: Category[] = [];

    const findPath = (cats: Category[], targetId: string, currentPath: Category[]): boolean => {
      for (const category of cats) {
        const newPath = [...currentPath, category];

        if (category.category_id === targetId) {
          path.push(...newPath);
          return true;
        }

        if (category.children && category.children.length > 0) {
          if (findPath(category.children, targetId, newPath)) {
            return true;
          }
        }
      }
      return false;
    };

    findPath(categories, categoryId, []);
    return path;
  }

  // Check if moving a category would create a circular reference
  wouldCreateCircularReference(categories: Category[], categoryId: string, newParentId: string): boolean {
    const category = this.findCategoryInTree(categories, categoryId);
    if (!category) return false;

    // Check if newParentId is a descendant of categoryId
    const isDescendant = (cats: Category[], targetId: string): boolean => {
      for (const cat of cats) {
        if (cat.category_id === targetId) return true;
        if (cat.children && this.isDescendant(cat.children, targetId)) return true;
      }
      return false;
    };

    return category.children ? isDescendant(category.children, newParentId) : false;
  }

  // Get category statistics
  getCategoryStats(category: Category): { directTickets: number; totalTickets: number; subcategories: number } {
    return {
      directTickets: category.direct_ticket_count || 0,
      totalTickets: category.total_ticket_count || 0,
      subcategories: category.subcategory_count || 0
    };
  }

  // Filter categories by search term
  filterCategoriesBySearch(categories: Category[], searchTerm: string): Category[] {
    if (!searchTerm.trim()) return categories;

    const term = searchTerm.toLowerCase();
    const filtered: Category[] = [];

    const filterRecursive = (cats: Category[]): Category[] => {
      const result: Category[] = [];

      for (const category of cats) {
        const matches =
          category.name.toLowerCase().includes(term) ||
          category.description?.toLowerCase().includes(term) ||
          category.full_path?.toLowerCase().includes(term);

        let filteredChildren: Category[] = [];
        if (category.children && category.children.length > 0) {
          filteredChildren = filterRecursive(category.children);
        }

        if (matches || filteredChildren.length > 0) {
          result.push({
            ...category,
            children: filteredChildren,
            expanded: true // Auto-expand matching categories
          });
        }
      }

      return result;
    };

    return filterRecursive(categories);
  }

  // Toggle category expansion state
  toggleCategoryExpansion(categories: Category[], categoryId: string): Category[] {
    return categories.map(category => {
      if (category.category_id === categoryId) {
        return { ...category, expanded: !category.expanded };
      }
      if (category.children && category.children.length > 0) {
        return {
          ...category,
          children: this.toggleCategoryExpansion(category.children, categoryId)
        };
      }
      return category;
    });
  }

  // Expand all categories
  expandAllCategories(categories: Category[]): Category[] {
    return categories.map(category => ({
      ...category,
      expanded: true,
      children: category.children ? this.expandAllCategories(category.children) : []
    }));
  }

  // Collapse all categories
  collapseAllCategories(categories: Category[]): Category[] {
    return categories.map(category => ({
      ...category,
      expanded: false,
      children: category.children ? this.collapseAllCategories(category.children) : []
    }));
  }
}

export const categoriesService = new CategoriesService();
