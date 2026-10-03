/**
 * Phase 11 — Hooks pour les widgets E-commerce.
 * Fournit les données produit, panier et commande.
 */
import { useEffect, useState, useCallback } from "react";
import { useParams, useLocation } from "react-router-dom";

// ============================================================
//  Produit courant (depuis /produit/:slug ou :slug direct)
// ============================================================

const productCache = new Map();

export function useCurrentProduct(explicitSlug) {
  const { slug: routeSlug } = useParams();
  const slug = explicitSlug || routeSlug;
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!slug) {
      setLoading(false);
      return;
    }
    if (productCache.has(slug)) {
      setProduct(productCache.get(slug));
      setLoading(false);
      return;
    }
    setLoading(true);
    fetch(`/api/v1/catalog/products/${slug}/`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        productCache.set(slug, data);
        setProduct(data);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [slug]);

  return { product, loading, error };
}

// ============================================================
//  Liste de produits (filtrable)
// ============================================================

export function useProducts({
  category,
  isFeatured,
  isOnSale,
  ordering,
  limit = 12,
  excludeId,
} = {}) {
  const [data, setData] = useState({ results: [], count: 0, loading: true, error: null });

  useEffect(() => {
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    if (isFeatured) params.set("is_featured", "true");
    if (isOnSale) params.set("is_on_sale", "true");
    if (ordering) params.set("ordering", ordering);
    if (limit) params.set("limit", limit);

    setData((d) => ({ ...d, loading: true }));

    fetch(`/api/v1/catalog/products/?${params.toString()}`)
      .then((res) => (res.ok ? res.json() : { results: [], count: 0 }))
      .then((json) => {
        const list = Array.isArray(json) ? json : json.results || [];
        const filtered = excludeId ? list.filter((p) => p.id !== excludeId) : list;
        setData({
          results: filtered,
          count: json.count || filtered.length,
          loading: false,
          error: null,
        });
      })
      .catch((err) => setData({ results: [], count: 0, loading: false, error: err.message }));
  }, [category, isFeatured, isOnSale, ordering, limit, excludeId]);

  return data;
}

// ============================================================
//  Catégories produit
// ============================================================

let categoriesCache = null;

export function useProductCategories() {
  const [categories, setCategories] = useState(categoriesCache || []);
  const [loading, setLoading] = useState(!categoriesCache);

  useEffect(() => {
    if (categoriesCache) return;
    fetch("/api/v1/catalog/categories/")
      .then((res) => (res.ok ? res.json() : []))
      .then((json) => {
        const list = Array.isArray(json) ? json : json.results || [];
        categoriesCache = list;
        setCategories(list);
      })
      .catch(() => setCategories([]))
      .finally(() => setLoading(false));
  }, []);

  return { categories, loading };
}

// ============================================================
//  Panier (tente d'utiliser CartContext, sinon fallback API)
// ============================================================

export function useCartData() {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(() => {
    setLoading(true);
    fetch("/api/v1/cart/", { credentials: "include" })
      .then((res) => (res.ok ? res.json() : { lines: [], subtotal: "0.00", totalItems: 0 }))
      .then((data) => setCart(data))
      .catch(() => setCart({ lines: [], subtotal: "0.00", totalItems: 0 }))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { cart, loading, refresh };
}

// ============================================================
//  Utilitaire : formatage prix
// ============================================================

export function formatPrice(amount, currency = "EUR") {
  const n = Number(amount || 0);
  const symbols = { EUR: "€", USD: "$", XOF: "FCFA", GBP: "£" };
  const symbol = symbols[currency] || currency;
  return `${n.toFixed(2)} ${symbol}`;
}
