import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useFetch } from "../hooks/useFetch.js";
import { getProduct } from "../api/catalog.js";
import { useCart } from "../context/CartContext.jsx";
import { attributeLabel, formatPrice } from "../utils.js";
import { ErrorState } from "../components/StateBlocks.jsx";
import { SkeletonGrid } from "../components/Skeleton.jsx";
import SEO from "../components/SEO.jsx";
import ButtonSpinner from "../components/ButtonSpinner.jsx";
import { Link as RouterLink } from "react-router-dom";

export default function ProductDetail() {
  const { slug } = useParams();
  const { data: product, loading, error, refetch } = useFetch(() => getProduct(slug), [slug]);
  const { addItem } = useCart();

  const [selectedAttrs, setSelectedAttrs] = useState({});
  const [quantity, setQuantity] = useState(1);
  const [activeImage, setActiveImage] = useState(0);
  const [adding, setAdding] = useState(false);
  const [addedMessage, setAddedMessage] = useState("");

  const variantOptions = useMemo(() => {
    if (!product?.variants?.length) return {};
    const options = {};
    for (const variant of product.variants) {
      for (const [code, value] of Object.entries(variant.attributes || {})) {
        options[code] = options[code] || new Set();
        options[code].add(value);
      }
    }
    return Object.fromEntries(Object.entries(options).map(([k, v]) => [k, Array.from(v)]));
  }, [product]);

  const matchedVariant = useMemo(() => {
    if (!product?.variants?.length) return null;
    return product.variants.find((variant) =>
      Object.entries(variant.attributes || {}).every(([code, value]) => selectedAttrs[code] === value)
    );
  }, [product, selectedAttrs]);

  if (loading) return <div className="container" style={{ padding: "60px 0" }}><SkeletonGrid count={1} /></div>;
  if (error || !product) {
    return <div className="container" style={{ padding: "60px 0" }}><ErrorState title="Produit introuvable" onRetry={refetch} /></div>;
  }

  const hasVariants = product.productType === "variant";
  const needsSelection = hasVariants && !matchedVariant;
  const images = product.images?.length ? product.images : [];
  const effectivePrice = matchedVariant?.effectivePrice ?? product.price;
  const inStock = hasVariants ? (matchedVariant ? matchedVariant.stock > 0 : true) : product.inStock;

  async function handleAddToCart() {
    if (needsSelection) return;
    setAdding(true);
    try {
      await addItem(product, matchedVariant, quantity);
      setAddedMessage("Ajouté au panier !");
      setTimeout(() => setAddedMessage(""), 2000);
    } finally {
      setAdding(false);
    }
  }

  const displayAttributes = Object.entries(product.attributes || {}).filter(([code]) => !Object.keys(variantOptions).includes(code));

  return (
    <>
      <SEO title={`${product.name} — NAWA`} description={product.shortDescription} />

      <section className="section product-detail">
        <div className="container product-detail-grid">
          <div className="product-gallery">
            <div className="product-media" style={images[activeImage] ? { backgroundImage: `url(${images[activeImage].image})`, backgroundSize: "cover", backgroundPosition: "center" } : {}} />
            {images.length > 1 && (
              <div className="gallery-thumbs">
                {images.map((img, i) => (
                  <button key={img.id} className={`gallery-thumb${activeImage === i ? " active" : ""}`} style={{ backgroundImage: `url(${img.image})`, backgroundSize: "cover" }} onClick={() => setActiveImage(i)} aria-label={`Photo ${i + 1}`} />
                ))}
              </div>
            )}
          </div>

          <div className="product-info">
            <nav className="breadcrumb">
              <Link to={`/boutique/${product.category?.slug}`}>{product.category?.name}</Link>
            </nav>
            <h1>{product.name}</h1>
            {product.brand && <p className="muted">{product.brand.name}</p>}
            <p className="product-price">
              {formatPrice(effectivePrice, product.currency)}
              {product.compareAtPrice && <span className="muted"> — au lieu de {formatPrice(product.compareAtPrice, product.currency)}</span>}
            </p>
            <p className="product-short">{product.shortDescription}</p>

            {Object.entries(variantOptions).map(([code, values]) => (
              <div className="variant-picker" key={code}>
                <h4>{attributeLabel(code)}</h4>
                <div className="filter-list" style={{ flexDirection: "row", flexWrap: "wrap" }}>
                  {values.map((value) => (
                    <button
                      key={value}
                      className={selectedAttrs[code] === value ? "active" : ""}
                      onClick={() => setSelectedAttrs((prev) => ({ ...prev, [code]: value }))}
                    >
                      {value}
                    </button>
                  ))}
                </div>
              </div>
            ))}

            {displayAttributes.length > 0 && (
              <div className="producer-mini">
                {displayAttributes.map(([code, value]) => (
                  <div key={code}><strong>{attributeLabel(code)} :</strong> {Array.isArray(value) ? value.join(", ") : String(value)}</div>
                ))}
              </div>
            )}

            {product.productType === "booking" ? (
              <RouterLink to={`/reservations/${product.slug}`} className="btn btn-primary btn-lg">Voir les créneaux disponibles</RouterLink>
            ) : (
              <>
                <div className="quantity-row">
                  <div className="quantity-picker">
                    <button onClick={() => setQuantity((q) => Math.max(1, q - 1))}>−</button>
                    <span>{quantity}</span>
                    <button onClick={() => setQuantity((q) => q + 1)}>+</button>
                  </div>
                  <button className="btn btn-primary btn-lg" disabled={!inStock || needsSelection || adding} onClick={handleAddToCart}>
                    {needsSelection ? "Choisir une option" : inStock ? (adding ? <ButtonSpinner label="Ajout…" /> : "Ajouter au panier") : "Épuisé"}
                  </button>
                </div>
                {addedMessage && <p className="newsletter-success">{addedMessage}</p>}
              </>
            )}

            <div className="tabs-panel">
              <h3>Description</h3>
              <p>{product.description || product.shortDescription}</p>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
