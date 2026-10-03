import { Link } from "react-router-dom";
import SEO from "../components/SEO.jsx";

export default function NotFound() {
  return (
    <>
      <SEO title="Page introuvable — NAWA" description="Cette page n'existe pas." />
      <section className="section not-found">
        <div className="container">
          <h1>404</h1>
          <p>Cette page n'existe pas ou plus.</p>
          <Link to="/" className="btn btn-primary">Retour à l'accueil</Link>
        </div>
      </section>
    </>
  );
}
