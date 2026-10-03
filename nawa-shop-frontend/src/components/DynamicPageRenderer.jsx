import { useApi } from "../hooks/useApi";

// Registre des composants de blocs disponibles
const BLOCK_COMPONENTS = {
  // hero: HeroBlock,
  // product_grid: ProductGridBlock,
  // blog_list: BlogListBlock,
  // banner: BannerBlock,
  // cta: CtaBlock,
  // text: TextBlock,
};

/**
 * Rend une page dynamique en boucle sur ses blocs.
 * Usage : <DynamicPageRenderer templateId={1} />
 */
export default function DynamicPageRenderer({ templateId }) {
  const { data: page, loading, error } = useApi(`/api/v1/cms/templates/${templateId}/`);

  if (loading) return <div className="page-loading">Chargement...</div>;
  if (error) return <div className="page-error">Erreur : {error}</div>;
  if (!page) return null;

  const blocks = (page.blocks || [])
    .filter((b) => b.is_visible)
    .sort((a, b) => a.order - b.order);

  return (
    <div className="dynamic-page">
      {blocks.map((block) => {
        const Component = BLOCK_COMPONENTS[block.block_type];
        return (
          <section key={block.id} className={`block block-${block.block_type}`}>
            {block.title && (
              <div className="container section-header">
                <h2 className="section-title">{block.title}</h2>
                {block.subtitle && <p className="section-subtitle">{block.subtitle}</p>}
              </div>
            )}
            {Component ? (
              <Component config={block.config} />
            ) : (
              <div className="container block-placeholder">
                Bloc de type <code>{block.block_type}</code> non implémenté.
              </div>
            )}
          </section>
        );
      })}
    </div>
  );
}
