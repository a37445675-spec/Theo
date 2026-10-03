import { useEffect, useState } from "react";
import { getProducts } from "../../api/catalog.js";
import ProductCard from "../shop/ProductCard.jsx";
import { SkeletonGrid } from "../Skeleton.jsx";
import { ErrorState } from "../StateBlocks.jsx";

export default function ProductGridBlock({ config }) {
  const [products, setProducts] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const params = {};
    if (config?.source === "featured") params.isFeatured = true;
    if (config?.category) params.category = config.category;
    params.ordering = config?.ordering || "-createdAt";
    getProducts(params)
      .then((data) => setProducts((data.results ?? data).slice(0, config?.columns ? config.columns * 2 : 8)))
      .catch(setError);
  }, [config]);

  return (
    <section className="section">
      <div className="container">
        {config?.title && (
          <div className="section-header-row">
            <h2>{config.title}</h2>
          </div>
        )}
        {error && <ErrorState onRetry={() => window.location.reload()} />}
        {!error && !products && <SkeletonGrid count={config?.columns || 4} />}
        {!error && products && products.length === 0 && <p className="muted">Aucun produit à afficher pour le moment.</p>}
        {!error && products && products.length > 0 && (
          <div className="product-grid stagger">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
