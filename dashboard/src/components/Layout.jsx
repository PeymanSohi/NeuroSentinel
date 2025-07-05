import React, { useState } from 'react';
import { 
  Brain, 
  Activity, 
  Shield, 
  AlertTriangle, 
  BarChart3, 
  Settings, 
  Menu, 
  X,
  Wifi,
  WifiOff,
  Bell,
  User
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Layout = ({ children, activePage, wsStatus = 'connecting' }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigation = [
    { name: 'Dashboard', href: '/', icon: BarChart3, current: activePage === 'dashboard' },
    { name: 'Real-time Events', href: '/events', icon: Activity, current: activePage === 'events' },
    { name: 'Anomaly Detection', href: '/anomalies', icon: AlertTriangle, current: activePage === 'anomalies' },
    { name: 'ML Models', href: '/models', icon: Brain, current: activePage === 'models' },
    { name: 'Threat Intelligence', href: '/threats', icon: Shield, current: activePage === 'threats' },
    { name: 'System Health', href: '/health', icon: Activity, current: activePage === 'health' },
    { name: 'Settings', href: '/settings', icon: Settings, current: activePage === 'settings' },
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected':
        return 'text-success-400';
      case 'connecting':
        return 'text-warning-400';
      case 'disconnected':
      case 'failed':
        return 'text-danger-400';
      default:
        return 'text-gray-400';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
        return <Wifi className="w-4 h-4" />;
      case 'connecting':
        return <Wifi className="w-4 h-4 animate-pulse" />;
      case 'disconnected':
      case 'failed':
        return <WifiOff className="w-4 h-4" />;
      default:
        return <WifiOff className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-dark-900">
      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.div
        initial={{ x: -300 }}
        animate={{ x: sidebarOpen ? 0 : -300 }}
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-dark-800 border-r border-dark-700 lg:translate-x-0 lg:static lg:inset-0 transition-transform duration-300 ease-in-out`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-dark-700">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-white">NeuroSentinel</h1>
                <p className="text-xs text-gray-400">Cyber Defense Platform</p>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-1 rounded-md text-gray-400 hover:text-white hover:bg-dark-700"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className={`flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200 ${
                  item.current
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-300 hover:bg-dark-700 hover:text-white'
                }`}
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.name}
              </a>
            ))}
          </nav>

          {/* Status */}
          <div className="p-4 border-t border-dark-700">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">Connection</span>
              <div className={`flex items-center space-x-1 ${getStatusColor(wsStatus)}`}>
                {getStatusIcon(wsStatus)}
                <span className="capitalize">{wsStatus}</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Header */}
        <header className="bg-dark-800 border-b border-dark-700 h-16 flex items-center justify-between px-6">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-md text-gray-400 hover:text-white hover:bg-dark-700"
            >
              <Menu className="w-5 h-5" />
            </button>
            <h2 className="text-xl font-semibold text-white">
              {navigation.find(item => item.current)?.name || 'Dashboard'}
            </h2>
          </div>

          <div className="flex items-center space-x-4">
            {/* Notifications */}
            <button className="p-2 rounded-md text-gray-400 hover:text-white hover:bg-dark-700 relative">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-danger-500 rounded-full"></span>
            </button>

            {/* User menu */}
            <button className="flex items-center space-x-2 p-2 rounded-md text-gray-400 hover:text-white hover:bg-dark-700">
              <User className="w-5 h-5" />
              <span className="text-sm font-medium">Admin</span>
            </button>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout; 