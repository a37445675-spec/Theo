/**
 * Phase 10 — Widgets Post (7 composants).
 * Contexte : article en cours de lecture.
 */
import { apiFetch } from "../../utils/apiClient";
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

    const wordCount = (post.content || "").split(/\s+/).length;
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
