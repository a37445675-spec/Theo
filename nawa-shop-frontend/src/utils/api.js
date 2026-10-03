/**
 * Client API centralisé.
 * Ajoute automatiquement le token d'authentification si présent.
 */
const API_BASE = "/api/v1/v1";

export async function apiCall(endpoint, options = {}) {
  const token = localStorage.getItem("access_token");

  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || `Erreur HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  get: (url) => apiCall(url),
  post: (url, data) => apiCall(url, { method: "POST", body: JSON.stringify(data) }),
  put: (url, data) => apiCall(url, { method: "PUT", body: JSON.stringify(data) }),
  patch: (url, data) => apiCall(url, { method: "PATCH", body: JSON.stringify(data) }),
  delete: (url) => apiCall(url, { method: "DELETE" }),
};
