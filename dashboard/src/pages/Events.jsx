import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Filter, 
  Search, 
  RefreshCw, 
  Eye, 
  AlertTriangle, 
  Shield, 
  Clock,
  Wifi,
  WifiOff
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { apiService, wsService } from '../services/api';
import { format } from 'date-fns';

const Events = () => {
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [wsConnected, setWsConnected] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const eventTypes = ['all', 'system_scan', 'anomaly_detected', 'threat_detected', 'user_activity'];
  const statusTypes = ['all', 'normal', 'anomaly', 'warning'];

  useEffect(() => {
    loadEvents();
    setupWebSocket();

    if (autoRefresh) {
      const interval = setInterval(loadEvents, 10000); // Refresh every 10 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  useEffect(() => {
    filterEvents();
  }, [events, searchTerm, selectedType, selectedStatus]);

  const loadEvents = async () => {
    try {
      setLoading(true);
      const data = await apiService.getEvents(100);
      setEvents(data);
    } catch (error) {
      console.error('Failed to load events:', error);
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocket = () => {
    wsService.connect();
    
    wsService.subscribe('connection', (data) => {
      setWsConnected(data.status === 'connected');
    });
    
    wsService.subscribe('message', (data) => {
      // Add new event to the top of the list
      setEvents(prev => [data, ...prev.slice(0, 99)]);
    });
  };

  const filterEvents = () => {
    let filtered = events;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(event => 
        event.agent_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.event_type?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by event type
    if (selectedType !== 'all') {
      filtered = filtered.filter(event => event.event_type === selectedType);
    }

    // Filter by status
    if (selectedStatus !== 'all') {
      filtered = filtered.filter(event => {
        if (selectedStatus === 'anomaly') return event.is_anomaly;
        if (selectedStatus === 'normal') return !event.is_anomaly;
        if (selectedStatus === 'warning') return event.severity === 'warning';
        return true;
      });
    }

    setFilteredEvents(filtered);
  };

  const getEventIcon = (eventType) => {
    switch (eventType) {
      case 'system_scan':
        return <Activity className="w-4 h-4" />;
      case 'anomaly_detected':
        return <AlertTriangle className="w-4 h-4" />;
      case 'threat_detected':
        return <Shield className="w-4 h-4" />;
      case 'user_activity':
        return <Clock className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  const getEventColor = (eventType) => {
    switch (eventType) {
      case 'system_scan':
        return 'text-primary-400';
      case 'anomaly_detected':
        return 'text-danger-400';
      case 'threat_detected':
        return 'text-warning-400';
      case 'user_activity':
        return 'text-success-400';
      default:
        return 'text-gray-400';
    }
  };

  const EventCard = ({ event, index }) => (
    <motion.div
      key={event.id || index}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className={`card hover:border-primary-500 transition-all duration-300 ${
        event.is_anomaly ? 'border-l-4 border-l-danger-500' : ''
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4">
          <div className={`p-2 rounded-lg bg-dark-700 ${getEventColor(event.event_type)}`}>
            {getEventIcon(event.event_type)}
          </div>
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <h4 className="font-semibold text-white">{event.event_type}</h4>
              <span className={`status-indicator ${event.is_anomaly ? 'status-offline' : 'status-online'}`}>
                {event.is_anomaly ? 'Anomaly' : 'Normal'}
              </span>
            </div>
            <p className="text-sm text-gray-400 mb-2">
              Agent: <span className="text-white">{event.agent_id}</span>
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-400">CPU:</span>
                <span className="text-white ml-1">
                  {event.cpu_percent ? `${event.cpu_percent.toFixed(1)}%` : 'N/A'}
                </span>
              </div>
              <div>
                <span className="text-gray-400">Memory:</span>
                <span className="text-white ml-1">
                  {event.memory_percent ? `${event.memory_percent.toFixed(1)}%` : 'N/A'}
                </span>
              </div>
              <div>
                <span className="text-gray-400">Processes:</span>
                <span className="text-white ml-1">
                  {event.process_count || 'N/A'}
                </span>
              </div>
              <div>
                <span className="text-gray-400">Connections:</span>
                <span className="text-white ml-1">
                  {event.network_connections || 'N/A'}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-400">
            {format(new Date(event.timestamp), 'HH:mm:ss')}
          </p>
          <p className="text-xs text-gray-500">
            {format(new Date(event.timestamp), 'MMM dd, yyyy')}
          </p>
        </div>
      </div>
    </motion.div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Real-time Events</h1>
          <p className="text-gray-400">Live system events and monitoring data</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm">
            {wsConnected ? (
              <Wifi className="w-4 h-4 text-success-400" />
            ) : (
              <WifiOff className="w-4 h-4 text-danger-400" />
            )}
            <span className={wsConnected ? 'text-success-400' : 'text-danger-400'}>
              {wsConnected ? 'Live' : 'Offline'}
            </span>
          </div>
          <button
            onClick={loadEvents}
            disabled={loading}
            className="btn-secondary text-sm"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col lg:flex-row lg:items-center space-y-4 lg:space-y-0 lg:space-x-6">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search events..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          {/* Event Type Filter */}
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {eventTypes.map(type => (
                <option key={type} value={type}>
                  {type === 'all' ? 'All Types' : type.replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div className="flex items-center space-x-2">
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {statusTypes.map(status => (
                <option key={status} value={status}>
                  {status === 'all' ? 'All Status' : status.charAt(0).toUpperCase() + status.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Auto Refresh Toggle */}
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="autoRefresh"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="w-4 h-4 text-primary-600 bg-dark-700 border-dark-600 rounded focus:ring-primary-500"
            />
            <label htmlFor="autoRefresh" className="text-sm text-gray-400">
              Auto refresh
            </label>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="text-center">
            <p className="text-2xl font-bold text-white">{filteredEvents.length}</p>
            <p className="text-sm text-gray-400">Total Events</p>
          </div>
        </div>
        <div className="card">
          <div className="text-center">
            <p className="text-2xl font-bold text-danger-400">
              {filteredEvents.filter(e => e.is_anomaly).length}
            </p>
            <p className="text-sm text-gray-400">Anomalies</p>
          </div>
        </div>
        <div className="card">
          <div className="text-center">
            <p className="text-2xl font-bold text-primary-400">
              {new Set(filteredEvents.map(e => e.agent_id)).size}
            </p>
            <p className="text-sm text-gray-400">Active Agents</p>
          </div>
        </div>
        <div className="card">
          <div className="text-center">
            <p className="text-2xl font-bold text-success-400">
              {filteredEvents.filter(e => !e.is_anomaly).length}
            </p>
            <p className="text-sm text-gray-400">Normal Events</p>
          </div>
        </div>
      </div>

      {/* Events List */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="loading-spinner"></div>
            <span className="ml-3 text-gray-400">Loading events...</span>
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="card text-center py-12">
            <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-white mb-2">No events found</h3>
            <p className="text-gray-400">Try adjusting your filters or search terms</p>
          </div>
        ) : (
          <AnimatePresence>
            {filteredEvents.map((event, index) => (
              <EventCard key={event.id || index} event={event} index={index} />
            ))}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
};

export default Events; 