import { useNavigation } from "../context/NavigationContext";
import DynamicMenu from "./DynamicMenu";

/**
 * Pied de page dynamique piloté par le CMS.
 * Affiche le menu de location "footer".
 */
export default function DynamicFooter() {
  const { getMenu, loading } = useNavigation();
  const menu = getMenu("footer");

  if (loading) return null;

  return (
    <footer className="site-footer">
      <div className="container footer-inner">
        <div className="footer-brand">
          <h3>NAWA</h3>
          <p>La beauté d'Afrique, sublimée.</p>
        </div>

        {menu && menu.items && menu.items.length > 0 && (
          <nav className="footer-nav-wrapper">
            <h4>Informations</h4>
            <DynamicMenu location="footer" className="footer-nav" />
          </nav>
        )}

        <div className="footer-copyright">
          <p>© {new Date().getFullYear()} NAWA Commerce. Tous droits réservés.</p>
        </div>
      </div>
    </footer>
  );
}
