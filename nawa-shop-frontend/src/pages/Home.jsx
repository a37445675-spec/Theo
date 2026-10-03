import { useEffect, useState } from "react";
import { getTemplate } from "../api/cms.js";
import BlockRenderer from "../components/blocks/BlockRenderer.jsx";
import HeroBlock from "../components/blocks/HeroBlock.jsx";
import ProductGridBlock from "../components/blocks/ProductGridBlock.jsx";
import BlogListBlock from "../components/blocks/BlogListBlock.jsx";

export default function Home() {
  const [template, setTemplate] = useState(undefined);

  useEffect(() => {
    getTemplate("home")
      .then(setTemplate)
      .catch(() => setTemplate(null));
  }, []);

  // Le gabarit "Accueil" est piloté par le Theme Builder headless
  // (apps.cms) : si le backend en expose un, on le rend tel quel. Sinon,
  // repli sur une composition par défaut équivalente — jamais d'écran vide.
  if (template) {
    return <BlockRenderer blocks={template.blocks} />;
  }

  return (
    <>
      <HeroBlock config={{}} />
      <ProductGridBlock config={{ title: "Nos coups de cœur", source: "featured", columns: 4 }} />
      <BlogListBlock config={{ limit: 3 }} />
    </>
  );
}
