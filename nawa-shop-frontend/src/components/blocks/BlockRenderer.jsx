import HeroBlock from "./HeroBlock.jsx";
import HeadingBlock from "./HeadingBlock.jsx";
import TextBlock from "./TextBlock.jsx";
import ImageBlock from "./ImageBlock.jsx";
import ButtonBlock from "./ButtonBlock.jsx";
import ProductGridBlock from "./ProductGridBlock.jsx";
import BlogListBlock from "./BlogListBlock.jsx";
import FAQBlock from "./FAQBlock.jsx";

/**
 * Dispatcher central du Theme Builder headless : chaque `block_type` renvoyé
 * par /api/v1/cms/templates/ est résolu vers son composant React. Ajouter un
 * nouveau type de bloc côté backend (apps/cms/models.py::PageBlockType) +
 * son composant ici suffit à l'exposer partout où un gabarit l'utilise.
 */
const BLOCK_COMPONENTS = {
  hero: HeroBlock,
  heading: HeadingBlock,
  text: TextBlock,
  image: ImageBlock,
  button: ButtonBlock,
  product_grid: ProductGridBlock,
  blog_list: BlogListBlock,
  faq: FAQBlock,
};

export default function BlockRenderer({ blocks }) {
  return (
    <>
      {(blocks || [])
        .filter((block) => block.isVisible !== false)
        .map((block) => {
          const Component = BLOCK_COMPONENTS[block.blockType];
          if (!Component) return null;
          return <Component key={block.id} config={block.config} dynamicContent={block.dynamicContent} />;
        })}
    </>
  );
}
