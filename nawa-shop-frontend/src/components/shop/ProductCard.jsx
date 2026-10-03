import { Link } from "react-router-dom";
import { formatPrice } from "../../utils.js";

export default function ProductCard({ product }) {
  return (
    <Link to={`/produit/${product.slug}`} className="product-card">
      <div className="product-card-media">
        {product.coverImage ? (
          <img src={product.coverImage} alt={product.name} loading="lazy" />
        ) : (
          <div className="media-placeholder" />
        )}
        {!product.inStock && <span className="badge badge-muted">Épuisé</span>}
        {product.isFeatured && product.inStock && <span className="badge">Coup de cœur</span>}
      </div>
      <div className="product-card-body">
        {product.brand && <span className="product-card-brand">{product.brand.name}</span>}
        <h3 className="product-card-name">{product.name}</h3>
        <div className="product-card-meta">
          <span className="price">{formatPrice(product.price, product.currency)}</span>
          {product.ratingAverage > 0 && <span className="rating">★ {product.ratingAverage}</span>}
        </div>
      </div>
    </Link>
  );
}
