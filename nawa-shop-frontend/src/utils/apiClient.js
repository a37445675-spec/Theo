/**
 * Client API universel — NAWA Commerce.
 *
 * Gère automatiquement :
 *  - Le token CSRF (cookie + header X-CSRFToken)
 *  - Le token JWT si présent dans localStorage
 *  - Les credentials (cookies de session)
 *  - Le parsing JSON + gestion d'erreurs
 *
 * Usage :
 *   import { apiFetch } from "../utils/apiClient";
 *   const data = await apiFetch("/api/v1/cart/lines/", {
 *     method: "POST",
 *     body: { product: 1, quantity: 2 },
 *   });
 */

const API_BASE = ""; // Les URLs incluent déjà /api/v1/


// ============================================================
//  LECTURE DES TOKENS
// ============================================================

export function getCsrfToken() {
  if (typeof document === "undefined") return "";
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : "";
}

export function getJwtToken() {
  if (typeof localStorage === "undefined") return "";
  return localStorage.getItem("access_token") || "";
}


// ============================================================
//  BOOTSTRAP CSRF
// ============================================================

let csrfBootstrapped = false;

/**
 * Appelé au boot de l'app pour obtenir le cookie CSRF.
 * Idempotent : ne fait qu'un seul appel par session.
 */
export async function bootstrapCsrf() {
  if (csrfBootstrapped) return getCsrfToken();
  try {
    const res = await fetch("/api/v1/csrf/", {
      credentials: "include",
      headers: { Accept: "application/json" },
    });
    if (res.ok) {
      const data = await res.json();
      csrfBootstrapped = true;
      return data.csrfToken || getCsrfToken();
    }
  } catch (err) {
    console.warn("Bootstrap CSRF échoué :", err);
  }
  return "";
}


// ============================================================
//  API FETCH
// ============================================================

export async function apiFetch(path, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const isUnsafe = ["POST", "PUT", "PATCH", "DELETE"].includes(method);

  const headers = {
    Accept: "application/json",
    ...(options.headers || {}),
  };

  // Content-Type si body JSON (et pas déjà défini)
  if (options.body && !headers["Content-Type"] && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  // JWT
  const jwt = getJwtToken();
  if (jwt) {
    headers["Authorization"] = `Bearer ${jwt}`;
  }

  // CSRF pour les méthodes d'écriture
  if (isUnsafe) {
    let token = getCsrfToken();
    if (!token) {
      token = await bootstrapCsrf();
    }
    if (token) {
      headers["X-CSRFToken"] = token;
    }
  }

  // Body
  let body = options.body;
  if (body && typeof body === "object" && !(body instanceof FormData)) {
    body = JSON.stringify(body);
  }

  const url = path.startsWith("http") ? path : (API_BASE + path);

  const res = await fetch(url, {
    ...options,
    method,
    headers,
    body,
    credentials: "include",
  });

  // Parsing
  let data = null;
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) {
    try { data = await res.json(); } catch { data = null; }
  } else {
    try { data = await res.text(); } catch { data = null; }
  }

  if (!res.ok) {
    const err = new Error(
      (data && (data.detail || data.message)) || `HTTP ${res.status}`
    );
    err.status = res.status;
    err.data = data;
    throw err;
  }

  return data;
}


// ============================================================
//  RACCOURCIS
// ============================================================

export const api = {
  get: (path, opts) => apiFetch(path, { ...opts, method: "GET" }),
  post: (path, body, opts) => apiFetch(path, { ...opts, method: "POST", body }),
  put: (path, body, opts) => apiFetch(path, { ...opts, method: "PUT", body }),
  patch: (path, body, opts) => apiFetch(path, { ...opts, method: "PATCH", body }),
  delete: (path, opts) => apiFetch(path, { ...opts, method: "DELETE" }),
};
