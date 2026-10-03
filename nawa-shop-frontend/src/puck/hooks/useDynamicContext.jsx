/**
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
