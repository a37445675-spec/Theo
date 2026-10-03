/**
 * API Panier — NAWA Commerce.
 *
 * Toutes les requêtes passent par `client` (instance axios configurée
 * dans client.js), qui gère automatiquement :
 *   - les cookies de session (withCredentials)
 *   - le token CSRF (xsrfCookieName/xsrfHeaderName)
 *   - le token JWT (intercepteur)
 */
import { client } from "./client.js";


// ============================================================
//  LECTURE DU PANIER
// ============================================================

export async function getCart() {
  const { data } = await client.get("/api/v1/cart/");
  return data;
}


// ============================================================
//  AJOUTER UNE LIGNE
// ============================================================

export async function addLine({ productId, variantId, quantity = 1 }) {
  const { data } = await client.post("/api/v1/cart/lines/", {
    productId,
    variantId,
    quantity,
  });
  return data;
}


// ============================================================
//  MODIFIER UNE LIGNE
// ============================================================

export async function updateLine(lineId, quantity) {
  const { data } = await client.patch(`/api/v1/cart/lines/${lineId}/`, {
    quantity,
  });
  return data;
}


// ============================================================
//  SUPPRIMER UNE LIGNE
// ============================================================

export async function removeLine(lineId) {
  const { data } = await client.delete(`/api/v1/cart/lines/${lineId}/`);
  return data;
}