import { Link } from "react-router-dom";
import { useCart } from "../context/CartContext.jsx";
import { formatPrice } from "../utils.js";
import { EmptyState } from "../components/StateBlocks.jsx";
import { SkeletonGrid } from "../components/Skeleton.jsx";
import SEO from "../components/SEO.jsx";

export default function Cart() {
  const { cart, loading, updateQuantity, removeLine } = useCart();

  return (
    <>
      <SEO title="Mon panier — NAWA" description="Votre panier NAWA." />

      <section className="page-header">
        <div className="container"><h1>Mon panier</h1></div>
      </section>

      <section className="section">
        <div className="container">
          {loading && <SkeletonGrid count={2} />}

          {!loading && (!cart || cart.lines.length === 0) && (
            <EmptyState icon="🛍️" title="Votre panier est vide" action={<Link to="/boutique/cosmetiques" className="btn btn-primary">Découvrir la boutique</Link>} />
          )}

          {!loading && cart && cart.lines.length > 0 && (
            <div className="cart-layout">
              <div className="cart-items">
                {cart.lines.map((line) => (
                  <div className="cart-row" key={line.id}>
                    <div className="cart-row-media" style={line.product.coverImage ? { backgroundImage: `url(${line.product.coverImage})`, backgroundSize: "cover" } : {}} />
                    <div className="cart-row-info">
                      <Link to={`/produit/${line.product.slug}`}>{line.product.name}</Link>
                      {line.variant && <span className="muted">{Object.values(line.variant.attributes || {}).join(" · ")}</span>}
                      <span className="muted">{formatPrice(line.unitPrice, cart.currency)} / unité</span>
                    </div>
                    <div className="quantity-picker">
                      <button onClick={() => updateQuantity(line.id, line.quantity - 1)}>−</button>
                      <span>{line.quantity}</span>
                      <button onClick={() => updateQuantity(line.id, line.quantity + 1)}>+</button>
                    </div>
                    <span className="cart-row-total">{formatPrice(line.lineTotal, cart.currency)}</span>
                    <button className="cart-row-remove" onClick={() => removeLine(line.id)} aria-label="Retirer">✕</button>
                  </div>
                ))}
              </div>

              <div className="cart-summary">
                <h2>Résumé</h2>
                <div className="summary-line"><span>Sous-total</span><span>{formatPrice(cart.subtotal, cart.currency)}</span></div>
                <div className="summary-line muted"><span>Frais de livraison</span><span>Calculés à l'étape suivante</span></div>
                <div className="summary-line total"><span>Total estimé</span><span>{formatPrice(cart.subtotal, cart.currency)}</span></div>
                <Link to="/commande" className="btn btn-primary btn-lg btn-block">Passer la commande</Link>
              </div>
            </div>
          )}
        </div>
      </section>
    </>
  );
}
