import axios from 'axios';

// Create axios instances for different services
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

const mlClient = axios.create({
  baseURL: '/ml',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service class
class ApiService {
  // Health checks
  async getServerHealth() {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('Server health check failed:', error);
      throw error;
    }
  }

  async getMLHealth() {
    try {
      const response = await mlClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('ML health check failed:', error);
      throw error;
    }
  }

  // Events
  async getEvents(limit = 100, offset = 0) {
    try {
      const response = await apiClient.get(`/events?limit=${limit}&offset=${offset}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch events:', error);
      throw error;
    }
  }

  async getEventById(id) {
    try {
      const response = await apiClient.get(`/events/${id}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch event:', error);
      throw error;
    }
  }

  // ML Models
  async getModels() {
    try {
      const response = await mlClient.get('/models');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch models:', error);
      throw error;
    }
  }

  async predict(data, modelType = 'isolation_forest', modelId = null) {
    try {
      const payload = {
        data,
        model_type: modelType,
        ...(modelId && { model_id: modelId })
      };
      const response = await mlClient.post('/predict', payload);
      return response.data;
    } catch (error) {
      console.error('Prediction failed:', error);
      throw error;
    }
  }

  // System metrics
  async getSystemMetrics() {
    try {
      const response = await apiClient.get('/metrics/system');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch system metrics:', error);
      throw error;
    }
  }

  // Agent status
  async getAgentStatus() {
    try {
      const response = await apiClient.get('/agents/status');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch agent status:', error);
      throw error;
    }
  }

  // Anomalies
  async getAnomalies(limit = 50) {
    try {
      const response = await apiClient.get(`/anomalies?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch anomalies:', error);
      throw error;
    }
  }

  // Threat intelligence
  async getThreatIntel() {
    try {
      const response = await apiClient.get('/threat-intel');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch threat intelligence:', error);
      throw error;
    }
  }

  // Dashboard stats
  async getDashboardStats() {
    try {
      const response = await apiClient.get('/dashboard/stats');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
      throw error;
    }
  }
}

// WebSocket service for real-time updates
class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.listeners = new Map();
  }

  connect() {
    try {
      this.ws = new WebSocket('ws://localhost:8000/ws/events');
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.notifyListeners('connection', { status: 'connected' });
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifyListeners('message', data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.notifyListeners('connection', { status: 'disconnected' });
        this.reconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.notifyListeners('error', error);
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('Max reconnection attempts reached');
      this.notifyListeners('connection', { status: 'failed' });
    }
  }

  subscribe(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  unsubscribe(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  notifyListeners(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in WebSocket listener:', error);
        }
      });
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}

// Create singleton instances
const apiService = new ApiService();
const wsService = new WebSocketService();

export { apiService, wsService };
export default apiService; 