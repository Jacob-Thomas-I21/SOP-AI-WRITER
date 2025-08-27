// API service for SOP Author Pharmaceutical system
class APIService {
  private baseURL = '/api/v1';
  private authToken: string | null = null;

  constructor() {
    // Try to get token from localStorage
    this.authToken = localStorage.getItem('demo_auth_token');
  }

  // Set auth token
  setAuthToken(token: string) {
    this.authToken = token;
    localStorage.setItem('demo_auth_token', token);
  }

  // Get auth headers
  private getAuthHeaders() {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    return headers;
  }

  // Generic API call method
  private async makeRequest(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      headers: this.getAuthHeaders(),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Authentication methods
  async getDemoAuthToken() {
    const result = await this.makeRequest('/demo/demo-auth', {
      method: 'POST',
    });
    
    if (result.access_token) {
      this.setAuthToken(result.access_token);
    }
    
    return result;
  }

  async getDemoStatus() {
    return await this.makeRequest('/demo/demo-status');
  }

  // SOP methods
  async createSOP(sopData: any) {
    return await this.makeRequest('/sops', {
      method: 'POST',
      body: JSON.stringify(sopData),
    });
  }

  async getSOPStatus(jobId: string) {
    return await this.makeRequest(`/sops/${jobId}`);
  }

  async downloadSOPPDF(jobId: string) {
    const url = `${this.baseURL}/sops/${jobId}/pdf`;
    const response = await fetch(url, {
      headers: this.getAuthHeaders(),
    });
    
    if (!response.ok) {
      throw new Error('Failed to download PDF');
    }
    
    return response.blob();
  }

  // Health check
  async healthCheck() {
    return await this.makeRequest('/health', { method: 'GET' });
  }

  // System health
  async detailedHealthCheck() {
    return await this.makeRequest('/health/detailed', { method: 'GET' });
  }

  // Initialize demo authentication
  async initializeDemo() {
    try {
      // Try to get a demo token if we don't have one
      if (!this.authToken) {
        await this.getDemoAuthToken();
      }
      return true;
    } catch (error) {
      console.warn('Failed to initialize demo auth:', error);
      return false;
    }
  }
}

// Create singleton instance
export const apiService = new APIService();

// Export for use in components
export default apiService;