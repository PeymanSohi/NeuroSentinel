import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Shield, 
  AlertTriangle, 
  Brain, 
  Cpu, 
  HardDrive, 
  Wifi, 
  Users,
  TrendingUp,
  TrendingDown,
  Clock,
  Eye
} from 'lucide-react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { motion } from 'framer-motion';
import { apiService, wsService } from '../services/api';
import { format } from 'date-fns';

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    totalEvents: 0,
    anomalies: 0,
    activeAgents: 0,
    systemHealth: 100,
    cpuUsage: 0,
    memoryUsage: 0,
    networkConnections: 0,
    activeProcesses: 0
  });
  const [recentEvents, setRecentEvents] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    setupWebSocket();

    // Refresh data every 30 seconds
    const interval = setInterval(loadDashboardData, 30000);

    return () => {
      clearInterval(interval);
      wsService.disconnect();
    };
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load events
      const events = await apiService.getEvents(10);
      setRecentEvents(events);
      
      // Update metrics
      setMetrics(prev => ({
        ...prev,
        totalEvents: events.length,
        anomalies: events.filter(e => e.is_anomaly).length,
        activeAgents: new Set(events.map(e => e.agent_id)).size,
        cpuUsage: events[0]?.cpu_percent || 0,
        memoryUsage: events[0]?.memory_percent || 0,
        networkConnections: events[0]?.network_connections || 0,
        activeProcesses: events[0]?.process_count || 0
      }));

      // Generate chart data from recent events
      const chartData = events.slice(-20).map((event, index) => ({
        time: format(new Date(event.timestamp), 'HH:mm'),
        cpu: event.cpu_percent || 0,
        memory: event.memory_percent || 0,
        processes: event.process_count || 0,
        connections: event.network_connections || 0
      }));
      setChartData(chartData);

    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocket = () => {
    wsService.connect();
    
    wsService.subscribe('message', (data) => {
      // Update metrics in real-time
      if (data.event_type === 'system_scan') {
        setMetrics(prev => ({
          ...prev,
          totalEvents: prev.totalEvents + 1,
          cpuUsage: data.system?.cpu_percent || prev.cpuUsage,
          memoryUsage: data.system?.memory_percent || prev.memoryUsage,
          networkConnections: data.network?.connections || prev.networkConnections,
          activeProcesses: data.process?.count || prev.activeProcesses
        }));

        // Add to recent events
        setRecentEvents(prev => [data, ...prev.slice(0, 9)]);
      }
    });
  };

  const MetricCard = ({ title, value, icon: Icon, change, changeType = 'neutral', subtitle }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="metric-card"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="metric-label">{title}</p>
          <p className="metric-value">{value}</p>
          {subtitle && <p className="text-sm text-gray-400 mt-1">{subtitle}</p>}
        </div>
        <div className="p-3 bg-primary-600 rounded-lg">
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
      {change && (
        <div className="flex items-center mt-2">
          {changeType === 'positive' ? (
            <TrendingUp className="w-4 h-4 text-success-400 mr-1" />
          ) : changeType === 'negative' ? (
            <TrendingDown className="w-4 h-4 text-danger-400 mr-1" />
          ) : (
            <Clock className="w-4 h-4 text-gray-400 mr-1" />
          )}
          <span className={`text-sm ${changeType === 'positive' ? 'text-success-400' : changeType === 'negative' ? 'text-danger-400' : 'text-gray-400'}`}>
            {change}
          </span>
        </div>
      )}
    </motion.div>
  );

  const COLORS = ['#0ea5e9', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner"></div>
        <span className="ml-3 text-gray-400">Loading dashboard...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">System Overview</h1>
          <p className="text-gray-400">Real-time monitoring and analytics</p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-400">
          <div className="w-2 h-2 bg-success-400 rounded-full animate-pulse"></div>
          <span>Live</span>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Events"
          value={metrics.totalEvents.toLocaleString()}
          icon={Activity}
          change="+12%"
          changeType="positive"
          subtitle="Last 24 hours"
        />
        <MetricCard
          title="Anomalies Detected"
          value={metrics.anomalies}
          icon={AlertTriangle}
          change={metrics.anomalies > 0 ? `${metrics.anomalies} new` : "None"}
          changeType={metrics.anomalies > 0 ? "negative" : "positive"}
          subtitle="Security alerts"
        />
        <MetricCard
          title="Active Agents"
          value={metrics.activeAgents}
          icon={Users}
          change="Online"
          changeType="positive"
          subtitle="Connected systems"
        />
        <MetricCard
          title="System Health"
          value={`${metrics.systemHealth}%`}
          icon={Shield}
          change="Optimal"
          changeType="positive"
          subtitle="Overall status"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Performance Chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">System Performance</h3>
            <div className="flex items-center space-x-4 text-sm">
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-primary-500 rounded"></div>
                <span className="text-gray-400">CPU</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-success-500 rounded"></div>
                <span className="text-gray-400">Memory</span>
              </div>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px'
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="cpu" 
                  stroke="#0ea5e9" 
                  fill="#0ea5e9" 
                  fillOpacity={0.3} 
                />
                <Area 
                  type="monotone" 
                  dataKey="memory" 
                  stroke="#22c55e" 
                  fill="#22c55e" 
                  fillOpacity={0.3} 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Resource Usage Chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Resource Usage</h3>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={[
                { name: 'CPU', value: metrics.cpuUsage, color: '#0ea5e9' },
                { name: 'Memory', value: metrics.memoryUsage, color: '#22c55e' },
                { name: 'Processes', value: (metrics.activeProcesses / 1000) * 100, color: '#f59e0b' },
                { name: 'Network', value: (metrics.networkConnections / 100) * 100, color: '#ef4444' }
              ]}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px'
                  }}
                />
                <Bar dataKey="value" fill="#0ea5e9" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Events */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Recent Events</h3>
          <button className="btn-secondary text-sm">
            <Eye className="w-4 h-4 mr-2" />
            View All
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-dark-700">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Time</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Agent</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Event Type</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">CPU</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Status</th>
              </tr>
            </thead>
            <tbody>
              {recentEvents.map((event, index) => (
                <motion.tr
                  key={event.id || index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border-b border-dark-700 hover:bg-dark-700 transition-colors"
                >
                  <td className="py-3 px-4 text-sm text-gray-300">
                    {format(new Date(event.timestamp), 'HH:mm:ss')}
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-300">
                    {event.agent_id}
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-300">
                    {event.event_type}
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-300">
                    {event.cpu_percent ? `${event.cpu_percent.toFixed(1)}%` : 'N/A'}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`status-indicator ${event.is_anomaly ? 'status-offline' : 'status-online'}`}>
                      {event.is_anomaly ? 'Anomaly' : 'Normal'}
                    </span>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 