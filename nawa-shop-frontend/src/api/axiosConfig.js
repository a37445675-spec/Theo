/**
 * Bootstrap CSRF pour NAWA Commerce.
 *
 * À appeler UNE SEULE FOIS au démarrage de l'app (dans App.jsx).
 * Force Django à poser le cookie `csrftoken` que axios lira ensuite
 * automatiquement sur chaque requête non-GET.
 *
 * Importer ce fichier dans main.jsx :
 *   import "./api/axiosConfig";
 */

import { client } from "./client.js";

let csrfBootstrapped = false;

/**
 * Appelé au boot. Idempotent (un seul appel par session).
 */
export async function bootstrapCsrf() {
  if (csrfBootstrapped) return;
  try {
    const res = await client.get("/api/v1/csrf/");
    csrfBootstrapped = true;
    console.log("✅ CSRF bootstrapped");
    return res.data?.csrfToken || "";
  } catch (err) {
    console.warn("⚠️ Bootstrap CSRF échoué :", err?.message);
    return "";
  }
}

export default client;