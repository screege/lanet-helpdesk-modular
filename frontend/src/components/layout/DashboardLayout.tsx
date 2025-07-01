import React, { useState } from 'react';
import { Link, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import {
  Home,
  Ticket,
  Building2,
  Users,
  Settings,
  Clock,
  Mail,
  Shield,
  UserCircle,
  Plus,
  MapPin,
  BarChart3,
  BookOpen,
  Menu,
  X,
  ChevronDown,
  ChevronRight,
  LogOut,
  Bell,
  Search,
} from 'lucide-react';

interface NavItem {
  name: string;
  href?: string;
  icon: React.ComponentType<any>;
  permission?: string | null;
  submenu?: NavItem[];
}

const DashboardLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [expandedMenus, setExpandedMenus] = useState<string[]>(['Configuración']);
  const [showUserDropdown, setShowUserDropdown] = useState(false);

  const handleLogout = async () => {
    await logout();
  };

  const isCurrentPath = (path: string): boolean => {
    return location.pathname === path;
  };

  const toggleSubmenu = (menuName: string) => {
    setExpandedMenus(prev =>
      prev.includes(menuName)
        ? prev.filter(name => name !== menuName)
        : [...prev, menuName]
    );
  };

  // Role-based navigation
  const getNavigationForRole = (): NavItem[] => {
    const baseNavigation: NavItem[] = [
      {
        name: 'Panel Principal',
        href: '/dashboard',
        icon: Home,
        permission: null,
      },
    ];

    if (user?.role === 'superadmin' || user?.role === 'admin' || user?.role === 'technician') {
      // Admin and Technician navigation
      return [
        ...baseNavigation,
        {
          name: 'Tickets',
          href: '/tickets',
          icon: Ticket,
          permission: 'tickets.read',
        },
        {
          name: 'Clientes',
          href: '/clients',
          icon: Building2,
          permission: 'clients.read',
        },
        {
          name: 'Usuarios',
          href: '/users',
          icon: Users,
          permission: 'users.read',
        },
        {
          name: 'Configuración',
          icon: Settings,
          permission: null,
          submenu: user?.role === 'superadmin' || user?.role === 'admin' ? [
            {
              name: 'Categorías y Subcategorías',
              href: '/admin/categories',
              icon: Settings,
              permission: 'admin.categories',
            },
            {
              name: 'Gestión de SLA',
              href: '/admin/sla-management',
              icon: Clock,
              permission: 'manage_sla',
            },
            {
              name: 'Plantillas de Email',
              href: '/email-templates',
              icon: Mail,
              permission: 'manage_notifications',
            },
            {
              name: 'Configuración de Email',
              href: '/admin/email-config',
              icon: Mail,
              permission: 'system.configure',
            },
            {
              name: 'Configuración del Sistema',
              href: '/admin/system-config',
              icon: Shield,
              permission: 'system.configure',
            },
            {
              name: 'Mi Perfil',
              href: '/profile',
              icon: UserCircle,
              permission: null,
            },
          ] : [
            {
              name: 'Mi Perfil',
              href: '/profile',
              icon: UserCircle,
              permission: null,
            },
          ],
        },
      ];
    } else if (user?.role === 'client_admin') {
      // Client Admin Portal Navigation
      return [
        ...baseNavigation,
        {
          name: 'Crear Ticket',
          href: '/tickets/new',
          icon: Plus,
          permission: null,
        },
        {
          name: 'Mi Organización',
          href: `/clients/${user.client_id}`,
          icon: Building2,
          permission: null,
        },
        {
          name: 'Sitios',
          href: '/sites',
          icon: MapPin,
          permission: null,
        },
        {
          name: 'Usuarios',
          href: '/users',
          icon: Users,
          permission: null,
        },
        {
          name: 'Tickets',
          href: '/tickets',
          icon: Ticket,
          permission: null,
        },
        {
          name: 'Reportes',
          href: '/reports',
          icon: BarChart3,
          permission: null,
        },
        {
          name: 'Mi Perfil',
          href: '/profile',
          icon: UserCircle,
          permission: null,
        },
      ];
    } else if (user?.role === 'solicitante') {
      // Solicitante Self-Service Portal Navigation
      return [
        ...baseNavigation,
        {
          name: 'Crear Ticket',
          href: '/tickets/new',
          icon: Plus,
          permission: null,
        },
        {
          name: 'Mis Tickets',
          href: '/tickets',
          icon: Ticket,
          permission: null,
        },
        {
          name: 'Mis Sitios',
          href: '/sites',
          icon: MapPin,
          permission: null,
        },
        {
          name: 'Base de Conocimiento',
          href: '/knowledge-base',
          icon: BookOpen,
          permission: null,
        },
        {
          name: 'Mi Perfil',
          href: '/profile',
          icon: UserCircle,
          permission: null,
        },
      ];
    }

    // Default navigation for unknown roles
    return baseNavigation;
  };

  const navigation = getNavigationForRole();

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

  return (
    <div className="h-screen flex overflow-hidden bg-gray-100">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 flex z-40 md:hidden ${sidebarOpen ? '' : 'hidden'}`}>
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
        <div className="relative flex-1 flex flex-col max-w-xs w-full bg-white">
          <div className="absolute top-0 right-0 -mr-12 pt-2">
            <button
              className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="h-6 w-6 text-white" />
            </button>
          </div>
          <SidebarContent
            navigation={navigation}
            isCurrentPath={isCurrentPath}
            user={user}
            expandedMenus={expandedMenus}
            toggleSubmenu={toggleSubmenu}
          />
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden md:flex md:flex-shrink-0">
        <div className="flex flex-col w-64">
          <SidebarContent
            navigation={navigation}
            isCurrentPath={isCurrentPath}
            user={user}
            expandedMenus={expandedMenus}
            toggleSubmenu={toggleSubmenu}
          />
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-col w-0 flex-1 overflow-hidden">
        {/* Top navigation */}
        <div className="relative z-10 flex-shrink-0 flex h-16 bg-white shadow">
          <button
            className="px-4 border-r border-gray-200 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-lanet-blue-500 md:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </button>
          
          <div className="flex-1 px-4 flex justify-between">
            <div className="flex-1 flex">
              <div className="w-full flex md:ml-0">
                <label htmlFor="search-field" className="sr-only">
                  Buscar
                </label>
                <div className="relative w-full text-gray-400 focus-within:text-gray-600">
                  <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                    <Search className="h-5 w-5" />
                  </div>
                  <input
                    id="search-field"
                    className="block w-full h-full pl-8 pr-3 py-2 border-transparent text-gray-900 placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-0 focus:border-transparent"
                    placeholder="Buscar tickets, clientes, usuarios..."
                    type="search"
                  />
                </div>
              </div>
            </div>
            
            <div className="ml-4 flex items-center md:ml-6">
              {/* Notifications */}
              <button className="bg-white p-1 rounded-full text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-lanet-blue-500">
                <Bell className="h-6 w-6" />
              </button>

              {/* Profile dropdown */}
              <div className="ml-3 relative">
                <div>
                  <button
                    className="max-w-xs bg-white flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-lanet-blue-500"
                    onClick={() => setShowUserDropdown(!showUserDropdown)}
                  >
                    <div className="h-8 w-8 rounded-full bg-lanet-blue-600 flex items-center justify-center">
                      <span className="text-sm font-medium text-white">
                        {user?.name?.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div className="ml-3 text-left">
                      <p className="text-sm font-medium text-gray-700">{user?.name}</p>
                      <p className="text-xs text-gray-500">{getRoleDisplayName(user?.role || '')}</p>
                    </div>
                  </button>
                </div>

                {showUserDropdown && (
                  <div className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 focus:outline-none">
                    <Link
                      to="/profile"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setShowUserDropdown(false)}
                    >
                      <UserCircle className="mr-3 h-4 w-4 text-gray-400" />
                      Mi Perfil
                    </Link>

                    <div className="border-t border-gray-100"></div>

                    <button
                      onClick={() => {
                        setShowUserDropdown(false);
                        handleLogout();
                      }}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                    >
                      <LogOut className="mr-3 h-4 w-4 text-gray-400" />
                      Cerrar Sesión
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1 relative overflow-y-auto focus:outline-none">
          <div className="py-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

interface SidebarContentProps {
  navigation: NavItem[];
  isCurrentPath: (path: string) => boolean;
  user: any;
  expandedMenus: string[];
  toggleSubmenu: (menuName: string) => void;
}

const SidebarContent: React.FC<SidebarContentProps> = ({
  navigation,
  isCurrentPath,
  expandedMenus,
  toggleSubmenu,
}) => {
  return (
    <div className="flex flex-col h-0 flex-1 border-r border-gray-200 bg-white">
      {/* Logo */}
      <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
        <div className="flex items-center flex-shrink-0 px-4">
          <div className="flex items-center">
            <Shield className="h-8 w-8 text-lanet-blue-600" />
            <div className="ml-3">
              <h1 className="text-lg font-semibold text-gray-900">LANET Helpdesk V3</h1>
              <p className="text-xs text-gray-500">LANET Systems</p>
            </div>
          </div>
        </div>
        
        {/* Navigation */}
        <nav className="mt-8 flex-1 px-2 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;

            // Handle submenu items
            if (item.submenu) {
              const isExpanded = expandedMenus.includes(item.name);

              return (
                <div key={item.name}>
                  <button
                    onClick={() => toggleSubmenu(item.name)}
                    className="w-full flex items-center justify-between px-2 py-2 text-sm font-medium rounded-md text-gray-600 hover:bg-gray-50 hover:text-gray-900 group"
                  >
                    <div className="flex items-center">
                      <Icon className="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500" />
                      {item.name}
                    </div>
                    {isExpanded ? (
                      <ChevronDown className="h-4 w-4" />
                    ) : (
                      <ChevronRight className="h-4 w-4" />
                    )}
                  </button>

                  {isExpanded && (
                    <div className="ml-6 mt-1 space-y-1">
                      {item.submenu.map((subItem) => {
                        const SubIcon = subItem.icon;
                        const current = subItem.href ? isCurrentPath(subItem.href) : false;

                        return (
                          <Link
                            key={subItem.name}
                            to={subItem.href || '#'}
                            className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                              current
                                ? 'bg-lanet-blue-100 text-lanet-blue-900'
                                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                            }`}
                          >
                            <SubIcon className={`mr-3 h-4 w-4 ${
                              current ? 'text-lanet-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                            }`} />
                            {subItem.name}
                          </Link>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            }

            // Regular navigation items
            const current = item.href ? isCurrentPath(item.href) : false;

            return (
              <Link
                key={item.name}
                to={item.href || '#'}
                className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                  current
                    ? 'bg-lanet-blue-100 text-lanet-blue-900'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon className={`mr-3 h-5 w-5 ${
                  current ? 'text-lanet-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                }`} />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
};

export default DashboardLayout;
