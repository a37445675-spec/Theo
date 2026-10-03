"""
Phase 10 — Widgets Dynamiques (Post/Blog) : 17 widgets.
Connecte les widgets aux données réelles du backend.

Usage : python inject_phase10.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
WIDGETS_DIR = os.path.join(SRC_DIR, "puck", "widgets")
HOOKS_DIR = os.path.join(SRC_DIR, "puck", "hooks")


# ============================================================
#              HOOKS DYNAMIQUES (contexte)
# ============================================================

HOOKS_JSX = '''/**
 * Phase 10 — Hooks pour le contexte dynamique des widgets.
 * Détecte l'URL actuelle et fournit les données au reste de l'app.
 */
import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";

// ============================================================
//  Contexte global de route
// ============================================================

export function useRouteContext() {
  const location = useLocation();
  const params = useParams();
  const search = new URLSearchParams(location.search);

  const pathname = location.pathname;

  // Détection du type de page
  if (pathname.startsWith("/journal/") && params.slug) {
    return { type: "post", slug: params.slug, categorySlug: null };
  }
  if (pathname.startsWith("/journal") || pathname.startsWith("/blog")) {
    return {
      type: "archive",
      categorySlug: search.get("category") || null,
      tagSlug: search.get("tag") || null,
      authorId: search.get("author") || null,
      searchQuery: search.get("q") || null,
    };
  }
  if (pathname.startsWith("/boutique/")) {
    return { type: "shop", categorySlug: params.categorySlug || null };
  }
  if (pathname.startsWith("/produit/")) {
    return { type: "product", slug: params.slug || null };
  }
  if (pathname === "/") {
    return { type: "home" };
  }
  return { type: "page" };
}

// ============================================================
//  Post courant (depuis le slug de l'URL)
// ============================================================

const postCache = new Map();

export function useCurrentPost(explicitSlug) {
  const { slug: routeSlug } = useParams();
  const slug = explicitSlug || routeSlug;
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!slug) {
      setLoading(false);
      return;
    }
    if (postCache.has(slug)) {
      setPost(postCache.get(slug));
      setLoading(false);
      return;
    }
    setLoading(true);
    fetch(`/api/v1/blog/posts/${slug}/`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        postCache.set(slug, data);
        setPost(data);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [slug]);

  return { post, loading, error };
}

// ============================================================
//  Config globale du site (logo, nom, tagline)
// ============================================================

let siteConfigCache = null;

export function useSiteConfig() {
  const [config, setConfig] = useState(siteConfigCache);
  const [loading, setLoading] = useState(!siteConfigCache);

  useEffect(() => {
    if (siteConfigCache) return;
    fetch("/api/v1/design-system/active/")
      .then((res) => (res.ok ? res.json() : {}))
      .then((data) => {
        siteConfigCache = data;
        setConfig(data);
      })
      .catch(() => setConfig({}))
      .finally(() => setLoading(false));
  }, []);

  return {
    config: config || {},
    siteName: config?.site_name || "NAWA",
    siteTagline: config?.site_tagline || "La beauté d'Afrique, sublimée.",
    logoUrl: config?.logo_principal || null,
    faviconUrl: config?.favicon || null,
    loading,
  };
}

// ============================================================
//  Archive de posts (avec filtres)
// ============================================================

export function useArchivePosts({ category, tag, author, search, limit = 9, page = 1 } = {}) {
  const [data, setData] = useState({ results: [], count: 0, loading: true, error: null });

  useEffect(() => {
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    if (tag) params.set("tag", tag);
    if (author) params.set("author", author);
    if (search) params.set("search", search);
    params.set("limit", limit);
    params.set("page", page);

    setData((d) => ({ ...d, loading: true }));

    fetch(`/api/v1/blog/posts/?${params.toString()}`)
      .then((res) => (res.ok ? res.json() : { results: [], count: 0 }))
      .then((json) => {
        const list = Array.isArray(json) ? json : json.results || [];
        setData({ results: list, count: json.count || list.length, loading: false, error: null });
      })
      .catch((err) => setData({ results: [], count: 0, loading: false, error: err.message }));
  }, [category, tag, author, search, limit, page]);

  return data;
}

// ============================================================
//  Categories & Tags
// ============================================================

export function useTaxonomies() {
  const [data, setData] = useState({ categories: [], tags: [], loading: true });

  useEffect(() => {
    Promise.all([
      fetch("/api/v1/blog/categories/").then((r) => (r.ok ? r.json() : [])).catch(() => []),
      fetch("/api/v1/blog/tags/").then((r) => (r.ok ? r.json() : [])).catch(() => []),
    ]).then(([cats, tags]) => {
      const catList = Array.isArray(cats) ? cats : cats.results || [];
      const tagList = Array.isArray(tags) ? tags : tags.results || [];
      setData({ categories: catList, tags: tagList, loading: false });
    });
  }, []);

  return data;
}

// ============================================================
//  Commentaires d'un post
// ============================================================

export function usePostComments(postId) {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!postId) {
      setLoading(false);
      return;
    }
    fetch(`/api/v1/blog/comments/?post=${postId}`)
      .then((res) => (res.ok ? res.json() : []))
      .then((json) => {
        const list = Array.isArray(json) ? json : json.results || [];
        setComments(list);
      })
      .catch(() => setComments([]))
      .finally(() => setLoading(false));
  }, [postId]);

  return { comments, loading };
}
'''


# ============================================================
#              POST WIDGETS (7)
# ============================================================

POST_WIDGETS_JSX = '''/**
 * Phase 10 — Widgets Post (7 composants).
 * Contexte : article en cours de lecture.
 */
import React from "react";
import { Link } from "react-router-dom";
import { useCurrentPost, usePostComments } from "../hooks/useDynamicContext";

function formatDate(dateStr) {
  if (!dateStr) return "";
  try {
    return new Date(dateStr).toLocaleDateString("fr-FR", {
      day: "numeric", month: "long", year: "numeric",
    });
  } catch {
    return dateStr;
  }
}

// ============================================================
//  POST TITLE — Titre de l'article courant
// ============================================================

export const PostTitle = {
  fields: {
    level: {
      type: "select", label: "Niveau",
      options: [
        { label: "H1", value: "h1" },
        { label: "H2", value: "h2" },
        { label: "H3", value: "h3" },
      ],
    },
    align: {
      type: "radio", label: "Alignement",
      options: [
        { label: "Gauche", value: "left" },
        { label: "Centre", value: "center" },
      ],
    },
    fallback: { type: "text", label: "Titre de secours", defaultValue: "Sans titre" },
  },
  defaultProps: { level: "h1", align: "left", fallback: "Sans titre" },
  render: ({ level, align, fallback }) => {
    const { post, loading } = useCurrentPost();
    const Tag = level;

    if (loading) return <div style={{ height: "2.5em", background: "#f5f5f5", borderRadius: 8 }} />;
    return (
      <Tag style={{ textAlign: align }}>
        {post?.title || fallback}
      </Tag>
    );
  },
};

// ============================================================
//  POST CONTENT — Contenu HTML de l'article
// ============================================================

export const PostContent = {
  fields: {
    className: { type: "text", label: "Classes CSS", defaultValue: "post-content" },
  },
  defaultProps: { className: "post-content" },
  render: ({ className }) => {
    const { post, loading } = useCurrentPost();
    if (loading) return <div style={{ padding: "2rem", color: "#888" }}>Chargement de l'article...</div>;
    if (!post) return <div style={{ padding: "2rem", color: "#888" }}>Aucun article.</div>;

    return (
      <div
        className={className}
        style={{ lineHeight: 1.8, color: "#221B15" }}
        dangerouslySetInnerHTML={{ __html: post.content || post.body || "<p>(Article vide)</p>" }}
      />
    );
  },
};

// ============================================================
//  POST EXCERPT — Extrait
// ============================================================

export const PostExcerpt = {
  fields: {
    length: { type: "number", label: "Longueur max (caractères)", defaultValue: 200 },
    showReadMore: {
      type: "radio", label: "Afficher 'Lire la suite'",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
  },
  defaultProps: { length: 200, showReadMore: "false" },
  render: ({ length, showReadMore }) => {
    const { post } = useCurrentPost();
    const text = post?.excerpt || post?.summary || (post?.content || "").replace(/<[^>]*>/g, "");
    const excerpt = text.slice(0, length) + (text.length > length ? "…" : "");

    return (
      <div>
        <p style={{ color: "#6B6259", fontStyle: "italic", lineHeight: 1.6 }}>{excerpt}</p>
        {showReadMore === "true" && post?.slug && (
          <Link to={`/journal/${post.slug}`} style={{ color: "#C1652F", fontWeight: 600 }}>
            Lire la suite →
          </Link>
        )}
      </div>
    );
  },
};

// ============================================================
//  POST INFO — Auteur / date / catégorie
// ============================================================

export const PostInfo = {
  fields: {
    showAuthor: {
      type: "radio", label: "Auteur",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    showDate: {
      type: "radio", label: "Date",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    showCategory: {
      type: "radio", label: "Catégorie",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    showReadingTime: {
      type: "radio", label: "Temps de lecture",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    showAuthor: "true", showDate: "true",
    showCategory: "true", showReadingTime: "true",
  },
  render: ({ showAuthor, showDate, showCategory, showReadingTime }) => {
    const { post } = useCurrentPost();
    if (!post) return null;

    const wordCount = (post.content || "").split(/\\s+/).length;
    const readingTime = Math.max(1, Math.round(wordCount / 200));

    return (
      <div style={{
        display: "flex", gap: "16px", flexWrap: "wrap",
        color: "#6B6259", fontSize: "0.9rem", alignItems: "center",
      }}>
        {showAuthor === "true" && post.author_name && (
          <span>✍️ {post.author_name}</span>
        )}
        {showDate === "true" && post.published_at && (
          <span>📅 {formatDate(post.published_at)}</span>
        )}
        {showCategory === "true" && post.category_name && (
          <span>🏷 {post.category_name}</span>
        )}
        {showReadingTime === "true" && (
          <span>⏱ {readingTime} min de lecture</span>
        )}
      </div>
    );
  },
};

// ============================================================
//  POST NAVIGATION — Précédent / Suivant
// ============================================================

export const PostNavigation = {
  fields: {
    prevLabel: { type: "text", label: "Libellé précédent", defaultValue: "← Précédent" },
    nextLabel: { type: "text", label: "Libellé suivant", defaultValue: "Suivant →" },
  },
  defaultProps: { prevLabel: "← Précédent", nextLabel: "Suivant →" },
  render: ({ prevLabel, nextLabel }) => {
    const { post } = useCurrentPost();
    if (!post) return null;

    return (
      <nav style={{ display: "flex", justifyContent: "space-between", gap: "16px", marginTop: "32px" }}>
        {post.previous ? (
          <Link
            to={`/journal/${post.previous.slug}`}
            style={{
              flex: 1, padding: "16px", background: "#F7F0E4",
              borderRadius: "12px", textDecoration: "none", color: "#221B15",
            }}
          >
            <div style={{ fontSize: "0.8rem", color: "#C1652F", fontWeight: 600, marginBottom: "4px" }}>
              {prevLabel}
            </div>
            <div style={{ fontWeight: 600 }}>{post.previous.title}</div>
          </Link>
        ) : <div style={{ flex: 1 }} />}
        {post.next ? (
          <Link
            to={`/journal/${post.next.slug}`}
            style={{
              flex: 1, padding: "16px", background: "#F7F0E4",
              borderRadius: "12px", textDecoration: "none", color: "#221B15", textAlign: "right",
            }}
          >
            <div style={{ fontSize: "0.8rem", color: "#C1652F", fontWeight: 600, marginBottom: "4px" }}>
              {nextLabel}
            </div>
            <div style={{ fontWeight: 600 }}>{post.next.title}</div>
          </Link>
        ) : <div style={{ flex: 1 }} />}
      </nav>
    );
  },
};

// ============================================================
//  POST COMMENTS — Commentaires de l'article
// ============================================================

export const PostComments = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Commentaires" },
    showForm: {
      type: "radio", label: "Formulaire",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: { title: "Commentaires", showForm: "true" },
  render: ({ title, showForm }) => {
    const { post } = useCurrentPost();
    const { comments, loading } = usePostComments(post?.id);

    if (!post) return null;

    return (
      <section style={{ marginTop: "48px" }}>
        <h3>{title} ({comments.length})</h3>
        {loading ? (
          <p style={{ color: "#888" }}>Chargement...</p>
        ) : comments.length === 0 ? (
          <p style={{ color: "#888" }}>Aucun commentaire pour le moment.</p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0 }}>
            {comments.map((c) => (
              <li key={c.id} style={{
                padding: "16px", background: "#F7F0E4",
                borderRadius: "12px", marginBottom: "12px",
              }}>
                <div style={{ fontWeight: 600, marginBottom: "6px" }}>
                  {c.author_name || c.author || "Anonyme"}
                </div>
                <div style={{ color: "#6B6259", fontSize: "0.9rem", lineHeight: 1.6 }}>
                  {c.content || c.body}
                </div>
                {c.created_at && (
                  <div style={{ fontSize: "0.75rem", color: "#999", marginTop: "6px" }}>
                    {formatDate(c.created_at)}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
        {showForm === "true" && (
          <div style={{ marginTop: "24px", padding: "20px", background: "#F7F0E4", borderRadius: "12px" }}>
            <div style={{ fontWeight: 600, marginBottom: "12px" }}>Laisser un commentaire</div>
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <input
                type="text"
                placeholder="Votre nom"
                style={{ padding: "10px 14px", border: "1px solid #ddd", borderRadius: "8px" }}
              />
              <textarea
                placeholder="Votre commentaire..."
                rows={4}
                style={{ padding: "10px 14px", border: "1px solid #ddd", borderRadius: "8px", fontFamily: "inherit" }}
              />
              <button className="btn btn-primary" style={{ alignSelf: "flex-start" }}>
                Envoyer
              </button>
            </div>
          </div>
        )}
      </section>
    );
  },
};

// ============================================================
//  AUTHOR BOX — Bloc auteur
// ============================================================

export const AuthorBox = {
  fields: {
    showAvatar: {
      type: "radio", label: "Avatar",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    showBio: {
      type: "radio", label: "Bio",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: { showAvatar: "true", showBio: "true" },
  render: ({ showAvatar, showBio }) => {
    const { post } = useCurrentPost();
    if (!post?.author_name) return null;

    const initials = post.author_name
      .split(" ").map((s) => s[0]).join("").slice(0, 2).toUpperCase();

    return (
      <div style={{
        display: "flex", gap: "16px", padding: "20px",
        background: "#F7F0E4", borderRadius: "16px", marginTop: "32px",
      }}>
        {showAvatar === "true" && (
          <div style={{
            width: 64, height: 64, borderRadius: "50%",
            background: "#C1652F", color: "#fff",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "1.4rem", fontWeight: 700, flexShrink: 0,
          }}>
            {post.author_avatar_url ? (
              <img src={post.author_avatar_url} alt="" style={{ width: "100%", height: "100%", borderRadius: "50%", objectFit: "cover" }} />
            ) : initials}
          </div>
        )}
        <div>
          <div style={{ fontWeight: 700, marginBottom: "4px" }}>{post.author_name}</div>
          {showBio === "true" && post.author_bio && (
            <p style={{ color: "#6B6259", fontSize: "0.9rem", margin: 0, lineHeight: 1.6 }}>
              {post.author_bio}
            </p>
          )}
        </div>
      </div>
    );
  },
};
'''


# ============================================================
#          ARCHIVE & SITE WIDGETS (10)
# ============================================================

ARCHIVE_WIDGETS_JSX = '''/**
 * Phase 10 — Widgets Archive & Site (10 composants).
 * Contexte : listes, catégories, recherche, identité du site.
 */
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
'''


# ============================================================
#              PATCH DU CONFIG
# ============================================================

MARKER = "/* === PHASE 10 WIDGETS === */"


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
        print("  [SKIP] config.jsx déjà patché Phase 10")
        return

    shutil.copy2(config_path, config_path + ".bak")
    print(f"  [BACKUP] config.jsx.bak")

    imports = (
        f"\n{MARKER}\n"
        'import {\n'
        '  PostTitle, PostContent, PostExcerpt, PostInfo,\n'
        '  PostNavigation, PostComments, AuthorBox,\n'
        '} from "./widgets/postWidgets";\n'
        'import {\n'
        '  ArchiveTitle, ArchivePosts, Breadcrumbs, LoopGrid, LoopCarousel,\n'
        '  Taxonomy, SiteLogo, SiteTitle, SitelinkSearch, PostPortfolio,\n'
        '} from "./widgets/archiveWidgets";\n'
        f"{MARKER}\n"
    )

    content = re.sub(
        r'(import React from "react";\n)',
        r'\1' + imports,
        content,
        count=1,
    )

    new_components = (
        "    // === Phase 10 : Post dynamique ===\n"
        "    PostTitle, PostContent, PostExcerpt, PostInfo,\n"
        "    PostNavigation, PostComments, AuthorBox,\n"
        "    // === Phase 10 : Archive & Site ===\n"
        "    ArchiveTitle, ArchivePosts, Breadcrumbs, LoopGrid, LoopCarousel,\n"
        "    Taxonomy, SiteLogo, SiteTitle, SitelinkSearch, PostPortfolio,\n"
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

    new_categories = (
        '    postDynamic: { title: "Article (dynamique)", components: [\n'
        '      "PostTitle", "PostContent", "PostExcerpt", "PostInfo",\n'
        '      "PostNavigation", "PostComments", "AuthorBox",\n'
        '    ]},\n'
        '    archiveDynamic: { title: "Archive & Liste", components: [\n'
        '      "ArchiveTitle", "ArchivePosts", "Breadcrumbs",\n'
        '      "LoopGrid", "LoopCarousel", "Taxonomy", "PostPortfolio",\n'
        '    ]},\n'
        '    siteIdentity: { title: "Identité du site", components: [\n'
        '      "SiteLogo", "SiteTitle", "SitelinkSearch",\n'
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
    print("  [OK] config.jsx patché (17 widgets + 3 catégories)")


# ============================================================
#                    MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  PHASE 10 — WIDGETS DYNAMIQUES (Post/Blog)")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable dans {BASE_DIR}")
        return

    print("\n[1/4] Création des hooks dynamiques...")
    write_file(os.path.join(HOOKS_DIR, "useDynamicContext.jsx"), HOOKS_JSX)

    print("\n[2/4] Création des widgets Post (7)...")
    write_file(os.path.join(WIDGETS_DIR, "postWidgets.jsx"), POST_WIDGETS_JSX)

    print("\n[3/4] Création des widgets Archive & Site (10)...")
    write_file(os.path.join(WIDGETS_DIR, "archiveWidgets.jsx"), ARCHIVE_WIDGETS_JSX)

    print("\n[4/4] Mise à jour de puckConfig...")
    update_config()

    print("\n" + "=" * 60)
    print("  ✅ PHASE 10 — 17 WIDGETS AJOUTÉS")
    print("=" * 60)
    print("\nArticle dynamique (7) :")
    print("  PostTitle, PostContent, PostExcerpt, PostInfo,")
    print("  PostNavigation, PostComments, AuthorBox")
    print("\nArchive & Liste (7) :")
    print("  ArchiveTitle, ArchivePosts, Breadcrumbs, LoopGrid,")
    print("  LoopCarousel, Taxonomy, PostPortfolio")
    print("\nIdentité du site (3) :")
    print("  SiteLogo, SiteTitle, SitelinkSearch")


if __name__ == "__main__":
    main()