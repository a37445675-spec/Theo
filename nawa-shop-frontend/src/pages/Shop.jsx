import { useEffect, useMemo, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { getCategoryAttributes, getProducts } from "../api/catalog.js";
import ProductCard from "../components/shop/ProductCard.jsx";
import CategoryFilterSidebar from "../components/shop/CategoryFilterSidebar.jsx";
import { SkeletonGrid } from "../components/Skeleton.jsx";
import { EmptyState, ErrorState } from "../components/StateBlocks.jsx";
import SEO from "../components/SEO.jsx";

const CATEGORY_TITLES = {
  cosmetiques: "Cosmétiques naturels",
  vetements: "Vêtements",
  chaussures: "Chaussures",
  electromenager: "Électroménager",
};

export default function Shop() {
  const { categorySlug } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const [attributeSet, setAttributeSet] = useState(null);
  const [products, setProducts] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const search = searchParams.get("q") || "";
  const ordering = searchParams.get("ordering") || "-createdAt";

  const activeFilters = useMemo(() => {
    const entries = {};
    for (const [key, value] of searchParams.entries()) {
      if (!["q", "ordering"].includes(key)) entries[key] = value;
    }
    return entries;
  }, [searchParams]);

  useEffect(() => {
    getCategoryAttributes(categorySlug)
      .then((data) => setAttributeSet(data.attributeSet))
      .catch(() => setAttributeSet(null));
  }, [categorySlug]);

  useEffect(() => {
    setLoading(true);
    setError(null);
    const params = { category: categorySlug, ordering, ...activeFilters };
    if (search) params.search = search;
    getProducts(params)
      .then((data) => setProducts(data.results ?? data))
      .catch(setError)
      .finally(() => setLoading(false));
  }, [categorySlug, ordering, search, JSON.stringify(activeFilters)]);

  function updateFilters(nextFilters) {
    const next = new URLSearchParams();
    if (search) next.set("q", search);
    next.set("ordering", ordering);
    Object.entries(nextFilters).forEach(([key, value]) => {
      if (value) next.set(key, value);
    });
    setSearchParams(next);
  }

  const title = CATEGORY_TITLES[categorySlug] || categorySlug;

  return (
    <>
      <SEO title={`${title} — NAWA`} description={`Découvrez notre sélection ${title.toLowerCase()} sur NAWA.`} />

      <section className="page-header">
        <div className="container">
          <span className="eyebrow">Boutique</span>
          <h1>{title}</h1>
        </div>
      </section>

      <section className="section">
        <div className="container shop-layout">
          <CategoryFilterSidebar attributeSet={attributeSet} activeFilters={activeFilters} onChange={updateFilters} onClear={() => updateFilters({})} />

          <div className="shop-main">
            <div className="shop-toolbar">
              <span className="muted">{products ? `${products.length} produit(s)` : "Chargement…"}</span>
              <label>
                Trier par
                <select value={ordering} onChange={(e) => setSearchParams((prev) => { const p = new URLSearchParams(prev); p.set("ordering", e.target.value); return p; })}>
                  <option value="-createdAt">Nouveautés</option>
                  <option value="price">Prix croissant</option>
                  <option value="-price">Prix décroissant</option>
                  <option value="-ratingAverage">Mieux notés</option>
                </select>
              </label>
            </div>

            {loading && <SkeletonGrid count={8} />}
            {error && <ErrorState onRetry={() => window.location.reload()} />}
            {!loading && !error && products?.length === 0 && (
              <EmptyState icon="🔍" title="Aucun produit ne correspond à ces filtres" action={<button className="btn btn-ghost" onClick={() => updateFilters({})}>Réinitialiser les filtres</button>} />
            )}
            {!loading && !error && products?.length > 0 && (
              <div className="product-grid stagger">
                {products.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            )}
          </div>
        </div>
      </section>
    </>
  );
}
