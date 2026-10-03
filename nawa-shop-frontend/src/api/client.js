/**
 * Instance axios centrale + helpers pour NAWA Commerce.
 *
 * Exports :
 *  - client (instance axios)
 *  - api (raccourcis GET/POST/PUT/PATCH/DELETE)
 *  - getTokens / setTokens / clearTokens
 *  - getCsrfToken / ensureCsrf
 *  - extractErrorMessage
 */
import axios from "axios";


// ============================================================
//  GESTION DES TOKENS JWT
// ============================================================

const ACCESS_KEY = "access_token";
const REFRESH_KEY = "refresh_token";

export function getTokens() {
  if (typeof localStorage === "undefined") {
    return { access: null, refresh: null };
  }
  return {
    access: localStorage.getItem(ACCESS_KEY),
    refresh: localStorage.getItem(REFRESH_KEY),
  };
}

export function setTokens({ access, refresh }) {
  if (typeof localStorage === "undefined") return;
  if (access) localStorage.setItem(ACCESS_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens() {
  if (typeof localStorage === "undefined") return;
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}


// ============================================================
//  GESTION DU CSRF
// ============================================================

export function getCsrfToken() {
  if (typeof document === "undefined") return "";
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : "";
}

let csrfBootstrapped = false;

export async function ensureCsrf() {
  const token = getCsrfToken();
  if (token) return token;
  if (csrfBootstrapped) return "";
  try {
    await client.get("/api/v1/csrf/");
    csrfBootstrapped = true;
    return getCsrfToken();
  } catch {
    return "";
  }
}


// ============================================================
//  EXTRACTEUR DE MESSAGE D'ERREUR
// ============================================================

/**
 * Extrait un message lisible depuis une erreur axios/API.
 */
export function extractErrorMessage(error, fallback = "Une erreur est survenue.") {
  if (!error) return fallback;

  // Erreur axios avec réponse
  if (error.response) {
    const data = error.response.data;

    // Django REST Framework : detail, message, error
    if (typeof data === "string") return data;
    if (data?.detail) return data.detail;
    if (data?.message) return data.message;
    if (data?.error) return data.error;

    // Erreurs de validation par champ
    if (data && typeof data === "object") {
      const firstKey = Object.keys(data)[0];
      const firstVal = data[firstKey];
      if (Array.isArray(firstVal) && firstVal.length) {
        return `${firstKey} : ${firstVal[0]}`;
      }
      if (typeof firstVal === "string") {
        return `${firstKey} : ${firstVal}`;
      }
    }

    return `Erreur ${error.response.status}`;
  }

  // Erreur réseau
  if (error.request) return "Le serveur ne répond pas.";
  if (error.message) return error.message;

  return fallback;
}


// ============================================================
//  INSTANCE AXIOS
// ============================================================

const client = axios.create({
  baseURL: "",
  withCredentials: true,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});


// ============================================================
//  INTERCEPTEUR REQUÊTE : INJECTER LE JWT
// ============================================================

client.interceptors.request.use(
  (config) => {
    const { access } = getTokens();
    if (access) {
      config.headers = config.headers || {};
      config.headers["Authorization"] = `Bearer ${access}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);


// ============================================================
//  INTERCEPTEUR RÉPONSE : REFRESH AUTO SUR 401
// ============================================================

let isRefreshing = false;
let refreshSubscribers = [];

function onRefreshed(token) {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error?.response?.status;

    if (status === 401 && !originalRequest._retry) {
      const { refresh } = getTokens();
      if (!refresh) {
        clearTokens();
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve) => {
          refreshSubscribers.push((token) => {
            originalRequest.headers["Authorization"] = `Bearer ${token}`;
            resolve(client(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const res = await axios.post("/api/v1/auth/token/refresh/", { refresh });
        const newAccess = res.data?.access;
        if (newAccess) {
          setTokens({ access: newAccess, refresh });
          onRefreshed(newAccess);
          originalRequest.headers["Authorization"] = `Bearer ${newAccess}`;
          return client(originalRequest);
        }
      } catch (refreshError) {
        clearTokens();
        if (typeof window !== "undefined") {
          window.location.href = "/connexion";
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);


// ============================================================
//  RACCOURCIS API
// ============================================================

export const api = {
  get: (url, config) => client.get(url, config),
  post: (url, data, config) => client.post(url, data, config),
  put: (url, data, config) => client.put(url, data, config),
  patch: (url, data, config) => client.patch(url, data, config),
  delete: (url, config) => client.delete(url, config),
};


export { client };
export default client;