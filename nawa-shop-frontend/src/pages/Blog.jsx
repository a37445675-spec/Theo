import { useState } from "react";
import { Link } from "react-router-dom";
import { useFetch } from "../hooks/useFetch.js";
import { getBlogCategories, getPosts } from "../api/blog.js";
import { formatDate, truncate } from "../utils.js";
import { EmptyState, ErrorState } from "../components/StateBlocks.jsx";
import { SkeletonGrid } from "../components/Skeleton.jsx";
import SEO from "../components/SEO.jsx";

export default function Blog() {
  const [activeCategory, setActiveCategory] = useState("");
  const { data: categories } = useFetch(getBlogCategories, []);
  const { data: posts, loading, error, refetch } = useFetch(
    () => getPosts(activeCategory ? { category__slug: activeCategory } : {}),
    [activeCategory]
  );

  return (
    <>
      <SEO title="Journal NAWA" description="Conseils beauté, mode et maison par l'équipe éditoriale NAWA." />

      <section className="page-header">
        <div className="container">
          <span className="eyebrow">Journal</span>
          <h1>Le journal NAWA</h1>
          <p>Rituels cheveux, soins de la peau, mode et astuces maison.</p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          {categories?.length > 0 && (
            <div className="filter-list" style={{ flexDirection: "row", flexWrap: "wrap", marginBottom: 32 }}>
              <button className={activeCategory === "" ? "active" : ""} onClick={() => setActiveCategory("")}>Tous</button>
              {categories.map((cat) => (
                <button key={cat.id} className={activeCategory === cat.slug ? "active" : ""} onClick={() => setActiveCategory(cat.slug)}>{cat.name}</button>
              ))}
            </div>
          )}

          {loading && <SkeletonGrid count={6} />}
          {error && <ErrorState onRetry={refetch} />}
          {!loading && !error && posts?.length === 0 && <EmptyState icon="📰" title="Aucun article pour le moment" />}
          {!loading && !error && posts?.length > 0 && (
            <div className="blog-grid stagger">
              {posts.map((post) => (
                <Link key={post.id} to={`/journal/${post.slug}`} className="blog-card">
                  {post.category && <span className="blog-cluster">{post.category.name}</span>}
                  <h2>{post.title}</h2>
                  <p className="muted">{truncate(post.excerpt, 120)}</p>
                  <span className="muted">{formatDate(post.publishedAt)}</span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  );
}
