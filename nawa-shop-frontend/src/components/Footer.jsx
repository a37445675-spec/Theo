import DynamicMenu from "./DynamicMenu";

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="container footer-inner">
        {/* Colonne 1 : Marque */}
        <div className="footer-col footer-brand">
          <h3>NAWA</h3>
          <p>La beauté d'Afrique, sublimée.</p>
        </div>

        {/* Colonne 2 : Liens (dynamique via le CMS) */}
        <div className="footer-col">
          <h4>Informations</h4>
          <DynamicMenu location="footer" className="footer-nav" />
        </div>

        {/* Colonne 3 : Contact */}
        <div className="footer-col">
          <h4>Contact</h4>
          <p>contact@nawa.com</p>
          <p>Abidjan, Côte d'Ivoire</p>
        </div>
      </div>

      <div className="container footer-copyright">
        <p>
          © {new Date().getFullYear()} NAWA Commerce. Tous droits réservés.
        </p>
      </div>
    </footer>
  );
}