const API = {
  getAuthToken() {
    const t = localStorage.getItem('cg_token');
    if (!t || t === 'null' || t === 'undefined' || t === 'None') return '';
    return t;
  },

  setAuthToken(token) {
    if (token && token !== 'null' && token !== 'undefined') {
      localStorage.setItem('cg_token', token);
    }
  },

  clearAuthToken() {
    localStorage.removeItem('cg_token');
  },

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };
    const token = this.getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  },

  async handleResponse(res) {
    if (res.status === 401) {
      // If 401 token error occurs, clear stale token
      this.clearAuthToken();
      // If unauthorized on protected route, redirect to login
      if (window.location.pathname !== '/login/' && window.location.pathname !== '/register/') {
        try {
            await fetch('/api/auth/logout/', { method: 'POST' });
        } catch (e) {}
        window.location.href = '/login/';
      }
    }
    try {
      const data = await res.json();
      if (!res.ok) {
        // DRF validation errors often come as object keys rather than a single 'error' string
        if (!data.error && typeof data === 'object') {
          const errors = Object.values(data).flat();
          if (errors.length > 0) {
            data.error = errors.join(' ');
          }
        }
      }
      return data;
    } catch (e) {
      return { error: 'Failed to parse server response' };
    }
  },

  async register(data) {
    const res = await fetch('/api/auth/register/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await this.handleResponse(res);
    // Note: register doesn't return access token by default in our setup, user must login
    return result;
  },

  async login(username, password) {
    const res = await fetch('/api/auth/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const result = await this.handleResponse(res);
    if (result.access) {
      this.setAuthToken(result.access);
    }
    return result;
  },

  async logout() {
    this.clearAuthToken();
    try {
      await fetch('/api/auth/logout/', {
        method: 'POST',
        headers: this.getHeaders()
      });
    } catch (e) {}
    window.location.href = '/login/';
  },

  async createProject(name, description, repository_url) {
    const res = await fetch('/api/projects/', {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ name, description, repository_url })
    });
    return this.handleResponse(res);
  },

  async submitReview(formData) {
    const token = this.getAuthToken();
    const headers = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const res = await fetch('/api/reviews/submit/', {
      method: 'POST',
      headers: headers,
      body: formData
    });
    return this.handleResponse(res);
  },

  async fetchGitHubCode(repo_url, file_path = '') {
    const res = await fetch('/api/reviews/fetch_github/', {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ repo_url, file_path })
    });
    return this.handleResponse(res);
  },

  async analyzeInstant(code, filename = 'main.py', projectId = null) {
    const res = await fetch('/api/reviews/analyze_instant/', {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ code, filename, project_id: projectId })
    });
    return this.handleResponse(res);
  },

  async auditRepository(projectId) {
    const res = await fetch('/api/reviews/audit_repo/', {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ project_id: projectId })
    });
    return this.handleResponse(res);
  },

  async compareReviews(review1Id, review2Id) {
    const res = await fetch(`/api/reviews/compare/?review1=${review1Id}&review2=${review2Id}`, {
      headers: this.getHeaders()
    });
    return this.handleResponse(res);
  }
};
