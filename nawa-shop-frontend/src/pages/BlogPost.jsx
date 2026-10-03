import { useState } from "react";
import { useParams } from "react-router-dom";
import { useFetch } from "../hooks/useFetch.js";
import { createComment, getPost } from "../api/blog.js";
import { extractErrorMessage } from "../api/client.js";
import { formatDate } from "../utils.js";
import { ErrorState } from "../components/StateBlocks.jsx";
import { SkeletonGrid } from "../components/Skeleton.jsx";
import SEO from "../components/SEO.jsx";

export default function BlogPost() {
  const { slug } = useParams();
  const { data: post, loading, error, refetch } = useFetch(() => getPost(slug), [slug]);
  const [form, setForm] = useState({ authorName: "", authorEmail: "", content: "" });
  const [sent, setSent] = useState(false);
  const [commentError, setCommentError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (loading) return <div className="container" style={{ padding: "60px 0" }}><SkeletonGrid count={1} /></div>;
  if (error || !post) return <div className="container" style={{ padding: "60px 0" }}><ErrorState title="Article introuvable" onRetry={refetch} /></div>;

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setCommentError("");
    try {
      await createComment({ post: post.id, ...form });
      setSent(true);
      setForm({ authorName: "", authorEmail: "", content: "" });
    } catch (err) {
      setCommentError(extractErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <SEO title={`${post.title} — Journal NAWA`} description={post.metaDescription || post.excerpt} />

      <article className="section blog-post-container">
        <div className="container">
          {post.category && <span className="blog-cluster">{post.category.name}</span>}
          <h1>{post.title}</h1>
          <p className="muted">{formatDate(post.publishedAt)}</p>
          <div className="blog-post-body">
            {post.content.split("\n").filter(Boolean).map((paragraph, i) => <p key={i}>{paragraph}</p>)}
          </div>

          <h2 style={{ marginTop: 48 }}>Commentaires ({post.comments.length})</h2>
          {post.comments.length === 0 && <p className="muted">Soyez le premier à commenter cet article.</p>}
          <ul className="order-list" style={{ marginBottom: 32 }}>
            {post.comments.map((comment, i) => (
              <li key={i} style={{ flexDirection: "column", alignItems: "flex-start" }}>
                <strong>{comment.authorName}</strong>
                <span>{comment.content}</span>
                <span className="muted">{formatDate(comment.createdAt)}</span>
              </li>
            ))}
          </ul>

          {sent ? (
            <p className="newsletter-success">Merci, votre commentaire a été soumis et sera publié après modération.</p>
          ) : (
            <form className="auth-form" onSubmit={handleSubmit}>
              {commentError && <p className="promo-error">{commentError}</p>}
              <label>Nom<input required value={form.authorName} onChange={(e) => setForm((f) => ({ ...f, authorName: e.target.value }))} /></label>
              <label>Email<input required type="email" value={form.authorEmail} onChange={(e) => setForm((f) => ({ ...f, authorEmail: e.target.value }))} /></label>
              <label>Commentaire<textarea required rows={4} value={form.content} onChange={(e) => setForm((f) => ({ ...f, content: e.target.value }))} /></label>
              <button type="submit" className="btn btn-primary" disabled={submitting}>{submitting ? "Envoi…" : "Publier le commentaire"}</button>
            </form>
          )}
        </div>
      </article>
    </>
  );
}
