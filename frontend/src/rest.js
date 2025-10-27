const STORAGE_KEY = "pwrank.auth";

const API_BASE_URL =
  (typeof process !== "undefined" && process.env?.VUE_APP_API_BASE_URL) ||
  "http://localhost:5000";

class HttpError extends Error {
  constructor(response, payload) {
    super(`HTTP ${response.status}`);
    this.name = "HttpError";
    this.response = response;
    this.payload = payload;
  }
}

class RestClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  get auth() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (error) {
      console.warn("Failed to read auth payload:", error);
      return null;
    }
  }

  set auth(payload) {
    if (!payload) {
      localStorage.removeItem(STORAGE_KEY);
      return;
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  }

  logout() {
    this.auth = null;
  }

  userIdentity() {
    return this.auth;
  }

  async login(email, password) {
    this.logout();
    try {
      const data = await this._requestJson("POST", "/auth", {
        body: { email, password },
        includeAuth: false,
      });
      this.auth = {
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        identity: data.identity,
      };
      return { ok: true };
    } catch (error) {
      const message =
        error instanceof HttpError
          ? error.payload?.message || "Authentication failed."
          : "Unable to reach the backend.";
      return { ok: false, message };
    }
  }

  async refreshToken() {
    const auth = this.auth;
    if (!auth?.refreshToken) {
      return false;
    }

    try {
      const data = await this._fetchJson("/auth", {
        method: "GET",
        headers: this._headers(auth.refreshToken),
      });
      if (!data?.access_token) {
        this.logout();
        return false;
      }
      this.auth = { ...auth, accessToken: data.access_token };
      return true;
    } catch (error) {
      this.logout();
      return false;
    }
  }

  async get(endpoint) {
    return this._requestJson("GET", endpoint);
  }

  async post(endpoint, body) {
    return this._requestJson("POST", endpoint, { body });
  }

  async put(endpoint, body) {
    return this._requestJson("PUT", endpoint, { body });
  }

  async del(endpoint, body) {
    return this._requestJson("DELETE", endpoint, { body });
  }

  async _requestJson(method, endpoint, options = {}) {
    const { body, includeAuth = true } = options;
    const response = await this._request(method, endpoint, {
      body,
      includeAuth,
    });
    const payload = await this._maybeJson(response);
    if (!response.ok) {
      throw new HttpError(response, payload);
    }
    return payload;
  }

  async _request(method, endpoint, { body, includeAuth }) {
    const url = `${this.baseUrl}${endpoint}`;
    const auth = this.auth;
    const headers = this._headers(includeAuth ? auth?.accessToken : "");

    const response = await fetch(url, {
      method,
      headers,
      body: this._bodyForRequest(method, body),
    });

    if (response.status === 401 && includeAuth && auth?.refreshToken) {
      const refreshed = await this.refreshToken();
      if (refreshed) {
        return this._request(method, endpoint, { body, includeAuth });
      }
    }

    return response;
  }

  _headers(token) {
    const headers = { "Content-Type": "application/json" };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    return headers;
  }

  _bodyForRequest(method, body) {
    if (method === "GET" || typeof body === "undefined") {
      return undefined;
    }
    return JSON.stringify(body);
  }

  async _maybeJson(response) {
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      return response.json();
    }
    return null;
  }

  async _fetchJson(endpoint, options) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, options);
    if (!response.ok) {
      throw new HttpError(response, await this._maybeJson(response));
    }
    return this._maybeJson(response);
  }
}

export const REST = new RestClient(API_BASE_URL);
export { HttpError };
