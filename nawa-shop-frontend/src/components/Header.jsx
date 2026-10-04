import { useState } from "react";
import MegaMenuHeader from "./MegaMenuHeader";
import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { useCart } from "../context/CartContext.jsx";

export default function Header() {
  const { isAuthenticated, isShopManager, user, logout } = useAuth();
  const { itemCount } = useCart();
  const [menuOpen, setMenuOpen] = useState(false);
  const [accountOpen, setAccountOpen] = useState(false);

  return (
    <header className="site-header">
      <div className="container header-inner">
        <Link to="/" className="logo">NAWA</Link>

        <button className="menu-toggle" onClick={() => setMenuOpen((v) => !v)} aria-label="Menu">
          <span /><span /><span />
        </button>

        <div className={`nav-backdrop ${menuOpen ? "is-open" : ""}`} onClick={() => setMenuOpen(false)} />
        <nav className={`main-nav ${menuOpen ? "is-open" : ""}`}>
          <NavLink to="/boutique/cosmetiques" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>Cosmétiques</NavLink>
          <NavLink to="/boutique/vetements" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>Vêtements</NavLink>
          <NavLink to="/boutique/chaussures" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>Chaussures</NavLink>
          <NavLink to="/boutique/electromenager" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>Électroménager</NavLink>
          <NavLink to="/journal" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>Journal</NavLink>
          {isShopManager && <NavLink to="/gestion/commandes" className="nav-link nav-link-cta">Gestion</NavLink>}
        </nav>

        <div className="header-actions">
          <div className="account-menu">
            <button className="icon-link" onClick={() => setAccountOpen((v) => !v)} aria-label="Mon compte">
              <span className="icon">👤</span>
            </button>
            {accountOpen && (
              <div className="account-dropdown" onMouseLeave={() => setAccountOpen(false)}>
                {isAuthenticated ? (
                  <>
                    <div className="account-dropdown-name">{user?.firstName || user?.username}</div>
                    <Link to="/compte" onClick={() => setAccountOpen(false)}>Mon profil</Link>
                    <Link to="/compte/commandes" onClick={() => setAccountOpen(false)}>Mes commandes</Link>
                    <Link to="/compte/fidelite" onClick={() => setAccountOpen(false)}>Fidélité</Link>
                    <Link to="/compte/abonnements" onClick={() => setAccountOpen(false)}>Abonnements</Link>
                    <Link to="/compte/factures" onClick={() => setAccountOpen(false)}>Factures</Link>
                    <Link to="/compte/adresses" onClick={() => setAccountOpen(false)}>Adresses</Link>
                    <button onClick={() => { logout(); setAccountOpen(false); }}>Se déconnecter</button>
                  </>
                ) : (
                  <>
                    <Link to="/connexion" onClick={() => setAccountOpen(false)}>Connexion</Link>
                    <Link to="/inscription" onClick={() => setAccountOpen(false)}>Créer un compte</Link>
                  </>
                )}
              </div>
            )}
          </div>
          <Link to="/panier" className="icon-link" aria-label="Panier">
            <span className="icon">🛍️</span>
            {itemCount > 0 && <span className="cart-badge">{itemCount}</span>}
          </Link>
        </div>
      </div>
    </header>
  );
}
