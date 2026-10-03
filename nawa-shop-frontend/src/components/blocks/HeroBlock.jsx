import { Link } from "react-router-dom";
import Reveal from "../Reveal.jsx";

export default function HeroBlock({ config }) {
  // Si l'image n'est pas définie dans le CMS, on utilise une image par défaut
  const imageUrl = config?.image || "https://files.catbox.moe/cwkin3.jpg";

  return (
    <section className="hero">
      <div className="hero-halo" />
      <div className="container hero-inner">
        <Reveal className="hero-copy hero-anim">
          <span className="eyebrow">Marketplace NAWA</span>
          
          {/* J'ai ajouté les "||" qui manquaient pour les valeurs par défaut */}
          <h1>{config?.title || "La beauté d'Afrique, sublimée."}</h1>
          <p>{config?.subtitle || "Cosmétiques naturels, mode, chaussures et électroménager — une seule marketplace, un même souci du détail."}</p>
          
          <div className="hero-actions">
            <Link to="/boutique/cosmetiques" className="btn btn-primary btn-lg">Découvrir la boutique</Link>
            <Link to="/journal" className="btn btn-ghost btn-lg">Lire le journal</Link>
          </div>
        </Reveal>

        {/* C'est ici que l'image est ajoutée ! */}
        <Reveal as="div" className="hero-visual hero-anim">
          <img 
            src={imageUrl} 
            alt={config?.title || "La beauté d'Afrique, sublimée"} 
            className="hero-image" 
          />
        </Reveal>
      </div>
    </section>
  );
}
