"""
Phase 11 — Widgets E-commerce (20 widgets).
NE MODIFIE AUCUN fichier existant sauf config.jsx (ajout à la fin).

Usage : python inject_phase11.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
WIDGETS_DIR = os.path.join(SRC_DIR, "puck", "widgets")
HOOKS_DIR = os.path.join(SRC_DIR, "puck", "hooks")


# ============================================================
#              HOOKS PRODUIT / PANIER
# ============================================================

PRODUCT_HOOKS = '''/**
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
'''


# ============================================================
#              PRODUCT WIDGETS (13)
# ============================================================

PRODUCT_WIDGETS_JSX = '''/**
 * Phase 11 — Widgets Produit (13 composants).
 */
import React from "react";
import { Link } from "react-router-dom";
import { useCurrentProduct, useProducts, formatPrice } from "../hooks/useProductContext";

// ============================================================
//  PRODUCT TITLE
// ============================================================

export const ProductTitle = {
  fields: {
    level: {
      type: "select", label: "Niveau",
      options: [
        { label: "H1", value: "h1" },
        { label: "H2", value: "h2" },
        { label: "H3", value: "h3" },
      ],
    },
    fallback: { type: "text", label: "Titre de secours", defaultValue: "Produit" },
  },
  defaultProps: { level: "h1", fallback: "Produit" },
  render: ({ level, fallback }) => {
    const { product, loading } = useCurrentProduct();
    const Tag = level;
    if (loading) return <div style={{ height: "2.5em", background: "#f5f5f5", borderRadius: 8 }} />;
    return <Tag>{product?.name || fallback}</Tag>;
  },
};

// ============================================================
//  PRODUCT IMAGES
// ============================================================

export const ProductImages = {
  fields: {
    ratio: {
      type: "select", label: "Ratio",
      options: [
        { label: "Carré", value: "1/1" },
        { label: "4/5", value: "4/5" },
        { label: "16/9", value: "16/9" },
      ],
    },
    showThumbnails: {
      type: "radio", label: "Miniatures",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: { ratio: "1/1", showThumbnails: "true" },
  render: ({ ratio, showThumbnails }) => {
    const { product } = useCurrentProduct();
    const [active, setActive] = React.useState(0);
    const images = product?.images || (product?.cover_image ? [{ image: product.cover_image }] : []);
    const fallback = "/fallbacks/product-fallback.jpg";

    if (!product) return <div style={{ aspectRatio: ratio, background: "#f5f5f5", borderRadius: 16 }} />;

    const urls = images.length > 0
      ? images.map((i) => i.image_url || i.image || fallback)
      : [fallback];

    return (
      <div>
        <div style={{ aspectRatio: ratio, borderRadius: "16px", overflow: "hidden", background: "#f5f5f5" }}>
          <img
            src={urls[active]}
            alt={product.name}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
            onError={(e) => { e.currentTarget.src = fallback; }}
          />
        </div>
        {showThumbnails === "true" && urls.length > 1 && (
          <div style={{ display: "flex", gap: "8px", marginTop: "12px" }}>
            {urls.map((url, i) => (
              <button
                key={i}
                onClick={() => setActive(i)}
                style={{
                  width: 64, height: 64, borderRadius: "8px",
                  overflow: "hidden", border: i === active ? "2px solid #C1652F" : "2px solid #eee",
                  background: "none", cursor: "pointer", padding: 0,
                }}
              >
                <img src={url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              </button>
            ))}
          </div>
        )}
      </div>
    );
  },
};

// ============================================================
//  PRODUCT PRICE
// ============================================================

export const ProductPrice = {
  fields: {
    showCompareAt: {
      type: "radio", label: "Prix barré",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    size: {
      type: "select", label: "Taille",
      options: [
        { label: "Normal", value: "normal" },
        { label: "Grand", value: "large" },
      ],
    },
  },
  defaultProps: { showCompareAt: "true", size: "normal" },
  render: ({ showCompareAt, size }) => {
    const { product } = useCurrentProduct();
    if (!product) return <div style={{ height: 40 }} />;
    const fontSize = size === "large" ? "2.5rem" : "1.75rem";
    const hasCompare = showCompareAt === "true" && product.compare_at_price && Number(product.compare_at_price) > Number(product.price);

    return (
      <div style={{ display: "flex", alignItems: "baseline", gap: "12px" }}>
        <span style={{ fontSize, fontWeight: 700, color: "#C1652F" }}>
          {formatPrice(product.price, product.currency)}
        </span>
        {hasCompare && (
          <span style={{ fontSize: "1rem", color: "#999", textDecoration: "line-through" }}>
            {formatPrice(product.compare_at_price, product.currency)}
          </span>
        )}
      </div>
    );
  },
};

// ============================================================
//  ADD TO CART
// ============================================================

export const AddToCart = {
  fields: {
    label: { type: "text", label: "Libellé", defaultValue: "Ajouter au panier" },
    showQuantity: {
      type: "radio", label: "Sélecteur de quantité",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    variant: {
      type: "radio", label: "Style",
      options: [
        { label: "Primaire", value: "primary" },
        { label: "Ghost", value: "ghost" },
      ],
    },
  },
  defaultProps: { label: "Ajouter au panier", showQuantity: "true", variant: "primary" },
  render: ({ label, showQuantity, variant }) => {
    const { product } = useCurrentProduct();
    const [qty, setQty] = React.useState(1);
    const [status, setStatus] = React.useState(null);

    const handleAdd = async () => {
      if (!product) return;
      setStatus("loading");
      try {
        const res = await fetch("/api/v1/cart/lines/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ product: product.id, quantity: qty }),
        });
        if (res.ok) {
          setStatus("success");
          setTimeout(() => setStatus(null), 2000);
        } else {
          setStatus("error");
        }
      } catch {
        setStatus("error");
      }
    };

    if (!product) return null;

    return (
      <div>
        {showQuantity === "true" && (
          <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "12px" }}>
            <span style={{ fontSize: "0.9rem", color: "#6B6259" }}>Quantité :</span>
            <div style={{ display: "flex", alignItems: "center", border: "1px solid #ddd", borderRadius: "8px" }}>
              <button
                onClick={() => setQty((q) => Math.max(1, q - 1))}
                style={{ width: 36, height: 36, border: "none", background: "none", cursor: "pointer", fontSize: "1.2rem" }}
              >−</button>
              <span style={{ padding: "0 12px", fontWeight: 600, minWidth: 32, textAlign: "center" }}>{qty}</span>
              <button
                onClick={() => setQty((q) => q + 1)}
                style={{ width: 36, height: 36, border: "none", background: "none", cursor: "pointer", fontSize: "1.2rem" }}
              >+</button>
            </div>
          </div>
        )}
        <button
          onClick={handleAdd}
          disabled={status === "loading"}
          className={variant === "primary" ? "btn btn-primary btn-lg" : "btn btn-ghost btn-lg"}
          style={{ width: "100%" }}
        >
          {status === "loading" ? "Ajout..." : status === "success" ? "✓ Ajouté !" : status === "error" ? "Erreur" : label}
        </button>
      </div>
    );
  },
};

// ============================================================
//  PRODUCT RATING
// ============================================================

export const ProductRating = {
  fields: {
    showCount: {
      type: "radio", label: "Nombre d'avis",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: { showCount: "true" },
  render: ({ showCount }) => {
    const { product } = useCurrentProduct();
    if (!product) return null;
    const rating = Number(product.rating_average || 0);
    const count = product.reviews_count || 0;

    return (
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <div style={{ color: "#D4A843", fontSize: "1.1rem" }}>
          {"★".repeat(Math.round(rating))}
          {"☆".repeat(5 - Math.round(rating))}
        </div>
        <span style={{ fontSize: "0.9rem", color: "#6B6259" }}>
          {rating.toFixed(1)}
          {showCount === "true" && count > 0 && ` (${count} avis)`}
        </span>
      </div>
    );
  },
};

// ============================================================
//  PRODUCT STOCK
// ============================================================

export const ProductStock = {
  fields: {
    lowStockThreshold: { type: "number", label: "Seuil stock bas", defaultValue: 5 },
  },
  defaultProps: { lowStockThreshold: 5 },
  render: ({ lowStockThreshold }) => {
    const { product } = useCurrentProduct();
    if (!product) return null;
    const inStock = product.in_stock !== false;
    const stock = product.stock || 0;

    if (!inStock) {
      return <span style={{ color: "#DC2626", fontWeight: 600 }}>✗ Rupture de stock</span>;
    }
    if (stock > 0 && stock <= lowStockThreshold) {
      return <span style={{ color: "#D4A843", fontWeight: 600 }}>⚠ Plus que {stock} en stock</span>;
    }
    return <span style={{ color: "#16A34A", fontWeight: 600 }}>✓ En stock</span>;
  },
};

// ============================================================
//  PRODUCT META
// ============================================================

export const ProductMeta = {
  fields: {
    showSku: { type: "radio", label: "SKU", options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }] },
    showCategory: { type: "radio", label: "Catégorie", options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }] },
    showBrand: { type: "radio", label: "Marque", options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }] },
  },
  defaultProps: { showSku: "true", showCategory: "true", showBrand: "true" },
  render: ({ showSku, showCategory, showBrand }) => {
    const { product } = useCurrentProduct();
    if (!product) return null;

    return (
      <div style={{ display: "flex", gap: "16px", flexWrap: "wrap", fontSize: "0.85rem", color: "#6B6259" }}>
        {showSku === "true" && product.sku && <span><strong>SKU :</strong> {product.sku}</span>}
        {showCategory === "true" && product.category && <span><strong>Catégorie :</strong> {product.category.name}</span>}
        {showBrand === "true" && product.brand && <span><strong>Marque :</strong> {product.brand.name}</span>}
      </div>
    );
  },
};

// ============================================================
//  SHORT DESCRIPTION
// ============================================================

export const ShortDescription = {
  fields: {
    maxLength: { type: "number", label: "Longueur max", defaultValue: 300 },
  },
  defaultProps: { maxLength: 300 },
  render: ({ maxLength }) => {
    const { product } = useCurrentProduct();
    if (!product) return null;
    const text = product.short_description || product.shortDescription || "";
    const truncated = text.slice(0, maxLength) + (text.length > maxLength ? "…" : "");
    return <p style={{ color: "#6B6259", lineHeight: 1.7 }}>{truncated}</p>;
  },
};

// ============================================================
//  PRODUCT CONTENT
// ============================================================

export const ProductContent = {
  fields: {
    className: { type: "text", label: "Classes CSS", defaultValue: "product-content" },
  },
  defaultProps: { className: "product-content" },
  render: ({ className }) => {
    const { product } = useCurrentProduct();
    if (!product) return null;
    const html = product.description || product.long_description || "<p>Aucune description.</p>";
    return (
      <div
        className={className}
        style={{ lineHeight: 1.8 }}
        dangerouslySetInnerHTML={{ __html: html }}
      />
    );
  },
};

// ============================================================
//  PRODUCT DATA TABS
// ============================================================

export const ProductDataTabs = {
  fields: {
    showAdditionalInfo: {
      type: "radio", label: "Infos complémentaires",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    showReviews: {
      type: "radio", label: "Avis",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: { showAdditionalInfo: "true", showReviews: "true" },
  render: ({ showAdditionalInfo, showReviews }) => {
    const { product } = useCurrentProduct();
    const [active, setActive] = React.useState("desc");
    if (!product) return null;

    const tabs = [
      { key: "desc", label: "Description", content: product.description || "—" },
      ...(showAdditionalInfo === "true" ? [{ key: "info", label: "Informations", content: product.additional_info || "—" }] : []),
      ...(showReviews === "true" ? [{ key: "reviews", label: `Avis (${product.reviews_count || 0})`, content: "Aucun avis pour le moment." }] : []),
    ];

    return (
      <div>
        <div style={{ display: "flex", gap: "8px", borderBottom: "1px solid #eee", marginBottom: "20px" }}>
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setActive(t.key)}
              style={{
                padding: "12px 20px", background: "none", border: "none",
                cursor: "pointer", fontWeight: active === t.key ? 700 : 400,
                borderBottom: active === t.key ? "2px solid #C1652F" : "2px solid transparent",
                color: active === t.key ? "#C1652F" : "#6B6259",
              }}
            >
              {t.label}
            </button>
          ))}
        </div>
        <div dangerouslySetInnerHTML={{ __html: tabs.find((t) => t.key === active)?.content || "" }} />
      </div>
    );
  },
};

// ============================================================
//  PRODUCT GRID
// ============================================================

export const ProductGrid = {
  fields: {
    source: {
      type: "select", label: "Source",
      options: [
        { label: "Tous", value: "all" },
        { label: "Vedettes", value: "featured" },
        { label: "Promotions", value: "sale" },
        { label: "Nouveautés", value: "new" },
      ],
    },
    columns: { type: "number", label: "Colonnes", defaultValue: 4 },
    limit: { type: "number", label: "Nombre", defaultValue: 8 },
  },
  defaultProps: { source: "featured", columns: 4, limit: 8 },
  render: ({ source, columns, limit }) => {
    const { results, loading } = useProducts({
      isFeatured: source === "featured" ? true : undefined,
      isOnSale: source === "sale" ? true : undefined,
      ordering: source === "new" ? "-created_at" : undefined,
      limit,
    });

    if (loading) {
      return (
        <div style={{ display: "grid", gridTemplateColumns: `repeat(${columns}, 1fr)`, gap: "20px" }}>
          {Array.from({ length: limit }).map((_, i) => (
            <div key={i} style={{ aspectRatio: "1/1.3", background: "#f5f5f5", borderRadius: "12px" }} />
          ))}
        </div>
      );
    }

    if (!results.length) return <div style={{ textAlign: "center", color: "#888", padding: "3rem" }}>Aucun produit.</div>;

    return (
      <div style={{ display: "grid", gridTemplateColumns: `repeat(auto-fill, minmax(${Math.floor(1200 / columns) - 20}px, 1fr))`, gap: "20px" }}>
        {results.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
    );
  },
};

function ProductCard({ product }) {
  const fallback = "/fallbacks/product-fallback.jpg";
  const hasCompare = product.compare_at_price && Number(product.compare_at_price) > Number(product.price);

  return (
    <Link to={`/produit/${product.slug}`} style={{ textDecoration: "none", color: "inherit" }}>
      <article style={{
        background: "#fff", borderRadius: "16px", overflow: "hidden",
        boxShadow: "0 2px 12px rgba(0,0,0,0.06)", transition: "transform 0.2s, box-shadow 0.2s",
      }}>
        <div style={{ position: "relative", aspectRatio: "1/1", background: "#f5f5f5" }}>
          <img
            src={product.cover_image_url || product.coverImageUrl || fallback}
            alt={product.name}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
            onError={(e) => { e.currentTarget.src = fallback; }}
          />
          {hasCompare && (
            <span style={{
              position: "absolute", top: 12, left: 12,
              background: "#DC2626", color: "#fff", fontSize: "0.75rem",
              fontWeight: 700, padding: "4px 10px", borderRadius: "999px",
            }}>PROMO</span>
          )}
        </div>
        <div style={{ padding: "16px" }}>
          <h3 style={{ margin: "0 0 8px", fontSize: "1rem", fontWeight: 600 }}>{product.name}</h3>
          <div style={{ display: "flex", alignItems: "baseline", gap: "8px" }}>
            <span style={{ fontSize: "1.15rem", fontWeight: 700, color: "#C1652F" }}>
              {formatPrice(product.price, product.currency)}
            </span>
            {hasCompare && (
              <span style={{ fontSize: "0.85rem", color: "#999", textDecoration: "line-through" }}>
                {formatPrice(product.compare_at_price, product.currency)}
              </span>
            )}
          </div>
        </div>
      </article>
    </Link>
  );
}

// ============================================================
//  UPSELLS
// ============================================================

export const Upsells = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Vous aimerez aussi" },
    columns: { type: "number", label: "Colonnes", defaultValue: 4 },
    limit: { type: "number", label: "Nombre", defaultValue: 4 },
  },
  defaultProps: { title: "Vous aimerez aussi", columns: 4, limit: 4 },
  render: ({ title, columns, limit }) => {
    const { product } = useCurrentProduct();
    const { results } = useProducts({ isFeatured: true, limit, excludeId: product?.id });
    if (!results.length) return null;

    return (
      <section style={{ marginTop: "48px" }}>
        <h3 style={{ marginBottom: "20px" }}>{title}</h3>
        <div style={{ display: "grid", gridTemplateColumns: `repeat(auto-fill, minmax(${Math.floor(1200 / columns) - 20}px, 1fr))`, gap: "16px" }}>
          {results.map((p) => <ProductCard key={p.id} product={p} />)}
        </div>
      </section>
    );
  },
};

// ============================================================
//  RELATED PRODUCTS
// ============================================================

export const RelatedProducts = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Produits similaires" },
    columns: { type: "number", label: "Colonnes", defaultValue: 4 },
    limit: { type: "number", label: "Nombre", defaultValue: 4 },
  },
  defaultProps: { title: "Produits similaires", columns: 4, limit: 4 },
  render: ({ title, columns, limit }) => {
    const { product } = useCurrentProduct();
    const category = product?.category?.slug;
    const { results } = useProducts({ category, limit: limit + 1, excludeId: product?.id });
    if (!results.length) return null;

    return (
      <section style={{ marginTop: "48px" }}>
        <h3 style={{ marginBottom: "20px" }}>{title}</h3>
        <div style={{ display: "grid", gridTemplateColumns: `repeat(auto-fill, minmax(${Math.floor(1200 / columns) - 20}px, 1fr))`, gap: "16px" }}>
          {results.slice(0, limit).map((p) => <ProductCard key={p.id} product={p} />)}
        </div>
      </section>
    );
  },
};

// ============================================================
//  PRODUCT CATEGORIES
// ============================================================

export const ProductCategories = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Catégories" },
    display: {
      type: "radio", label: "Affichage",
      options: [
        { label: "Grille", value: "grid" },
        { label: "Liste", value: "list" },
      ],
    },
    columns: { type: "number", label: "Colonnes", defaultValue: 3 },
  },
  defaultProps: { title: "Catégories", display: "grid", columns: 3 },
  render: ({ title, display, columns }) => {
    const { categories, loading } = useProductCategories();
    if (loading) return <div style={{ color: "#888" }}>Chargement...</div>;
    if (!categories.length) return null;

    if (display === "list") {
      return (
        <div>
          <h3>{title}</h3>
          <ul style={{ listStyle: "none", padding: 0 }}>
            {categories.map((c) => (
              <li key={c.id} style={{ padding: "10px 0", borderBottom: "1px solid #eee" }}>
                <Link to={`/boutique/${c.slug}`} style={{ color: "#221B15", textDecoration: "none" }}>
                  → {c.name}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      );
    }

    return (
      <div>
        <h3>{title}</h3>
        <div style={{ display: "grid", gridTemplateColumns: `repeat(${columns}, 1fr)`, gap: "16px" }}>
          {categories.map((c) => (
            <Link
              key={c.id}
              to={`/boutique/${c.slug}`}
              style={{
                display: "block", padding: "24px", background: "#F7F0E4",
                borderRadius: "16px", textDecoration: "none", color: "#221B15",
                textAlign: "center", fontWeight: 600,
              }}
            >
              {c.icon && <div style={{ fontSize: "2rem", marginBottom: "8px" }}>{c.icon}</div>}
              {c.name}
            </Link>
          ))}
        </div>
      </div>
    );
  },
};
'''


# ============================================================
#              COMMERCE WIDGETS (7)
# ============================================================

COMMERCE_WIDGETS_JSX = '''/**
 * Phase 11 — Widgets Commerce (7 composants).
 * Panier, checkout, compte, résumé.
 */
import React from "react";
import { Link } from "react-router-dom";
import { useCurrentProduct, useCartData, useProducts, formatPrice } from "../hooks/useProductContext";

// ============================================================
//  CART — Panier complet
// ============================================================

export const Cart = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Mon panier" },
    showContinue: {
      type: "radio", label: "Bouton continuer",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: { title: "Mon panier", showContinue: "true" },
  render: ({ title, showContinue }) => {
    const { cart, loading, refresh } = useCartData();

    if (loading) return <div style={{ padding: "2rem", textAlign: "center", color: "#888" }}>Chargement...</div>;

    const lines = cart?.lines || [];
    const subtotal = cart?.subtotal || "0.00";

    if (!lines.length) {
      return (
        <div style={{ padding: "3rem", textAlign: "center", background: "#F7F0E4", borderRadius: "16px" }}>
          <div style={{ fontSize: "3rem", marginBottom: "12px" }}>🛍</div>
          <h3>{title} est vide</h3>
          <p style={{ color: "#6B6259", marginBottom: "20px" }}>Découvrez notre sélection.</p>
          <Link to="/boutique/cosmetiques" className="btn btn-primary">Découvrir la boutique</Link>
        </div>
      );
    }

    return (
      <div>
        <h2>{title} ({lines.length})</h2>
        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "24px", marginTop: "20px" }}>
          <div>
            {lines.map((line) => (
              <div key={line.id} style={{
                display: "flex", gap: "16px", padding: "16px",
                background: "#fff", borderRadius: "12px", marginBottom: "12px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
              }}>
                <div style={{ width: 80, height: 80, borderRadius: "8px", overflow: "hidden", background: "#f5f5f5", flexShrink: 0 }}>
                  <img
                    src={line.image_url || "/fallbacks/product-fallback.jpg"}
                    alt={line.product_name}
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600 }}>{line.product_name}</div>
                  <div style={{ fontSize: "0.85rem", color: "#6B6259" }}>Quantité : {line.quantity}</div>
                  <div style={{ fontWeight: 700, color: "#C1652F", marginTop: "6px" }}>
                    {formatPrice(line.unit_price || line.price, cart.currency)}
                  </div>
                </div>
                <button
                  onClick={async () => {
                    await fetch(`/api/v1/cart/lines/${line.id}/`, { method: "DELETE", credentials: "include" });
                    refresh();
                  }}
                  style={{ background: "none", border: "none", cursor: "pointer", color: "#DC2626", fontSize: "1.2rem" }}
                >×</button>
              </div>
            ))}
            {showContinue === "true" && (
              <Link to="/boutique/cosmetiques" style={{ color: "#C1652F", fontWeight: 600 }}>
                ← Continuer mes achats
              </Link>
            )}
          </div>
          <div style={{ background: "#F7F0E4", padding: "24px", borderRadius: "16px", alignSelf: "start" }}>
            <h3>Sous-total</h3>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "16px", fontSize: "1.2rem", fontWeight: 700 }}>
              <span>Total</span>
              <span>{formatPrice(subtotal, cart.currency)}</span>
            </div>
            <Link to="/commande" className="btn btn-primary btn-lg" style={{ display: "block", textAlign: "center", width: "100%" }}>
              Passer commande
            </Link>
          </div>
        </div>
      </div>
    );
  },
};

// ============================================================
//  CHECKOUT — Tunnel de commande (info)
// ============================================================

export const Checkout = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Finaliser la commande" },
  },
  defaultProps: { title: "Finaliser la commande" },
  render: ({ title }) => {
    const { cart } = useCartData();
    const total = cart?.subtotal || "0.00";

    return (
      <div style={{ maxWidth: "600px", margin: "0 auto" }}>
        <h2>{title}</h2>
        <div style={{ background: "#F7F0E4", padding: "24px", borderRadius: "16px", marginTop: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "12px" }}>
            <span>Sous-total</span>
            <span>{formatPrice(total, cart?.currency || "EUR")}</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", paddingTop: "12px", borderTop: "1px solid #ddd", fontWeight: 700, fontSize: "1.15rem" }}>
            <span>Total</span>
            <span>{formatPrice(total, cart?.currency || "EUR")}</span>
          </div>
        </div>
        <Link to="/commande" className="btn btn-primary btn-lg" style={{ display: "block", textAlign: "center", marginTop: "20px" }}>
          Continuer vers le paiement
        </Link>
      </div>
    );
  },
};

// ============================================================
//  PURCHASE SUMMARY — Récap commande
// ============================================================

export const PurchaseSummary = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Récapitulatif" },
  },
  defaultProps: { title: "Récapitulatif" },
  render: ({ title }) => {
    const { cart } = useCartData();
    const lines = cart?.lines || [];
    const subtotal = cart?.subtotal || "0.00";

    return (
      <div style={{ background: "#fff", padding: "24px", borderRadius: "16px", boxShadow: "0 2px 12px rgba(0,0,0,0.06)" }}>
        <h3>{title}</h3>
        <ul style={{ listStyle: "none", padding: 0, margin: "16px 0" }}>
          {lines.map((l) => (
            <li key={l.id} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid #eee" }}>
              <span>{l.product_name} × {l.quantity}</span>
              <span>{formatPrice((l.unit_price || 0) * l.quantity, cart.currency)}</span>
            </li>
          ))}
        </ul>
        <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 700, fontSize: "1.1rem" }}>
          <span>Total</span>
          <span>{formatPrice(subtotal, cart?.currency || "EUR")}</span>
        </div>
      </div>
    );
  },
};

// ============================================================
//  MY ACCOUNT — Espace client
// ============================================================

export const MyAccount = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Mon compte" },
  },
  defaultProps: { title: "Mon compte" },
  render: ({ title }) => (
    <div style={{ maxWidth: "800px", margin: "0 auto" }}>
      <h2>{title}</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px", marginTop: "20px" }}>
        {[
          { to: "/compte", label: "Profil", icon: "👤" },
          { to: "/compte/commandes", label: "Commandes", icon: "📦" },
          { to: "/compte/fidelite", label: "Fidélité", icon: "🎁" },
          { to: "/compte/adresses", label: "Adresses", icon: "📍" },
          { to: "/compte/factures", label: "Factures", icon: "🧾" },
          { to: "/compte/abonnements", label: "Abonnements", icon: "🔄" },
        ].map((item) => (
          <Link
            key={item.to}
            to={item.to}
            style={{
              display: "block", padding: "24px", background: "#F7F0E4",
              borderRadius: "16px", textDecoration: "none", color: "#221B15", textAlign: "center",
            }}
          >
            <div style={{ fontSize: "2rem", marginBottom: "8px" }}>{item.icon}</div>
            <div style={{ fontWeight: 600 }}>{item.label}</div>
          </Link>
        ))}
      </div>
    </div>
  ),
};

// ============================================================
//  WC BREADCRUMBS (déjà couvert par Breadcrumbs, version commerce)
// ============================================================

export const WcBreadcrumbs = {
  fields: {
    homeLabel: { type: "text", label: "Accueil", defaultValue: "Accueil" },
    shopLabel: { type: "text", label: "Boutique", defaultValue: "Boutique" },
  },
  defaultProps: { homeLabel: "Accueil", shopLabel: "Boutique" },
  render: ({ homeLabel, shopLabel }) => {
    const { product } = useCurrentProduct();
    const path = window.location.pathname;

    let crumbs = [{ label: homeLabel, to: "/" }, { label: shopLabel, to: "/boutique" }];
    if (path.includes("/boutique/")) {
      const cat = path.split("/boutique/")[1].split("/")[0];
      crumbs.push({ label: cat.replace(/-/g, " "), to: null });
    } else if (path.includes("/produit/")) {
      if (product?.category) {
        crumbs.push({ label: product.category.name, to: `/boutique/${product.category.slug}` });
      }
      crumbs.push({ label: product?.name || "Produit", to: null });
    }

    return (
      <nav style={{ fontSize: "0.85rem", color: "#6B6259", marginBottom: "16px" }}>
        {crumbs.map((c, i) => (
          <React.Fragment key={i}>
            {i > 0 && <span style={{ margin: "0 8px" }}>/</span>}
            {c.to ? (
              <Link to={c.to} style={{ color: "#6B6259", textDecoration: "none" }}>{c.label}</Link>
            ) : (
              <span style={{ color: "#C1652F", fontWeight: 600 }}>{c.label}</span>
            )}
          </React.Fragment>
        ))}
      </nav>
    );
  },
};

// ============================================================
//  MENU CART ÉTENDU (basé sur CartContext)
// ============================================================

export const MenuCartExtended = {
  fields: {
    iconLabel: { type: "text", label: "Icône", defaultValue: "🛒" },
    showItems: {
      type: "radio", label: "Afficher les articles",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: { iconLabel: "🛒", showItems: "true" },
  render: ({ iconLabel, showItems }) => {
    const { cart, loading } = useCartData();
    const [open, setOpen] = React.useState(false);
    const lines = cart?.lines || [];
    const totalItems = lines.reduce((acc, l) => acc + (l.quantity || 0), 0);

    return (
      <div
        style={{ position: "relative", display: "inline-block" }}
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
      >
        <button style={{ position: "relative", background: "none", border: "none", cursor: "pointer", fontSize: "1.5rem", padding: "8px" }}>
          {iconLabel}
          {totalItems > 0 && (
            <span style={{
              position: "absolute", top: 0, right: 0,
              background: "#C1652F", color: "#fff", fontSize: "10px", fontWeight: 700,
              minWidth: "18px", height: "18px", borderRadius: "999px",
              display: "inline-flex", alignItems: "center", justifyContent: "center", padding: "0 4px",
            }}>
              {totalItems}
            </span>
          )}
        </button>

        {open && showItems === "true" && (
          <div style={{
            position: "absolute", top: "100%", right: 0, width: "320px",
            background: "#fff", borderRadius: "12px",
            boxShadow: "0 10px 40px rgba(0,0,0,0.15)", padding: "16px",
            zIndex: 100, marginTop: "8px",
          }}>
            {loading ? (
              <div style={{ color: "#888", textAlign: "center", padding: "1rem" }}>Chargement...</div>
            ) : lines.length === 0 ? (
              <div style={{ textAlign: "center", color: "#888", padding: "1rem" }}>Panier vide</div>
            ) : (
              <>
                {lines.slice(0, 3).map((l) => (
                  <div key={l.id} style={{ display: "flex", gap: "12px", padding: "8px 0", borderBottom: "1px solid #eee" }}>
                    <div style={{ width: 50, height: 50, borderRadius: "6px", overflow: "hidden", background: "#f5f5f5" }}>
                      <img src={l.image_url || "/fallbacks/product-fallback.jpg"} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: "0.9rem", fontWeight: 600 }}>{l.product_name}</div>
                      <div style={{ fontSize: "0.8rem", color: "#6B6259" }}>× {l.quantity}</div>
                    </div>
                    <div style={{ fontWeight: 600, fontSize: "0.9rem" }}>
                      {formatPrice((l.unit_price || 0) * l.quantity, cart.currency)}
                    </div>
                  </div>
                ))}
                <div style={{ display: "flex", gap: "8px", marginTop: "12px" }}>
                  <Link to="/panier" className="btn btn-ghost" style={{ flex: 1, textAlign: "center", padding: "8px", textDecoration: "none" }}>Voir</Link>
                  <Link to="/commande" className="btn btn-primary" style={{ flex: 1, textAlign: "center", padding: "8px", textDecoration: "none" }}>Commander</Link>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    );
  },
};
'''


# ============================================================
#              PATCH DU CONFIG (append safe)
# ============================================================

MARKER = "/* === PHASE 11 WIDGETS === */"


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    label = os.path.relpath(path, BASE_DIR)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read().strip() == content.strip():
                print(f"  [SKIP] {label}")
                return False
        shutil.copy2(path, path + ".bak")
        print(f"  [BACKUP] {label}.bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {label}")
    return True


def update_config():
    config_path = os.path.join(SRC_DIR, "puck", "config.jsx")
    if not os.path.exists(config_path):
        print("  [ERREUR] config.jsx introuvable.")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    if MARKER in content:
        print("  [SKIP] config.jsx déjà patché Phase 11")
        return

    shutil.copy2(config_path, config_path + ".bak")
    print("  [BACKUP] config.jsx.bak")

    # Imports (ajoutés après le dernier import)
    imports = (
        f'\n{MARKER}\n'
        f'import {{\n'
        f'  ProductTitle, ProductImages, ProductPrice, AddToCart,\n'
        f'  ProductRating, ProductStock, ProductMeta, ShortDescription,\n'
        f'  ProductContent, ProductDataTabs, ProductGrid, Upsells,\n'
        f'  RelatedProducts, ProductCategories,\n'
        f'}} from "./widgets/productWidgets";\n'
        f'import {{\n'
        f'  Cart, Checkout, PurchaseSummary, MyAccount,\n'
        f'  WcBreadcrumbs, MenuCartExtended,\n'
        f'}} from "./widgets/commerceWidgets";\n'
        f'{MARKER}\n'
    )

    # Insérer après le dernier import (avant la première déclaration const)
    const_match = re.search(r'^const\s+\w+', content, re.MULTILINE)
    if const_match:
        content = content[:const_match.start()] + imports + "\n" + content[const_match.start():]
    else:
        content = imports + content

    # Ajouter les composants dans puckConfig.components
    new_components = (
        "    // === Phase 11 : Produit ===\n"
        "    ProductTitle, ProductImages, ProductPrice, AddToCart,\n"
        "    ProductRating, ProductStock, ProductMeta, ShortDescription,\n"
        "    ProductContent, ProductDataTabs, ProductGrid, Upsells,\n"
        "    RelatedProducts, ProductCategories,\n"
        "    // === Phase 11 : Commerce ===\n"
        "    Cart, Checkout, PurchaseSummary, MyAccount,\n"
        "    WcBreadcrumbs, MenuCartExtended,\n"
    )

    components_pattern = re.compile(
        r'(components:\s*\{)(.*?)(\n\s*\},\s*\n\s*categories:)',
        re.DOTALL,
    )
    match = components_pattern.search(content)
    if match:
        content = (
            content[: match.start(2)] + "\n" + new_components
            + match.group(2).rstrip() + "\n  "
            + content[match.start(3):]
        )
    else:
        print("  [ATTENTION] Structure 'components: {' non standard.")

    # Ajouter les catégories
    new_categories = (
        '    productEcommerce: { title: "Produit", components: [\n'
        '      "ProductTitle", "ProductImages", "ProductPrice", "AddToCart",\n'
        '      "ProductRating", "ProductStock", "ProductMeta", "ShortDescription",\n'
        '      "ProductContent", "ProductDataTabs",\n'
        '    ]},\n'
        '    shopEcommerce: { title: "Boutique", components: [\n'
        '      "ProductGrid", "Upsells", "RelatedProducts", "ProductCategories",\n'
        '    ]},\n'
        '    cartEcommerce: { title: "Panier & Commande", components: [\n'
        '      "Cart", "Checkout", "PurchaseSummary", "MenuCartExtended",\n'
        '    ]},\n'
        '    accountEcommerce: { title: "Compte & Navigation", components: [\n'
        '      "MyAccount", "WcBreadcrumbs",\n'
        '    ]},\n'
    )

    cat_pattern = re.compile(r'(categories:\s*\{)(.*?)(\n\s*\},)', re.DOTALL)
    cat_match = cat_pattern.search(content)
    if cat_match:
        content = (
            content[: cat_match.start(2)] + "\n" + new_categories
            + cat_match.group(2) + content[cat_match.start(3):]
        )

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] config.jsx patché (20 widgets + 4 catégories)")


# ============================================================
#                    MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  PHASE 11 — WIDGETS E-COMMERCE")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable dans {BASE_DIR}")
        return

    print("\n[1/4] Création des hooks E-commerce...")
    write_file(os.path.join(HOOKS_DIR, "useProductContext.jsx"), PRODUCT_HOOKS)

    print("\n[2/4] Création des widgets Produit (14)...")
    write_file(os.path.join(WIDGETS_DIR, "productWidgets.jsx"), PRODUCT_WIDGETS_JSX)

    print("\n[3/4] Création des widgets Commerce (6)...")
    write_file(os.path.join(WIDGETS_DIR, "commerceWidgets.jsx"), COMMERCE_WIDGETS_JSX)

    print("\n[4/4] Mise à jour de puckConfig...")
    update_config()

    print("\n" + "=" * 60)
    print("  ✅ PHASE 11 — 20 WIDGETS AJOUTÉS")
    print("=" * 60)
    print("\nProduit (10) :")
    print("  ProductTitle, ProductImages, ProductPrice, AddToCart,")
    print("  ProductRating, ProductStock, ProductMeta, ShortDescription,")
    print("  ProductContent, ProductDataTabs")
    print("\nBoutique (4) :")
    print("  ProductGrid, Upsells, RelatedProducts, ProductCategories")
    print("\nPanier & Commande (4) :")
    print("  Cart, Checkout, PurchaseSummary, MenuCartExtended")
    print("\nCompte & Navigation (2) :")
    print("  MyAccount, WcBreadcrumbs")


if __name__ == "__main__":
    main()