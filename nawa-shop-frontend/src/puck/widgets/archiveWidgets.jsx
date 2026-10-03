/**
 * Phase 10 — Widgets Archive & Site (10 composants).
 * Contexte : listes, catégories, recherche, identité du site.
 */
import { apiFetch } from "../../utils/apiClient";
import React from "react";
import { Link } from "react-router-dom";
import {
  useRouteContext,
  useArchivePosts,
  useTaxonomies,
  useSiteConfig,
} from "../hooks/useDynamicContext";

function formatDate(d) {
  if (!d) return "";
  try { return new Date(d).toLocaleDateString("fr-FR", { day: "numeric", month: "short", year: "numeric" }); }
  catch { return d; }
}

// ============================================================
//  ARCHIVE TITLE — Titre de l'archive
// ============================================================

export const ArchiveTitle = {
  fields: {
    prefix: { type: "text", label: "Préfixe", defaultValue: "" },
    defaultTitle: { type: "text", label: "Titre par défaut", defaultValue: "Le Journal" },
  },
  defaultProps: { prefix: "", defaultTitle: "Le Journal" },
  render: ({ prefix, defaultTitle }) => {
    const ctx = useRouteContext();
    let title = defaultTitle;
    if (ctx.type === "archive") {
      if (ctx.categorySlug) title = `Catégorie : ${ctx.categorySlug}`;
      else if (ctx.tagSlug) title = `Tag : ${ctx.tagSlug}`;
      else if (ctx.searchQuery) title = `Recherche : "${ctx.searchQuery}"`;
    }
    return <h1>{prefix} {title}</h1>;
  },
};

// ============================================================
//  ARCHIVE POSTS — Liste paginée
// ============================================================

export const ArchivePosts = {
  fields: {
    columns: { type: "number", label: "Colonnes", defaultValue: 3 },
    limit: { type: "number", label: "Articles par page", defaultValue: 9 },
    showImage: {
      type: "radio", label: "Afficher l'image",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    showExcerpt: {
      type: "radio", label: "Afficher l'extrait",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: { columns: 3, limit: 9, showImage: "true", showExcerpt: "true" },
  render: ({ columns, limit, showImage, showExcerpt }) => {
    const ctx = useRouteContext();
    const { results, count, loading } = useArchivePosts({
      category: ctx.categorySlug,
      tag: ctx.tagSlug,
      author: ctx.authorId,
      search: ctx.searchQuery,
      limit,
    });

    if (loading) return <div style={{ padding: "2rem", textAlign: "center", color: "#888" }}>Chargement...</div>;
    if (!results.length) return <div style={{ padding: "2rem", textAlign: "center", color: "#888" }}>Aucun article.</div>;

    return (
      <div>
        <div style={{
          display: "grid",
          gridTemplateColumns: `repeat(auto-fill, minmax(${280}px, 1fr))`,
          gap: "24px",
        }}>
          {results.map((post) => (
            <Link
              key={post.id}
              to={`/journal/${post.slug}`}
              style={{ textDecoration: "none", color: "inherit" }}
            >
              <article style={{
                background: "#fff", borderRadius: "16px",
                overflow: "hidden", boxShadow: "0 2px 12px rgba(0,0,0,0.06)",
                transition: "transform 0.2s",
              }}>
                {showImage === "true" && post.image_url && (
                  <img
                    src={post.image_url}
                    alt={post.title}
                    style={{ width: "100%", aspectRatio: "16/9", objectFit: "cover" }}
                  />
                )}
                <div style={{ padding: "20px" }}>
                  <h3 style={{ marginBottom: "8px", fontSize: "1.1rem" }}>{post.title}</h3>
                  {showExcerpt === "true" && post.excerpt && (
                    <p style={{ color: "#6B6259", fontSize: "0.9rem", lineHeight: 1.5 }}>
                      {post.excerpt.slice(0, 120)}…
                    </p>
                  )}
                  <div style={{ fontSize: "0.8rem", color: "#999", marginTop: "12px" }}>
                    {formatDate(post.published_at)}
                  </div>
                </div>
              </article>
            </Link>
          ))}
        </div>
        <div style={{ textAlign: "center", marginTop: "24px", color: "#888", fontSize: "0.9rem" }}>
          {count} article{count > 1 ? "s" : ""} au total
        </div>
      </div>
    );
  },
};

// ============================================================
//  BREADCRUMBS — Fil d'Ariane
// ============================================================

export const Breadcrumbs = {
  fields: {
    homeLabel: { type: "text", label: "Accueil", defaultValue: "Accueil" },
    separator: { type: "text", label: "Séparateur", defaultValue: "/" },
  },
  defaultProps: { homeLabel: "Accueil", separator: "/" },
  render: ({ homeLabel, separator }) => {
    const ctx = useRouteContext();
    const crumbs = [{ label: homeLabel, url: "/" }];

    if (ctx.type === "post" && ctx.slug) {
      crumbs.push({ label: "Journal", url: "/journal" });
      crumbs.push({ label: ctx.slug.replace(/-/g, " "), url: null });
    } else if (ctx.type === "archive") {
      crumbs.push({ label: "Journal", url: null });
    } else if (ctx.type === "shop" && ctx.categorySlug) {
      crumbs.push({ label: "Boutique", url: "/boutique" });
      crumbs.push({ label: ctx.categorySlug, url: null });
    } else if (ctx.type === "product") {
      crumbs.push({ label: "Produit", url: null });
    }

    return (
      <nav aria-label="breadcrumbs" style={{ fontSize: "0.85rem", color: "#6B6259", marginBottom: "16px" }}>
        {crumbs.map((c, i) => (
          <React.Fragment key={i}>
            {i > 0 && <span style={{ margin: "0 8px" }}>{separator}</span>}
            {c.url ? (
              <Link to={c.url} style={{ color: "#6B6259", textDecoration: "none" }}>{c.label}</Link>
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
//  LOOP GRID — Grille en boucle
// ============================================================

export const LoopGrid = {
  fields: {
    columns: { type: "number", label: "Colonnes", defaultValue: 3 },
    limit: { type: "number", label: "Nombre d'articles", defaultValue: 6 },
    source: {
      type: "select", label: "Source",
      options: [
        { label: "Derniers articles", value: "recent" },
        { label: "Articles vedettes", value: "featured" },
        { label: "Catégorie de l'URL", value: "current_category" },
      ],
    },
  },
  defaultProps: { columns: 3, limit: 6, source: "recent" },
  render: ({ columns, limit, source }) => {
    const ctx = useRouteContext();
    const category = source === "current_category" ? ctx.categorySlug : null;
    const { results, loading } = useArchivePosts({ category, limit });

    if (loading) return <div style={{ padding: "2rem", textAlign: "center", color: "#888" }}>Chargement...</div>;
    if (!results.length) return <div style={{ textAlign: "center", color: "#888", padding: "2rem" }}>Aucun article.</div>;

    return (
      <div style={{
        display: "grid",
        gridTemplateColumns: `repeat(auto-fit, minmax(${Math.floor(1200 / columns) - 20}px, 1fr))`,
        gap: "20px",
      }}>
        {results.map((post) => (
          <Link
            key={post.id}
            to={`/journal/${post.slug}`}
            style={{
              textDecoration: "none", color: "inherit",
              background: "#fff", borderRadius: "12px",
              overflow: "hidden", boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
            }}
          >
            {post.image_url && (
              <img src={post.image_url} alt={post.title} style={{ width: "100%", aspectRatio: "16/9", objectFit: "cover" }} />
            )}
            <div style={{ padding: "16px" }}>
              <h4 style={{ marginBottom: "6px", fontSize: "1rem" }}>{post.title}</h4>
              <div style={{ fontSize: "0.75rem", color: "#999" }}>{formatDate(post.published_at)}</div>
            </div>
          </Link>
        ))}
      </div>
    );
  },
};

// ============================================================
//  LOOP CAROUSEL — Carrousel d'articles
// ============================================================

export const LoopCarousel = {
  fields: {
    limit: { type: "number", label: "Nombre d'articles", defaultValue: 5 },
    interval: { type: "number", label: "Intervalle (ms)", defaultValue: 4000 },
  },
  defaultProps: { limit: 5, interval: 4000 },
  render: ({ limit, interval }) => {
    const { results } = useArchivePosts({ limit });
    const [index, setIndex] = React.useState(0);

    React.useEffect(() => {
      if (results.length <= 1) return;
      const id = setInterval(() => setIndex((i) => (i + 1) % results.length), interval);
      return () => clearInterval(id);
    }, [results.length, interval]);

    if (!results.length) return null;
    const post = results[index];

    return (
      <div style={{ position: "relative", borderRadius: "20px", overflow: "hidden", background: "#221B15", color: "#fff", minHeight: "400px" }}>
        {post.image_url && (
          <img src={post.image_url} alt="" style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", opacity: 0.4 }} />
        )}
        <div style={{ position: "relative", padding: "60px 40px", maxWidth: "700px" }}>
          <div style={{ fontSize: "0.85rem", color: "#D4A843", marginBottom: "8px" }}>
            {formatDate(post.published_at)}
          </div>
          <h2 style={{ fontSize: "2rem", marginBottom: "16px", color: "#fff" }}>{post.title}</h2>
          {post.excerpt && (
            <p style={{ opacity: 0.85, marginBottom: "24px", lineHeight: 1.6 }}>
              {post.excerpt.slice(0, 180)}…
            </p>
          )}
          <Link to={`/journal/${post.slug}`} className="btn btn-primary">
            Lire l'article
          </Link>
        </div>
        <div style={{ position: "absolute", bottom: 20, left: 40, display: "flex", gap: "6px" }}>
          {results.map((_, i) => (
            <button
              key={i}
              onClick={() => setIndex(i)}
              style={{
                width: i === index ? "24px" : "8px", height: "8px",
                borderRadius: "999px", border: "none",
                background: i === index ? "#D4A843" : "rgba(255,255,255,0.4)",
                cursor: "pointer", transition: "all 0.3s",
              }}
            />
          ))}
        </div>
      </div>
    );
  },
};

// ============================================================
//  TAXONOMY — Catégories / Tags
// ============================================================

export const Taxonomy = {
  fields: {
    taxonomyType: {
      type: "select", label: "Type",
      options: [
        { label: "Catégories", value: "categories" },
        { label: "Tags", value: "tags" },
      ],
    },
    display: {
      type: "radio", label: "Affichage",
      options: [
        { label: "Liste", value: "list" },
        { label: "Pills", value: "pills" },
      ],
    },
  },
  defaultProps: { taxonomyType: "categories", display: "pills" },
  render: ({ taxonomyType, display }) => {
    const { categories, tags } = useTaxonomies();
    const list = taxonomyType === "tags" ? tags : categories;

    if (!list.length) return <div style={{ color: "#888" }}>Aucune taxonomie.</div>;

    if (display === "pills") {
      return (
        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
          {list.map((t) => (
            <Link
              key={t.id || t.slug}
              to={`/journal?${taxonomyType === "tags" ? "tag" : "category"}=${t.slug}`}
              style={{
                padding: "8px 18px", borderRadius: "999px",
                background: "#F7F0E4", color: "#221B15",
                textDecoration: "none", fontSize: "0.9rem", fontWeight: 500,
              }}
            >
              {t.name}
            </Link>
          ))}
        </div>
      );
    }

    return (
      <ul style={{ listStyle: "none", padding: 0 }}>
        {list.map((t) => (
          <li key={t.id || t.slug} style={{ marginBottom: "8px" }}>
            <Link to={`/journal?${taxonomyType === "tags" ? "tag" : "category"}=${t.slug}`} style={{ color: "#221B15" }}>
              → {t.name}
            </Link>
          </li>
        ))}
      </ul>
    );
  },
};

// ============================================================
//  SITE LOGO — Logo dynamique
// ============================================================

export const SiteLogo = {
  fields: {
    height: { type: "text", label: "Hauteur", defaultValue: "40px" },
    linkHome: {
      type: "radio", label: "Lien vers l'accueil",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: { height: "40px", linkHome: "true" },
  render: ({ height, linkHome }) => {
    const { logoUrl, siteName } = useSiteConfig();

    const content = logoUrl ? (
      <img src={logoUrl} alt={siteName} style={{ height, width: "auto", display: "block" }} />
    ) : (
      <span style={{ fontSize: height, fontFamily: "var(--font-heading, serif)", fontWeight: 700 }}>
        {siteName}
      </span>
    );

    if (linkHome === "true") {
      return <Link to="/" style={{ textDecoration: "none", color: "inherit" }}>{content}</Link>;
    }
    return content;
  },
};

// ============================================================
//  SITE TITLE — Nom du site
// ============================================================

export const SiteTitle = {
  fields: {
    showTagline: {
      type: "radio", label: "Afficher le slogan",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    align: {
      type: "radio", label: "Alignement",
      options: [
        { label: "Gauche", value: "left" },
        { label: "Centre", value: "center" },
      ],
    },
  },
  defaultProps: { showTagline: "true", align: "left" },
  render: ({ showTagline, align }) => {
    const { siteName, siteTagline } = useSiteConfig();
    return (
      <div style={{ textAlign: align }}>
        <div style={{ fontSize: "1.5rem", fontWeight: 700 }}>{siteName}</div>
        {showTagline === "true" && (
          <div style={{ fontSize: "0.85rem", color: "#6B6259" }}>{siteTagline}</div>
        )}
      </div>
    );
  },
};

// ============================================================
//  SITELINK SEARCH — Recherche
// ============================================================

export const SitelinkSearch = {
  fields: {
    placeholder: { type: "text", label: "Placeholder", defaultValue: "Rechercher..." },
    buttonLabel: { type: "text", label: "Bouton", defaultValue: "Rechercher" },
    targetPath: { type: "text", label: "Chemin cible", defaultValue: "/journal" },
  },
  defaultProps: { placeholder: "Rechercher...", buttonLabel: "Rechercher", targetPath: "/journal" },
  render: ({ placeholder, buttonLabel, targetPath }) => {
    const [query, setQuery] = React.useState("");

    const submit = (e) => {
      e.preventDefault();
      if (!query.trim()) return;
      window.location.href = `${targetPath}?q=${encodeURIComponent(query.trim())}`;
    };

    return (
      <form onSubmit={submit} style={{ display: "flex", gap: "8px" }}>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          style={{
            flex: 1, padding: "10px 14px",
            border: "1px solid #ddd", borderRadius: "8px", fontSize: "1rem",
          }}
        />
        <button type="submit" className="btn btn-primary">{buttonLabel}</button>
      </form>
    );
  },
};

// ============================================================
//  POST PORTFOLIO — Article + Portfolio (mixte)
// ============================================================

export const PostPortfolio = {
  fields: {
    layout: {
      type: "select", label: "Mise en page",
      options: [
        { label: "Grille", value: "grid" },
        { label: "Masonry", value: "masonry" },
      ],
    },
    columns: { type: "number", label: "Colonnes", defaultValue: 3 },
    limit: { type: "number", label: "Nombre d'articles", defaultValue: 6 },
  },
  defaultProps: { layout: "grid", columns: 3, limit: 6 },
  render: ({ layout, columns, limit }) => {
    const { results } = useArchivePosts({ limit });
    if (!results.length) return null;

    return (
      <div style={{
        display: "grid",
        gridTemplateColumns: `repeat(${columns}, 1fr)`,
        gap: "16px",
      }}>
        {results.map((post) => (
          <Link
            key={post.id}
            to={`/journal/${post.slug}`}
            style={{
              textDecoration: "none", color: "#fff",
              position: "relative", borderRadius: "16px", overflow: "hidden",
              aspectRatio: layout === "masonry" && post.id % 2 === 0 ? "3/4" : "1/1",
            }}
          >
            {post.image_url && (
              <img src={post.image_url} alt={post.title} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            )}
            <div style={{
              position: "absolute", inset: 0,
              background: "linear-gradient(to top, rgba(0,0,0,0.75), transparent 50%)",
              display: "flex", flexDirection: "column", justifyContent: "flex-end", padding: "20px",
            }}>
              <div style={{ fontWeight: 700, fontSize: "1.05rem" }}>{post.title}</div>
              <div style={{ fontSize: "0.8rem", opacity: 0.85 }}>{formatDate(post.published_at)}</div>
            </div>
          </Link>
        ))}
      </div>
    );
  },
};
