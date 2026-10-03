/**
 * Phase 11 — Widgets Produit (13 composants).
 */
import { apiFetch } from "../../utils/apiClient";
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
        const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1] || "";
const res = await fetch("/api/v1/cart/lines/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-CSRFToken": csrfToken,
  },
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
