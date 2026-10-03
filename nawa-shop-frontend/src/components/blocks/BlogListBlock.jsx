import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getPosts } from "../../api/blog.js";
import { formatDate, truncate } from "../../utils.js";
import { SkeletonGrid } from "../Skeleton.jsx";

export default function BlogListBlock({ config }) {
  const [posts, setPosts] = useState(null);

  useEffect(() => {
    getPosts()
      .then((data) => setPosts((data.results ?? data).slice(0, config?.limit || 3)))
      .catch(() => setPosts([]));
  }, [config]);

  return (
    <section className="section">
      <div className="container">
        <div className="section-header-row">
          <h2>Le journal NAWA</h2>
          <Link to="/journal" className="link-arrow">Tous les articles →</Link>
        </div>
        {!posts && <SkeletonGrid count={config?.limit || 3} />}
        {posts && posts.length === 0 && <p className="muted">Aucun article publié pour le moment.</p>}
        {posts && posts.length > 0 && (
          <div className="blog-grid stagger">
            {posts.map((post) => (
              <Link key={post.id} to={`/journal/${post.slug}`} className="blog-card">
                {post.category && <span className="blog-cluster">{post.category.name}</span>}
                <h3>{post.title}</h3>
                <p className="muted">{truncate(post.excerpt, 110)}</p>
                <span className="muted">{formatDate(post.publishedAt)}</span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
